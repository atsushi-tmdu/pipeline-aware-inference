from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from d8a_runner_engine import (
    simulate_combined,
    simulate_evaluation_only,
    simulate_job_replicate,
    simulate_reference_only,
)
from d8a_runner_seed import SeedInventory


ROOT = Path(__file__).resolve().parents[1]
GENERALIZED = ROOT.parent
RUN_PACKAGE = (
    GENERALIZED
    / "scientific_run_prelock_v1"
)
CLASSES = json.loads(
    (
        GENERALIZED
        / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
    ).read_text(encoding="utf-8")
)
JOBS = json.loads(
    (
        RUN_PACKAGE
        / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
    ).read_text(encoding="utf-8")
)
SEEDS = SeedInventory(
    RUN_PACKAGE
    / "D8A_SCIENTIFIC_SEED_INVENTORY.json"
)
CLASS_MAP = {
    item["class_id"]: item
    for item in CLASSES
}


def job_for(family: str):
    return next(
        item
        for item in JOBS
        if item["family"] == family
    )


class FamilyEngineTests(unittest.TestCase):
    def test_reference_family_dispatch(self) -> None:
        job = job_for("reference_only")
        result = simulate_job_replicate(
            job,
            CLASS_MAP[job["class_id"]],
            SEEDS,
            0,
            engineering_override={
                "reference_sizes": [16]
            },
        )
        self.assertEqual(
            result["family"],
            "reference_only",
        )

    def test_evaluation_family_dispatch(self) -> None:
        job = job_for("evaluation_only")
        result = simulate_job_replicate(
            job,
            CLASS_MAP[job["class_id"]],
            SEEDS,
            0,
            engineering_override={
                "evaluation_sizes": [16]
            },
        )
        self.assertEqual(
            result["family"],
            "evaluation_only",
        )

    def test_combined_family_dispatch(self) -> None:
        job = job_for("combined")
        result = simulate_job_replicate(
            job,
            CLASS_MAP[job["class_id"]],
            SEEDS,
            0,
            engineering_override={
                "combined_pairs": [[16, 16]]
            },
        )
        self.assertEqual(
            result["family"],
            "combined",
        )

    def test_reference_reproduces(self) -> None:
        job = job_for("reference_only")
        class_record = CLASS_MAP[
            job["class_id"]
        ]
        left = simulate_reference_only(
            job,
            class_record,
            SEEDS,
            2,
            sample_sizes=[16],
        )
        right = simulate_reference_only(
            job,
            class_record,
            SEEDS,
            2,
            sample_sizes=[16],
        )
        self.assertEqual(left, right)

    def test_evaluation_reproduces(self) -> None:
        job = job_for("evaluation_only")
        class_record = CLASS_MAP[
            job["class_id"]
        ]
        left = simulate_evaluation_only(
            job,
            class_record,
            SEEDS,
            2,
            sample_sizes=[16],
        )
        right = simulate_evaluation_only(
            job,
            class_record,
            SEEDS,
            2,
            sample_sizes=[16],
        )
        self.assertEqual(left, right)

    def test_combined_reproduces(self) -> None:
        job = job_for("combined")
        class_record = CLASS_MAP[
            job["class_id"]
        ]
        left = simulate_combined(
            job,
            class_record,
            SEEDS,
            2,
            pairs=[[16, 16]],
        )
        right = simulate_combined(
            job,
            class_record,
            SEEDS,
            2,
            pairs=[[16, 16]],
        )
        self.assertEqual(left, right)

    def test_reference_nested_prefix(self) -> None:
        job = job_for("reference_only")
        class_record = CLASS_MAP[
            job["class_id"]
        ]
        nested = simulate_reference_only(
            job,
            class_record,
            SEEDS,
            4,
            sample_sizes=[16, 32],
        )
        direct = simulate_reference_only(
            job,
            class_record,
            SEEDS,
            4,
            sample_sizes=[16],
        )
        self.assertEqual(
            nested["points"][0],
            direct["points"][0],
        )

    def test_evaluation_delta_identity(self) -> None:
        job = job_for("evaluation_only")
        result = simulate_evaluation_only(
            job,
            CLASS_MAP[job["class_id"]],
            SEEDS,
            1,
            sample_sizes=[32],
        )
        point = result["points"][0]
        self.assertAlmostEqual(
            point["delta_hat"],
            point["adaptive_estimate"]
            - point[
                "comparator_estimate"
            ],
        )


if __name__ == "__main__":
    unittest.main()
