from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from simulations.ess.phase3c_adaptive_policy_mechanism import (
    load_policy_pivot,
    mechanism_table,
)


class AdaptivePolicyMechanismTests(unittest.TestCase):
    def make_bank(self, path) -> None:
        rows = []
        base = [0.01, 0.2, 0.3, 0.4]
        full = [0.02, 0.01, 0.4, 0.03]
        activation = [True, True, False, False]

        for replication in range(4):
            values = {
                "fixed_base": base[replication],
                "fixed_full": full[replication],
                "promising_triggered": (
                    full[replication]
                    if activation[replication]
                    else base[replication]
                ),
                "rescue_triggered": (
                    base[replication]
                    if activation[replication]
                    else full[replication]
                ),
                "random_expansion": base[replication],
            }
            for policy, pvalue in values.items():
                rows.append(
                    {
                        "replication": replication,
                        "policy": policy,
                        "expanded": (
                            activation[replication]
                            if policy == "promising_triggered"
                            else False
                        ),
                        "base_stage_max_selection_roc_auc": (
                            0.8 - replication * 0.1
                        ),
                        "naive_empirical_p_value": pvalue,
                    }
                )
        pd.DataFrame(rows).to_csv(path, index=False)

    def test_exact_identity(self) -> None:
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as directory:
            path = Path(directory) / "bank.csv"
            self.make_bank(path)
            pivot, state = load_policy_pivot(path)
            result = mechanism_table(
                pivot,
                state,
                (0.05,),
                "test",
            )
            row = result.iloc[0]
            self.assertAlmostEqual(
                row["promising_identity_error"],
                0.0,
                places=12,
            )
            self.assertAlmostEqual(
                row["rescue_identity_error"],
                0.0,
                places=12,
            )

    def test_covariance_sign_matches_policy_difference(self) -> None:
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as directory:
            path = Path(directory) / "bank.csv"
            self.make_bank(path)
            pivot, state = load_policy_pivot(path)
            result = mechanism_table(
                pivot,
                state,
                (0.05,),
                "test",
            )
            row = result.iloc[0]
            observed_difference = (
                row["pi_promising_observed"]
                - row["pi_random_population_benchmark"]
            )
            self.assertAlmostEqual(
                observed_difference,
                row["cov_activation_increment"],
                places=12,
            )


if __name__ == "__main__":
    unittest.main()
