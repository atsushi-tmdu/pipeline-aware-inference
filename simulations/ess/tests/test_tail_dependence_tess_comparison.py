from __future__ import annotations

import unittest

from simulations.ess.tail_dependence_tess_comparison import (
    extremal_t_limit,
    gumbel_hougaard_tess,
    t_copula_nonrejection_probability,
    t_copula_tess,
)


class TailDependenceTessTests(unittest.TestCase):
    def test_t_copula_probability_bounds(self) -> None:
        q = t_copula_nonrejection_probability(0.05, 7, 0.5, 5)
        self.assertGreater(q, 0.0)
        self.assertLess(q, 1.0)

    def test_t_copula_deeper_tail_moves_toward_limit(self) -> None:
        moderate = t_copula_tess(0.2, 20, 0.5, 3)
        deep = t_copula_tess(0.001, 20, 0.5, 3)
        limit = extremal_t_limit(20, 0.5, 3)
        self.assertGreater(deep, moderate)
        self.assertLess(abs(deep - limit), abs(moderate - limit))

    def test_heavier_tails_have_stronger_extremal_dependence(self) -> None:
        theta3 = extremal_t_limit(20, 0.5, 3)
        theta10 = extremal_t_limit(20, 0.5, 10)
        self.assertLess(theta3, theta10)
        self.assertLess(theta10, 20.0)

    def test_extremal_t_known_values(self) -> None:
        self.assertAlmostEqual(extremal_t_limit(20, 0.5, 3), 6.0937, delta=0.01)
        self.assertAlmostEqual(extremal_t_limit(20, 0.5, 5), 8.5981, delta=0.01)

    def test_gumbel_is_threshold_constant(self) -> None:
        self.assertAlmostEqual(gumbel_hougaard_tess(20, 2), 20 ** 0.5, places=12)

    def test_t_copula_known_finite_threshold_value(self) -> None:
        self.assertAlmostEqual(t_copula_tess(0.05, 20, 0.5, 3), 5.5601, delta=0.01)


if __name__ == "__main__":
    unittest.main()
