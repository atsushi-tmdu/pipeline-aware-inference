from __future__ import annotations

import unittest

import numpy as np

from d6_core import (
    branch_rejection,
    candidate_threshold_jump_field,
    complete_replication_resample,
    contrast_summary,
    direct_incremental_threshold_jump,
    evaluation_influence_contrast,
    policy_state,
    tess_derivative,
    tess_transform,
    validate_nested_pools,
    winner_indices,
)


class D6CoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = (0, 1)
        self.full = (0, 1, 2)

    def test_nested_pool_validation(self) -> None:
        pools = validate_nested_pools(self.base, self.full, 3)
        self.assertEqual(pools.base, self.base)
        self.assertEqual(pools.full, self.full)
        with self.assertRaises(ValueError):
            validate_nested_pools((0, 2), (0, 1), 3)

    def test_unique_winner_indices(self) -> None:
        scores = np.array([[0.9, 0.8, 0.7], [0.6, 0.7, 0.95]])
        np.testing.assert_array_equal(
            winner_indices(scores, self.base),
            np.array([0, 1]),
        )
        np.testing.assert_array_equal(
            winner_indices(scores, self.full),
            np.array([0, 2]),
        )

    def test_exact_tie_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            winner_indices(np.array([[0.8, 0.8, 0.7]]), self.base)

    def test_winner_region_representation(self) -> None:
        scores = np.array(
            [[0.9, 0.8, 0.7], [0.6, 0.7, 0.95], [0.65, 0.85, 0.8]]
        )
        thresholds = np.array([0.75, 0.8, 0.9])
        winners = winner_indices(scores, self.full)
        direct = branch_rejection(scores, winners, thresholds)
        represented = np.zeros(scores.shape[0], dtype=bool)
        for candidate in self.full:
            represented |= (
                (winners == candidate)
                & (scores[:, candidate] > thresholds[candidate])
            )
        np.testing.assert_array_equal(direct, represented)

    def test_policy_state_uses_nested_random_winners(self) -> None:
        scores = np.array([[0.9, 0.8, 0.7], [0.8, 0.7, 0.95]])
        state = policy_state(
            scores,
            np.array([0.2, 0.9]),
            np.array([0.85, 0.75, 0.9]),
            self.base,
            self.full,
            0.5,
        )
        np.testing.assert_array_equal(state.base_winner, [0, 0])
        np.testing.assert_array_equal(state.full_winner, [0, 2])
        np.testing.assert_array_equal(state.activation, [False, True])

    def test_covariance_identity(self) -> None:
        scores = np.array(
            [
                [0.9, 0.8, 0.7],
                [0.8, 0.7, 0.95],
                [0.65, 0.85, 0.9],
                [0.7, 0.6, 0.8],
            ]
        )
        state = policy_state(
            scores,
            np.array([0.2, 0.9, 0.8, 0.1]),
            np.array([0.85, 0.8, 0.85]),
            self.base,
            self.full,
            0.5,
        )
        summary = contrast_summary(state)
        a = state.activation.astype(float)
        m = state.incremental.astype(float)
        expected = np.mean(a * m) - np.mean(a) * np.mean(m)
        self.assertAlmostEqual(summary.delta_pi, expected, places=15)

    def test_evaluation_influence_is_centered(self) -> None:
        scores = np.array(
            [
                [0.9, 0.8, 0.7],
                [0.8, 0.7, 0.95],
                [0.65, 0.85, 0.9],
                [0.7, 0.6, 0.8],
            ]
        )
        state = policy_state(
            scores,
            np.array([0.2, 0.9, 0.8, 0.1]),
            np.array([0.85, 0.8, 0.85]),
            self.base,
            self.full,
            0.5,
        )
        self.assertAlmostEqual(
            float(np.mean(evaluation_influence_contrast(state))),
            0.0,
            places=15,
        )

    def _single_state(self, row: np.ndarray, thresholds: np.ndarray):
        return policy_state(
            row[None, :],
            np.array([0.0]),
            thresholds,
            self.base,
            self.full,
            1.0,
        )

    def test_displaced_base_winner_jump_is_positive(self) -> None:
        row = np.array([0.8, 0.7, 0.9])
        thresholds = np.array([0.8, 0.5, 0.85])
        field = candidate_threshold_jump_field(
            self._single_state(row, thresholds),
            0,
            self.base,
            self.full,
        )
        self.assertEqual(int(field[0]), 1)
        self.assertEqual(
            direct_incremental_threshold_jump(
                row, thresholds, self.base, self.full, 0
            ),
            1,
        )

    def test_extra_full_winner_jump_is_negative(self) -> None:
        row = np.array([0.8, 0.7, 0.9])
        thresholds = np.array([0.85, 0.5, 0.9])
        field = candidate_threshold_jump_field(
            self._single_state(row, thresholds),
            2,
            self.base,
            self.full,
        )
        self.assertEqual(int(field[0]), -1)
        self.assertEqual(
            direct_incremental_threshold_jump(
                row, thresholds, self.base, self.full, 2
            ),
            -1,
        )

    def test_shared_base_full_winner_jump_is_zero(self) -> None:
        row = np.array([0.9, 0.8, 0.7])
        thresholds = np.array([0.9, 0.5, 0.6])
        field = candidate_threshold_jump_field(
            self._single_state(row, thresholds),
            0,
            self.base,
            self.full,
        )
        self.assertEqual(int(field[0]), 0)
        self.assertEqual(
            direct_incremental_threshold_jump(
                row, thresholds, self.base, self.full, 0
            ),
            0,
        )

    def test_nonwinner_jump_is_zero(self) -> None:
        row = np.array([0.9, 0.8, 0.7])
        thresholds = np.array([0.6, 0.8, 0.6])
        field = candidate_threshold_jump_field(
            self._single_state(row, thresholds),
            1,
            self.base,
            self.full,
        )
        self.assertEqual(int(field[0]), 0)
        self.assertEqual(
            direct_incremental_threshold_jump(
                row, thresholds, self.base, self.full, 1
            ),
            0,
        )

    def test_vector_jump_field_matches_direct_jumps(self) -> None:
        scores = np.array(
            [[0.8, 0.7, 0.9], [0.9, 0.8, 0.7], [0.65, 0.85, 0.8]]
        )
        thresholds = np.array([0.8, 0.85, 0.9])
        state = policy_state(
            scores,
            np.zeros(3),
            thresholds,
            self.base,
            self.full,
            1.0,
        )
        for candidate in self.full:
            field = candidate_threshold_jump_field(
                state, candidate, self.base, self.full
            )
            direct = np.array(
                [
                    direct_incremental_threshold_jump(
                        row,
                        thresholds,
                        self.base,
                        self.full,
                        candidate,
                    )
                    for row in scores
                ]
            )
            np.testing.assert_array_equal(field, direct)

    def test_complete_replication_resample_preserves_rows(self) -> None:
        scores = np.array(
            [[1.0, 10.0, 100.0], [2.0, 20.0, 200.0], [3.0, 30.0, 300.0]]
        )
        activation = np.array([0.1, 0.2, 0.3])
        indices = np.array([2, 0, 2, 1])
        sampled_scores, sampled_activation = complete_replication_resample(
            scores, activation, indices
        )
        np.testing.assert_array_equal(sampled_scores, scores[indices])
        np.testing.assert_array_equal(sampled_activation, activation[indices])

    def test_tess_derivative_matches_finite_difference(self) -> None:
        pi = 0.12
        alpha = 0.05
        h = 1e-7
        numeric = (
            tess_transform(pi + h, alpha)
            - tess_transform(pi - h, alpha)
        ) / (2.0 * h)
        self.assertAlmostEqual(tess_derivative(pi, alpha), numeric, places=7)


if __name__ == "__main__":
    unittest.main()
