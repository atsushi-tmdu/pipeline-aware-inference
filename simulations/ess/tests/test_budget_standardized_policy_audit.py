from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from simulations.ess.budget_standardized_policy_audit import (
    point_effects,
)


class BudgetStandardizedPolicyAuditTests(unittest.TestCase):
    def test_exact_covariance_identity(self) -> None:
        joined = pd.DataFrame(
            {
                "fixed_base": [0.01, 0.2, 0.3, 0.4],
                "fixed_full": [0.02, 0.01, 0.4, 0.03],
                "promising_triggered": [0.02, 0.01, 0.3, 0.4],
                "rescue_triggered": [0.01, 0.2, 0.4, 0.03],
                "random_expansion": [0.01, 0.2, 0.3, 0.03],
                "activation": [True, True, False, False],
            }
        )
        result = point_effects(joined, (0.05,), "test")
        row = result.iloc[0]
        self.assertAlmostEqual(
            row["pi_promising_minus_matched_random"],
            row["cov_activation_increment"],
            places=12,
        )
        self.assertAlmostEqual(
            row["pi_rescue_minus_matched_random"],
            -row["cov_activation_increment"],
            places=12,
        )

    def test_gain_capture_fraction(self) -> None:
        joined = pd.DataFrame(
            {
                "fixed_base": [0.2, 0.2, 0.2, 0.2],
                "fixed_full": [0.01, 0.01, 0.2, 0.2],
                "promising_triggered": [0.01, 0.2, 0.2, 0.2],
                "rescue_triggered": [0.2, 0.01, 0.2, 0.2],
                "random_expansion": [0.01, 0.2, 0.2, 0.2],
                "activation": [True, False, True, False],
            }
        )
        result = point_effects(joined, (0.05,), "test")
        self.assertAlmostEqual(
            float(result["promising_gain_capture_fraction"].iloc[0]),
            0.5,
            places=12,
        )


if __name__ == "__main__":
    unittest.main()
