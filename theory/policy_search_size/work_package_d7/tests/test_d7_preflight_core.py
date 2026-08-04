from __future__ import annotations

import unittest

import numpy as np

from d7_preflight_core import (
    base_maximum_cdf,
    candidate_thresholds,
    conditional_parameters,
    default_dgp,
    trigger_density_decomposition,
    trigger_threshold,
    validate_dgp,
)


class D7PreflightCoreTests(unittest.TestCase):
    def test_default_covariance_is_positive_definite(self) -> None:
        result = validate_dgp(default_dgp())
        self.assertGreater(result["minimum_covariance_eigenvalue"], 0.0)

    def test_trigger_quantile_hits_target_probability(self) -> None:
        dgp = default_dgp()
        trigger = trigger_threshold(dgp)
        self.assertAlmostEqual(
            base_maximum_cdf(dgp, trigger),
            1.0 - dgp.activation_rate,
            places=8,
        )

    def test_base_maximum_cdf_is_reproducible(self) -> None:
        dgp = default_dgp()
        trigger = trigger_threshold(dgp)
        first = base_maximum_cdf(dgp, trigger)
        second = base_maximum_cdf(dgp, trigger)
        self.assertEqual(first, second)

    def test_regular_threshold_separation_is_positive(self) -> None:
        dgp = default_dgp()
        thresholds = candidate_thresholds(dgp)
        trigger = trigger_threshold(dgp)
        separation = np.min(
            np.abs(
                thresholds[np.asarray(dgp.base_pool)]
                - trigger
            )
        )
        self.assertGreater(separation, 0.1)

    def test_conditional_covariance_is_positive_definite(self) -> None:
        dgp = default_dgp()
        _, _, covariance = conditional_parameters(dgp, 0, 0.5)
        self.assertGreater(
            float(np.min(np.linalg.eigvalsh(covariance))),
            0.0,
        )

    def test_maximum_density_decomposition_is_positive(self) -> None:
        dgp = default_dgp()
        density, terms = trigger_density_decomposition(
            dgp,
            trigger_threshold(dgp),
        )
        self.assertGreater(density, 0.0)
        self.assertEqual(len(terms), len(dgp.base_pool))
        self.assertTrue(all(value > 0.0 for value in terms))


if __name__ == "__main__":
    unittest.main()
