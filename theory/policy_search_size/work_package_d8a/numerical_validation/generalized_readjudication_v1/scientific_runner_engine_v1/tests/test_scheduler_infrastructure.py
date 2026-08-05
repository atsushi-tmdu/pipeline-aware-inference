from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from d8a_runner_io import (
    atomic_write_jsonl_batch,
)
from d8a_runner_scheduler import (
    deterministic_job_order,
    initialize_run_root,
    load_committed_rows,
    status_path,
    validate_execution_label,
    validate_status_against_rows,
    write_job_status,
)


class SchedulerInfrastructureTests(
    unittest.TestCase
):
    def test_order_families(self) -> None:
        jobs = [
            {
                "class_id": "a",
                "family": "combined",
                "job_id": "c",
            },
            {
                "class_id": "a",
                "family": "reference_only",
                "job_id": "r",
            },
            {
                "class_id": "a",
                "family": "evaluation_only",
                "job_id": "e",
            },
        ]
        ordered = deterministic_job_order(
            jobs
        )
        self.assertEqual(
            [
                item["family"]
                for item in ordered
            ],
            [
                "reference_only",
                "evaluation_only",
                "combined",
            ],
        )

    def test_order_classes(self) -> None:
        jobs = [
            {
                "class_id": "b",
                "family": "reference_only",
                "job_id": "b",
            },
            {
                "class_id": "a",
                "family": "reference_only",
                "job_id": "a",
            },
        ]
        ordered = deterministic_job_order(
            jobs
        )
        self.assertEqual(
            [
                item["class_id"]
                for item in ordered
            ],
            ["a", "b"],
        )

    def test_engineering_label_allowed(
        self,
    ) -> None:
        validate_execution_label(
            "NON_SCIENTIFIC_ENGINEERING_ONLY",
            allow_scientific=False,
        )

    def test_scientific_requires_authorization(
        self,
    ) -> None:
        with self.assertRaises(
            PermissionError
        ):
            validate_execution_label(
                "SCIENTIFIC",
                allow_scientific=False,
            )

    def test_scientific_authorized(
        self,
    ) -> None:
        validate_execution_label(
            "SCIENTIFIC",
            allow_scientific=True,
        )

    def test_unknown_label_rejected(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            validate_execution_label(
                "unknown",
                allow_scientific=False,
            )

    def test_initialize_root_creates_metadata(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "run"
            metadata = {"run_id": "x"}
            initialize_run_root(
                root,
                metadata,
            )
            self.assertEqual(
                json.loads(
                    (
                        root
                        / "RUN_METADATA.json"
                    ).read_text()
                ),
                metadata,
            )

    def test_initialize_root_idempotent(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "run"
            metadata = {"run_id": "x"}
            initialize_run_root(
                root,
                metadata,
            )
            observed = initialize_run_root(
                root,
                metadata,
            )
            self.assertEqual(
                observed,
                metadata,
            )

    def test_initialize_root_mismatch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "run"
            initialize_run_root(
                root,
                {"run_id": "x"},
            )
            with self.assertRaises(
                ValueError
            ):
                initialize_run_root(
                    root,
                    {"run_id": "y"},
                )

    def test_load_rows_empty(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.assertEqual(
                load_committed_rows(
                    root,
                    "job",
                ),
                [],
            )

    def test_load_rows_batch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            directory = (
                root / "jobs" / "job"
            )
            atomic_write_jsonl_batch(
                directory,
                "job",
                [
                    {
                        "job_id": "job",
                        "replicate_index": 0,
                    },
                    {
                        "job_id": "job",
                        "replicate_index": 1,
                    },
                ],
            )
            rows = load_committed_rows(
                root,
                "job",
            )
            self.assertEqual(
                len(rows),
                2,
            )

    def test_load_rows_rejects_mismatch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            batch = (
                root
                / "jobs"
                / "job"
                / "batches"
            )
            batch.mkdir(
                parents=True
            )
            (
                batch
                / "batch_0_0.jsonl"
            ).write_text(
                json.dumps(
                    {
                        "job_id": "other",
                        "replicate_index": 0,
                    }
                )
                + "\n"
            )
            with self.assertRaises(
                ValueError
            ):
                load_committed_rows(
                    root,
                    "job",
                )

    def test_status_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            status = {
                "job_id": "job",
                "replicate_count": 0,
            }
            write_job_status(
                root,
                "job",
                status,
            )
            observed = json.loads(
                status_path(
                    root,
                    "job",
                ).read_text()
            )
            self.assertEqual(
                observed,
                status,
            )

    def test_status_count_mismatch(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            validate_status_against_rows(
                {
                    "job_id": "job",
                    "replicate_count": 2,
                },
                [
                    {
                        "job_id": "job",
                        "replicate_index": 0,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
