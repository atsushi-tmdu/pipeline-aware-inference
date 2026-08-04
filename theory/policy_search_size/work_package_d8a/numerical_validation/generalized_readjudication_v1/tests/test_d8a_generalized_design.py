from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (
        ROOT / "D8A_GENERALIZED_DESIGN.json"
    ).read_text(encoding="utf-8")
)
CLASSES = json.loads(
    (
        ROOT / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
    ).read_text(encoding="utf-8")
)


class D8AGeneralizedDesignTests(unittest.TestCase):
    def test_historical_registry_rows_are_retained(self) -> None:
        self.assertEqual(
            CONFIG["historical_registry_rows"],
            75,
        )

    def test_equivalence_class_count(self) -> None:
        self.assertEqual(len(CLASSES), 25)

    def test_primary_class_count(self) -> None:
        self.assertEqual(
            sum(
                item["class_role"] == "primary"
                for item in CLASSES
            ),
            17,
        )

    def test_diagnostic_class_count(self) -> None:
        self.assertEqual(
            sum(
                item["class_role"] == "diagnostic"
                for item in CLASSES
            ),
            8,
        )

    def test_audit_row_count(self) -> None:
        self.assertEqual(
            sum(
                len(item["audit_member_cell_ids"])
                for item in CLASSES
            ),
            50,
        )

    def test_each_class_has_three_transforms(self) -> None:
        for item in CLASSES:
            self.assertEqual(
                set(item["transforms"]),
                {
                    "identity",
                    "exp_0_35",
                    "sinh_0_5",
                },
            )
            self.assertEqual(
                len(item["member_cell_ids"]),
                3,
            )

    def test_identity_is_canonical(self) -> None:
        for item in CLASSES:
            self.assertEqual(
                item["canonical_transform"],
                "identity",
            )
            self.assertTrue(
                item["canonical_cell_id"]
                in item["member_cell_ids"]
            )

    def test_candidate_coincidences_are_locked(self) -> None:
        self.assertEqual(
            CONFIG["active_candidate_coincidence_hyperplanes"],
            ["q0=q2", "q1=q2"],
        )

    def test_candidate_trigger_separation(self) -> None:
        self.assertGreaterEqual(
            min(
                item["latent_separation"]
                for item in CLASSES
            ),
            0.10,
        )

    def test_all_correlation_matrices_are_pd(self) -> None:
        for item in CLASSES:
            matrix = np.asarray(
                item["correlation_matrix"],
                dtype=float,
            )
            self.assertGreater(
                float(np.min(np.linalg.eigvalsh(matrix))),
                0.0,
            )

    def test_contrast_variances_are_positive(self) -> None:
        for item in CLASSES:
            self.assertGreater(
                min(
                    item[
                        "candidate_added_contrast_variances"
                    ]
                ),
                1e-12,
            )

    def test_common_transform_invariance(self) -> None:
        self.assertTrue(
            CONFIG[
                "common_monotone_transform_exact_invariance"
            ]
        )

    def test_acceptance_aggregates_classes(self) -> None:
        self.assertEqual(
            CONFIG["acceptance_unit"],
            "latent_equivalence_class",
        )
        self.assertEqual(
            CONFIG["primary_acceptance_denominator"],
            17,
        )

    def test_quantile_convention_is_unchanged(self) -> None:
        self.assertEqual(
            CONFIG["quantile_convention"],
            "k_B=ceil(B*p)",
        )

    def test_sample_grids_are_preserved(self) -> None:
        self.assertEqual(
            CONFIG["reference_B"],
            [250, 500, 1000, 3000, 10000],
        )
        self.assertEqual(
            CONFIG["evaluation_n"],
            [250, 500, 1000, 3000, 10000],
        )

    def test_tess_alpha_values_are_preserved(self) -> None:
        self.assertEqual(
            CONFIG["tess_alpha_values"],
            [0.01, 0.05],
        )

    def test_generalized_coefficient_is_required(self) -> None:
        self.assertEqual(
            CONFIG["reference_coefficient"],
            "C_Delta,B^gen",
        )
        self.assertFalse(
            CONFIG["ordinary_hessian_coefficient_allowed"]
        )

    def test_execution_remains_blocked(self) -> None:
        self.assertTrue(
            CONFIG["generalized_numerical_design_locked"]
        )
        self.assertFalse(
            CONFIG["implementation_locked"]
        )
        self.assertFalse(
            CONFIG["scientific_execution_authorized"]
        )
        self.assertFalse(
            CONFIG["scientific_simulation_run"]
        )


if __name__ == "__main__":
    unittest.main()
