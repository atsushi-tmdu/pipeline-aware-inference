#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

from d8a_runner_engine import (
    simulate_job_replicate,
)
from d8a_runner_io import (
    atomic_write_json,
    atomic_write_jsonl_batch,
    scan_committed_batches,
)
from d8a_runner_seed import (
    SeedInventory,
)


LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def main() -> None:
    engine = Path(__file__).resolve().parent
    generalized = engine.parent
    run_package = (
        generalized
        / "scientific_run_prelock_v1"
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

    diagnostic_classes = [
        item
        for item in classes
        if item["class_role"]
        == "diagnostic"
    ][:2]
    selected_class_ids = {
        item["class_id"]
        for item in diagnostic_classes
    }
    selected_jobs = [
        job
        for job in jobs
        if job["class_id"]
        in selected_class_ids
    ]

    if len(selected_jobs) != 6:
        raise SystemExit(
            "FAIL: expected six engineering jobs"
        )

    class_map = {
        item["class_id"]: item
        for item in diagnostic_classes
    }

    output = (
        engine / "engineering_smoke"
    )
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(
        parents=True,
        exist_ok=False,
    )

    family_counts = {
        "reference_only": 0,
        "evaluation_only": 0,
        "combined": 0,
    }
    total_rows = 0
    all_resume_checks_pass = True
    all_tess_outputs_valid = True

    override = {
        "reference_sizes": [64],
        "evaluation_sizes": [64],
        "combined_pairs": [[64, 64]],
    }

    for job in selected_jobs:
        job_id = str(
            job["job_id"]
        )
        class_record = class_map[
            job["class_id"]
        ]
        rows = []
        for replicate_index in range(20):
            result = simulate_job_replicate(
                job,
                class_record,
                seeds,
                replicate_index,
                engineering_override=override,
            )
            result["label"] = LABEL
            result[
                "scientific_simulation_run"
            ] = False
            rows.append(result)

            from d8a_runner_statistics import (
                tess_status_is_valid,
            )

            for point in result["points"]:
                for value in point[
                    "tess_contrasts"
                ].values():
                    if not tess_status_is_valid(
                        value
                    ):
                        all_tess_outputs_valid = False

        job_directory = (
            output / "jobs" / job_id
        )
        batch = atomic_write_jsonl_batch(
            job_directory,
            job_id,
            rows,
        )
        scan = scan_committed_batches(
            job_directory,
            job_id,
        )
        if (
            scan[
                "next_replicate_index"
            ] != 20
            or scan["row_count"] != 20
            or scan["batch_count"] != 1
        ):
            all_resume_checks_pass = False

        atomic_write_json(
            job_directory
            / "JOB_STATUS.json",
            {
                "label": LABEL,
                "job_id": job_id,
                "scientific_simulation_run": False,
                "batch": batch,
                "scan": scan,
            },
        )
        family_counts[
            job["family"]
        ] += 1
        total_rows += len(rows)

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "classes_executed": 2,
        "family_jobs_executed": 6,
        "replicates_per_job": 20,
        "total_job_replicates": total_rows,
        "family_job_counts": family_counts,
        "engineering_sample_override": override,
        "all_resume_checks_pass": (
            all_resume_checks_pass
        ),
        "all_tess_outputs_valid": (
            all_tess_outputs_valid
        ),
        "scientific_output_root_touched": False,
        "runner_engine_locked": False,
    }
    atomic_write_json(
        output
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_runner_smoke_summary.json",
        summary,
    )

    failures = []
    if total_rows != 120:
        failures.append(
            "unexpected job-replicate count"
        )
    if family_counts != {
        "reference_only": 2,
        "evaluation_only": 2,
        "combined": 2,
    }:
        failures.append(
            "unexpected family job counts"
        )
    if not all_resume_checks_pass:
        failures.append(
            "resume scan failed"
        )
    if not all_tess_outputs_valid:
        failures.append(
            "TESS output validation failed"
        )

    if failures:
        print(
            "D8-A runner engineering smoke: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A runner engineering smoke")
    print("=" * 80)
    print("Status: PASS")
    print("Engineering label: NON_SCIENTIFIC_ENGINEERING_ONLY")
    print("Diagnostic classes executed: 2")
    print("Family jobs executed: 6")
    print("Replicates per job: 20")
    print("Total job-replicates: 120")
    print("Reference-only jobs: 2")
    print("Evaluation-only jobs: 2")
    print("Combined jobs: 2")
    print("Atomic batch writes: PASS")
    print("Resume scans: PASS")
    print("Scientific output root touched: NO")
    print("Runner engine locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
