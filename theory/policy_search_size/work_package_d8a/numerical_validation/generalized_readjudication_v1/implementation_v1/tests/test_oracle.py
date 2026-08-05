from __future__ import annotations

import unittest

import numpy as np

from d8a_generalized_oracle import (
    branch_kappa,
    evaluation_variances,
    quantile_moment_oracle,
    target_kink_coefficients,
    theta_from_class,
)
from d8a_policy_engine import (
    policy_population_probabilities,
)


CLASS = {
    "class_id": "test-class",
    "dependence": "independent",
    "candidate_probability": 0.90,
    "trigger_probability": 0.50,
    "correlation_matrix": np.eye(3).tolist(),
}


class OracleTests(unittest.TestCase):
    def test_theta_shape(self) -> None:
        self.assertEqual(
            theta_from_class(CLASS).shape,
            (4,),
        )

    def test_quantile_moment_shapes(self) -> None:
        moments = quantile_moment_oracle(
            CLASS,
            500,
        )
        self.assertEqual(
            moments["bias_coefficient"].shape,
            (4,),
        )
        self.assertEqual(
            moments["covariance"].shape,
            (4, 4),
        )

    def test_covariance_is_symmetric(self) -> None:
        covariance = quantile_moment_oracle(
            CLASS,
            500,
        )["covariance"]
        np.testing.assert_allclose(
            covariance,
            covariance.T,
        )

    def test_covariance_is_psd(self) -> None:
        covariance = quantile_moment_oracle(
            CLASS,
            500,
        )["covariance"]
        self.assertGreaterEqual(
            float(
                np.min(
                    np.linalg.eigvalsh(
                        covariance
                    )
                )
            ),
            -1e-7,
        )

    def test_branch_kappas_are_negative(self) -> None:
        theta = theta_from_class(CLASS)
        correlation = np.eye(3)
        self.assertLess(
            branch_kappa(
                theta[0],
                0,
                correlation,
            ),
            0.0,
        )
        self.assertLess(
            branch_kappa(
                theta[1],
                1,
                correlation,
            ),
            0.0,
        )

    def test_target_has_two_kinks(self) -> None:
        coefficients = target_kink_coefficients(
            "delta_pi",
            CLASS,
        )
        self.assertEqual(
            coefficients.shape,
            (2,),
        )

    def test_kink_coefficients_are_finite(self) -> None:
        coefficients = target_kink_coefficients(
            "delta_pi",
            CLASS,
        )
        self.assertTrue(
            np.all(
                np.isfinite(coefficients)
            )
        )

    def test_population_probabilities_are_finite(self) -> None:
        probabilities = policy_population_probabilities(
            theta_from_class(CLASS),
            np.eye(3),
        )
        self.assertTrue(
            all(
                np.isfinite(value)
                for key, value in probabilities.items()
                if key
                not in {
                    "base_parts",
                    "incremental_parts",
                    "joint_parts",
                }
            )
        )

    def test_population_delta_identity(self) -> None:
        probabilities = policy_population_probabilities(
            theta_from_class(CLASS),
            np.eye(3),
        )
        self.assertAlmostEqual(
            probabilities["delta_pi"],
            probabilities[
                "adaptive_probability"
            ]
            - probabilities[
                "comparator_probability"
            ],
        )

    def test_evaluation_variances_are_finite(self) -> None:
        variances = evaluation_variances(
            CLASS
        )
        self.assertTrue(
            all(
                np.isfinite(value)
                and value >= -1e-12
                for value in variances.values()
            )
        )


if __name__ == "__main__":
    unittest.main()
