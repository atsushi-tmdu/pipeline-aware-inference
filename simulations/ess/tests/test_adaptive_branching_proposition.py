from __future__ import annotations

import unittest

import numpy as np

from simulations.ess.adaptive_branching_tess import (
    build_exact_grid,
)
from simulations.ess.adaptive_branching_proposition_check import (
    verify_equal_nonrejection_gaps,
    verify_order,
)


class AdaptiveBranchingPropositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alphas = (
            0.5,
            0.2,
            0.13,
            0.12944944,
            0.1,
            0.05,
            0.01,
            0.001,
            1e-6,
        )
        self.data = build_exact_grid(
            self.alphas,
            base_k=5,
            extra_k=15,
            expansion_probability=0.5,
        )

    def test_strict_order_at_all_checked_alphas(self) -> None:
        result = verify_order(self.data)
        self.assertTrue(bool(result["strict_order_verified"].all()))

    def test_random_nonrejection_is_exact_midpoint(self) -> None:
        result = verify_equal_nonrejection_gaps(self.data)
        self.assertLess(
            float(np.max(np.abs(result["gap_difference"]))),
            1e-12,
        )

    def test_same_expected_and_maximum_candidate_counts(self) -> None:
        adaptive = self.data[
            self.data["scenario"].isin(
                [
                    "promising_triggered",
                    "random_expansion",
                    "rescue_triggered",
                ]
            )
        ]
        self.assertEqual(
            adaptive["expected_evaluated_candidates"].nunique(),
            1,
        )
        self.assertEqual(
            adaptive["maximum_candidate_count"].nunique(),
            1,
        )
        self.assertAlmostEqual(
            float(adaptive["expected_evaluated_candidates"].iloc[0]),
            12.5,
            places=12,
        )
        self.assertEqual(
            int(adaptive["maximum_candidate_count"].iloc[0]),
            20,
        )

    def test_deep_tail_common_limit(self) -> None:
        deep = self.data[np.isclose(self.data["local_alpha"], 1e-6)]
        adaptive = deep[
            deep["scenario"].isin(
                [
                    "promising_triggered",
                    "random_expansion",
                    "rescue_triggered",
                ]
            )
        ]
        for value in adaptive["exact_tess"]:
            self.assertAlmostEqual(float(value), 12.5, delta=2e-4)


if __name__ == "__main__":
    unittest.main()
