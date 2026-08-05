from __future__ import annotations

import json
import unittest
from pathlib import Path

from d8a_engineering_smoke import (
    LABEL,
    select_smoke_classes,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (
        ROOT / "D8A_IMPLEMENTATION_CONFIG.json"
    ).read_text(encoding="utf-8")
)
CLASSES = json.loads(
    (
        ROOT.parents[0]
        / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
    ).read_text(encoding="utf-8")
)


class SmokeContractTests(unittest.TestCase):
    def test_scientific_execution_is_blocked(self) -> None:
        self.assertFalse(
            CONFIG[
                "scientific_execution_authorized"
            ]
        )
        self.assertFalse(
            CONFIG[
                "scientific_simulation_run"
            ]
        )

    def test_engineering_label(self) -> None:
        self.assertEqual(
            LABEL,
            "NON_SCIENTIFIC_ENGINEERING_ONLY",
        )

    def test_smoke_selects_two_diagnostic_classes(self) -> None:
        selected = select_smoke_classes(
            CLASSES,
            count=2,
        )
        self.assertEqual(
            len(selected),
            2,
        )
        self.assertTrue(
            all(
                item["class_role"]
                == "diagnostic"
                for item in selected
            )
        )


if __name__ == "__main__":
    unittest.main()
