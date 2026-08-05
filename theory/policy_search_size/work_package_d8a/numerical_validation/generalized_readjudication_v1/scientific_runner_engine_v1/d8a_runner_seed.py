from __future__ import annotations

import json
from pathlib import Path

import numpy as np


class SeedInventory:
    def __init__(
        self,
        inventory_path: Path,
    ) -> None:
        records = json.loads(
            inventory_path.read_text(
                encoding="utf-8"
            )
        )
        self._records = {
            record["job_id"]: record
            for record in records
        }

        if len(self._records) != len(records):
            raise ValueError(
                "duplicate job IDs in seed inventory"
            )

        prefixes = []
        for record in records:
            for stream in record["streams"]:
                prefixes.append(
                    tuple(
                        int(value)
                        for value in stream[
                            "spawn_prefix"
                        ]
                    )
                )
        if len(set(prefixes)) != len(prefixes):
            raise ValueError(
                "duplicate spawn prefixes"
            )

    @property
    def job_count(self) -> int:
        return len(self._records)

    def record(
        self,
        job_id: str,
    ) -> dict[str, object]:
        try:
            return self._records[job_id]
        except KeyError as exc:
            raise KeyError(
                f"unknown job ID: {job_id}"
            ) from exc

    def stream_names(
        self,
        job_id: str,
    ) -> tuple[str, ...]:
        return tuple(
            str(stream["stream_name"])
            for stream in self.record(
                job_id
            )["streams"]
        )

    def make_rng(
        self,
        job_id: str,
        stream_name: str,
        replicate_index: int,
    ) -> np.random.Generator:
        if replicate_index < 0:
            raise ValueError(
                "replicate_index must be nonnegative"
            )

        record = self.record(job_id)
        stream_map = {
            str(stream["stream_name"]): stream
            for stream in record["streams"]
        }
        if stream_name not in stream_map:
            raise KeyError(
                f"stream {stream_name!r} "
                f"is not registered for {job_id}"
            )

        stream = stream_map[stream_name]
        spawn_key = (
            *[
                int(value)
                for value in stream[
                    "spawn_prefix"
                ]
            ],
            int(replicate_index),
        )
        sequence = np.random.SeedSequence(
            entropy=int(
                record["master_seed"]
            ),
            spawn_key=spawn_key,
        )
        return np.random.Generator(
            np.random.PCG64DXSM(
                sequence
            )
        )
