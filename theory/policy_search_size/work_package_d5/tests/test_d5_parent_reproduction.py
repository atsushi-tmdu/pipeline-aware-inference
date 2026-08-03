from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[4]
D5 = REPO / "theory" / "policy_search_size" / "work_package_d5"
D4 = D5.parent / "work_package_d4"

sys.path.insert(0, str(D5))
sys.path.insert(0, str(D4))

from d5_core import estimate_bridge
from d4_core import estimate_d4
from d4_validation_core import sample_dgp


EXPECTED_D4_COMMIT = "9b0a2530bfb5e363f59bd7b290d1c064c82b5eaa"
EXPECTED_D4_TAG = "d4-validation-full-v1"
MASTER_SEED = 20261117
TOLERANCE = 1e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class D5ParentReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replications = (
            D4
            / "outputs"
            / "full_v1"
            / "D4_VALIDATION_REPLICATIONS.csv.gz"
        )
        if not cls.replications.is_file():
            raise unittest.SkipTest(
                f"local frozen D4 replication file is unavailable: "
                f"{cls.replications}"
            )

    def test_expected_d4_annotated_tag_commit(self) -> None:
        observed = subprocess.check_output(
            ["git", "rev-parse", f"{EXPECTED_D4_TAG}^{{commit}}"],
            cwd=REPO,
            text=True,
        ).strip()
        self.assertEqual(observed, EXPECTED_D4_COMMIT)

    def test_d4_lock_manifest_hashes(self) -> None:
        manifest_path = D4 / "D4_LOCK_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        failures: list[str] = []

        for record in manifest["files"]:
            path = D4 / record["file"]
            if not path.is_file():
                failures.append(f"missing: {record['file']}")
                continue
            observed = sha256_file(path)
            if observed != record["sha256"]:
                failures.append(
                    f"hash mismatch: {record['file']}: "
                    f"{observed} != {record['sha256']}"
                )

        self.assertEqual(failures, [])

    def test_frozen_replication_file_hash(self) -> None:
        manifest_path = (
            D4
            / "results_freeze"
            / "full_v1"
            / "D4_OUTPUTS_SHA256.txt"
        )
        expected: str | None = None

        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split(maxsplit=1)
            if relative.strip() == "./D4_VALIDATION_REPLICATIONS.csv.gz":
                expected = digest
                break

        self.assertIsNotNone(expected)
        self.assertEqual(sha256_file(self.replications), expected)

    def test_one_regenerated_dataset_per_cell_matches_frozen_d4(self) -> None:
        identity_columns = [
            "dgp_index",
            "cell_index",
            "outer_index",
            "dgp",
            "B",
            "n",
            "alpha",
            "activation_rate_target",
        ]
        estimate_columns = [
            "q0_hat",
            "q1_hat",
            "c_hat",
            "e0_hat",
            "activation_rate_hat",
            "mu_hat",
            "nu_hat",
            "pi_adaptive_hat",
            "pi_comparator_hat",
            "delta_pi_hat",
            "tess_adaptive_hat",
            "tess_comparator_hat",
            "delta_tess_hat",
        ]

        frame = pd.read_csv(
            self.replications,
            usecols=identity_columns + estimate_columns,
        )
        rows = (
            frame.sort_values(["cell_index", "outer_index"])
            .groupby("cell_index", as_index=False)
            .first()
            .sort_values("cell_index")
        )
        self.assertEqual(len(rows), 36)

        maximum_d4_error = 0.0
        maximum_d5_quantile_error = 0.0

        for row in rows.itertuples(index=False):
            rng = np.random.default_rng(
                np.random.SeedSequence(
                    [
                        MASTER_SEED,
                        int(row.dgp_index),
                        int(row.cell_index),
                        int(row.outer_index),
                    ]
                )
            )
            reference = sample_dgp(rng, str(row.dgp), int(row.B))
            evaluation = sample_dgp(rng, str(row.dgp), int(row.n))

            d4_estimate = estimate_d4(
                reference,
                evaluation,
                float(row.alpha),
                float(row.activation_rate_target),
            )
            d5_quantile = estimate_bridge(
                reference,
                evaluation,
                float(row.alpha),
                float(row.activation_rate_target),
            ).quantile

            for field in estimate_columns:
                stored = float(getattr(row, field))
                maximum_d4_error = max(
                    maximum_d4_error,
                    abs(float(getattr(d4_estimate, field)) - stored),
                )
                maximum_d5_quantile_error = max(
                    maximum_d5_quantile_error,
                    abs(float(getattr(d5_quantile, field)) - stored),
                )

        self.assertLessEqual(maximum_d4_error, TOLERANCE)
        self.assertLessEqual(maximum_d5_quantile_error, TOLERANCE)


if __name__ == "__main__":
    unittest.main()
