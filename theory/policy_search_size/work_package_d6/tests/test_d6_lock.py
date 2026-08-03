from __future__ import annotations

import json
import unittest
from pathlib import Path

from verify_d6_lock_manifest import verify_manifest


class D6LockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]

    def test_locked_configs_and_final_counts(self) -> None:
        theory = json.loads(
            (self.root / "D6_CONFIG.json").read_text(encoding="utf-8")
        )
        numerical = json.loads(
            (self.root / "D6_NUMERICAL_CONFIG.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(theory["status"], "locked_before_scientific_run")
        self.assertEqual(
            numerical["status"],
            "locked_before_scientific_run",
        )
        self.assertEqual(
            numerical["full_grid"]["outer_repetitions_per_cell"],
            2000,
        )
        self.assertEqual(
            numerical["bootstrap"]["outer_datasets_per_cell"],
            500,
        )
        self.assertEqual(
            numerical["bootstrap"]["resamples_per_dataset"],
            249,
        )

    def test_manifest_verifies(self) -> None:
        result = verify_manifest(self.root)
        self.assertTrue(result["pass"], msg=str(result))
        self.assertGreaterEqual(int(result["checked"]), 20)

    def test_full_runner_uses_locked_config_and_verification(self) -> None:
        runner = (self.root / "run_d6_validation_full.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("verify_d6_lock_manifest.py", runner)
        self.assertIn("D6_NUMERICAL_CONFIG.json", runner)
        self.assertIn("outputs/full_v1", runner)
        self.assertNotIn("D6_NUMERICAL_CONFIG_DRAFT.json", runner)

    def test_generated_outputs_remain_ignored(self) -> None:
        ignore = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("outputs/", ignore)
        self.assertIn("preflight_output/", ignore)
        self.assertIn("results_freeze/", ignore)


if __name__ == "__main__":
    unittest.main()
