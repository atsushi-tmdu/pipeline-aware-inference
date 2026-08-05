#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import (
    ProcessPoolExecutor,
    as_completed,
)
from pathlib import Path


ENGINE = Path(__file__).resolve().parent
GENERALIZED = ENGINE.parent
IMPLEMENTATION = (
    GENERALIZED / "implementation_v1"
)
RUN_PACKAGE = (
    GENERALIZED
    / "scientific_run_prelock_v1"
)

for path in (
    ENGINE,
    IMPLEMENTATION,
):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)


def repository_root() -> Path:
    completed = subprocess.run(
        [
            "git",
            "rev-parse",
            "--show-toplevel",
        ],
        cwd=ENGINE,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "cannot resolve repository root"
        )
    return Path(
        completed.stdout.strip()
    ).resolve()


def verify_engine_lock() -> dict[str, object]:
    lock_path = (
        ENGINE
        / "D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK.json"
    )
    verifier = (
        ENGINE
        / "verify_d8a_scientific_runner_engine_lock.py"
    )

    reasons = []
    if not lock_path.is_file():
        reasons.append(
            "runner-engine lock is absent"
        )
    if not verifier.is_file():
        reasons.append(
            "runner-engine lock verifier is absent"
        )

    lock = None
    if lock_path.is_file():
        lock = json.loads(
            lock_path.read_text(
                encoding="utf-8"
            )
        )
        if not lock.get(
            "runner_engine_locked",
            False,
        ):
            reasons.append(
                "runner-engine lock does not "
                "authorize execution"
            )
        if lock.get(
            "scientific_simulation_run",
            False,
        ):
            reasons.append(
                "runner-engine lock is marked "
                "post-execution"
            )

    if not reasons:
        verification = subprocess.run(
            [
                sys.executable,
                str(verifier),
            ],
            cwd=repository_root(),
            check=False,
        )
        if verification.returncode != 0:
            reasons.append(
                "runner-engine lock verifier failed"
            )

    if reasons:
        print("=" * 80)
        print("D8-A scientific executor")
        print("=" * 80)
        print("Execution authorization: REFUSED")
        for reason in reasons:
            print(f"- {reason}")
        print("Scientific output root touched: NO")
        print("Scientific simulation run: NO")
        raise SystemExit(2)

    return lock


def _worker(
    payload: dict[str, object],
) -> dict[str, object]:
    from d8a_runner_scheduler import (
        run_family_job,
    )
    from d8a_runner_seed import (
        SeedInventory,
    )
    from d8a_runner_stopping import (
        StoppingSchedule,
    )

    jobs = json.loads(
        Path(
            payload[
                "job_registry_path"
            ]
        ).read_text(
            encoding="utf-8"
        )
    )
    classes = json.loads(
        Path(
            payload[
                "class_registry_path"
            ]
        ).read_text(
            encoding="utf-8"
        )
    )
    job_map = {
        item["job_id"]: item
        for item in jobs
    }
    class_map = {
        item["class_id"]: item
        for item in classes
    }

    job = job_map[
        payload["job_id"]
    ]
    class_record = class_map[
        job["class_id"]
    ]
    schedule_record = payload[
        "schedules"
    ][
        class_record["class_role"]
    ]
    schedule = StoppingSchedule(
        **schedule_record
    )
    seeds = SeedInventory(
        Path(
            payload[
                "seed_inventory_path"
            ]
        )
    )

    return run_family_job(
        job=job,
        class_record=class_record,
        seed_inventory=seeds,
        run_root=Path(
            payload["run_root"]
        ),
        schedule=schedule,
        precision_target=float(
            payload[
                "precision_target"
            ]
        ),
        label="SCIENTIFIC",
        allow_scientific=True,
        max_new_batches=(
            payload[
                "max_new_batches"
            ]
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--execute",
        action="store_true",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--job-id",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--max-new-batches-per-job",
        type=int,
        default=None,
    )
    arguments = parser.parse_args()

    repo = repository_root()
    run_config = json.loads(
        (
            RUN_PACKAGE
            / "D8A_SCIENTIFIC_RUN_CONFIG.json"
        ).read_text(encoding="utf-8")
    )
    jobs = json.loads(
        (
            RUN_PACKAGE
            / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )

    from d8a_runner_scheduler import (
        deterministic_job_order,
        initialize_run_root,
    )

    ordered = deterministic_job_order(
        jobs
    )
    if arguments.job_id:
        requested = set(
            arguments.job_id
        )
        known = {
            job["job_id"]
            for job in ordered
        }
        unknown = requested - known
        if unknown:
            raise SystemExit(
                "unknown job IDs: "
                + ", ".join(
                    sorted(unknown)
                )
            )
        ordered = [
            job
            for job in ordered
            if job["job_id"]
            in requested
        ]

    run_root = (
        repo
        / run_config[
            "output_root_relative_to_repo"
        ]
    )

    if not arguments.execute:
        print("=" * 80)
        print("D8-A scientific executor plan")
        print("=" * 80)
        print(
            f"Selected family jobs: "
            f"{len(ordered)}"
        )
        print(
            f"Workers: {arguments.workers}"
        )
        print(
            f"Output root: {run_root}"
        )
        print("Scientific execution requested: NO")
        print(
            "Scientific output root touched: NO"
        )
        print("Scientific simulation run: NO")
        return

    if arguments.workers < 1:
        raise SystemExit(
            "--workers must be positive"
        )
    if (
        arguments.max_new_batches_per_job
        is not None
        and arguments.max_new_batches_per_job
        < 1
    ):
        raise SystemExit(
            "--max-new-batches-per-job "
            "must be positive"
        )

    lock = verify_engine_lock()

    precision_contract = json.loads(
        (
            ENGINE
            / "D8A_PROSPECTIVE_NATURAL_SCALE_PRECISION_CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    stopping_contract = json.loads(
        (
            ENGINE
            / "D8A_LOCKED_MONTE_CARLO_CONTRACT.json"
        ).read_text(encoding="utf-8")
    )

    lock_tag = str(lock["lock_tag"])
    lock_commit = subprocess.check_output(
        [
            "git",
            "rev-parse",
            f"{lock_tag}^{{commit}}",
        ],
        cwd=repo,
        text=True,
    ).strip()

    metadata = {
        "schema_version": "1.0",
        "label": "SCIENTIFIC",
        "run_id": (
            "TESS_D8A_GENERALIZED_SCIENTIFIC_RUN_V1"
        ),
        "runner_engine_lock_id": (
            lock["lock_id"]
        ),
        "runner_engine_lock_tag": (
            lock_tag
        ),
        "runner_engine_lock_commit": (
            lock_commit
        ),
        "scientific_job_count": 75,
        "selected_job_ids": [
            job["job_id"]
            for job in ordered
        ],
        "master_seed": run_config[
            "monte_carlo_contract"
        ]["master_seed"],
        "scientific_simulation_run": True,
    }
    initialize_run_root(
        run_root,
        metadata,
    )

    common = {
        "job_registry_path": str(
            RUN_PACKAGE
            / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
        ),
        "class_registry_path": str(
            GENERALIZED
            / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
        ),
        "seed_inventory_path": str(
            RUN_PACKAGE
            / "D8A_SCIENTIFIC_SEED_INVENTORY.json"
        ),
        "run_root": str(run_root),
        "schedules": stopping_contract[
            "normalized_schedules"
        ],
        "precision_target": (
            precision_contract[
                "precision_target_primary"
            ]
        ),
        "max_new_batches": (
            arguments.max_new_batches_per_job
        ),
    }
    payloads = [
        {
            **common,
            "job_id": job["job_id"],
        }
        for job in ordered
    ]

    statuses = []
    if arguments.workers == 1:
        for index, payload in enumerate(
            payloads,
            start=1,
        ):
            status = _worker(payload)
            statuses.append(status)
            print(
                f"[{index}/{len(payloads)}] "
                f"{status['job_id']}: "
                f"{status['stop_reason']} "
                f"R={status['replicate_count']}"
            )
    else:
        with ProcessPoolExecutor(
            max_workers=arguments.workers
        ) as executor:
            future_map = {
                executor.submit(
                    _worker,
                    payload,
                ): payload["job_id"]
                for payload in payloads
            }
            for future in as_completed(
                future_map
            ):
                status = future.result()
                statuses.append(status)
                print(
                    f"{status['job_id']}: "
                    f"{status['stop_reason']} "
                    f"R={status['replicate_count']}"
                )

    statuses.sort(
        key=lambda item: item["job_id"]
    )
    run_status = {
        "schema_version": "1.0",
        "label": "SCIENTIFIC",
        "selected_job_count": len(
            statuses
        ),
        "complete_job_count": sum(
            bool(status["complete"])
            for status in statuses
        ),
        "all_selected_jobs_complete": all(
            bool(status["complete"])
            for status in statuses
        ),
        "precision_limited_primary_classes": sorted(
            {
                status["class_id"]
                for status in statuses
                if status[
                    "precision_limited"
                ]
            }
        ),
        "jobs": statuses,
        "scientific_simulation_run": True,
    }

    from d8a_runner_io import (
        atomic_write_json,
    )
    atomic_write_json(
        run_root / "RUN_STATUS.json",
        run_status,
    )

    print("=" * 80)
    print("D8-A scientific executor")
    print("=" * 80)
    print("Execution authorization: VERIFIED")
    print(
        f"Selected jobs complete: "
        f"{run_status['complete_job_count']}/"
        f"{run_status['selected_job_count']}"
    )
    print(
        "All selected jobs complete: "
        f"{run_status['all_selected_jobs_complete']}"
    )
    print(
        "Scientific output root touched: YES"
    )
    print("Scientific simulation run: YES")


if __name__ == "__main__":
    main()
