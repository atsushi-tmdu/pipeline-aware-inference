from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    assemble_joint_quantile_covariance,
    expectation_level_reference_coefficient,
    hessian_covariance_block_contraction,
    threshold_ordering_stability_radius,
)


class D8AJointMomentTests(unittest.TestCase):
    def test_joint_covariance_diagonal(self) -> None:
        probabilities = np.array([0.8, 0.9])
        densities = np.array([2.0, 3.0])
        joint = np.array([[0.8, 0.72], [0.72, 0.9]])
        covariance = assemble_joint_quantile_covariance(
            probabilities,
            densities,
            joint,
        )
        self.assertAlmostEqual(
            covariance[0, 0],
            0.8 * 0.2 / 4.0,
        )
        self.assertAlmostEqual(
            covariance[1, 1],
            0.9 * 0.1 / 9.0,
        )

    def test_independent_off_diagonal_is_zero(self) -> None:
        probabilities = np.array([0.8, 0.9])
        densities = np.array([2.0, 3.0])
        joint = np.array([[0.8, 0.72], [0.72, 0.9]])
        covariance = assemble_joint_quantile_covariance(
            probabilities,
            densities,
            joint,
        )
        self.assertAlmostEqual(covariance[0, 1], 0.0)

    def test_joint_covariance_is_symmetric(self) -> None:
        probabilities = np.array([0.6, 0.7])
        densities = np.array([1.5, 2.0])
        joint = np.array([[0.6, 0.5], [0.5, 0.7]])
        covariance = assemble_joint_quantile_covariance(
            probabilities,
            densities,
            joint,
        )
        np.testing.assert_allclose(covariance, covariance.T)

    def test_joint_covariance_example_is_positive_semidefinite(self) -> None:
        probabilities = np.array([0.6, 0.7])
        densities = np.array([1.5, 2.0])
        joint = np.array([[0.6, 0.5], [0.5, 0.7]])
        covariance = assemble_joint_quantile_covariance(
            probabilities,
            densities,
            joint,
        )
        self.assertGreaterEqual(
            float(np.min(np.linalg.eigvalsh(covariance))),
            -1e-12,
        )

    def test_block_contraction_matches_full_trace(self) -> None:
        h_qq = np.array([[1.0, 0.2], [0.2, 0.8]])
        h_qc = np.array([0.4, -0.3])
        h_cc = 1.2
        s_qq = np.array([[1.1, 0.1], [0.1, 0.9]])
        s_qc = np.array([0.25, -0.15])
        s_cc = 0.7

        pieces = hessian_covariance_block_contraction(
            h_qq,
            h_qc,
            h_cc,
            s_qq,
            s_qc,
            s_cc,
        )
        h_full = np.block(
            [
                [h_qq, h_qc[:, None]],
                [h_qc[None, :], np.array([[h_cc]])],
            ]
        )
        s_full = np.block(
            [
                [s_qq, s_qc[:, None]],
                [s_qc[None, :], np.array([[s_cc]])],
            ]
        )
        expected = float(0.5 * np.trace(h_full @ s_full))
        self.assertAlmostEqual(pieces["total"], expected)

    def test_cross_term_is_retained(self) -> None:
        pieces = hessian_covariance_block_contraction(
            np.eye(2),
            np.array([2.0, -1.0]),
            0.0,
            np.eye(2),
            np.array([0.4, 0.3]),
            0.0,
        )
        self.assertAlmostEqual(
            pieces["candidate_trigger"],
            0.5,
        )

    def test_expectation_level_coefficient(self) -> None:
        gradient = np.array([0.5, -0.1])
        bias_b = np.array([0.2, 0.3])
        hessian = np.array([[1.0, 0.2], [0.2, 0.8]])
        covariance = np.array([[1.1, 0.1], [0.1, 0.9]])
        expected = float(
            gradient @ bias_b
            + 0.5 * np.trace(hessian @ covariance)
        )
        observed = expectation_level_reference_coefficient(
            gradient,
            bias_b,
            hessian,
            covariance,
        )
        self.assertAlmostEqual(observed, expected)

    def test_positive_separation_has_stability_radius(self) -> None:
        radius = threshold_ordering_stability_radius(
            np.array([1.0, 2.0, 3.0]),
            1.4,
        )
        self.assertAlmostEqual(radius, 0.2)

    def test_coincidence_has_zero_stability_radius(self) -> None:
        radius = threshold_ordering_stability_radius(
            np.array([1.0, 2.0, 3.0]),
            2.0,
        )
        self.assertEqual(radius, 0.0)


if __name__ == "__main__":
    unittest.main()
