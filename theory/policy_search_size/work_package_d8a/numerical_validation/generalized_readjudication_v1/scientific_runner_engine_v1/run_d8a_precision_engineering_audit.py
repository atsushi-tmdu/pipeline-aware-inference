#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

from d8a_runner_precision import (
    evaluate_job_precision,
)
from d8a_runner_precision_scales import (
    build_job_scale_spec,
)


LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def load_rows(
    path: Path,
) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
    ]


def projected_replicates(
    replicate_count: int,
    scaled_mcse: float,
    target: float,
) -> int:
    if scaled_mcse <= target:
        return int(replicate_count)
    return int(
        math.ceil(
            replicate_count
            * (
                scaled_mcse
                / target
            ) ** 2
        )
    )


def main() -> None:
    engine = Path(__file__).resolve().parent
    generalized = engine.parent
    run_package = (
        generalized
        / "scientific_run_prelock_v1"
    )
    smoke = engine / "engineering_smoke"

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
    class_map = {
        item["class_id"]: item
        for item in classes
    }
    job_map = {
        item["job_id"]: item
        for item in jobs
    }

    job_results = []
    failures = []

    for batch in sorted(
        (smoke / "jobs").glob(
            "*/batches/*.jsonl"
        )
    ):
        rows = load_rows(batch)
        job_id = str(rows[0]["job_id"])
        job = job_map[job_id]
        class_record = class_map[
            job["class_id"]
        ]
        scale_spec = build_job_scale_spec(
            job,
            class_record,
            rows[0],
        )
        result = evaluate_job_precision(
            rows,
            scale_spec,
            target=0.03,
        )
        projected = projected_replicates(
            len(rows),
            float(
                result[
                    "maximum_scaled_mcse"
                ]
            ),
            0.03,
        )
        job_results.append(
            {
                "result": result,
                "scale_spec": scale_spec,
                "engineering_projected_replicates": (
                    projected
                ),
                "class_role": (
                    class_record[
                        "class_role"
                    ]
                ),
            }
        )

        if result["precision_pass"]:
            failures.append(
                f"20-replicate job unexpectedly "
                f"passes: {job_id}"
            )
        if result[
            "maximum_scaled_mcse"
        ] <= 0.0:
            failures.append(
                f"nonpositive scaled MCSE: "
                f"{job_id}"
            )

    if len(job_results) != 6:
        failures.append(
            "expected six engineering jobs"
        )

    distinct_maxima = {
        round(
            float(
                item["result"][
                    "maximum_scaled_mcse"
                ]
            ),
            12,
        )
        for item in job_results
    }

    projections = [
        int(
            item[
                "engineering_projected_replicates"
            ]
        )
        for item in job_results
    ]

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "jobs_evaluated": len(job_results),
        "replicates_per_job": 20,
        "target": 0.03,
        "all_jobs_correctly_fail_at_20": (
            not failures
        ),
        "distinct_maximum_scaled_mcse_values": (
            len(distinct_maxima)
        ),
        "minimum_engineering_projected_replicates": (
            min(projections)
            if projections
            else None
        ),
        "maximum_engineering_projected_replicates": (
            max(projections)
            if projections
            else None
        ),
        "studentized_mcse_constant_rule_used": False,
        "rate_aware_bias_scale_used_for_stopping": False,
        "rate_aware_bias_scale_retained_for_acceptance": True,
        "job_results": job_results,
        "runner_engine_locked": False,
        "scientific_output_root_touched": False,
    }

    output = (
        engine
        / "precision_engineering_audit"
    )
    output.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        output
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_natural_scale_precision_audit_summary.json"
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
            "D8-A natural-scale precision "
            "engineering audit: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A natural-scale precision "
        "engineering audit"
    )
    print("=" * 80)
    print("Status: PASS")
    print("Engineering jobs evaluated: 6")
    print("Replicates per job: 20")
    print(
        "All jobs correctly fail target 0.03: YES"
    )
    print(
        "Distinct maximum scaled-MCSE values: "
        f"{len(distinct_maxima)}"
    )
    print(
        "Minimum projected replicates: "
        f"{min(projections)}"
    )
    print(
        "Maximum projected replicates: "
        f"{max(projections)}"
    )
    print(
        "Studentized constant rule used: NO"
    )
    print(
        "Rate-aware bias scale used "
        "for stopping: NO"
    )
    print(
        "Rate-aware bias scale retained "
        "for acceptance: YES"
    )
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
