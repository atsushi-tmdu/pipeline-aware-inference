from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from d8a_runner_seed import SeedInventory


ROOT = Path(__file__).resolve().parents[1]
RUN_PACKAGE = (
    ROOT.parent
    / "scientific_run_prelock_v1"
)
INVENTORY = SeedInventory(
    RUN_PACKAGE
    / "D8A_SCIENTIFIC_SEED_INVENTORY.json"
)
JOBS = json.loads(
    (
        RUN_PACKAGE
        / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
    ).read_text(encoding="utf-8")
)


class SeedInventoryTests(unittest.TestCase):
    def test_inventory_has_75_jobs(self) -> None:
        self.assertEqual(
            INVENTORY.job_count,
            75,
        )

    def test_same_seed_reproduces(self) -> None:
        job = JOBS[0]
        stream = job["stream_names"][0]
        left = INVENTORY.make_rng(
            job["job_id"],
            stream,
            3,
        ).normal(size=8)
        right = INVENTORY.make_rng(
            job["job_id"],
            stream,
            3,
        ).normal(size=8)
        np.testing.assert_array_equal(
            left,
            right,
        )

    def test_replicates_differ(self) -> None:
        job = JOBS[0]
        stream = job["stream_names"][0]
        left = INVENTORY.make_rng(
            job["job_id"],
            stream,
            0,
        ).normal(size=8)
        right = INVENTORY.make_rng(
            job["job_id"],
            stream,
            1,
        ).normal(size=8)
        self.assertFalse(
            np.array_equal(left, right)
        )

    def test_combined_streams_differ(self) -> None:
        job = next(
            item
            for item in JOBS
            if item["family"]
            == "combined"
        )
        left = INVENTORY.make_rng(
            job["job_id"],
            "scientific_reference",
            0,
        ).normal(size=8)
        right = INVENTORY.make_rng(
            job["job_id"],
            "scientific_evaluation",
            0,
        ).normal(size=8)
        self.assertFalse(
            np.array_equal(left, right)
        )

    def test_unknown_stream_raises(self) -> None:
        job = JOBS[0]
        with self.assertRaises(KeyError):
            INVENTORY.make_rng(
                job["job_id"],
                "not_registered",
                0,
            )


if __name__ == "__main__":
    unittest.main()
