from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    adaptive_evaluation_influence,
    adaptive_rejection_estimator,
    bernoulli_variance,
    comparator_conditional_mean,
    comparator_evaluation_influence,
    comparator_rejection_estimator,
    final_policy_bias_approximation,
    second_order_expectation_coefficient,
    tess_evaluation_bias_coefficient,
    tess_reference_bias_coefficient,
    tess_second_order_bias_approximation,
)


class D8AFinalTheoryTests(unittest.TestCase):
    def test_expectation_delta_coefficient(self) -> None:
        gradient = np.array([0.4, -0.2])
        bias = np.array([0.1, 0.3])
        hessian = np.array([[1.0, 0.2], [0.2, 0.8]])
        covariance = np.array([[1.1, 0.1], [0.1, 0.9]])
        expected = float(
            gradient @ bias
            + 0.5 * np.trace(hessian @ covariance)
        )
        self.assertAlmostEqual(
            second_order_expectation_coefficient(
                gradient,
                bias,
                hessian,
                covariance,
            ),
            expected,
        )

    def test_final_policy_bias_retains_interaction(self) -> None:
        delta = 0.03
        coefficient = -0.7
        B, n = 3000, 5000
        observed = final_policy_bias_approximation(
            delta,
            coefficient,
            B,
            n,
            retain_interaction=True,
        )
        expected = (
            coefficient / B
            - delta / n
            - coefficient / (B * n)
        )
        self.assertAlmostEqual(observed, expected)

    def test_comparator_conditional_mean(self) -> None:
        observed = comparator_conditional_mean(
            comparator_probability=0.08,
            policy_delta=0.01,
            evaluation_size=100,
        )
        self.assertAlmostEqual(observed, 0.0801)

    def test_evaluation_estimators(self) -> None:
        r0 = np.array([0.0, 1.0, 0.0, 0.0])
        a = np.array([1.0, 1.0, 0.0, 1.0])
        m = np.array([1.0, 0.0, 1.0, 0.0])
        h = r0 + a * m
        self.assertAlmostEqual(
            adaptive_rejection_estimator(h),
            np.mean(h),
        )
        self.assertAlmostEqual(
            comparator_rejection_estimator(r0, a, m),
            np.mean(r0) + np.mean(a) * np.mean(m),
        )

    def test_adaptive_influence_is_centered(self) -> None:
        h = np.array([0.0, 1.0, 1.0, 0.0])
        influence = adaptive_evaluation_influence(
            h,
            np.mean(h),
        )
        self.assertAlmostEqual(float(np.mean(influence)), 0.0)

    def test_comparator_influence_is_centered(self) -> None:
        r0 = np.array([0.0, 1.0, 0.0, 1.0])
        a = np.array([1.0, 1.0, 0.0, 0.0])
        m = np.array([1.0, 0.0, 1.0, 0.0])
        influence = comparator_evaluation_influence(
            r0,
            a,
            m,
            np.mean(r0),
            np.mean(a),
            np.mean(m),
        )
        self.assertAlmostEqual(float(np.mean(influence)), 0.0)

    def test_bernoulli_variance(self) -> None:
        self.assertAlmostEqual(
            bernoulli_variance(0.2),
            0.16,
        )

    def test_tess_reference_coefficient(self) -> None:
        observed = tess_reference_bias_coefficient(
            alpha=0.05,
            adaptive_probability=0.08,
            comparator_probability=0.075,
            adaptive_reference_mean_bias=-0.4,
            comparator_reference_mean_bias=-0.3,
            adaptive_reference_variance=0.20,
            comparator_reference_variance=0.18,
        )
        self.assertTrue(np.isfinite(observed))

    def test_tess_evaluation_coefficient_includes_delta(self) -> None:
        with_delta = tess_evaluation_bias_coefficient(
            alpha=0.05,
            adaptive_probability=0.08,
            comparator_probability=0.075,
            policy_delta=0.005,
            adaptive_evaluation_variance=0.0736,
            comparator_evaluation_variance=0.06,
        )
        without_delta = tess_evaluation_bias_coefficient(
            alpha=0.05,
            adaptive_probability=0.08,
            comparator_probability=0.075,
            policy_delta=0.0,
            adaptive_evaluation_variance=0.0736,
            comparator_evaluation_variance=0.06,
        )
        self.assertNotAlmostEqual(with_delta, without_delta)

    def test_tess_total_bias_is_sum_of_rates(self) -> None:
        observed = tess_second_order_bias_approximation(
            reference_coefficient=-0.6,
            evaluation_coefficient=0.2,
            reference_size=3000,
            evaluation_size=5000,
        )
        self.assertAlmostEqual(
            observed,
            -0.6 / 3000 + 0.2 / 5000,
        )


if __name__ == "__main__":
    unittest.main()
