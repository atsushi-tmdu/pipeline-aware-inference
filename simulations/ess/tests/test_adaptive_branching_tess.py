from __future__ import annotations

import unittest

from simulations.ess.adaptive_branching_tess import (
    exact_nonrejection,
    expected_candidates,
    tess_from_nonrejection,
    trigger_threshold,
)


class AdaptiveBranchingTessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base_k = 5
        self.extra_k = 15
        self.r = 0.5
        self.tau = trigger_threshold(self.base_k, self.r)

    def tess(self, scenario: str, alpha: float) -> float:
        q = exact_nonrejection(
            scenario,
            alpha,
            self.base_k,
            self.extra_k,
            self.tau,
            self.r,
        )
        return tess_from_nonrejection(q, alpha)

    def test_trigger_probability_is_half(self) -> None:
        probability = 1.0 - (1.0 - self.tau) ** self.base_k
        self.assertAlmostEqual(probability, 0.5, places=12)

    def test_fixed_boundaries(self) -> None:
        self.assertAlmostEqual(self.tess("fixed_base", 0.05), 5.0, places=12)
        self.assertAlmostEqual(self.tess("fixed_full", 0.05), 20.0, places=12)

    def test_adaptive_rules_have_same_expected_k(self) -> None:
        values = [
            expected_candidates(
                scenario,
                self.base_k,
                self.extra_k,
                self.tau,
                self.r,
            )
            for scenario in (
                "random_expansion",
                "promising_triggered",
                "rescue_triggered",
            )
        ]
        for value in values:
            self.assertAlmostEqual(value, 12.5, places=12)

    def test_activation_rule_changes_tess(self) -> None:
        alpha = 0.10
        promising = self.tess("promising_triggered", alpha)
        random = self.tess("random_expansion", alpha)
        rescue = self.tess("rescue_triggered", alpha)
        self.assertLess(promising, random)
        self.assertLess(random, rescue)

    def test_above_trigger_promising_equals_base(self) -> None:
        alpha = 0.20
        self.assertAlmostEqual(
            self.tess("promising_triggered", alpha),
            5.0,
            places=12,
        )

    def test_above_trigger_rescue_equals_full(self) -> None:
        alpha = 0.20
        self.assertAlmostEqual(
            self.tess("rescue_triggered", alpha),
            20.0,
            places=12,
        )

    def test_deep_tail_converges_to_expected_k(self) -> None:
        alpha = 1e-7
        for scenario in (
            "random_expansion",
            "promising_triggered",
            "rescue_triggered",
        ):
            self.assertAlmostEqual(self.tess(scenario, alpha), 12.5, delta=1e-4)

    def test_known_values(self) -> None:
        self.assertAlmostEqual(
            self.tess("promising_triggered", 0.10),
            6.23158,
            delta=1e-5,
        )
        self.assertAlmostEqual(
            self.tess("rescue_triggered", 0.10),
            15.59228,
            delta=1e-5,
        )


if __name__ == "__main__":
    unittest.main()
