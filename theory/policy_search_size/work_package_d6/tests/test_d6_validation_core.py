from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from d6_validation_core import (
    build_dgps,
    compute_population_benchmark,
    empirical_quantile_index,
    empirical_threshold_bundle,
    plus_one_threshold_index,
    policy_estimate,
    run_outer_replication,
    validate_dgp,
)


class D6ValidationCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config_path = (
            Path(__file__).resolve().parents[1]
            / "D6_NUMERICAL_CONFIG_SMOKE.json"
        )
        cls.config = json.loads(config_path.read_text(encoding="utf-8"))
        cls.dgps = build_dgps(cls.config)

    def test_all_declared_dgps_are_positive_definite(self) -> None:
        self.assertEqual(len(self.dgps), 3)
        for dgp in self.dgps:
            validation = validate_dgp(dgp)
            self.assertGreater(
                validation["minimum_covariance_eigenvalue"],
                0.0,
            )

    def test_k20_marginal_variances_match_declared_pattern(self) -> None:
        expected_sds = np.array(
            [0.85 + 0.05 * (index % 5) for index in range(20)]
        )
        for dgp in self.dgps[1:]:
            actual = np.sqrt(np.diag(dgp.covariance))[1:]
            np.testing.assert_allclose(
                actual,
                expected_sds,
                atol=1e-12,
                rtol=0.0,
            )

    def test_quantile_and_plus_one_indices_have_declared_gap(self) -> None:
        for size in [500, 1000, 3000]:
            for alpha in [0.01, 0.05, 0.10]:
                regular = empirical_quantile_index(
                    size,
                    1.0 - alpha,
                )
                plus = plus_one_threshold_index(size, alpha)
                self.assertIn(plus - regular, [0, 1])

    def test_empirical_threshold_bundle_is_candidate_specific(self) -> None:
        reference = np.array(
            [
                [0.1, 1.0, 10.0, 100.0],
                [0.2, 2.0, 20.0, 200.0],
                [0.3, 3.0, 30.0, 300.0],
                [0.4, 4.0, 40.0, 400.0],
                [0.5, 5.0, 50.0, 500.0],
                [0.6, 6.0, 60.0, 600.0],
                [0.7, 7.0, 70.0, 700.0],
                [0.8, 8.0, 80.0, 800.0],
                [0.9, 9.0, 90.0, 900.0],
                [1.0, 10.0, 100.0, 1000.0],
            ],
            dtype=float,
        )
        bundle, plus = empirical_threshold_bundle(
            reference,
            alpha=0.20,
            activation_rate=0.50,
        )
        np.testing.assert_array_equal(
            bundle.candidate,
            np.array([8.0, 80.0, 800.0]),
        )
        np.testing.assert_array_equal(
            plus,
            np.array([9.0, 90.0, 900.0]),
        )
        self.assertEqual(bundle.activation, 0.5)

    def test_tiny_benchmark_is_finite(self) -> None:
        dgp = self.dgps[0]
        benchmark = compute_population_benchmark(
            dgp,
            alpha=0.05,
            activation_rate=0.50,
            benchmark_config={
                "unconditional_draws_per_dgp": 512,
                "conditional_draws_per_boundary": 256,
                "batches": 4,
            },
            seed_root=12345,
            dgp_index=0,
            alpha_index=0,
        )
        self.assertTrue(
            np.isfinite(benchmark["population"]["delta_pi"])
        )
        self.assertTrue(
            np.isfinite(
                benchmark["influence"]["var_phi_eval_delta"]
            )
        )
        self.assertEqual(len(benchmark["coefficients"]["beta_delta"]), 3)

    def test_outer_replication_passes_bridge_support(self) -> None:
        dgp = self.dgps[0]
        benchmark = compute_population_benchmark(
            dgp,
            alpha=0.05,
            activation_rate=0.50,
            benchmark_config={
                "unconditional_draws_per_dgp": 1024,
                "conditional_draws_per_boundary": 512,
                "batches": 4,
            },
            seed_root=54321,
            dgp_index=0,
            alpha_index=0,
        )
        result = run_outer_replication(
            dgp,
            alpha=0.05,
            activation_rate=0.50,
            reference_size=200,
            evaluation_size=250,
            seed_components=(111, 0, 0, 0, 0),
            benchmark=benchmark,
        )
        self.assertEqual(result["support_violation_count"], 0)
        self.assertLessEqual(
            result["covariance_identity_error"],
            1e-12,
        )
        self.assertTrue(np.isfinite(result["delta_pi_regular"]))
        self.assertTrue(np.isfinite(result["var_total_delta_hat"]))

    def test_policy_estimate_rejects_wrong_dimension(self) -> None:
        dgp = self.dgps[0]
        with self.assertRaises(ValueError):
            policy_estimate(
                np.zeros((10, 3)),
                dgp,
                np.zeros(3),
                0.0,
                0.05,
            )


if __name__ == "__main__":
    unittest.main()
