from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from simulations.ess.phase3c_adaptive_ml_policy import (
    apply_promising_trigger,
    calibrate_promising_trigger,
    candidate_winners,
    empirical_upper_p,
    pvalues_for_winners,
    random_trigger,
    summarize_curves,
)


class Phase3CAdaptiveMLPolicyTests(unittest.TestCase):
    def test_empirical_upper_p(self) -> None:
        reference = np.asarray([0.1, 0.2, 0.3, 0.4])
        self.assertAlmostEqual(empirical_upper_p(0.3, reference), 3 / 5)
        self.assertAlmostEqual(empirical_upper_p(0.5, reference), 1 / 5)

    def test_candidate_tie_uses_candidate_order(self) -> None:
        matrix = pd.DataFrame(
            {
                "a": [0.7, 0.6],
                "b": [0.7, 0.8],
            },
            index=[0, 1],
        )
        models, scores = candidate_winners(matrix, ["a", "b"])
        self.assertEqual(models.tolist(), ["a", "b"])
        self.assertEqual(scores.tolist(), [0.7, 0.8])

    def test_trigger_calibration(self) -> None:
        values = np.linspace(0.5, 0.9, 1000)
        threshold, tie_probability = calibrate_promising_trigger(values, 0.5)
        trigger = apply_promising_trigger(
            values,
            np.arange(values.size),
            threshold,
            tie_probability,
            seed=1,
        )
        self.assertAlmostEqual(float(trigger.mean()), 0.5, delta=0.002)

    def test_random_trigger_is_reproducible(self) -> None:
        ids = np.arange(1000)
        first = random_trigger(ids, 0.5, seed=17)
        second = random_trigger(ids, 0.5, seed=17)
        self.assertTrue(np.array_equal(first, second))
        self.assertAlmostEqual(float(first.mean()), 0.5, delta=0.05)

    def test_model_specific_pvalues(self) -> None:
        lookup = {
            "a": np.asarray([0.1, 0.2, 0.3]),
            "b": np.asarray([0.5, 0.6, 0.7]),
        }
        pvalues = pvalues_for_winners(
            np.asarray(["a", "b"], dtype=object),
            np.asarray([0.25, 0.65]),
            lookup,
        )
        self.assertTrue(np.allclose(pvalues, [0.5, 0.5]))

    def test_curve_summary_orders_fixed_example(self) -> None:
        bank = pd.DataFrame(
            {
                "replication": list(range(10)) * 2,
                "policy": ["fixed_base"] * 10 + ["fixed_full"] * 10,
                "policy_label": ["base"] * 10 + ["full"] * 10,
                "expanded": [False] * 10 + [True] * 10,
                "evaluated_candidate_count": [7] * 10 + [20] * 10,
                "naive_empirical_p_value": (
                    [0.01, 0.02, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                    + [0.01, 0.02, 0.03, 0.04, 0.05, 0.2, 0.3, 0.4, 0.5, 0.6]
                ),
            }
        )
        summary = summarize_curves(bank, (0.05,))
        base = float(summary.loc[summary["policy"] == "fixed_base", "tess"].iloc[0])
        full = float(summary.loc[summary["policy"] == "fixed_full", "tess"].iloc[0])
        self.assertGreater(full, base)


if __name__ == "__main__":
    unittest.main()
