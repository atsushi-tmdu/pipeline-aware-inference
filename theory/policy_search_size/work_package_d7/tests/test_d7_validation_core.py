from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

from d7_numerical_design import build_dgp
from d7_validation_core import (
    CellDefinition,
    build_cell_definitions,
    empirical_quantile_batch,
    estimate_batch,
    maximum_cdf,
    plus_one_threshold_batch,
    policy_state_batch,
    stable_seed,
    tess_value,
)


ROOT = Path(__file__).resolve().parents[1]


class D7ValidationCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "D7_NUMERICAL_CONFIG.json").read_text(
                encoding="utf-8"
            )
        )
        cls.specifications = json.loads(
            (ROOT / "D7_DGP_SPECIFICATIONS.json").read_text(
                encoding="utf-8"
            )
        )
        cls.dgp = build_dgp(
            "transparent_k3_max_trigger",
            cls.specifications["dgps"][
                "transparent_k3_max_trigger"
            ],
        )

    def test_stable_seed_is_reproducible(self) -> None:
        self.assertEqual(
            stable_seed("a", 1, 2.0),
            stable_seed("a", 1, 2.0),
        )
        self.assertNotEqual(
            stable_seed("a", 1),
            stable_seed("a", 2),
        )

    def test_empirical_quantile_uses_generalized_inverse(self) -> None:
        values = np.array(
            [
                [[4.0], [1.0], [3.0], [2.0]],
                [[8.0], [5.0], [7.0], [6.0]],
            ]
        )
        result, index = empirical_quantile_batch(values, 0.75)
        self.assertEqual(index, 2)
        np.testing.assert_array_equal(result[:, 0], [3.0, 7.0])

    def test_plus_one_threshold_is_not_below_regular_tail(self) -> None:
        values = np.arange(1, 21, dtype=float).reshape(1, 20, 1)
        plus, _, attainable = plus_one_threshold_batch(values, 0.10)
        regular, _ = empirical_quantile_batch(values, 0.90)
        self.assertTrue(attainable)
        self.assertGreaterEqual(float(plus[0, 0]), float(regular[0, 0]))

    def test_policy_covariance_identity(self) -> None:
        scores = np.array(
            [
                [
                    [0.9, 0.8, 0.7],
                    [0.8, 0.7, 0.95],
                    [0.65, 0.85, 0.9],
                    [0.7, 0.6, 0.8],
                ]
            ]
        )
        state, ties = policy_state_batch(
            scores,
            np.array([0.85, 0.8, 0.85]),
            0.75,
            self.dgp,
        )
        self.assertEqual(sum(ties.values()), 0)
        r0 = state.base_reject.astype(float)
        a = state.activation.astype(float)
        m = state.incremental.astype(float)
        h = state.adaptive_reject.astype(float)
        delta = np.mean(h) - (
            np.mean(r0) + np.mean(a) * np.mean(m)
        )
        covariance = np.mean(a * m) - np.mean(a) * np.mean(m)
        self.assertAlmostEqual(float(delta), float(covariance), places=15)

    def test_maximum_cdf_is_between_zero_and_one(self) -> None:
        value = maximum_cdf(
            self.dgp,
            0.5,
            maxpts=100000,
            abseps=1e-7,
            releps=1e-7,
            seed=123,
        )
        self.assertGreater(value, 0.0)
        self.assertLess(value, 1.0)

    def test_cell_definitions_include_main_and_diagnostics(self) -> None:
        _, cells = build_cell_definitions(
            self.config,
            self.specifications,
            include_diagnostics=True,
            cdf_settings={
                "maxpts": 100000,
                "abseps": 1e-7,
                "releps": 1e-7,
                "master_seed": 123,
            },
        )
        self.assertEqual(
            sum(cell.cell_type == "main" for cell in cells),
            18,
        )
        self.assertEqual(
            sum(cell.cell_type == "near" for cell in cells),
            8,
        )
        self.assertEqual(
            sum(cell.cell_type == "exact" for cell in cells),
            1,
        )

    def test_tess_zero_is_zero(self) -> None:
        self.assertEqual(tess_value(0.0, 0.05), 0.0)

    def test_small_batch_estimation_is_finite(self) -> None:
        _, cells = build_cell_definitions(
            self.config,
            self.specifications,
            include_diagnostics=False,
            cdf_settings={
                "maxpts": 100000,
                "abseps": 1e-7,
                "releps": 1e-7,
                "master_seed": 123,
            },
        )
        cell = next(
            cell for cell in cells
            if cell.dgp == "transparent_k3_max_trigger"
            and math.isclose(cell.alpha, 0.05)
        )
        rng = np.random.default_rng(123)
        reference = rng.multivariate_normal(
            self.dgp.mean,
            self.dgp.covariance,
            size=(2, 100),
        )
        evaluation = rng.multivariate_normal(
            self.dgp.mean,
            self.dgp.covariance,
            size=(2, 120),
        )
        estimate = estimate_batch(
            reference,
            evaluation,
            cell,
            self.dgp,
        )
        self.assertTrue(
            np.isfinite(estimate["regular"]["delta_pi"]).all()
        )
        self.assertTrue(
            np.isfinite(estimate["regular"]["delta_s"]).all()
        )
        self.assertEqual(estimate["support_violations"], 0)


if __name__ == "__main__":
    unittest.main()
