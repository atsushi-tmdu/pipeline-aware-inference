from __future__ import annotations

import math
import unittest
from statistics import NormalDist

import numpy as np

from d1_core import (
    empirical_quantile_inverted_cdf,
    independent_normal_benchmark,
    independent_normal_boundary_derivatives,
    independent_normal_rejection_at_thresholds,
)


class D1CoreTests(unittest.TestCase):
    def test_empirical_generalized_inverse(self) -> None:
        x = np.array([4.0, 1.0, 3.0, 2.0])
        self.assertEqual(empirical_quantile_inverted_cdf(x, 0.50), 2.0)
        self.assertEqual(empirical_quantile_inverted_cdf(x, 0.75), 3.0)

    def test_primary_debug_benchmark(self) -> None:
        result = independent_normal_benchmark(
            alpha=0.05, activation_rate=0.50, lambda_ratio=1.0
        )
        self.assertAlmostEqual(result.rejection_probability, 0.07375, places=12)
        self.assertAlmostEqual(result.tess, 1.493589040957266, places=12)
        self.assertAlmostEqual(result.total_variance_sqrt_n, 0.1241828125, places=12)

    def test_boundary_derivatives_match_finite_difference(self) -> None:
        alpha = 0.05
        r = 0.50
        q = NormalDist().inv_cdf(1.0 - alpha)
        d0, d1 = independent_normal_boundary_derivatives(q, q, activation_rate=r)
        eps = 1e-6
        m0_plus = independent_normal_rejection_at_thresholds(q + eps, q, activation_rate=r)
        m0_minus = independent_normal_rejection_at_thresholds(q - eps, q, activation_rate=r)
        m1_plus = independent_normal_rejection_at_thresholds(q, q + eps, activation_rate=r)
        m1_minus = independent_normal_rejection_at_thresholds(q, q - eps, activation_rate=r)
        fd0 = (m0_plus - m0_minus) / (2.0 * eps)
        fd1 = (m1_plus - m1_minus) / (2.0 * eps)
        self.assertAlmostEqual(d0, fd0, places=7)
        self.assertAlmostEqual(d1, fd1, places=7)

    def test_variance_components_positive(self) -> None:
        result = independent_normal_benchmark(
            alpha=0.10, activation_rate=0.25, lambda_ratio=2.0
        )
        self.assertGreater(result.evaluation_variance, 0.0)
        self.assertGreater(result.reference_variance, 0.0)
        self.assertGreater(result.tess_variance_sqrt_n, 0.0)


if __name__ == "__main__":
    unittest.main()
