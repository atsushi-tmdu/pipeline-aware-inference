from __future__ import annotations

import unittest

import pandas as pd

from simulations.ess.confirmatory_policy_interaction_v1 import effects


class ConfirmatoryPolicyInteractionTests(unittest.TestCase):
    def test_positive_promising_effect(self) -> None:
        frame = pd.DataFrame(
            {
                "fixed_base": [0.2, 0.2, 0.2, 0.2],
                "fixed_full": [0.01, 0.01, 0.2, 0.2],
                "promising_triggered": [0.01, 0.01, 0.2, 0.2],
                "rescue_triggered": [0.2, 0.2, 0.2, 0.2],
                "activation": [True, True, False, False],
            }
        )
        result = effects(frame, 0.05)
        self.assertGreater(
            result["promising_tess_minus_matched_random"],
            0.0,
        )
        self.assertLess(
            result["rescue_tess_minus_matched_random"],
            0.0,
        )
        self.assertGreater(result["cov_activation_increment"], 0.0)


if __name__ == "__main__":
    unittest.main()
