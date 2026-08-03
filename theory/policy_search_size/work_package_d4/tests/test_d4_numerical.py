from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

from d4_validation_core import (
    benchmark_dgp,
    benchmark_gradient_finite_difference,
    sample_dgp,
)


ROOT = Path(__file__).resolve().parents[1]


class D4NumericalTests(unittest.TestCase):
    def test_sampling_shapes(self) -> None:
        rng = np.random.default_rng(20261111)
        for name in ["independent_normal", "gaussian_factor", "nonlinear_smooth"]:
            sample = sample_dgp(rng, name, 37)
            self.assertEqual(sample.shape, (37, 3))
            self.assertTrue(np.isfinite(sample).all())

    def test_independent_benchmark_is_zero_contrast(self) -> None:
        benchmark = benchmark_dgp("independent_normal", 0.05, 0.5, 1.0)
        self.assertAlmostEqual(benchmark["delta_pi"], 0.0, places=10)
        self.assertAlmostEqual(benchmark["delta_tess"], 0.0, places=10)
        self.assertLess(benchmark["reference_variance_fraction_delta_tess"], 1e-10)
        self.assertGreater(benchmark["sigma_total_delta_tess_2_sqrt_n"], 0.0)

    def test_dependent_benchmark_signs(self) -> None:
        gaussian = benchmark_dgp("gaussian_factor", 0.05, 0.5, 1.0)
        nonlinear = benchmark_dgp("nonlinear_smooth", 0.05, 0.5, 1.0)
        self.assertGreater(gaussian["delta_tess"], 0.0)
        self.assertLess(nonlinear["delta_tess"], 0.0)
        for benchmark in [gaussian, nonlinear]:
            self.assertGreater(benchmark["sigma_total_delta_pi_2_sqrt_n"], 0.0)
            self.assertGreater(benchmark["sigma_total_delta_tess_2_sqrt_n"], 0.0)
            self.assertTrue(math.isfinite(benchmark["reference_variance_fraction_delta_tess"]))

    def test_boundary_gradients(self) -> None:
        for name in ["independent_normal", "gaussian_factor", "nonlinear_smooth"]:
            check = benchmark_gradient_finite_difference(name, 0.05, 0.5, step=2e-4)
            self.assertLess(check["delta_pi"]["maximum_absolute_error"], 2e-5)
            self.assertLess(check["delta_tess"]["maximum_absolute_error"], 2e-5)

    def test_locked_config(self) -> None:
        config = json.loads((ROOT / "D4_NUMERICAL_CONFIG.json").read_text(encoding="utf-8"))
        self.assertEqual(config["study_id"], "TESS_THEORY_D4_NUMERICAL_VALIDATION_V1")
        self.assertEqual(config["status"], "locked_before_run")
        self.assertEqual(config["outer_repetitions"], 3000)
        self.assertEqual(config["bootstrap_repetitions"], 999)
        self.assertEqual(config["master_seed"], 20261117)
        self.assertEqual(config["required_lock_tag"], "tess-theory-work-package-d4-v1-lock-20260802")
        self.assertEqual(len(config["data_generating_laws"]), 3)
        self.assertEqual(len(config["designs"]), 4)
        self.assertEqual(len(config["alphas"]), 3)

    def test_smoke_config(self) -> None:
        config = json.loads((ROOT / "D4_NUMERICAL_CONFIG_SMOKE.json").read_text(encoding="utf-8"))
        self.assertEqual(config["status"], "smoke_not_scientific")
        self.assertLess(config["outer_repetitions"], 100)
        self.assertLess(config["bootstrap_repetitions"], 100)


if __name__ == "__main__":
    unittest.main()
