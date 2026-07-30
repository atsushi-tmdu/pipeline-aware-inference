#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

from simulations.ess.ess_estimators import (
    ess_adjusted_p_value,
    estimate_tail_ess,
    estimate_tail_ess_curve,
    local_alpha_for_global_alpha,
    sidak_equivalent_ess,
)


class TestEffectiveSearchSize(unittest.TestCase):
    def test_single_search_boundary(self) -> None:
        self.assertAlmostEqual(sidak_equivalent_ess(0.05, 0.05), 1.0)

    def test_independent_k_boundary(self) -> None:
        alpha = 0.05
        for k in (2, 7, 20):
            global_rejection = 1.0 - (1.0 - alpha) ** k
            self.assertAlmostEqual(
                sidak_equivalent_ess(global_rejection, alpha),
                float(k),
                places=12,
            )

    def test_adjustment_inverse(self) -> None:
        global_alpha = 0.05
        ess = 3.7
        local = local_alpha_for_global_alpha(global_alpha, ess)
        self.assertAlmostEqual(ess_adjusted_p_value(local, ess), global_alpha)

    def test_curve_uses_strict_threshold(self) -> None:
        estimates = estimate_tail_ess_curve(
            p_values=(0.001, 0.01, 0.05, 0.20, 0.80),
            local_alphas=(0.05, 0.10),
        )
        self.assertEqual(estimates[0].rejections, 2)
        self.assertEqual(estimates[1].rejections, 3)
        self.assertEqual(estimates[0].repetitions, 5)

    def test_phase3c_mixed_k20(self) -> None:
        estimate = estimate_tail_ess(
            rejections=597,
            repetitions=2000,
            local_alpha=0.05,
        )
        self.assertAlmostEqual(estimate.ess, 6.91190502916246)
        self.assertLess(estimate.ess_low, estimate.ess)
        self.assertGreater(estimate.ess_high, estimate.ess)


if __name__ == "__main__":
    unittest.main()
