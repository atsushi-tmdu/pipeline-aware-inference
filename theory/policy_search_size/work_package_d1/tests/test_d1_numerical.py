from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

import d1_validate


ROOT = Path(__file__).resolve().parents[1]


class D1NumericalTests(unittest.TestCase):
    def test_locked_config_is_valid(self) -> None:
        config = json.loads((ROOT / "D1_NUMERICAL_CONFIG.json").read_text(encoding="utf-8"))
        d1_validate._validate_config(config)
        self.assertEqual(config["outer_repetitions"], 3000)
        self.assertEqual(config["bootstrap_repetitions"], 999)
        self.assertEqual(len(config["alphas"]) * len(config["designs"]), 12)

    def test_smoke_config_is_valid(self) -> None:
        config = json.loads((ROOT / "D1_NUMERICAL_CONFIG_SMOKE.json").read_text(encoding="utf-8"))
        d1_validate._validate_config(config)
        self.assertEqual(config["status"], "smoke_not_scientific")

    def test_one_outer_returns_finite_values(self) -> None:
        row = d1_validate._one_outer(
            master_seed=12345,
            cell_index=0,
            outer_index=0,
            B=200,
            n=200,
            alpha=0.05,
            activation_rate=0.5,
            bootstrap_repetitions=25,
        )
        for key in [
            "pi_hat",
            "tess_hat",
            "pi_bootstrap_sd",
            "tess_bootstrap_sd",
            "pi_basic_low",
            "pi_basic_high",
        ]:
            self.assertTrue(math.isfinite(float(row[key])), key)
        self.assertLess(row["pi_basic_low"], row["pi_basic_high"])

    def test_exact_primary_benchmark(self) -> None:
        row = d1_validate._one_outer(
            master_seed=54321,
            cell_index=1,
            outer_index=0,
            B=200,
            n=200,
            alpha=0.05,
            activation_rate=0.5,
            bootstrap_repetitions=25,
        )
        self.assertAlmostEqual(float(row["pi_truth"]), 0.07375, places=12)
        self.assertAlmostEqual(float(row["tess_truth"]), 1.4935890409572679, places=12)


if __name__ == "__main__":
    unittest.main()
