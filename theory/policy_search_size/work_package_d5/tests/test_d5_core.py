from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

import numpy as np


D5 = Path(__file__).resolve().parents[1]
D4 = D5.parent / "work_package_d4"
sys.path.insert(0, str(D5))
sys.path.insert(0, str(D4))

from d5_core import (
    boundary_info,
    candidate_threshold,
    estimate_bridge,
    plus_one_index,
    plus_one_pvalue,
    plus_one_rejects,
    quantile_index,
)
from d4_core import estimate_d4


class D5CoreTests(unittest.TestCase):
    def test_d4_grid_has_adjacent_plus_one_boundary(self) -> None:
        for B in (500, 1000, 3000):
            for alpha in (0.01, 0.05, 0.10):
                info = boundary_info(B, alpha)
                self.assertTrue(info.plus_one_attainable)
                self.assertEqual(info.index_gap, 1)
                self.assertAlmostEqual(
                    info.tail_probability_gap,
                    1.0 / (B + 1),
                    places=15,
                )

    def test_adjacent_identity_over_dense_grid(self) -> None:
        for B in (1, 2, 3, 5, 10, 31, 100):
            for alpha in np.linspace(0.001, 0.999, 999):
                info = boundary_info(B, float(alpha))
                if info.plus_one_attainable:
                    self.assertIn(info.index_gap, (0, 1))
                    self.assertEqual(
                        info.plus_one_index - info.quantile_index,
                        info.index_gap,
                    )

    def test_unattainable_strict_plus_one_region(self) -> None:
        B = 9
        alpha = 0.10
        info = boundary_info(B, alpha)
        self.assertFalse(info.plus_one_attainable)
        self.assertIsNone(info.plus_one_index)
        reference = np.arange(B, dtype=float)
        for x in (-1.0, 0.0, 8.0, 9.0, 100.0):
            self.assertFalse(plus_one_rejects(reference, x, alpha))
        self.assertTrue(
            math.isinf(candidate_threshold(reference, alpha, "plus_one"))
        )

    def test_exact_event_equivalence_with_ties(self) -> None:
        reference = np.array([1.0, 1.0, 2.0, 3.0, 3.0])
        x_grid = (-1.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0)

        for alpha in (0.20, 0.34, 0.50, 0.80, 0.99):
            index = plus_one_index(reference.size, alpha)
            threshold = (
                math.inf
                if index is None
                else float(np.partition(reference, index - 1)[index - 1])
            )
            for x in x_grid:
                direct = plus_one_pvalue(reference, x) < alpha
                order_event = x > threshold
                self.assertEqual(
                    direct,
                    order_event,
                    msg=f"alpha={alpha}, x={x}",
                )

    def test_quantile_index_matches_d4_convention(self) -> None:
        self.assertEqual(quantile_index(5, 0.20), 4)
        self.assertEqual(quantile_index(10, 0.05), 10)
        self.assertEqual(quantile_index(100, 0.10), 90)

    def test_quantile_mode_matches_d4_estimator(self) -> None:
        rng = np.random.default_rng(8842)
        reference = rng.normal(size=(500, 3))
        evaluation = rng.normal(size=(700, 3))
        alpha = 0.05
        activation_rate = 0.50

        d4 = estimate_d4(
            reference,
            evaluation,
            alpha,
            activation_rate,
        )
        d5 = estimate_bridge(
            reference,
            evaluation,
            alpha,
            activation_rate,
        ).quantile

        fields = (
            "q0_hat",
            "q1_hat",
            "c_hat",
            "e0_hat",
            "activation_rate_hat",
            "mu_hat",
            "nu_hat",
            "pi_adaptive_hat",
            "pi_comparator_hat",
            "delta_pi_hat",
            "tess_adaptive_hat",
            "tess_comparator_hat",
            "delta_tess_hat",
        )
        for field in fields:
            self.assertAlmostEqual(
                float(getattr(d4, field)),
                float(getattr(d5, field)),
                places=15,
                msg=field,
            )

    def test_modes_share_activation_threshold_and_realization(self) -> None:
        rng = np.random.default_rng(9981)
        reference = rng.normal(size=(500, 3))
        evaluation = rng.normal(size=(800, 3))
        bridge = estimate_bridge(reference, evaluation, 0.05, 0.50)

        self.assertEqual(
            bridge.quantile.c_hat,
            bridge.plus_one.c_hat,
        )
        self.assertEqual(
            bridge.quantile.activation_rate_hat,
            bridge.plus_one.activation_rate_hat,
        )
        self.assertGreaterEqual(bridge.q0_spacing, 0.0)
        self.assertGreaterEqual(bridge.q1_spacing, 0.0)

    def test_plus_one_policy_matches_direct_pvalue_events(self) -> None:
        reference = np.array(
            [
                [-2.0, 0.0, 0.4],
                [-1.0, 0.2, 0.6],
                [0.0, 0.4, 0.8],
                [1.0, 0.6, 1.0],
                [2.0, 0.8, 1.2],
            ]
        )
        evaluation = np.array(
            [
                [-1.5, 0.1, 0.5],
                [-0.5, 0.3, 0.7],
                [0.5, 0.5, 0.9],
                [1.5, 0.7, 1.1],
                [2.5, 0.9, 1.3],
            ]
        )
        alpha = 0.50
        activation_rate = 0.40

        plus = estimate_bridge(
            reference,
            evaluation,
            alpha,
            activation_rate,
        ).plus_one

        r0 = np.array(
            [
                plus_one_rejects(reference[:, 1], x, alpha)
                for x in evaluation[:, 1]
            ],
            dtype=float,
        )
        r1 = np.array(
            [
                plus_one_rejects(reference[:, 2], x, alpha)
                for x in evaluation[:, 2]
            ],
            dtype=float,
        )
        activation = (evaluation[:, 0] > plus.c_hat).astype(float)
        increment = (r0 == 0.0).astype(float) * r1
        adaptive = r0 + activation * increment

        expected_pi_a = float(np.mean(adaptive))
        expected_pi_c = float(
            np.mean(r0) + np.mean(activation) * np.mean(increment)
        )

        self.assertAlmostEqual(
            plus.pi_adaptive_hat,
            expected_pi_a,
            places=15,
        )
        self.assertAlmostEqual(
            plus.pi_comparator_hat,
            expected_pi_c,
            places=15,
        )


if __name__ == "__main__":
    unittest.main()
