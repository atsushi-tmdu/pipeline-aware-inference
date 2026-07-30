from __future__ import annotations

import math
import unittest

from simulations.ess.gaussian_copula_tess_exact import (
    gaussian_equicorrelated_nonrejection_probability,
    gaussian_equicorrelated_tess,
)


class GaussianCopulaTessExactTests(unittest.TestCase):
    def test_independence_recovers_k(self) -> None:
        for alpha in (0.2, 0.05, 0.005, 1e-5):
            self.assertAlmostEqual(
                gaussian_equicorrelated_tess(alpha, 20, 0.0),
                20.0,
                places=11,
            )

    def test_complete_dependence_recovers_one(self) -> None:
        for alpha in (0.2, 0.05, 0.005, 1e-5):
            self.assertAlmostEqual(
                gaussian_equicorrelated_tess(alpha, 20, 1.0),
                1.0,
                places=11,
            )

    def test_single_candidate_recovers_one(self) -> None:
        self.assertAlmostEqual(
            gaussian_equicorrelated_tess(0.05, 1, 0.37),
            1.0,
            places=11,
        )

    def test_probability_bounds(self) -> None:
        q, err = gaussian_equicorrelated_nonrejection_probability(0.05, 7, 0.5)
        self.assertGreater(q, 0.0)
        self.assertLess(q, 1.0)
        self.assertGreaterEqual(err, 0.0)

    def test_tess_decreases_with_rho(self) -> None:
        values = [
            gaussian_equicorrelated_tess(0.05, 20, rho)
            for rho in (0.0, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0)
        ]
        self.assertTrue(all(a >= b for a, b in zip(values, values[1:])))

    def test_deeper_tail_moves_toward_k_for_rho_below_one(self) -> None:
        moderate = gaussian_equicorrelated_tess(0.2, 20, 0.5)
        deep = gaussian_equicorrelated_tess(1e-5, 20, 0.5)
        self.assertGreater(deep, moderate)
        self.assertLess(deep, 20.0)

    def test_known_exact_value(self) -> None:
        value = gaussian_equicorrelated_tess(0.05, 20, 0.5)
        self.assertAlmostEqual(value, 8.0858, delta=0.002)


if __name__ == "__main__":
    unittest.main()
