from __future__ import annotations

import unittest

import numpy as np

from d6_preflight_core import (
    conditional_gaussian_parameters,
    default_gaussian_dgp,
    draw_conditional_gaussian,
    population_thresholds,
    validate_dgp,
)


class D6PreflightCoreTests(unittest.TestCase):
    def test_default_covariance_is_positive_definite(self) -> None:
        validation = validate_dgp(default_gaussian_dgp())
        self.assertGreater(
            validation["minimum_covariance_eigenvalue"],
            0.0,
        )

    def test_population_thresholds_are_finite(self) -> None:
        candidates, activation = population_thresholds(
            default_gaussian_dgp()
        )
        self.assertEqual(candidates.shape, (3,))
        self.assertTrue(np.all(np.isfinite(candidates)))
        self.assertTrue(np.isfinite(activation))

    def test_conditional_covariance_is_positive_definite(self) -> None:
        dgp = default_gaussian_dgp()
        _, _, covariance = conditional_gaussian_parameters(
            dgp,
            2,
            1.0,
        )
        self.assertGreater(float(np.min(np.linalg.eigvalsh(covariance))), 0.0)

    def test_conditional_draw_fixes_requested_coordinate(self) -> None:
        dgp = default_gaussian_dgp()
        draws = draw_conditional_gaussian(
            dgp,
            1,
            1.25,
            128,
            np.random.default_rng(123),
        )
        np.testing.assert_array_equal(
            draws[:, 1],
            np.full(128, 1.25),
        )


if __name__ == "__main__":
    unittest.main()
