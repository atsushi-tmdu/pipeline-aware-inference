from __future__ import annotations

import unittest

from scipy.stats import norm

from d8a_coincidence_core import (
    centered_gaussian_positive_part_second_moment,
    gaussian_cell_branch_base_derivative,
    gaussian_cell_branch_kink_coefficient,
    gaussian_cell_branch_kink_jump,
    gaussian_cell_branch_piecewise_quadratic,
    gaussian_cell_branch_probability,
    generalized_kink_expectation_coefficient,
    ordinary_c2_applicable_at_candidate_coincidence,
)


class D8ACoincidenceRepairTests(unittest.TestCase):
    def test_one_sided_mixed_derivatives_differ(self) -> None:
        threshold = float(norm.ppf(0.95))
        step = 1e-6
        center = gaussian_cell_branch_base_derivative(
            threshold,
            threshold,
        )
        from_below = (
            center
            - gaussian_cell_branch_base_derivative(
                threshold,
                threshold - step,
            )
        ) / step
        from_above = (
            gaussian_cell_branch_base_derivative(
                threshold,
                threshold + step,
            )
            - center
        ) / step
        self.assertAlmostEqual(from_below, 0.0, places=10)
        self.assertAlmostEqual(
            from_above,
            gaussian_cell_branch_kink_jump(threshold),
            places=6,
        )

    def test_kink_coefficient_is_half_jump(self) -> None:
        threshold = float(norm.ppf(0.95))
        self.assertAlmostEqual(
            gaussian_cell_branch_kink_coefficient(threshold),
            0.5 * gaussian_cell_branch_kink_jump(threshold),
        )

    def test_piecewise_expansion_on_base_above_added_cone(self) -> None:
        threshold = float(norm.ppf(0.95))
        direction = (1.2, -0.7)
        errors = []
        for step in (2e-3, 1e-3, 5e-4):
            exact = gaussian_cell_branch_probability(
                threshold + step * direction[0],
                threshold + step * direction[1],
            )
            approx = gaussian_cell_branch_piecewise_quadratic(
                threshold,
                step * direction[0],
                step * direction[1],
            )
            errors.append(abs(exact - approx) / step**2)
        self.assertLess(errors[-1], errors[0])
        self.assertLess(errors[-1], 1e-3)

    def test_piecewise_expansion_on_added_above_base_cone(self) -> None:
        threshold = float(norm.ppf(0.95))
        direction = (-0.6, 1.1)
        errors = []
        for step in (2e-3, 1e-3, 5e-4):
            exact = gaussian_cell_branch_probability(
                threshold + step * direction[0],
                threshold + step * direction[1],
            )
            approx = gaussian_cell_branch_piecewise_quadratic(
                threshold,
                step * direction[0],
                step * direction[1],
            )
            errors.append(abs(exact - approx) / step**2)
        self.assertLess(errors[-1], errors[0])
        self.assertLess(errors[-1], 1e-3)

    def test_piecewise_expansion_on_coincident_direction(self) -> None:
        threshold = float(norm.ppf(0.95))
        direction = (0.8, 0.8)
        step = 5e-4
        exact = gaussian_cell_branch_probability(
            threshold + step * direction[0],
            threshold + step * direction[1],
        )
        approx = gaussian_cell_branch_piecewise_quadratic(
            threshold,
            step * direction[0],
            step * direction[1],
        )
        self.assertLess(abs(exact - approx) / step**2, 1e-3)

    def test_positive_part_second_moment(self) -> None:
        self.assertAlmostEqual(
            centered_gaussian_positive_part_second_moment(3.2),
            1.6,
        )

    def test_generalized_expectation_coefficient(self) -> None:
        self.assertAlmostEqual(
            generalized_kink_expectation_coefficient(
                -0.4,
                3.2,
            ),
            -0.64,
        )

    def test_ordinary_c2_is_blocked(self) -> None:
        self.assertFalse(
            ordinary_c2_applicable_at_candidate_coincidence()
        )


if __name__ == "__main__":
    unittest.main()
