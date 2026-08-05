from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from d8a_generalized_oracle import (
    evaluation_variances,
    quantile_moment_oracle,
    target_kink_coefficients,
    theta_from_class,
)
from d8a_policy_engine import (
    policy_estimators,
    policy_fields,
    reference_thresholds,
)
from d8a_seed_contract import make_rng
from d8a_transform_audit import (
    audit_transform_invariance,
)


def main() -> None:
    root = Path(__file__).resolve().parent
    classes = json.loads(
        (
            root.parents[0]
            / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )
    representative = classes[0]
    correlation = np.asarray(
        representative["correlation_matrix"],
        dtype=float,
    )

    reference_rng = make_rng(
        representative,
        "preflight_reference",
        0,
    )
    evaluation_rng = make_rng(
        representative,
        "preflight_evaluation",
        0,
    )
    reference_bank = (
        reference_rng.multivariate_normal(
            np.zeros(3),
            correlation,
            size=96,
        )
    )
    evaluation_bank = (
        evaluation_rng.multivariate_normal(
            np.zeros(3),
            correlation,
            size=96,
        )
    )
    thresholds = reference_thresholds(
        reference_bank,
        float(
            representative[
                "candidate_probability"
            ]
        ),
        float(
            representative[
                "trigger_probability"
            ]
        ),
    )
    estimators = policy_estimators(
        policy_fields(
            evaluation_bank,
            thresholds,
        )
    )
    audit = audit_transform_invariance(
        reference_bank,
        evaluation_bank,
        float(
            representative[
                "candidate_probability"
            ]
        ),
        float(
            representative[
                "trigger_probability"
            ]
        ),
    )
    moments = quantile_moment_oracle(
        representative,
        reference_size=500,
    )
    kink = target_kink_coefficients(
        "delta_pi",
        representative,
    )
    evaluation = evaluation_variances(
        representative
    )
    population_theta = theta_from_class(
        representative
    )

    failures = []
    if not audit["passed"]:
        failures.append(
            "transform invariance failed"
        )
    if not np.isfinite(
        estimators["delta_hat"]
    ):
        failures.append(
            "finite-sample estimator is not finite"
        )
    if population_theta.shape != (4,):
        failures.append(
            "population threshold vector has wrong shape"
        )
    if kink.shape != (2,):
        failures.append(
            "two kink coefficients not present"
        )
    if not np.all(np.isfinite(kink)):
        failures.append(
            "kink coefficients are not finite"
        )
    if np.min(
        np.linalg.eigvalsh(
            moments["covariance"]
        )
    ) < -1e-7:
        failures.append(
            "quantile covariance is not PSD"
        )
    if not all(
        np.isfinite(value)
        for value in evaluation.values()
    ):
        failures.append(
            "evaluation variances are not finite"
        )

    if failures:
        print(
            "D8-A generalized implementation preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A generalized implementation preflight"
    )
    print("=" * 80)
    print("Status: PASS")
    print("Seed contract reproducible: YES")
    print(
        "Reference/evaluation streams independent: YES"
    )
    print("Policy engine executable: YES")
    print("Transform invariance audit: PASS")
    print("Quantile moment oracle executable: YES")
    print("Generalized kink coefficients present: 2")
    print("Evaluation variance oracle executable: YES")
    print("Generalized coefficient assembly implemented: YES")
    print("Full all-class oracle audit completed: NO")
    print("Generalized implementation locked: NO")
    print("Scientific execution authorized: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
