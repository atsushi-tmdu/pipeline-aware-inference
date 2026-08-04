from __future__ import annotations

import unittest

from d8a_core import (
    beta_order_statistic_mean,
    beta_order_statistic_second_central_about_probability,
    beta_order_statistic_variance,
    inverse_cdf_first_derivative,
    inverse_cdf_second_derivative,
    quantile_lattice_offset,
    quantile_order_index,
    scalar_quantile_mean_bias_leading_term,
    scalar_quantile_taylor_bias_from_exact_beta_moments,
    uniform_order_statistic_bias,
)


class D8AScalarQuantileLemmaTests(unittest.TestCase):
    def test_beta_order_statistic_mean(self) -> None:
        self.assertAlmostEqual(
            beta_order_statistic_mean(99, 25),
            0.25,
        )

    def test_beta_order_statistic_variance(self) -> None:
        observed = beta_order_statistic_variance(9, 5)
        expected = 5 * 5 / (10**2 * 11)
        self.assertAlmostEqual(observed, expected)

    def test_second_moment_about_probability(self) -> None:
        B, p = 99, 0.25
        k = quantile_order_index(B, p)
        mean_shift = beta_order_statistic_mean(B, k) - p
        expected = (
            beta_order_statistic_variance(B, k)
            + mean_shift**2
        )
        self.assertAlmostEqual(
            beta_order_statistic_second_central_about_probability(
                B,
                p,
            ),
            expected,
        )

    def test_uniform_exact_bias(self) -> None:
        B, p = 1000, 0.99
        exact = uniform_order_statistic_bias(B, p)
        lattice = quantile_lattice_offset(B, p)
        self.assertAlmostEqual(
            exact,
            lattice / (B + 1),
            places=15,
        )

    def test_uniform_leading_term(self) -> None:
        B, p = 1000, 0.99
        leading = scalar_quantile_mean_bias_leading_term(
            B,
            p,
            density_at_quantile=1.0,
            density_derivative_at_quantile=0.0,
        )
        self.assertAlmostEqual(leading, -0.99 / B)

    def test_inverse_cdf_derivatives(self) -> None:
        self.assertAlmostEqual(
            inverse_cdf_first_derivative(2.0),
            0.5,
        )
        self.assertAlmostEqual(
            inverse_cdf_second_derivative(2.0, -3.0),
            3.0 / 8.0,
        )

    def test_exact_beta_taylor_uses_exact_moments(self) -> None:
        B, p = 1000, 0.99
        observed = (
            scalar_quantile_taylor_bias_from_exact_beta_moments(
                B,
                p,
                density_at_quantile=1.0,
                density_derivative_at_quantile=0.0,
            )
        )
        self.assertAlmostEqual(
            observed,
            uniform_order_statistic_bias(B, p),
            places=15,
        )

    def test_lattice_coefficient_is_bounded(self) -> None:
        for B in range(10, 100):
            offset = quantile_lattice_offset(B, 0.37)
            self.assertLessEqual(abs(offset), 1.0)


if __name__ == "__main__":
    unittest.main()
