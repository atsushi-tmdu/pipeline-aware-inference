from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    candidate_trigger_cross_curvature,
    combined_bias_approximation,
    empirical_covariance_estimator,
    exact_conditional_expectation,
    exact_evaluation_bias,
    exact_mean_from_truncated_reference_expansion,
    second_order_reference_coefficient,
    tess_first_derivative,
    tess_second_derivative,
    tess_value,
    transformed_second_order_bias,
)


class D8ACoreTests(unittest.TestCase):
    def test_exact_conditional_factor(self) -> None:
        self.assertAlmostEqual(exact_conditional_expectation(0.24, 10), 0.216)
        self.assertAlmostEqual(exact_evaluation_bias(0.24, 10), -0.024)

    def test_empirical_covariance(self) -> None:
        a = np.array([0.0, 1.0, 1.0, 0.0])
        m = np.array([0.0, 0.0, 1.0, 1.0])
        self.assertAlmostEqual(empirical_covariance_estimator(a, m), 0.0)

    def test_reference_coefficient(self) -> None:
        g = np.array([2.0, -1.0])
        b = np.array([0.3, 0.2])
        h = np.array([[1.0, 0.5], [0.5, 2.0]])
        s = np.array([[4.0, 1.0], [1.0, 3.0]])
        expected = float(g @ b + 0.5 * np.trace(h @ s))
        self.assertAlmostEqual(
            second_order_reference_coefficient(g, b, h, s),
            expected,
        )

    def test_cross_curvature(self) -> None:
        h = np.array([[2.0], [-1.0]])
        s = np.array([[0.4], [0.3]])
        self.assertAlmostEqual(candidate_trigger_cross_curvature(h, s), 0.5)

    def test_combined_bias_matches_exact_truncated_mean(self) -> None:
        delta, coefficient, B, n = 0.08, -0.6, 1000, 500
        exact_bias = (
            exact_mean_from_truncated_reference_expansion(
                delta, coefficient, B, n
            )
            - delta
        )
        self.assertAlmostEqual(
            combined_bias_approximation(delta, coefficient, B, n, True),
            exact_bias,
        )

    def test_interaction_term(self) -> None:
        with_term = combined_bias_approximation(0.1, 1.5, 2000, 3000, True)
        without = combined_bias_approximation(0.1, 1.5, 2000, 3000, False)
        self.assertAlmostEqual(without - with_term, 1.5 / (2000 * 3000))

    def test_tess_derivatives(self) -> None:
        x, alpha, h = 0.08, 0.05, 1e-5
        fd1 = (tess_value(x + h, alpha) - tess_value(x - h, alpha)) / (2*h)
        fd2 = (
            tess_value(x + h, alpha)
            - 2*tess_value(x, alpha)
            + tess_value(x - h, alpha)
        ) / h**2
        self.assertAlmostEqual(fd1, tess_first_derivative(x, alpha), places=7)
        self.assertAlmostEqual(fd2, tess_second_derivative(x, alpha), places=4)

    def test_transformed_bias_has_curvature(self) -> None:
        self.assertAlmostEqual(
            transformed_second_order_bias(3.0, 4.0, 0.2, 0.5),
            1.6,
        )


if __name__ == "__main__":
    unittest.main()
