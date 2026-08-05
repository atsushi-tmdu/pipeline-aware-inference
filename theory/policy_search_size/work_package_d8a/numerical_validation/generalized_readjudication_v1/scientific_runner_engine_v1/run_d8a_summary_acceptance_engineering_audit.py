#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from d8a_runner_acceptance import (
    aggregate_combined_policy_acceptance,
    aggregate_exact_identity,
    aggregate_precision_limited,
    aggregate_reference_acceptance,
    aggregate_tess_acceptance,
    formal_acceptance,
)
from d8a_runner_precision_scales import (
    build_job_scale_spec,
)
from d8a_runner_summary import (
    summarize_job_rows,
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
    class_map = {
        item["class_id"]: item
        for item in classes
    }
    job_map = {
        item["job_id"]: item
        for item in jobs
    }

    smoke_summaries = []
    for batch in sorted(
        (
            engine
            / "engineering_smoke"
            / "jobs"
        ).glob(
            "*/batches/*.jsonl"
        )
    ):
        rows = load_rows(batch)
        job = job_map[
            rows[0]["job_id"]
        ]
        class_record = class_map[
            job["class_id"]
        ]
        scale_spec = build_job_scale_spec(
            job,
            class_record,
            rows[0],
        )
        smoke_summaries.append(
            summarize_job_rows(
                rows,
                scale_spec,
            )
        )

    reference_records = [
        {
            "class_id": (
                f"d8a-primary-{index:03d}"
            ),
            "normalized_residual_B500": 0.20,
            "normalized_residual_B10000": 0.10,
            "second_order_improved": (
                index < 13
            ),
        }
        for index in range(17)
    ]
    combined_records = [
        {
            "class_id": (
                f"d8a-primary-{index:03d}"
            ),
            "normalized_residual": 0.10,
        }
        for index in range(17)
    ]
    tess_records = [
        {
            "class_id": (
                f"d8a-primary-{index:03d}"
            ),
            "alpha": alpha,
            "normalized_residual": 0.20,
            "nonfinite_record_count": 0,
        }
        for alpha in (0.01, 0.05)
        for index in range(17)
    ]
    exact_records = [
        {"passed": True}
        for _ in range(34)
    ]

    reference = (
        aggregate_reference_acceptance(
            reference_records
        )
    )
    combined = (
        aggregate_combined_policy_acceptance(
            combined_records
        )
    )
    tess = aggregate_tess_acceptance(
        tess_records,
        alpha_values=(0.01, 0.05),
    )
    exact = aggregate_exact_identity(
        exact_records,
        expected_comparisons=34,
    )
    precision = (
        aggregate_precision_limited(
            ["d8a-primary-000"]
        )
    )
    formal = formal_acceptance(
        reference=reference,
        combined_policy=combined,
        tess=tess,
        exact_identity=exact,
        precision_limited=precision,
        fatal_checks_pass=True,
    )

    failing_tess_records = list(
        tess_records
    )
    failing_tess_records[0] = {
        **failing_tess_records[0],
        "nonfinite_record_count": 1,
    }
    failing_tess = (
        aggregate_tess_acceptance(
            failing_tess_records,
            alpha_values=(0.01, 0.05),
        )
    )
    failing_formal = formal_acceptance(
        reference=reference,
        combined_policy=combined,
        tess=failing_tess,
        exact_identity=exact,
        precision_limited=precision,
        fatal_checks_pass=True,
    )

    failures = []
    if len(smoke_summaries) != 6:
        failures.append(
            "expected six smoke summaries"
        )
    if formal["formal_status"] != "PASS":
        failures.append(
            "synthetic passing fixture failed"
        )
    if (
        failing_formal["formal_status"]
        != "FAIL"
    ):
        failures.append(
            "TESS boundary failure did not "
            "propagate"
        )

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "smoke_jobs_summarized": (
            len(smoke_summaries)
        ),
        "smoke_summaries": smoke_summaries,
        "synthetic_passing_acceptance": {
            "reference": reference,
            "combined_policy": combined,
            "tess": tess,
            "exact_identity": exact,
            "precision_limited": precision,
            "formal": formal,
        },
        "synthetic_tess_boundary_failure": {
            "tess": failing_tess,
            "formal": failing_formal,
        },
        "engineering_audit_pass": (
            not failures
        ),
        "runner_engine_locked": False,
        "scientific_output_root_touched": False,
    }

    output = (
        engine
        / "summary_acceptance_engineering_audit"
    )
    output.mkdir(
        parents=True,
        exist_ok=True,
    )
    (
        output
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_summary_acceptance_audit.json"
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
            "D8-A summary/acceptance "
            "engineering audit: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A summary/acceptance "
        "engineering audit"
    )
    print("=" * 80)
    print("Status: PASS")
    print("Engineering smoke jobs summarized: 6")
    print(
        "Synthetic passing fixture: PASS"
    )
    print(
        "Synthetic TESS-boundary fixture: FAIL"
    )
    print(
        "Primary acceptance denominator: 17"
    )
    print(
        "Maximum precision-limited "
        "primary classes: 1"
    )
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
