from __future__ import annotations

import unittest

import numpy as np
from scipy.stats import norm

from d8a_coincidence_core import (
    gaussian_toy_policy_contrast,
    gaussian_toy_policy_local_components,
    gaussian_toy_policy_piecewise_quadratic,
    generalized_policy_expectation_coefficient,
    generalized_policy_kink_coefficients,
    generalized_policy_quadratic_value,
    generalized_smooth_composition_coefficient,
)


class D8AGeneralizedPolicyTests(unittest.TestCase):
    def test_policy_kink_coefficient_formula(self) -> None:
        observed = generalized_policy_kink_coefficients(
            activation_probability=0.3,
            active_am_flags=np.array([1.0, 0.0]),
            branch_kink_coefficients=np.array([-0.2, -0.4]),
        )
        np.testing.assert_allclose(
            observed,
            np.array([-0.14, 0.12]),
        )

    def test_generalized_quadratic_value(self) -> None:
        increment = np.array([1.0, -1.0])
        hessian = np.eye(2)
        directions = np.array([[1.0, -1.0]])
        coefficients = np.array([-0.25])
        observed = generalized_policy_quadratic_value(
            increment,
            hessian,
            directions,
            coefficients,
        )
        expected = 1.0 - 1.0
        self.assertAlmostEqual(observed, expected)

    def test_generalized_expectation_coefficient(self) -> None:
        gradient = np.array([0.4, -0.2, 0.1])
        bias = np.array([0.1, 0.3, -0.2])
        hessian = np.array(
            [
                [1.0, 0.2, 0.0],
                [0.2, 0.8, -0.1],
                [0.0, -0.1, 0.6],
            ]
        )
        covariance = np.array(
            [
                [1.0, 0.3, 0.1],
                [0.3, 0.9, -0.2],
                [0.1, -0.2, 0.7],
            ]
        )
        directions = np.array(
            [[1.0, -1.0, 0.0]]
        )
        coefficients = np.array([-0.25])
        observed = generalized_policy_expectation_coefficient(
            gradient,
            bias,
            hessian,
            covariance,
            directions,
            coefficients,
        )
        contrast_variance = float(
            directions[0]
            @ covariance
            @ directions[0]
        )
        expected = float(
            gradient @ bias
            + 0.5 * np.trace(hessian @ covariance)
            - 0.25 * 0.5 * contrast_variance
        )
        self.assertAlmostEqual(observed, expected)

    def test_smooth_composition_rule(self) -> None:
        gradient = np.array([0.3, -0.1])
        covariance = np.array(
            [[1.0, 0.2], [0.2, 0.8]]
        )
        observed = generalized_smooth_composition_coefficient(
            transform_first_derivative=1.4,
            transform_second_derivative=-0.6,
            probability_gradient=gradient,
            probability_generalized_coefficient=0.25,
            covariance=covariance,
        )
        expected = float(
            1.4 * 0.25
            - 0.3
            * (gradient @ covariance @ gradient)
        )
        self.assertAlmostEqual(observed, expected)

    def test_toy_policy_expansion_base_above_added(self) -> None:
        threshold = float(norm.ppf(0.95))
        trigger = 0.4
        direction = np.array([1.1, -0.7, 0.3])
        errors = []
        for step in (2e-3, 1e-3, 5e-4):
            exact = gaussian_toy_policy_contrast(
                threshold + step * direction[0],
                threshold + step * direction[1],
                trigger + step * direction[2],
            )
            approx = gaussian_toy_policy_piecewise_quadratic(
                threshold,
                trigger,
                step * direction[0],
                step * direction[1],
                step * direction[2],
            )
            errors.append(
                abs(exact - approx) / step**2
            )
        self.assertLess(errors[-1], errors[0])
        self.assertLess(errors[-1], 1e-3)

    def test_toy_policy_expansion_added_above_base(self) -> None:
        threshold = float(norm.ppf(0.95))
        trigger = 0.4
        direction = np.array([-0.8, 1.2, -0.2])
        errors = []
        for step in (2e-3, 1e-3, 5e-4):
            exact = gaussian_toy_policy_contrast(
                threshold + step * direction[0],
                threshold + step * direction[1],
                trigger + step * direction[2],
            )
            approx = gaussian_toy_policy_piecewise_quadratic(
                threshold,
                trigger,
                step * direction[0],
                step * direction[1],
                step * direction[2],
            )
            errors.append(
                abs(exact - approx) / step**2
            )
        self.assertLess(errors[-1], errors[0])
        self.assertLess(errors[-1], 1e-3)

    def test_toy_policy_components_have_one_kink(self) -> None:
        threshold = float(norm.ppf(0.95))
        components = gaussian_toy_policy_local_components(
            threshold,
            0.4,
        )
        self.assertEqual(
            components["kink_directions"].shape,
            (1, 3),
        )
        self.assertEqual(
            components["kink_coefficients"].shape,
            (1,),
        )

    def test_toy_policy_smooth_hessian_is_symmetric(self) -> None:
        threshold = float(norm.ppf(0.95))
        components = gaussian_toy_policy_local_components(
            threshold,
            0.4,
        )
        np.testing.assert_allclose(
            components["smooth_hessian"],
            components["smooth_hessian"].T,
        )


if __name__ == "__main__":
    unittest.main()
