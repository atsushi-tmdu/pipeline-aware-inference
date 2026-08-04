from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    independent_gaussian_cell_components,
    independent_gaussian_cell_contrast,
    independent_gaussian_cell_contrast_derivatives,
    moving_face_first_derivative_sign,
    moving_face_mixed_derivative_sign,
    policy_contrast_gradient,
    policy_contrast_hessian,
    separated_activation_regime,
    winner_cell_incremental_is_possible,
)


class D8APolicyC2TheoremTests(unittest.TestCase):
    def test_moving_face_signs(self) -> None:
        self.assertEqual(
            moving_face_first_derivative_sign(True),
            -1.0,
        )
        self.assertEqual(
            moving_face_first_derivative_sign(False),
            1.0,
        )
        self.assertEqual(
            moving_face_mixed_derivative_sign(True, False),
            -1.0,
        )

    def test_same_winner_has_no_incremental_branch(self) -> None:
        self.assertFalse(
            winner_cell_incremental_is_possible(2, 2)
        )
        self.assertTrue(
            winner_cell_incremental_is_possible(2, 5)
        )

    def test_regime_classification(self) -> None:
        self.assertEqual(
            separated_activation_regime(1.0, 0.5),
            "trigger_below_candidate",
        )
        self.assertEqual(
            separated_activation_regime(1.0, 1.5),
            "trigger_above_candidate",
        )
        self.assertEqual(
            separated_activation_regime(1.0, 1.0),
            "coincidence_nonregular",
        )

    def test_contrast_gradient_matches_finite_difference(self) -> None:
        point = np.array([0.6, 0.3, -0.2])
        step = 1e-5
        analytic, _ = independent_gaussian_cell_contrast_derivatives(
            *point
        )
        finite = np.zeros(3)
        for index in range(3):
            offset = np.zeros(3)
            offset[index] = step
            finite[index] = (
                independent_gaussian_cell_contrast(
                    *(point + offset)
                )
                - independent_gaussian_cell_contrast(
                    *(point - offset)
                )
            ) / (2.0 * step)
        np.testing.assert_allclose(
            finite,
            analytic,
            atol=1e-9,
            rtol=1e-7,
        )

    def test_contrast_hessian_matches_finite_difference(self) -> None:
        point = np.array([0.6, 0.3, -0.2])
        step = 1e-5
        _, analytic = independent_gaussian_cell_contrast_derivatives(
            *point
        )
        finite = np.zeros((3, 3))
        for index in range(3):
            offset = np.zeros(3)
            offset[index] = step
            gradient_plus, _ = (
                independent_gaussian_cell_contrast_derivatives(
                    *(point + offset)
                )
            )
            gradient_minus, _ = (
                independent_gaussian_cell_contrast_derivatives(
                    *(point - offset)
                )
            )
            finite[:, index] = (
                gradient_plus - gradient_minus
            ) / (2.0 * step)
        np.testing.assert_allclose(
            finite,
            analytic,
            atol=1e-8,
            rtol=1e-6,
        )

    def test_contrast_hessian_is_symmetric(self) -> None:
        _, hessian = independent_gaussian_cell_contrast_derivatives(
            0.6,
            0.3,
            -0.2,
        )
        np.testing.assert_allclose(hessian, hessian.T)

    def test_product_rule_gradient(self) -> None:
        components = independent_gaussian_cell_components(
            0.6,
            0.3,
            -0.2,
        )
        observed = policy_contrast_gradient(
            components["gradient_joint"],
            components["probability_activation"],
            components["gradient_activation"],
            components["probability_incremental"],
            components["gradient_incremental"],
        )
        expected, _ = independent_gaussian_cell_contrast_derivatives(
            0.6,
            0.3,
            -0.2,
        )
        np.testing.assert_allclose(observed, expected)

    def test_product_rule_hessian(self) -> None:
        components = independent_gaussian_cell_components(
            0.6,
            0.3,
            -0.2,
        )
        observed = policy_contrast_hessian(
            components["hessian_joint"],
            components["probability_activation"],
            components["gradient_activation"],
            components["hessian_activation"],
            components["probability_incremental"],
            components["gradient_incremental"],
            components["hessian_incremental"],
        )
        _, expected = independent_gaussian_cell_contrast_derivatives(
            0.6,
            0.3,
            -0.2,
        )
        np.testing.assert_allclose(observed, expected)


if __name__ == "__main__":
    unittest.main()
