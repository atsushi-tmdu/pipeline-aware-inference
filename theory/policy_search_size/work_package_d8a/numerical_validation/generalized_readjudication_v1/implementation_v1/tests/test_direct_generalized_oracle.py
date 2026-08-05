from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
from scipy.stats import norm

from d8a_generalized_oracle import (
    all_target_reference_oracle,
    generalized_directional_approximation,
    theta_from_class,
)
from d8a_policy_engine import (
    mvn3_cdf,
    policy_population_probabilities,
)


ROOT = Path(__file__).resolve().parents[1]
CLASSES = json.loads(
    (
        ROOT.parents[0]
        / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
    ).read_text(encoding="utf-8")
)


class DirectOracleTests(unittest.TestCase):
    def test_independent_equal_threshold_closed_form(self) -> None:
        probability = 0.90
        trigger_probability = 0.50
        candidate = float(
            norm.ppf(probability)
        )
        trigger = float(
            norm.ppf(
                trigger_probability**0.5
            )
        )
        result = policy_population_probabilities(
            np.array(
                [
                    candidate,
                    candidate,
                    candidate,
                    trigger,
                ]
            ),
            np.eye(3),
        )
        expected_incremental = (
            probability**2
            * (1.0 - probability)
        )
        expected_joint = (
            probability**2
            - trigger_probability
        ) * (1.0 - probability)
        self.assertAlmostEqual(
            result["incremental_probability"],
            expected_incremental,
            places=7,
        )
        self.assertAlmostEqual(
            result["joint_am_probability"],
            expected_joint,
            places=7,
        )

    def test_equal_threshold_incremental_cdf_identity(self) -> None:
        class_record = CLASSES[0]
        theta = theta_from_class(
            class_record
        )
        correlation = np.asarray(
            class_record[
                "correlation_matrix"
            ],
            dtype=float,
        )
        result = policy_population_probabilities(
            theta,
            correlation,
        )
        q = float(theta[0])
        base_lower = result[
            "incremental_probability"
        ]
        direct = (
            mvn3_cdf(
                np.array(
                    [q, q, np.inf]
                ),
                correlation,
            )
            - mvn3_cdf(
                np.array(
                    [q, q, q]
                ),
                correlation,
            )
        )
        self.assertAlmostEqual(
            base_lower,
            direct,
            places=6,
        )

    def test_all_class_population_probabilities_are_finite(self) -> None:
        for class_record in CLASSES:
            result = policy_population_probabilities(
                theta_from_class(
                    class_record
                ),
                np.asarray(
                    class_record[
                        "correlation_matrix"
                    ],
                    dtype=float,
                ),
            )
            self.assertTrue(
                all(
                    np.isfinite(value)
                    for key, value in result.items()
                    if key
                    not in {
                        "base_parts",
                        "incremental_parts",
                        "joint_parts",
                    }
                )
            )

    def test_vectorized_oracle_has_three_targets(self) -> None:
        oracle = all_target_reference_oracle(
            CLASSES[0],
            500,
            step=0.01,
        )
        self.assertEqual(
            set(oracle["targets"]),
            {
                "delta_pi",
                "adaptive_probability",
                "comparator_probability",
            },
        )

    def test_kink_identity_is_exact_by_assembly(self) -> None:
        oracle = all_target_reference_oracle(
            CLASSES[0],
            500,
            step=0.01,
        )
        for target in oracle[
            "targets"
        ].values():
            self.assertAlmostEqual(
                target[
                    "kink_correction"
                ],
                target[
                    "declared_kink_correction"
                ],
                places=12,
            )

    def test_directional_approximation_is_finite(self) -> None:
        oracle = all_target_reference_oracle(
            CLASSES[0],
            500,
            step=0.01,
        )
        exact, approximation = (
            generalized_directional_approximation(
                "delta_pi",
                CLASSES[0],
                np.array(
                    [1.0, 0.3, -0.8, 0.2]
                ),
                0.001,
                oracle,
            )
        )
        self.assertTrue(
            np.isfinite(exact)
        )
        self.assertTrue(
            np.isfinite(approximation)
        )


if __name__ == "__main__":
    unittest.main()
