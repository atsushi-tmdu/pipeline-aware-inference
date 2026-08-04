from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from d7_numerical_design import (
    build_dgp,
    candidate_thresholds,
    enumerate_bootstrap_cells,
    enumerate_main_cells,
    enumerate_near_coincidence_cells,
    trigger_boundary,
    validate_design,
)


ROOT = Path(__file__).resolve().parents[1]


def load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class D7NumericalDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_json("D7_NUMERICAL_CONFIG.json")
        cls.specs = load_json("D7_DGP_SPECIFICATIONS.json")
        cls.criteria = load_json("D7_SCIENTIFIC_CRITERIA.json")
        cls.dgp_order = cls.specs["dgp_order"]

    def test_all_covariances_are_positive_definite(self) -> None:
        for name in self.dgp_order:
            dgp = build_dgp(name, self.specs["dgps"][name])
            self.assertGreater(
                float(np.min(np.linalg.eigvalsh(dgp.covariance))),
                0.0,
            )

    def test_pools_are_fixed_and_nested(self) -> None:
        for name in self.dgp_order:
            dgp = build_dgp(name, self.specs["dgps"][name])
            self.assertTrue(set(dgp.base_pool).issubset(dgp.full_pool))
            self.assertIn(len(dgp.base_pool), {2, 7})
            self.assertIn(len(dgp.full_pool), {3, 20})

    def test_main_grid_has_72_cells_and_144000_rows(self) -> None:
        cells = enumerate_main_cells(self.config, self.dgp_order)
        self.assertEqual(len(cells), 72)
        self.assertEqual(
            sum(cell["outer_repetitions"] for cell in cells),
            144000,
        )

    def test_bootstrap_grid_has_18_cells_and_9000_rows(self) -> None:
        cells = enumerate_bootstrap_cells(
            self.config,
            self.dgp_order,
        )
        self.assertEqual(len(cells), 18)
        self.assertEqual(
            sum(cell["outer_datasets"] for cell in cells),
            9000,
        )

    def test_trigger_orderings_are_strict(self) -> None:
        for name in self.dgp_order:
            dgp = build_dgp(name, self.specs["dgps"][name])
            for alpha in self.config["alpha_grid"]:
                for regime_name, regime in self.config[
                    "trigger_regimes"
                ].items():
                    result = trigger_boundary(
                        dgp,
                        alpha,
                        regime_name,
                        regime,
                    )
                    self.assertTrue(result["ordering_pass"])
                    self.assertGreater(
                        result["minimum_standardized_gap"],
                        0.20,
                    )

    def test_near_coincidence_offsets_exclude_zero(self) -> None:
        cells = enumerate_near_coincidence_cells(self.config)
        self.assertEqual(len(cells), 8)
        self.assertTrue(
            all(cell["offset_in_anchor_sd"] != 0.0 for cell in cells)
        )

    def test_exact_coincidence_is_nonadjudicative(self) -> None:
        diagnostic = self.config["exact_coincidence_diagnostic"]
        self.assertFalse(
            diagnostic[
                "ordinary_bootstrap_coverage_is_adjudicative"
            ]
        )

    def test_complete_design_validation_passes(self) -> None:
        result = validate_design(
            self.config,
            self.specs,
            self.criteria,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(all(result["checks"].values()))


if __name__ == "__main__":
    unittest.main()
