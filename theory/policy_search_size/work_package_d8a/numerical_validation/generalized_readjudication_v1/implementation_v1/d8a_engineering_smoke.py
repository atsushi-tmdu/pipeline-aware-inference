from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from d8a_policy_engine import (
    policy_estimators,
    policy_fields,
    reference_thresholds,
)
from d8a_seed_contract import make_rng
from d8a_transform_audit import (
    audit_transform_invariance,
)


LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def select_smoke_classes(
    classes: list[dict[str, object]],
    count: int = 2,
) -> list[dict[str, object]]:
    diagnostic = [
        item
        for item in classes
        if item["class_role"] == "diagnostic"
    ]
    if len(diagnostic) < count:
        raise ValueError(
            "not enough diagnostic classes"
        )
    return diagnostic[:count]


def run_engineering_smoke(
    classes: list[dict[str, object]],
    output_dir: Path,
    *,
    replicate_count: int = 20,
    reference_size: int = 64,
    evaluation_size: int = 64,
) -> dict[str, object]:
    if len(classes) > 2:
        raise ValueError(
            "engineering smoke may use at most two classes"
        )
    if replicate_count > 20:
        raise ValueError(
            "engineering smoke may use at most 20 replicates"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    rows: list[dict[str, object]] = []

    for class_record in classes:
        correlation = np.asarray(
            class_record["correlation_matrix"],
            dtype=float,
        )
        candidate_probability = float(
            class_record[
                "candidate_probability"
            ]
        )
        trigger_probability = float(
            class_record[
                "trigger_probability"
            ]
        )

        for replicate_index in range(
            replicate_count
        ):
            reference_rng = make_rng(
                class_record,
                "engineering_reference",
                replicate_index,
            )
            evaluation_rng = make_rng(
                class_record,
                "engineering_evaluation",
                replicate_index,
            )
            reference_bank = (
                reference_rng.multivariate_normal(
                    np.zeros(3),
                    correlation,
                    size=reference_size,
                )
            )
            evaluation_bank = (
                evaluation_rng.multivariate_normal(
                    np.zeros(3),
                    correlation,
                    size=evaluation_size,
                )
            )
            thresholds = reference_thresholds(
                reference_bank,
                candidate_probability,
                trigger_probability,
            )
            fields = policy_fields(
                evaluation_bank,
                thresholds,
            )
            estimators = policy_estimators(
                fields
            )
            audit = audit_transform_invariance(
                reference_bank,
                evaluation_bank,
                candidate_probability,
                trigger_probability,
            )
            rows.append(
                {
                    "label": LABEL,
                    "class_id": class_record[
                        "class_id"
                    ],
                    "replicate_index": replicate_index,
                    "reference_size": reference_size,
                    "evaluation_size": evaluation_size,
                    "delta_hat": estimators[
                        "delta_hat"
                    ],
                    "transform_invariance_pass": (
                        audit["passed"]
                    ),
                }
            )

    csv_path = (
        output_dir
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_results.csv"
    )
    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(
                rows[0].keys()
            ),
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "classes_executed": len(classes),
        "replicates_per_class": replicate_count,
        "total_rows": len(rows),
        "reference_size": reference_size,
        "evaluation_size": evaluation_size,
        "all_transform_invariance_pass": all(
            bool(
                row[
                    "transform_invariance_pass"
                ]
            )
            for row in rows
        ),
        "results_file": csv_path.name,
    }
    (
        output_dir
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_summary.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary
