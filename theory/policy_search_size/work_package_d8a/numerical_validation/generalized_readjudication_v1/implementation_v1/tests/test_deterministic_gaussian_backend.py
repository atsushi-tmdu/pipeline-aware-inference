from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np
from scipy.stats import norm

from d8a_deterministic_gaussian import (
    bvn_cdf,
    linear_gaussian_cdf,
    mvn3_cdf,
)
from d8a_generalized_oracle import (
    all_target_reference_oracle,
    generalized_directional_approximation,
    theta_from_class,
)
from d8a_policy_engine import (
    _genz_linear_gaussian_cdf_legacy,
    _linear_gaussian_cdf,
    policy_population_probabilities,
)


ROOT = Path(__file__).resolve().parents[1]
CLASSES = json.loads(
    (
        ROOT.parents[0]
        / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
    ).read_text(encoding="utf-8")
)


class DeterministicGaussianBackendTests(
    unittest.TestCase
):
    def test_bvn_independence(self) -> None:
        left, right = 0.4, -0.3
        self.assertAlmostEqual(
            bvn_cdf(
                left,
                right,
                0.0,
            ),
            norm.cdf(left)
            * norm.cdf(right),
            places=13,
        )

    def test_bvn_zero_threshold_arcsine_identity(
        self,
    ) -> None:
        correlation = 0.4
        expected = (
            0.25
            + math.asin(correlation)
            / (2.0 * math.pi)
        )
        self.assertAlmostEqual(
            bvn_cdf(
                0.0,
                0.0,
                correlation,
            ),
            expected,
            places=12,
        )

    def test_trivariate_independence(self) -> None:
        bounds = np.array(
            [0.2, -0.4, 0.7],
            dtype=float,
        )
        expected = float(
            np.prod(
                norm.cdf(bounds)
            )
        )
        self.assertAlmostEqual(
            mvn3_cdf(
                bounds,
                np.eye(3),
            ),
            expected,
            places=10,
        )

    def test_linear_identity_map(self) -> None:
        bounds = np.array(
            [0.1, -0.2],
            dtype=float,
        )
        correlation = np.array(
            [
                [1.0, 0.3],
                [0.3, 1.0],
            ]
        )
        self.assertAlmostEqual(
            linear_gaussian_cdf(
                np.eye(2),
                bounds,
                correlation,
            ),
            bvn_cdf(
                bounds[0],
                bounds[1],
                0.3,
            ),
            places=12,
        )

    def test_production_backend_is_not_genz(
        self,
    ) -> None:
        self.assertIsNot(
            _linear_gaussian_cdf,
            _genz_linear_gaussian_cdf_legacy,
        )

    def test_independent_policy_closed_form(
        self,
    ) -> None:
        probability = 0.90
        candidate = float(
            norm.ppf(probability)
        )
        trigger_probability = 0.50
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
        expected_base = (
            1.0 - probability**2
        )
        self.assertAlmostEqual(
            result[
                "incremental_probability"
            ],
            expected_incremental,
            places=10,
        )
        self.assertAlmostEqual(
            result[
                "joint_am_probability"
            ],
            expected_joint,
            places=10,
        )
        self.assertAlmostEqual(
            result["base_probability"],
            expected_base,
            places=10,
        )

    def test_selected_directional_expansions(
        self,
    ) -> None:
        maximum = 0.0
        selected = (
            CLASSES[0],
            CLASSES[12],
            CLASSES[16],
            CLASSES[-1],
        )
        directions = (
            np.array(
                [1.0, 0.3, -0.8, 0.2]
            ),
            np.array(
                [-0.7, 1.0, 0.2, -0.2]
            ),
        )
        for class_record in selected:
            oracle = all_target_reference_oracle(
                class_record,
                500,
            )
            for target_name in (
                "delta_pi",
                "adaptive_probability",
                "comparator_probability",
            ):
                for direction in directions:
                    exact, approximation = (
                        generalized_directional_approximation(
                            target_name,
                            class_record,
                            direction,
                            0.002,
                            oracle,
                        )
                    )
                    maximum = max(
                        maximum,
                        abs(
                            exact
                            - approximation
                        )
                        / 0.002**2,
                    )
        self.assertLess(
            maximum,
            1e-4,
        )

    def test_all_class_values_are_finite(
        self,
    ) -> None:
        for class_record in CLASSES:
            result = (
                policy_population_probabilities(
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
            )
            scalar_values = [
                value
                for key, value in result.items()
                if key
                not in {
                    "base_parts",
                    "incremental_parts",
                    "joint_parts",
                }
            ]
            self.assertTrue(
                np.all(
                    np.isfinite(
                        scalar_values
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
