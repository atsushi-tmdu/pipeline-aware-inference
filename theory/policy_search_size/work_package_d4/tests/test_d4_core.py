from __future__ import annotations

import unittest

import numpy as np

from d4_core import (
    empirical_generalized_inverse,
    estimate_d4,
    finite_difference_gradient_gaussian,
    gaussian_d4_benchmark,
    paired_two_bank_bootstrap,
)


class D4CoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alpha = 0.05
        self.activation_rate = 0.50
        self.correlation = np.array(
            [
                [1.00, 0.50, 0.65],
                [0.50, 1.00, 0.30],
                [0.65, 0.30, 1.00],
            ],
            dtype=float,
        )

    def test_empirical_generalized_inverse(self) -> None:
        x = np.array([5.0, 1.0, 3.0, 2.0, 4.0])
        self.assertEqual(empirical_generalized_inverse(x, 0.8), 4.0)

    def test_dependent_gaussian_benchmark_is_finite(self) -> None:
        benchmark = gaussian_d4_benchmark(
            self.alpha,
            self.activation_rate,
            self.correlation,
        )
        required = [
            "delta_pi",
            "delta_tess",
            "sigma_e2_sqrt_n",
            "sigma_r2_sqrt_B",
            "sigma_total2_sqrt_n",
        ]
        self.assertTrue(all(np.isfinite(benchmark[key]) for key in required))
        self.assertGreater(benchmark["delta_tess"], 0.0)
        self.assertGreater(benchmark["sigma_e2_sqrt_n"], 0.0)
        self.assertGreater(benchmark["sigma_r2_sqrt_B"], 0.0)
        self.assertAlmostEqual(benchmark["evaluation_if_mean"], 0.0, places=8)

    def test_analytic_gradient_matches_finite_difference(self) -> None:
        benchmark = gaussian_d4_benchmark(
            self.alpha,
            self.activation_rate,
            self.correlation,
        )
        analytic = np.asarray(benchmark["gradient_delta_tess"], dtype=float)
        numeric = finite_difference_gradient_gaussian(
            self.alpha,
            self.activation_rate,
            self.correlation,
            step=2e-4,
        )
        np.testing.assert_allclose(analytic, numeric, rtol=3e-3, atol=3e-3)

    def test_independence_has_zero_population_contrast_and_reference_if(self) -> None:
        benchmark = gaussian_d4_benchmark(
            self.alpha,
            self.activation_rate,
            np.eye(3),
        )
        self.assertAlmostEqual(benchmark["delta_pi"], 0.0, places=6)
        self.assertAlmostEqual(benchmark["delta_tess"], 0.0, places=6)
        self.assertAlmostEqual(benchmark["sigma_r2_sqrt_B"], 0.0, places=6)

    def test_one_estimate_is_finite(self) -> None:
        rng = np.random.default_rng(8675309)
        reference = rng.multivariate_normal(np.zeros(3), self.correlation, size=800)
        evaluation = rng.multivariate_normal(np.zeros(3), self.correlation, size=900)
        estimate = estimate_d4(
            reference,
            evaluation,
            self.alpha,
            self.activation_rate,
        )
        values = np.array(list(estimate.to_dict().values()), dtype=float)
        self.assertTrue(np.all(np.isfinite(values)))

    def test_paired_bootstrap_is_finite(self) -> None:
        rng = np.random.default_rng(12345)
        reference = rng.multivariate_normal(np.zeros(3), self.correlation, size=500)
        evaluation = rng.multivariate_normal(np.zeros(3), self.correlation, size=600)
        bootstrap = paired_two_bank_bootstrap(
            reference,
            evaluation,
            self.alpha,
            self.activation_rate,
            repetitions=20,
            seed=98765,
        )
        self.assertEqual(bootstrap["delta_tess"].shape, (20,))
        self.assertTrue(np.all(np.isfinite(bootstrap["delta_tess"])))
        self.assertGreater(np.std(bootstrap["delta_tess"], ddof=1), 0.0)


if __name__ == "__main__":
    unittest.main()
