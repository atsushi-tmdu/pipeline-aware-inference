from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    bahadur_second_moment_entry_error_bound,
    exact_influence_covariance_from_atoms,
    joint_quantile_second_moment_limit,
    quantile_influence_vector,
    vector_moment_bound_from_component_bounds,
)


class D8AJointQuantileLiftingTests(unittest.TestCase):
    def test_quantile_influence_sign(self) -> None:
        observed = quantile_influence_vector(
            np.array([1.0, 0.0]),
            np.array([0.8, 0.9]),
            np.array([2.0, 3.0]),
        )
        np.testing.assert_allclose(
            observed,
            np.array([-0.1, 0.3]),
        )

    def test_atom_covariance_matches_joint_formula(self) -> None:
        # P(I1=1,I2=1)=0.5, marginals 0.6 and 0.7.
        atom_probabilities = np.array([0.2, 0.2, 0.1, 0.5])
        atoms = np.array(
            [
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],
            ]
        )
        probabilities = np.array([0.6, 0.7])
        densities = np.array([1.5, 2.0])

        exact = exact_influence_covariance_from_atoms(
            atom_probabilities,
            atoms,
            probabilities,
            densities,
        )
        joint = np.array([[0.6, 0.5], [0.5, 0.7]])
        formula = joint_quantile_second_moment_limit(
            joint,
            probabilities,
            densities,
        )
        np.testing.assert_allclose(exact, formula)

    def test_complete_vector_dependence_is_nonzero(self) -> None:
        joint = np.array([[0.6, 0.5], [0.5, 0.7]])
        covariance = joint_quantile_second_moment_limit(
            joint,
            np.array([0.6, 0.7]),
            np.array([1.5, 2.0]),
        )
        self.assertGreater(abs(covariance[0, 1]), 1e-6)

    def test_independence_gives_zero_cross_covariance(self) -> None:
        joint = np.array([[0.6, 0.42], [0.42, 0.7]])
        covariance = joint_quantile_second_moment_limit(
            joint,
            np.array([0.6, 0.7]),
            np.array([1.5, 2.0]),
        )
        self.assertAlmostEqual(covariance[0, 1], 0.0)

    def test_remainder_error_bound_vanishes(self) -> None:
        observed = bahadur_second_moment_entry_error_bound(
            leading_variance_left=0.4,
            leading_variance_right=0.7,
            scaled_l2_remainder_left=0.0,
            scaled_l2_remainder_right=0.0,
        )
        self.assertEqual(observed, 0.0)

    def test_remainder_error_bound_decreases(self) -> None:
        large = bahadur_second_moment_entry_error_bound(
            0.4,
            0.7,
            0.10,
            0.08,
        )
        small = bahadur_second_moment_entry_error_bound(
            0.4,
            0.7,
            0.01,
            0.008,
        )
        self.assertLess(small, large)

    def test_vector_moment_bound(self) -> None:
        observed = vector_moment_bound_from_component_bounds(
            np.array([2.0, 3.0, 5.0]),
            moment_order=4.0,
        )
        # d^(4/2-1) * sum = 3 * 10.
        self.assertAlmostEqual(observed, 30.0)

    def test_second_moment_limit_is_positive_semidefinite(self) -> None:
        joint = np.array([[0.6, 0.5], [0.5, 0.7]])
        covariance = joint_quantile_second_moment_limit(
            joint,
            np.array([0.6, 0.7]),
            np.array([1.5, 2.0]),
        )
        self.assertGreaterEqual(
            float(np.min(np.linalg.eigvalsh(covariance))),
            -1e-12,
        )


if __name__ == "__main__":
    unittest.main()
