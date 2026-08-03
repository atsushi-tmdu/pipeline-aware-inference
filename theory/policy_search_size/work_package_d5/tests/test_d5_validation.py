from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


D5 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(D5))

from d5_validate import (
    build_cells,
    build_tasks,
    canonical_d4_cell_index,
    dataframe_to_markdown,
    label_ratio,
    validate_config,
)


class D5ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.smoke_path = D5 / "D5_NUMERICAL_CONFIG_SMOKE.json"
        cls.smoke = json.loads(
            cls.smoke_path.read_text(encoding="utf-8")
        )

    def test_smoke_config_is_not_scientific(self) -> None:
        validate_config(self.smoke, scientific=False)
        with self.assertRaises(ValueError):
            validate_config(self.smoke, scientific=True)

    def test_cell_and_task_shapes(self) -> None:
        cells = build_cells(self.smoke)
        tasks = build_tasks(self.smoke, cells)
        self.assertEqual(
            len(cells),
            (
                len(self.smoke["data_generating_laws"])
                * len(self.smoke["designs"])
                * len(self.smoke["alphas"])
            ),
        )
        self.assertGreaterEqual(len(tasks), len(cells))

    def test_smoke_preserves_parent_d4_cell_indices(self) -> None:
        cells = build_cells(self.smoke)
        observed = [int(cell["cell_index"]) for cell in cells]
        self.assertEqual(
            observed,
            [0, 1, 2, 12, 13, 14, 24, 25, 26],
        )
        self.assertEqual(
            canonical_d4_cell_index(
                "gaussian_factor",
                500,
                500,
                0.05,
            ),
            (1, 13),
        )

    def test_markdown_renderer_has_no_optional_dependency(self) -> None:
        import pandas as pd

        frame = pd.DataFrame(
            {
                "name": ["a|b", "c"],
                "value": [1.23456789, float("nan")],
            }
        )
        rendered = dataframe_to_markdown(
            frame,
            columns=["name", "value"],
            float_format=".4g",
        )
        self.assertIn("| name | value |", rendered)
        self.assertIn("a\\|b", rendered)
        self.assertIn("1.235", rendered)
        self.assertNotIn("nan", rendered.lower())

    def test_ratio_labels(self) -> None:
        self.assertEqual(label_ratio(0.0), "negligible")
        self.assertEqual(label_ratio(0.099), "negligible")
        self.assertEqual(label_ratio(0.10), "small")
        self.assertEqual(label_ratio(0.249), "small")
        self.assertEqual(label_ratio(0.25), "material")


if __name__ == "__main__":
    unittest.main()
