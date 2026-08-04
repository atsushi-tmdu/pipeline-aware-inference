from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    joint_quantile_first_order_covariance,
    quantile_lattice_offset,
    scalar_quantile_bias_coefficient,
    second_order_reference_coefficient_b_dependent,
    uniform_order_statistic_bias,
)


class D8AQuantileExpansionTests(unittest.TestCase):
    def test_lattice_offset_can_oscillate(self) -> None:
        self.assertAlmostEqual(
            quantile_lattice_offset(100, 0.37),
            -0.37,
        )
        self.assertAlmostEqual(
            quantile_lattice_offset(101, 0.37),
            0.26,
        )

    def test_d7_candidate_grid_is_lattice_aligned(self) -> None:
        for probability in (0.99, 0.95, 0.90):
            for reference_size in (1000, 3000, 5000):
                self.assertAlmostEqual(
                    quantile_lattice_offset(
                        reference_size,
                        probability,
                    ),
                    -probability,
                    places=10,
                )

    def test_uniform_exact_bias_identity(self) -> None:
        B = 1000
        p = 0.99
        exact = uniform_order_statistic_bias(B, p)
        lattice = quantile_lattice_offset(B, p)
        self.assertAlmostEqual((B + 1) * exact, lattice, places=12)

    def test_scalar_quantile_bias_uniform_case(self) -> None:
        observed = scalar_quantile_bias_coefficient(
            reference_size=1000,
            probability=0.99,
            density_at_quantile=1.0,
            density_derivative_at_quantile=0.0,
        )
        self.assertAlmostEqual(observed, -0.99)

    def test_joint_quantile_covariance(self) -> None:
        observed = joint_quantile_first_order_covariance(
            joint_lower_probability=0.72,
            probability_left=0.8,
            probability_right=0.9,
            density_left=2.0,
            density_right=3.0,
        )
        self.assertAlmostEqual(observed, 0.0)

    def test_b_dependent_policy_coefficient(self) -> None:
        gradient = np.array([2.0, -1.0])
        bias_b = np.array([0.3, 0.2])
        hessian = np.array([[1.0, 0.5], [0.5, 2.0]])
        covariance = np.array([[4.0, 1.0], [1.0, 3.0]])
        expected = float(
            gradient @ bias_b
            + 0.5 * np.trace(hessian @ covariance)
        )
        observed = second_order_reference_coefficient_b_dependent(
            gradient,
            bias_b,
            hessian,
            covariance,
        )
        self.assertAlmostEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
