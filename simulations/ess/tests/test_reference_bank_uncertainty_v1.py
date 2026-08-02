from __future__ import annotations

import unittest

import numpy as np

from simulations.ess.reference_bank_uncertainty_v1 import (
    PreparedBanks,
    apply_trigger,
    compute_effect,
    pvalues_from_reference_weights,
    tess,
    weighted_trigger,
)


class ReferenceBankUncertaintyTests(unittest.TestCase):
    def make_prepared(self) -> PreparedBanks:
        # Four reference replications and two candidates. Candidate 0 is the
        # base family; candidate 1 is optional. The object is intentionally
        # small so every weighted tail can be verified by hand.
        ref = np.asarray(
            [
                [0.10, 0.40],
                [0.20, 0.30],
                [0.30, 0.20],
                [0.40, 0.10],
            ],
            dtype=float,
        )
        eval_scores = np.asarray(
            [
                [0.25, 0.35],
                [0.35, 0.15],
                [0.15, 0.45],
            ],
            dtype=float,
        )
        order = np.argsort(ref, axis=0, kind="mergesort").T
        sorted_ref = np.take_along_axis(ref.T, order, axis=1)
        base_model = np.zeros(3, dtype=np.int64)
        base_score = eval_scores[:, 0]
        full_model = np.argmax(eval_scores, axis=1).astype(np.int64)
        full_score = eval_scores[np.arange(3), full_model]
        base_pos = np.searchsorted(sorted_ref[0], base_score, side="left")
        full_pos = np.empty(3, dtype=np.int64)
        for i in range(3):
            full_pos[i] = np.searchsorted(
                sorted_ref[full_model[i]], full_score[i], side="left"
            )
        unique, group = np.unique(ref[:, 0], return_inverse=True)
        return PreparedBanks(
            replication_ids_reference=np.arange(4),
            replication_ids_evaluation=np.arange(3),
            reference_scores=ref,
            evaluation_scores=eval_scores,
            full_models=("base", "extra"),
            base_model_indices=np.asarray([0]),
            full_model_indices=np.asarray([0, 1]),
            ref_order_by_model=order,
            ref_base_unique_values=unique,
            ref_base_group_index=group,
            eval_base_winner_model=base_model,
            eval_base_winner_score=base_score,
            eval_full_winner_model=full_model,
            eval_full_winner_score=full_score,
            eval_base_reference_position=base_pos,
            eval_full_reference_position=full_pos,
            eval_base_max=base_score,
            eval_tie_uniform=np.asarray([0.2, 0.8, 0.4]),
        )

    def test_tess_boundaries(self) -> None:
        self.assertAlmostEqual(tess(0.05, 0.05), 1.0)
        pi_k3 = 1.0 - (1.0 - 0.05) ** 3
        self.assertAlmostEqual(tess(pi_k3, 0.05), 3.0)

    def test_weighted_trigger(self) -> None:
        values = np.asarray([0.1, 0.2, 0.3, 0.4])
        groups = np.arange(4)
        threshold, tie = weighted_trigger(
            values, groups, np.ones(4, dtype=int), 0.5
        )
        self.assertEqual(threshold, 0.3)
        self.assertEqual(tie, 1.0)
        activation = apply_trigger(
            np.asarray([0.2, 0.3, 0.4]),
            np.asarray([0.2, 0.8, 0.4]),
            threshold,
            tie,
        )
        np.testing.assert_array_equal(activation, [False, True, True])

    def test_weighted_empirical_pvalues(self) -> None:
        prepared = self.make_prepared()
        weights = np.asarray([2, 0, 1, 1], dtype=np.int32)
        p_base, p_full = pvalues_from_reference_weights(prepared, weights)
        # Base score 0.25 has weighted upper count 2 -> (1+2)/(4+1)=0.6.
        self.assertAlmostEqual(p_base[0], 0.6)
        # Extra score 0.35 has weighted upper count 2 -> 0.6.
        self.assertAlmostEqual(p_full[0], 0.6)
        self.assertTrue(np.all((p_base > 0) & (p_base <= 1)))
        self.assertTrue(np.all((p_full > 0) & (p_full <= 1)))

    def test_covariance_identity(self) -> None:
        prepared = self.make_prepared()
        ref_weights = np.ones(4, dtype=np.int32)
        eval_weights = np.ones(3, dtype=np.int32)
        result = compute_effect(
            prepared,
            ref_weights,
            eval_weights,
            alpha=0.7,
            target_expansion_probability=0.5,
        )
        rejection_difference = (
            result["pi_promising"] - result["pi_matched_random"]
        )
        self.assertAlmostEqual(
            rejection_difference,
            result["cov_activation_increment"],
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
