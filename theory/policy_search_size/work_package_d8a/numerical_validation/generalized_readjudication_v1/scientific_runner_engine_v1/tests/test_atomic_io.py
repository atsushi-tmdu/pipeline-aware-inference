from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from d8a_runner_io import (
    atomic_write_json,
    atomic_write_jsonl_batch,
    scan_committed_batches,
)


class AtomicIOTests(unittest.TestCase):
    def test_atomic_json(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "value.json"
            atomic_write_json(
                path,
                {"value": 3},
            )
            self.assertEqual(
                json.loads(
                    path.read_text()
                )["value"],
                3,
            )

    def test_batch_write_and_scan(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            job_dir = Path(raw) / "job"
            rows = [
                {
                    "job_id": "job",
                    "replicate_index": index,
                }
                for index in range(3)
            ]
            atomic_write_jsonl_batch(
                job_dir,
                "job",
                rows,
            )
            scan = scan_committed_batches(
                job_dir,
                "job",
            )
            self.assertEqual(
                scan[
                    "next_replicate_index"
                ],
                3,
            )

    def test_two_batches_are_contiguous(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            job_dir = Path(raw) / "job"
            for first in (0, 2):
                rows = [
                    {
                        "job_id": "job",
                        "replicate_index": index,
                    }
                    for index in range(
                        first,
                        first + 2,
                    )
                ]
                atomic_write_jsonl_batch(
                    job_dir,
                    "job",
                    rows,
                )
            scan = scan_committed_batches(
                job_dir,
                "job",
            )
            self.assertEqual(
                scan["row_count"],
                4,
            )

    def test_gap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            job_dir = Path(raw) / "job"
            atomic_write_jsonl_batch(
                job_dir,
                "job",
                [
                    {
                        "job_id": "job",
                        "replicate_index": 2,
                    }
                ],
            )
            with self.assertRaises(
                ValueError
            ):
                scan_committed_batches(
                    job_dir,
                    "job",
                )

    def test_mismatched_job_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            job_dir = Path(raw) / "job"
            with self.assertRaises(
                ValueError
            ):
                atomic_write_jsonl_batch(
                    job_dir,
                    "job",
                    [
                        {
                            "job_id": "other",
                            "replicate_index": 0,
                        }
                    ],
                )

    def test_temporary_file_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            job_dir = Path(raw) / "job"
            batch_dir = (
                job_dir / "batches"
            )
            batch_dir.mkdir(
                parents=True
            )
            (
                batch_dir
                / "batch_0_0.jsonl.tmp"
            ).write_text(
                "incomplete"
            )
            scan = scan_committed_batches(
                job_dir,
                "job",
            )
            self.assertEqual(
                scan["row_count"],
                0,
            )


if __name__ == "__main__":
    unittest.main()
