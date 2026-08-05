from __future__ import annotations

import unittest

import numpy as np
from scipy.stats import norm

from d8a_policy_engine import (
    base_max_cdf,
    base_max_quantile,
    bvn_cdf,
    empirical_order_quantile,
    policy_estimators,
    policy_fields,
    policy_population_probabilities,
    quantile_order_index,
    reference_thresholds,
)


class PolicyEngineTests(unittest.TestCase):
    def test_quantile_order_index(self) -> None:
        self.assertEqual(
            quantile_order_index(
                100,
                0.95,
            ),
            95,
        )

    def test_empirical_order_quantile(self) -> None:
        values = np.arange(
            1.0,
            11.0,
        )
        self.assertEqual(
            empirical_order_quantile(
                values,
                0.50,
            ),
            5.0,
        )

    def test_policy_fields_are_binary(self) -> None:
        bank = np.array(
            [
                [0.0, -1.0, 2.0],
                [2.0, 1.0, 0.0],
                [-2.0, -1.0, -0.5],
            ]
        )
        fields = policy_fields(
            bank,
            np.array(
                [1.0, 1.0, 1.0, 0.5]
            ),
        )
        for name in (
            "R0", "R1", "A", "M", "H"
        ):
            self.assertTrue(
                set(fields[name]).issubset(
                    {0.0, 1.0}
                )
            )

    def test_incremental_identity(self) -> None:
        bank = np.array(
            [
                [0.0, -1.0, 2.0],
                [2.0, 1.0, 0.0],
                [-2.0, -1.0, -0.5],
            ]
        )
        fields = policy_fields(
            bank,
            np.array(
                [1.0, 1.0, 1.0, 0.5]
            ),
        )
        np.testing.assert_array_equal(
            fields["M"],
            (1.0 - fields["R0"])
            * fields["R1"],
        )

    def test_adaptive_identity(self) -> None:
        bank = np.array(
            [
                [0.0, -1.0, 2.0],
                [2.0, 1.0, 0.0],
                [-2.0, -1.0, -0.5],
            ]
        )
        fields = policy_fields(
            bank,
            np.array(
                [1.0, 1.0, 1.0, 0.5]
            ),
        )
        np.testing.assert_array_equal(
            fields["H"],
            np.maximum(
                fields["R0"],
                fields["A"]
                * fields["M"],
            ),
        )

    def test_equal_threshold_incremental_simplification(self) -> None:
        rng = np.random.default_rng(4)
        bank = rng.normal(
            size=(200, 3)
        )
        q = 0.7
        fields = policy_fields(
            bank,
            np.array(
                [q, q, q, 0.0]
            ),
        )
        expected = (
            np.maximum(
                bank[:, 0],
                bank[:, 1],
            )
            <= q
        ) & (bank[:, 2] > q)
        np.testing.assert_array_equal(
            fields["M"],
            expected.astype(float),
        )

    def test_policy_estimators_delta_identity(self) -> None:
        rng = np.random.default_rng(5)
        bank = rng.normal(
            size=(200, 3)
        )
        fields = policy_fields(
            bank,
            np.array(
                [0.8, 0.8, 0.8, 0.2]
            ),
        )
        estimates = policy_estimators(
            fields
        )
        self.assertAlmostEqual(
            estimates["delta_hat"],
            estimates[
                "adaptive_probability"
            ]
            - estimates[
                "comparator_probability"
            ],
        )

    def test_bvn_independence(self) -> None:
        left, right = 0.4, -0.2
        self.assertAlmostEqual(
            bvn_cdf(
                left,
                right,
                0.0,
            ),
            norm.cdf(left)
            * norm.cdf(right),
            places=10,
        )

    def test_base_max_quantile(self) -> None:
        probability = 0.70
        threshold = base_max_quantile(
            probability,
            0.4,
        )
        self.assertAlmostEqual(
            base_max_cdf(
                threshold,
                0.4,
            ),
            probability,
            places=8,
        )

    def test_population_delta_identity(self) -> None:
        correlation = np.eye(3)
        probability = 0.95
        candidate = norm.ppf(
            probability
        )
        trigger = base_max_quantile(
            0.70,
            0.0,
        )
        probabilities = (
            policy_population_probabilities(
                np.array(
                    [
                        candidate,
                        candidate,
                        candidate,
                        trigger,
                    ]
                ),
                correlation,
            )
        )
        self.assertAlmostEqual(
            probabilities["delta_pi"],
            probabilities[
                "adaptive_probability"
            ]
            - probabilities[
                "comparator_probability"
            ],
        )


if __name__ == "__main__":
    unittest.main()
