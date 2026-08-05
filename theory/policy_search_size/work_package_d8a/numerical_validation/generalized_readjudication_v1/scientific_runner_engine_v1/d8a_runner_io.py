from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path


_BATCH_PATTERN = re.compile(
    r"^batch_(\d+)_(\d+)\.jsonl$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_text(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    temporary = path.with_name(
        path.name + ".tmp"
    )
    temporary.write_text(
        text,
        encoding="utf-8",
    )
    os.replace(
        temporary,
        path,
    )


def atomic_write_json(
    path: Path,
    value: object,
) -> None:
    atomic_write_text(
        path,
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def atomic_write_jsonl_batch(
    job_directory: Path,
    job_id: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    if not rows:
        raise ValueError(
            "rows must not be empty"
        )

    indices = [
        int(row["replicate_index"])
        for row in rows
    ]
    expected = list(
        range(
            indices[0],
            indices[-1] + 1,
        )
    )
    if indices != expected:
        raise ValueError(
            "replicate indices must be "
            "contiguous and ordered"
        )
    if any(
        row["job_id"] != job_id
        for row in rows
    ):
        raise ValueError(
            "row job IDs do not match"
        )

    batch_directory = (
        job_directory / "batches"
    )
    batch_directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    path = (
        batch_directory
        / (
            f"batch_{indices[0]}_"
            f"{indices[-1]}.jsonl"
        )
    )
    if path.exists():
        raise FileExistsError(
            f"batch already exists: {path}"
        )

    payload = "".join(
        json.dumps(
            row,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
        for row in rows
    )
    atomic_write_text(
        path,
        payload,
    )

    return {
        "filename": path.name,
        "first_replicate": indices[0],
        "last_replicate": indices[-1],
        "row_count": len(rows),
        "sha256": sha256(path),
    }


def scan_committed_batches(
    job_directory: Path,
    job_id: str,
) -> dict[str, object]:
    batch_directory = (
        job_directory / "batches"
    )
    if not batch_directory.exists():
        return {
            "batch_count": 0,
            "row_count": 0,
            "next_replicate_index": 0,
            "batches": [],
        }

    entries = []
    for path in batch_directory.iterdir():
        if path.name.endswith(".tmp"):
            continue
        match = _BATCH_PATTERN.match(
            path.name
        )
        if match is None:
            raise ValueError(
                f"invalid committed batch name: "
                f"{path.name}"
            )
        first = int(
            match.group(1)
        )
        last = int(
            match.group(2)
        )
        if last < first:
            raise ValueError(
                "batch interval is reversed"
            )

        rows = []
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines():
            row = json.loads(line)
            rows.append(row)

        expected_count = (
            last - first + 1
        )
        if len(rows) != expected_count:
            raise ValueError(
                f"batch row count mismatch: "
                f"{path.name}"
            )
        expected_indices = list(
            range(first, last + 1)
        )
        observed_indices = [
            int(row["replicate_index"])
            for row in rows
        ]
        if observed_indices != expected_indices:
            raise ValueError(
                f"batch replicate mismatch: "
                f"{path.name}"
            )
        if any(
            row["job_id"] != job_id
            for row in rows
        ):
            raise ValueError(
                f"batch job ID mismatch: "
                f"{path.name}"
            )

        entries.append(
            {
                "path": path,
                "first_replicate": first,
                "last_replicate": last,
                "row_count": len(rows),
                "sha256": sha256(path),
            }
        )

    entries.sort(
        key=lambda item: (
            item["first_replicate"],
            item["last_replicate"],
        )
    )

    next_index = 0
    for item in entries:
        if (
            item["first_replicate"]
            != next_index
        ):
            raise ValueError(
                "committed batch intervals "
                "are overlapping or noncontiguous"
            )
        next_index = (
            item["last_replicate"] + 1
        )

    return {
        "batch_count": len(entries),
        "row_count": sum(
            item["row_count"]
            for item in entries
        ),
        "next_replicate_index": next_index,
        "batches": [
            {
                key: value
                for key, value in item.items()
                if key != "path"
            }
            for item in entries
        ],
    }
