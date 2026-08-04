from __future__ import annotations

import unittest

import numpy as np

from d7_core import (
    candidate_threshold_jump_field,
    coincidence_directional_term,
    coincidence_relevance_field,
    complete_replication_resample,
    contrast_summary,
    evaluation_influence_contrast,
    generalized_inverse_quantile,
    maximum_trigger_quantile,
    maximum_trigger_score,
    policy_state,
    threshold_separation,
    validate_nested_pools,
    winner_indices,
)


class D7CoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = (0, 1)
        self.full = (0, 1, 2)

    def test_nested_pool_validation(self) -> None:
        pools = validate_nested_pools(self.base, self.full, 3)
        self.assertEqual(pools.base, self.base)
        self.assertEqual(pools.full, self.full)

    def test_unique_winner_is_required(self) -> None:
        with self.assertRaises(ValueError):
            winner_indices(
                np.array([[0.8, 0.8, 0.7]]),
                self.base,
            )

    def test_maximum_equals_base_winner_score(self) -> None:
        scores = np.array(
            [[0.9, 0.8, 0.95], [0.6, 0.7, 0.65]]
        )
        winners, maxima = maximum_trigger_score(scores, self.base)
        np.testing.assert_array_equal(winners, [0, 1])
        np.testing.assert_allclose(maxima, [0.9, 0.7])

    def test_generalized_inverse_quantile(self) -> None:
        values = np.array([4.0, 1.0, 3.0, 2.0])
        self.assertEqual(
            generalized_inverse_quantile(values, 0.50),
            2.0,
        )
        self.assertEqual(
            generalized_inverse_quantile(values, 0.75),
            3.0,
        )

    def test_maximum_trigger_quantile(self) -> None:
        scores = np.array(
            [[0.2, 0.4, 9.0], [0.8, 0.1, 9.0], [0.5, 0.6, 9.0]]
        )
        self.assertEqual(
            maximum_trigger_quantile(scores, self.base, 2.0 / 3.0),
            0.6,
        )

    def test_policy_activation_uses_base_maximum(self) -> None:
        scores = np.array(
            [[0.9, 0.8, 0.7], [0.6, 0.7, 0.95]]
        )
        state = policy_state(
            scores,
            np.array([0.85, 0.75, 0.9]),
            self.base,
            self.full,
            0.8,
        )
        np.testing.assert_array_equal(state.base_maximum, [0.9, 0.7])
        np.testing.assert_array_equal(state.activation, [True, False])

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
            np.array([0.85, 0.8, 0.85]),
            self.base,
            self.full,
            0.75,
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
            np.array([0.85, 0.8, 0.85]),
            self.base,
            self.full,
            0.75,
        )
        self.assertAlmostEqual(
            float(np.mean(evaluation_influence_contrast(state))),
            0.0,
            places=15,
        )

    def test_candidate_jump_field_is_inherited_from_d6(self) -> None:
        scores = np.array([[0.8, 0.7, 0.9]])
        state = policy_state(
            scores,
            np.array([0.8, 0.5, 0.85]),
            self.base,
            self.full,
            1.0,
        )
        self.assertEqual(
            int(
                candidate_threshold_jump_field(
                    state,
                    0,
                    self.base,
                    self.full,
                )[0]
            ),
            1,
        )

    def test_separation_detects_regular_regime(self) -> None:
        result = threshold_separation(
            np.array([0.9, 1.1, 1.3]),
            0.7,
            self.base,
        )
        np.testing.assert_allclose(result.differences, [0.2, 0.4])
        self.assertAlmostEqual(
            result.minimum_absolute_separation,
            0.2,
        )
        self.assertTrue(result.separated)

    def test_separation_detects_coincidence(self) -> None:
        result = threshold_separation(
            np.array([0.7, 1.1, 1.3]),
            0.7,
            self.base,
        )
        self.assertEqual(result.minimum_absolute_separation, 0.0)
        self.assertFalse(result.separated)

    def test_coincidence_relevance_field(self) -> None:
        scores = np.array(
            [[0.8, 0.7, 0.9], [0.9, 0.8, 0.7]]
        )
        state = policy_state(
            scores,
            np.array([0.8, 0.5, 0.85]),
            self.base,
            self.full,
            0.8,
        )
        np.testing.assert_array_equal(
            coincidence_relevance_field(state, 0, self.base),
            [True, False],
        )

    def test_positive_part_directional_term(self) -> None:
        self.assertEqual(
            coincidence_directional_term(2.0, 1.0, 0.0),
            2.0,
        )
        self.assertEqual(
            coincidence_directional_term(2.0, 0.0, 1.0),
            0.0,
        )
        self.assertEqual(
            coincidence_directional_term(2.0, 1.0, 1.0),
            0.0,
        )

    def test_directional_term_is_not_linear(self) -> None:
        first = coincidence_directional_term(1.0, 1.0, 0.0)
        second = coincidence_directional_term(1.0, 0.0, 1.0)
        combined = coincidence_directional_term(1.0, 1.0, 1.0)
        self.assertNotEqual(combined, first + second)

    def test_complete_vector_resampling_preserves_rows(self) -> None:
        scores = np.array(
            [[1.0, 10.0, 100.0], [2.0, 20.0, 200.0]]
        )
        indices = np.array([1, 0, 1])
        sampled = complete_replication_resample(scores, indices)
        np.testing.assert_array_equal(sampled, scores[indices])


if __name__ == "__main__":
    unittest.main()
