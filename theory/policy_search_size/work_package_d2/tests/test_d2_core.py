from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d2_core import (
    empirical_generalized_inverse,
    exact_finite_reference_mean,
    exact_independent_normal_benchmark,
    independent_normal_derivatives,
    independent_normal_policy_probability,
    one_outer_d2,
)


class D2CoreTests(unittest.TestCase):
    def test_empirical_generalized_inverse(self) -> None:
        x = np.array([5.0, 1.0, 3.0, 2.0, 4.0])
        self.assertEqual(empirical_generalized_inverse(x, 0.6), 3.0)

    def test_derivatives_match_finite_difference(self) -> None:
        t0, t1, c = 1.1, 1.3, 0.2
        analytic = independent_normal_derivatives(t0, t1, c)
        eps = 1e-6
        numerical = []
        base = [t0, t1, c]
        for j in range(3):
            plus = base.copy()
            minus = base.copy()
            plus[j] += eps
            minus[j] -= eps
            numerical.append(
                (
                    independent_normal_policy_probability(*plus)
                    - independent_normal_policy_probability(*minus)
                )
                / (2 * eps)
            )
        np.testing.assert_allclose(analytic, numerical, rtol=1e-6, atol=1e-8)

    def test_primary_benchmark(self) -> None:
        out = exact_independent_normal_benchmark(0.05, 0.5, 1.0)
        self.assertAlmostEqual(out["pi"], 0.07375, places=12)
        self.assertAlmostEqual(out["tess"], 1.4935890409572679, places=12)
        self.assertAlmostEqual(out["d_u"], 0.0475, places=12)
        self.assertAlmostEqual(out["sigma_r_d2_2_sqrt_B"], 0.0564359375, places=12)
        self.assertAlmostEqual(out["sigma_pi2_sqrt_n"], 0.124746875, places=12)

    def test_trigger_variance_increment_is_positive_under_independence(self) -> None:
        out = exact_independent_normal_benchmark(0.05, 0.5, 1.0)
        self.assertGreater(out["sigma_trigger_2_sqrt_B"], 0.0)
        self.assertGreater(out["sigma_r_d2_2_sqrt_B"], out["sigma_r_d1_2_sqrt_B"])

    def test_finite_reference_mean(self) -> None:
        out = exact_finite_reference_mean(0.05, 0.5, 1000, estimated_trigger=True)
        self.assertAlmostEqual(out["bias"], 0.001399825997380033, places=15)
        known = exact_finite_reference_mean(0.05, 0.5, 1000, estimated_trigger=False)
        self.assertAlmostEqual(known["bias"], 0.0013756735272719145, places=15)
        self.assertGreater(out["mean_pi"], known["mean_pi"])

    def test_one_outer_returns_finite_values(self) -> None:
        rng = np.random.default_rng(12345)
        out = one_outer_d2(rng, B=200, n=200, alpha=0.05, r=0.5, bootstrap_repetitions=10)
        for key in ["pi_hat", "tess_hat", "bootstrap_pi_sd", "bootstrap_tess_sd"]:
            self.assertTrue(math.isfinite(float(out[key])))


if __name__ == '__main__':
    unittest.main()
