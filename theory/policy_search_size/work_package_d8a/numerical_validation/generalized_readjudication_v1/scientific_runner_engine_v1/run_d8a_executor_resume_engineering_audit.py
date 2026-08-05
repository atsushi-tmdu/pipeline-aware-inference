#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from d8a_runner_scheduler import (
    deterministic_job_order,
    initialize_run_root,
    load_committed_rows,
    run_family_job,
)
from d8a_runner_seed import (
    SeedInventory,
)
from d8a_runner_stopping import (
    StoppingSchedule,
)


LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def main() -> None:
    engine = Path(__file__).resolve().parent
    generalized = engine.parent
    run_package = (
        generalized
        / "scientific_run_prelock_v1"
    )
    repo = Path(
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                "--show-toplevel",
            ],
            cwd=engine,
            text=True,
        ).strip()
    )

    run_config = json.loads(
        (
            run_package
            / "D8A_SCIENTIFIC_RUN_CONFIG.json"
        ).read_text(encoding="utf-8")
    )
    scientific_root = (
        repo
        / run_config[
            "output_root_relative_to_repo"
        ]
    )
    if scientific_root.exists():
        raise SystemExit(
            "FAIL: scientific output root exists"
        )

    classes = json.loads(
        (
            generalized
            / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )
    jobs = json.loads(
        (
            run_package
            / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )
    seeds = SeedInventory(
        run_package
        / "D8A_SCIENTIFIC_SEED_INVENTORY.json"
    )
    class_map = {
        item["class_id"]: item
        for item in classes
    }

    diagnostic_ids = [
        item["class_id"]
        for item in classes
        if item["class_role"]
        == "diagnostic"
    ][:2]
    selected = [
        job
        for job in deterministic_job_order(
            jobs
        )
        if job["class_id"]
        in diagnostic_ids
    ]
    if len(selected) != 6:
        raise SystemExit(
            "FAIL: expected six selected jobs"
        )

    audit_root = (
        engine
        / "executor_resume_engineering_audit"
    )
    if audit_root.exists():
        shutil.rmtree(audit_root)
    resumed_root = (
        audit_root / "resumed_run"
    )
    direct_root = (
        audit_root / "direct_run"
    )

    metadata = {
        "schema_version": "1.0",
        "label": LABEL,
        "run_id": (
            "D8A_EXECUTOR_RESUME_ENGINEERING_AUDIT"
        ),
        "scientific_simulation_run": False,
    }
    initialize_run_root(
        resumed_root,
        metadata,
    )
    initialize_run_root(
        direct_root,
        metadata,
    )

    schedule = StoppingSchedule(
        initial_replicates=8,
        batch_size=4,
        maximum_replicates=20,
    )
    target = 1e-12

    details = []
    failures = []

    for job in selected:
        class_record = class_map[
            job["class_id"]
        ]

        interrupted = run_family_job(
            job=job,
            class_record=class_record,
            seed_inventory=seeds,
            run_root=resumed_root,
            schedule=schedule,
            precision_target=target,
            label=LABEL,
            allow_scientific=False,
            max_new_batches=1,
        )
        if interrupted[
            "replicate_count"
        ] != 8:
            failures.append(
                f"interruption count mismatch: "
                f"{job['job_id']}"
            )
        if interrupted["complete"]:
            failures.append(
                f"interrupted job marked complete: "
                f"{job['job_id']}"
            )

        resumed = run_family_job(
            job=job,
            class_record=class_record,
            seed_inventory=seeds,
            run_root=resumed_root,
            schedule=schedule,
            precision_target=target,
            label=LABEL,
            allow_scientific=False,
        )
        direct = run_family_job(
            job=job,
            class_record=class_record,
            seed_inventory=seeds,
            run_root=direct_root,
            schedule=schedule,
            precision_target=target,
            label=LABEL,
            allow_scientific=False,
        )

        resumed_rows = load_committed_rows(
            resumed_root,
            job["job_id"],
        )
        direct_rows = load_committed_rows(
            direct_root,
            job["job_id"],
        )

        equal_rows = bool(
            resumed_rows == direct_rows
        )
        if not equal_rows:
            failures.append(
                f"resume differs from direct: "
                f"{job['job_id']}"
            )
        if (
            resumed["replicate_count"] != 20
            or direct["replicate_count"] != 20
        ):
            failures.append(
                f"maximum count mismatch: "
                f"{job['job_id']}"
            )
        if (
            resumed["stop_reason"]
            != "maximum_replicates_reached"
        ):
            failures.append(
                f"unexpected resume stop reason: "
                f"{job['job_id']}"
            )

        before = json.dumps(
            resumed_rows,
            sort_keys=True,
        )
        idempotent_status = run_family_job(
            job=job,
            class_record=class_record,
            seed_inventory=seeds,
            run_root=resumed_root,
            schedule=schedule,
            precision_target=target,
            label=LABEL,
            allow_scientific=False,
        )
        after_rows = load_committed_rows(
            resumed_root,
            job["job_id"],
        )
        after = json.dumps(
            after_rows,
            sort_keys=True,
        )
        idempotent = bool(
            before == after
            and idempotent_status[
                "replicate_count"
            ] == 20
        )
        if not idempotent:
            failures.append(
                f"completed rerun changed rows: "
                f"{job['job_id']}"
            )

        temporary_files = list(
            (
                resumed_root
                / "jobs"
                / job["job_id"]
            ).rglob("*.tmp")
        )
        if temporary_files:
            failures.append(
                f"temporary files remain: "
                f"{job['job_id']}"
            )

        details.append(
            {
                "job_id": job["job_id"],
                "family": job["family"],
                "interrupted_replicates": (
                    interrupted[
                        "replicate_count"
                    ]
                ),
                "resumed_replicates": (
                    resumed[
                        "replicate_count"
                    ]
                ),
                "direct_replicates": (
                    direct[
                        "replicate_count"
                    ]
                ),
                "resume_matches_direct": (
                    equal_rows
                ),
                "completed_rerun_idempotent": (
                    idempotent
                ),
                "temporary_files_remaining": (
                    len(temporary_files)
                ),
            }
        )

    executor = (
        engine
        / "execute_d8a_scientific_run.py"
    )
    refusal = subprocess.run(
        [
            sys.executable,
            str(executor),
            "--execute",
        ],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    executor_refused = bool(
        refusal.returncode == 2
        and "Execution authorization: REFUSED"
        in (
            refusal.stdout
            + refusal.stderr
        )
    )
    if not executor_refused:
        failures.append(
            "executor did not refuse without lock"
        )
    if scientific_root.exists():
        failures.append(
            "scientific output root was touched"
        )

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "jobs_tested": len(details),
        "interruption_point": 8,
        "resume_target": 20,
        "details": details,
        "resume_matches_direct": all(
            item[
                "resume_matches_direct"
            ]
            for item in details
        ),
        "completed_rerun_idempotent": all(
            item[
                "completed_rerun_idempotent"
            ]
            for item in details
        ),
        "executor_refused_without_lock": (
            executor_refused
        ),
        "executor_refusal_returncode": (
            refusal.returncode
        ),
        "scientific_output_root_touched": (
            scientific_root.exists()
        ),
        "engineering_audit_pass": (
            not failures
        ),
        "runner_engine_locked": False,
    }
    (
        audit_root
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_executor_resume_audit.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    if failures:
        print(
            "D8-A executor/resume "
            "engineering audit: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A executor/resume engineering audit"
    )
    print("=" * 80)
    print("Status: PASS")
    print("Diagnostic classes tested: 2")
    print("Family jobs tested: 6")
    print("Interrupted at replicates: 8")
    print("Resumed to replicates: 20")
    print("Resume matches direct execution: YES")
    print("Completed rerun idempotent: YES")
    print("Temporary files remaining: 0")
    print("Executor without lock: REFUSED")
    print("Final execution gate: CLOSED")
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
