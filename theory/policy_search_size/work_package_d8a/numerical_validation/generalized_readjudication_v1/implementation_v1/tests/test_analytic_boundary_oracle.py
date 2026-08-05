from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
from scipy.stats import norm

from d8a_analytic_policy_derivatives import (
    analytic_target_derivatives,
    gaussian_cdf_derivatives,
)
from d8a_generalized_oracle import (
    _numerical_smooth_derivatives_legacy,
    all_target_reference_oracle,
    generalized_directional_approximation,
    theta_from_class,
)

ROOT = Path(__file__).resolve().parents[1]
CLASSES = json.loads(
    (ROOT.parents[0] / "D8A_EQUIVALENCE_CLASS_REGISTRY.json").read_text(
        encoding="utf-8"
    )
)


class AnalyticBoundaryOracleTests(unittest.TestCase):
    def test_independent_bivariate_derivatives(self) -> None:
        bounds = np.array([0.3, -0.2])
        covariance = np.diag([1.0, 1.2])
        value, gradient, hessian = gaussian_cdf_derivatives(bounds, covariance)
        sd2 = np.sqrt(1.2)
        expected_value = norm.cdf(bounds[0]) * norm.cdf(bounds[1] / sd2)
        expected_gradient = np.array([
            norm.pdf(bounds[0]) * norm.cdf(bounds[1] / sd2),
            norm.cdf(bounds[0]) * norm.pdf(bounds[1] / sd2) / sd2,
        ])
        self.assertAlmostEqual(value, expected_value, places=12)
        np.testing.assert_allclose(gradient, expected_gradient, atol=1e-12)
        self.assertAlmostEqual(
            hessian[0, 1],
            norm.pdf(bounds[0]) * norm.pdf(bounds[1] / sd2) / sd2,
            places=12,
        )

    def test_bivariate_hessian_is_symmetric(self) -> None:
        _, _, hessian = gaussian_cdf_derivatives(
            np.array([0.3, -0.2]),
            np.array([[1.0, 0.4], [0.4, 1.2]]),
        )
        np.testing.assert_allclose(hessian, hessian.T)

    def test_policy_values_match_direct_engine(self) -> None:
        from d8a_policy_engine import policy_population_probabilities
        for class_record in (CLASSES[0], CLASSES[12], CLASSES[-1]):
            theta = theta_from_class(class_record)
            analytic = analytic_target_derivatives(class_record, theta)
            direct = policy_population_probabilities(
                theta,
                np.asarray(class_record["correlation_matrix"], dtype=float),
            )
            for name in (
                "delta_pi",
                "adaptive_probability",
                "comparator_probability",
            ):
                self.assertAlmostEqual(
                    analytic[name]["value"],
                    direct[name],
                    places=7,
                )

    def test_policy_hessians_are_symmetric(self) -> None:
        derivatives = analytic_target_derivatives(
            CLASSES[0], theta_from_class(CLASSES[0])
        )
        for target in derivatives.values():
            np.testing.assert_allclose(
                target["smooth_hessian"],
                target["smooth_hessian"].T,
            )

    def test_analytic_and_legacy_gradients_agree(self) -> None:
        class_record = CLASSES[0]
        analytic = analytic_target_derivatives(
            class_record, theta_from_class(class_record)
        )
        for name in (
            "delta_pi",
            "adaptive_probability",
            "comparator_probability",
        ):
            gradient, _ = _numerical_smooth_derivatives_legacy(
                name, class_record, step=0.01
            )
            np.testing.assert_allclose(
                analytic[name]["gradient"],
                gradient,
                atol=4e-5,
                rtol=4e-4,
            )

    def test_directional_error_at_radius_002(self) -> None:
        maximum = 0.0
        for class_record in (CLASSES[0], CLASSES[12], CLASSES[-1]):
            oracle = all_target_reference_oracle(class_record, 500)
            for direction in (
                np.array([1.0, 0.3, -0.8, 0.2]),
                np.array([-0.7, 1.0, 0.2, -0.2]),
            ):
                exact, approximation = generalized_directional_approximation(
                    "delta_pi", class_record, direction, 0.002, oracle
                )
                maximum = max(maximum, abs(exact - approximation) / 0.002**2)
        self.assertLess(maximum, 1e-4)

    def test_analytic_oracle_ignores_step_argument(self) -> None:
        left = all_target_reference_oracle(CLASSES[0], 500, step=0.02)
        right = all_target_reference_oracle(CLASSES[0], 500, step=0.005)
        for name in left["targets"]:
            self.assertAlmostEqual(
                left["targets"][name]["generalized_coefficient"],
                right["targets"][name]["generalized_coefficient"],
                places=14,
            )

    def test_all_three_targets_present(self) -> None:
        oracle = all_target_reference_oracle(CLASSES[0], 500)
        self.assertEqual(
            set(oracle["targets"]),
            {"delta_pi", "adaptive_probability", "comparator_probability"},
        )


if __name__ == "__main__":
    unittest.main()
