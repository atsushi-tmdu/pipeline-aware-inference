from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    bivariate_normal_candidate_gradient,
    bivariate_normal_candidate_second_derivative,
    bivariate_normal_policy_hessian,
    bivariate_normal_trigger_gradient,
    bivariate_normal_trigger_second_derivative,
    finite_winner_cell_count,
    local_threshold_box_is_order_stable,
)


class D8APolicySmoothnessTests(unittest.TestCase):
    def test_candidate_second_derivative_matches_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        finite = (
            bivariate_normal_candidate_gradient(q + h, c, r)
            - bivariate_normal_candidate_gradient(q - h, c, r)
        ) / (2.0 * h)
        analytic = bivariate_normal_candidate_second_derivative(q, c, r)
        self.assertAlmostEqual(finite, analytic, places=6)

    def test_trigger_second_derivative_matches_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        finite = (
            bivariate_normal_trigger_gradient(q, c + h, r)
            - bivariate_normal_trigger_gradient(q, c - h, r)
        ) / (2.0 * h)
        analytic = bivariate_normal_trigger_second_derivative(q, c, r)
        self.assertAlmostEqual(finite, analytic, places=6)

    def test_hessian_is_symmetric(self) -> None:
        hessian = bivariate_normal_policy_hessian(0.4, 0.8, 0.55)
        np.testing.assert_allclose(hessian, hessian.T)

    def test_mixed_partials_agree_by_finite_difference(self) -> None:
        q, c, r, h = 0.4, 0.8, 0.55, 1e-5
        q_then_c = (
            bivariate_normal_candidate_gradient(q, c + h, r)
            - bivariate_normal_candidate_gradient(q, c - h, r)
        ) / (2.0 * h)
        c_then_q = (
            bivariate_normal_trigger_gradient(q + h, c, r)
            - bivariate_normal_trigger_gradient(q - h, c, r)
        ) / (2.0 * h)
        self.assertAlmostEqual(q_then_c, c_then_q, places=6)

    def test_stable_box_inside_half_gap(self) -> None:
        candidates = np.array([1.0, 2.0, 3.0])
        self.assertTrue(
            local_threshold_box_is_order_stable(
                candidates,
                1.4,
                0.19,
            )
        )

    def test_unstable_box_at_or_beyond_half_gap(self) -> None:
        candidates = np.array([1.0, 2.0, 3.0])
        self.assertFalse(
            local_threshold_box_is_order_stable(
                candidates,
                1.4,
                0.20,
            )
        )

    def test_coincidence_has_no_positive_stable_box(self) -> None:
        candidates = np.array([1.0, 2.0, 3.0])
        self.assertFalse(
            local_threshold_box_is_order_stable(
                candidates,
                2.0,
                0.01,
            )
        )

    def test_finite_winner_cell_count(self) -> None:
        self.assertEqual(finite_winner_cell_count(7, 20), 140)


if __name__ == "__main__":
    unittest.main()
