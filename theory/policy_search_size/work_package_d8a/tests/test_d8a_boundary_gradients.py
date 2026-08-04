from __future__ import annotations

import unittest

from d8a_core import (
    bivariate_normal_candidate_beta,
    bivariate_normal_candidate_gradient,
    bivariate_normal_candidate_trigger_hessian,
    bivariate_normal_indicator_covariance,
    bivariate_normal_trigger_beta,
    bivariate_normal_trigger_gradient,
    boundary_gradient_from_if_coefficient,
    covariance_candidate_boundary_coefficient,
    covariance_trigger_boundary_coefficient,
    reference_if_coefficient_from_gradient,
)


class D8ABoundaryGradientTests(unittest.TestCase):
    def test_candidate_beta_algebra(self) -> None:
        observed = covariance_candidate_boundary_coefficient(
            activation_probability=0.4,
            conditional_activation_jump=-0.3,
            conditional_jump=-1.0,
        )
        self.assertAlmostEqual(observed, 0.1)

    def test_trigger_beta_algebra(self) -> None:
        observed = covariance_trigger_boundary_coefficient(
            incremental_probability=0.35,
            conditional_incremental_at_trigger=0.20,
        )
        self.assertAlmostEqual(observed, 0.15)

    def test_gradient_and_if_coefficient_are_inverse(self) -> None:
        gradient = boundary_gradient_from_if_coefficient(0.25, -0.4)
        self.assertAlmostEqual(gradient, -0.1)
        self.assertAlmostEqual(
            reference_if_coefficient_from_gradient(gradient, 0.25),
            -0.4,
        )

    def test_candidate_gradient_matches_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        finite = (
            bivariate_normal_indicator_covariance(q + h, c, r)
            - bivariate_normal_indicator_covariance(q - h, c, r)
        ) / (2.0 * h)
        analytic = bivariate_normal_candidate_gradient(q, c, r)
        self.assertAlmostEqual(finite, analytic, places=6)

    def test_trigger_gradient_matches_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        finite = (
            bivariate_normal_indicator_covariance(q, c + h, r)
            - bivariate_normal_indicator_covariance(q, c - h, r)
        ) / (2.0 * h)
        analytic = bivariate_normal_trigger_gradient(q, c, r)
        self.assertAlmostEqual(finite, analytic, places=6)

    def test_cross_hessian_matches_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        finite = (
            bivariate_normal_candidate_gradient(q, c + h, r)
            - bivariate_normal_candidate_gradient(q, c - h, r)
        ) / (2.0 * h)
        analytic = bivariate_normal_candidate_trigger_hessian(q, c, r)
        self.assertAlmostEqual(finite, analytic, places=6)

    def test_cross_hessian_is_nonzero_under_dependence(self) -> None:
        observed = bivariate_normal_candidate_trigger_hessian(
            0.4,
            0.8,
            0.55,
        )
        self.assertGreater(abs(observed), 1e-4)

    def test_cross_hessian_is_zero_under_independence(self) -> None:
        observed = bivariate_normal_candidate_trigger_hessian(
            0.4,
            0.8,
            0.0,
        )
        self.assertAlmostEqual(observed, 0.0, places=12)

    def test_beta_formulas_have_expected_symmetry(self) -> None:
        q, c, r = 0.4, 0.8, 0.55
        self.assertAlmostEqual(
            bivariate_normal_candidate_beta(q, c, r),
            bivariate_normal_trigger_beta(c, q, r),
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
