from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "D8A_NUMERICAL_DESIGN.json").read_text(
        encoding="utf-8"
    )
)
REGISTRY = json.loads(
    (ROOT / "D8A_CELL_REGISTRY.json").read_text(
        encoding="utf-8"
    )
)


class D8ANumericalDesignTests(unittest.TestCase):
    def test_design_is_locked_before_simulation(self) -> None:
        self.assertTrue(
            CONFIG["scientific_numerical_design_locked"]
        )
        self.assertFalse(
            CONFIG["scientific_simulation_run"]
        )

    def test_quantile_convention(self) -> None:
        self.assertEqual(
            CONFIG["scope"]["quantile_convention"],
            "k_B=ceil(B*p)",
        )

    def test_candidate_pools(self) -> None:
        self.assertEqual(
            CONFIG["scope"]["candidate_pool_base"],
            [0, 1],
        )
        self.assertEqual(
            CONFIG["scope"]["candidate_pool_full"],
            [0, 1, 2],
        )

    def test_sample_size_grids(self) -> None:
        self.assertEqual(
            CONFIG["sample_sizes"]["reference_B"],
            [250, 500, 1000, 3000, 10000],
        )
        self.assertEqual(
            CONFIG["sample_sizes"]["evaluation_n"],
            [250, 500, 1000, 3000, 10000],
        )

    def test_registry_counts(self) -> None:
        self.assertEqual(len(REGISTRY), 75)
        self.assertEqual(
            sum(cell["role"] == "primary" for cell in REGISTRY),
            34,
        )
        self.assertEqual(
            sum(cell["role"] == "diagnostic" for cell in REGISTRY),
            41,
        )

    def test_all_cells_are_separated(self) -> None:
        self.assertGreaterEqual(
            min(cell["latent_separation"] for cell in REGISTRY),
            0.10,
        )

    def test_all_correlation_matrices_are_positive_definite(self) -> None:
        for cell in REGISTRY:
            matrix = np.asarray(
                cell["correlation_matrix"],
                dtype=float,
            )
            self.assertGreater(
                float(np.min(np.linalg.eigvalsh(matrix))),
                0.0,
            )

    def test_transforms_are_locked(self) -> None:
        observed = {
            cell["transform"]
            for cell in REGISTRY
        }
        self.assertEqual(
            observed,
            {"identity", "exp_0_35", "sinh_0_5"},
        )

    def test_alpha_values(self) -> None:
        self.assertEqual(
            CONFIG["tess"]["alpha_values"],
            [0.01, 0.05],
        )

    def test_seed_and_stream_contract(self) -> None:
        mc = CONFIG["monte_carlo"]
        self.assertEqual(mc["master_seed"], 20260804)
        self.assertTrue(
            mc["reference_evaluation_streams_independent"]
        )
        self.assertTrue(
            mc["nested_common_random_numbers_across_sizes"]
        )

    def test_stopping_is_precision_only(self) -> None:
        mc = CONFIG["monte_carlo"]
        self.assertTrue(mc["precision_stopping_only"])
        self.assertFalse(mc["effect_dependent_stopping"])

    def test_no_post_hoc_cell_dropping(self) -> None:
        self.assertTrue(
            CONFIG["cell_registry"][
                "no_post_hoc_cell_dropping"
            ]
        )

    def test_combined_grid_contains_largest_pair(self) -> None:
        self.assertIn(
            [10000, 10000],
            CONFIG["sample_sizes"]["combined_pairs"],
        )

    def test_required_output_contract(self) -> None:
        self.assertIn(
            "acceptance_check_results.csv",
            CONFIG["outputs"]["required_tables"],
        )
        self.assertIn(
            "file_hashes.json",
            CONFIG["outputs"]["required_metadata"],
        )


if __name__ == "__main__":
    unittest.main()
