from __future__ import annotations

import numpy as np

from d8a_policy_engine import (
    policy_estimators,
    policy_fields,
    reference_thresholds,
    transform_scores,
)


def audit_transform_invariance(
    latent_reference: np.ndarray,
    latent_evaluation: np.ndarray,
    candidate_probability: float,
    trigger_probability: float,
) -> dict[str, object]:
    baseline_thresholds = reference_thresholds(
        latent_reference,
        candidate_probability,
        trigger_probability,
    )
    baseline_fields = policy_fields(
        latent_evaluation,
        baseline_thresholds,
    )
    baseline_estimators = policy_estimators(
        baseline_fields
    )

    reports: dict[str, object] = {}
    for transform_name in (
        "exp_0_35",
        "sinh_0_5",
    ):
        transformed_reference = transform_scores(
            latent_reference,
            transform_name,
        )
        transformed_evaluation = transform_scores(
            latent_evaluation,
            transform_name,
        )
        transformed_thresholds = reference_thresholds(
            transformed_reference,
            candidate_probability,
            trigger_probability,
        )
        transformed_fields = policy_fields(
            transformed_evaluation,
            transformed_thresholds,
        )
        transformed_estimators = policy_estimators(
            transformed_fields
        )

        field_equal = all(
            np.array_equal(
                baseline_fields[field],
                transformed_fields[field],
            )
            for field in (
                "base_winner",
                "full_winner",
                "R0",
                "R1",
                "A",
                "M",
                "H",
            )
        )
        estimator_difference = max(
            abs(
                baseline_estimators[key]
                - transformed_estimators[key]
            )
            for key in baseline_estimators
        )

        reports[transform_name] = {
            "field_equal": field_equal,
            "maximum_estimator_difference": float(
                estimator_difference
            ),
        }

    passed = all(
        report["field_equal"]
        and report[
            "maximum_estimator_difference"
        ]
        <= 1e-15
        for report in reports.values()
    )
    return {
        "passed": passed,
        "reports": reports,
    }
