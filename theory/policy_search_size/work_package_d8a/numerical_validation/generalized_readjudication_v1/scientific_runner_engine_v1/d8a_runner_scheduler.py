from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from d8a_runner_engine import (
    simulate_job_replicate,
)
from d8a_runner_io import (
    atomic_write_json,
    atomic_write_jsonl_batch,
    scan_committed_batches,
)
from d8a_runner_precision import (
    evaluate_job_precision,
)
from d8a_runner_precision_scales import (
    build_job_scale_spec,
)
from d8a_runner_summary import (
    summarize_job_rows,
)
from d8a_runner_stopping import (
    StoppingSchedule,
)


FAMILY_ORDER = {
    "reference_only": 0,
    "evaluation_only": 1,
    "combined": 2,
}

BATCH_PATTERN = re.compile(
    r"^batch_(\d+)_(\d+)\.jsonl$"
)

ALLOWED_LABELS = {
    "NON_SCIENTIFIC_ENGINEERING_ONLY",
    "SCIENTIFIC",
}


def deterministic_job_order(
    jobs: Iterable[dict[str, object]],
) -> list[dict[str, object]]:
    items = list(jobs)
    return sorted(
        items,
        key=lambda job: (
            str(job["class_id"]),
            FAMILY_ORDER[
                str(job["family"])
            ],
            str(job["job_id"]),
        ),
    )


def validate_execution_label(
    label: str,
    *,
    allow_scientific: bool,
) -> None:
    value = str(label)
    if value not in ALLOWED_LABELS:
        raise ValueError(
            f"unknown execution label: {value}"
        )
    if (
        value == "SCIENTIFIC"
        and not allow_scientific
    ):
        raise PermissionError(
            "scientific execution is not authorized"
        )


def initialize_run_root(
    run_root: Path,
    metadata: dict[str, object],
) -> dict[str, object]:
    root = Path(run_root)
    metadata_path = (
        root / "RUN_METADATA.json"
    )

    if root.exists():
        if not root.is_dir():
            raise ValueError(
                "run root exists but is not a directory"
            )
        if not metadata_path.is_file():
            raise ValueError(
                "existing run root lacks RUN_METADATA.json"
            )
        observed = json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )
        if observed != metadata:
            raise ValueError(
                "existing run metadata does not "
                "match the requested run"
            )
        return observed

    root.mkdir(
        parents=True,
        exist_ok=False,
    )
    atomic_write_json(
        metadata_path,
        metadata,
    )
    (root / "jobs").mkdir(
        parents=True,
        exist_ok=False,
    )
    return metadata


def job_directory(
    run_root: Path,
    job_id: str,
) -> Path:
    return (
        Path(run_root)
        / "jobs"
        / str(job_id)
    )


def status_path(
    run_root: Path,
    job_id: str,
) -> Path:
    return (
        job_directory(
            run_root,
            job_id,
        )
        / "JOB_STATUS.json"
    )


def _batch_sort_key(
    path: Path,
) -> tuple[int, int]:
    match = BATCH_PATTERN.match(
        path.name
    )
    if match is None:
        raise ValueError(
            f"invalid batch filename: {path.name}"
        )
    return (
        int(match.group(1)),
        int(match.group(2)),
    )


def load_committed_rows(
    run_root: Path,
    job_id: str,
) -> list[dict[str, object]]:
    directory = job_directory(
        run_root,
        job_id,
    )
    scan_committed_batches(
        directory,
        str(job_id),
    )

    batch_directory = (
        directory / "batches"
    )
    if not batch_directory.exists():
        return []

    rows = []
    for path in sorted(
        batch_directory.glob(
            "batch_*.jsonl"
        ),
        key=_batch_sort_key,
    ):
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines():
            row = json.loads(line)
            if row["job_id"] != job_id:
                raise ValueError(
                    "committed row job ID mismatch"
                )
            rows.append(row)

    expected = list(
        range(len(rows))
    )
    observed = [
        int(row["replicate_index"])
        for row in rows
    ]
    if observed != expected:
        raise ValueError(
            "committed replicate indices are "
            "not contiguous from zero"
        )
    return rows


def write_job_status(
    run_root: Path,
    job_id: str,
    status: dict[str, object],
) -> None:
    atomic_write_json(
        status_path(
            run_root,
            job_id,
        ),
        status,
    )


def validate_status_against_rows(
    status: dict[str, object],
    rows: list[dict[str, object]],
) -> None:
    if int(
        status["replicate_count"]
    ) != len(rows):
        raise ValueError(
            "status replicate count does not "
            "match committed rows"
        )
    if rows and any(
        row["job_id"] != status["job_id"]
        for row in rows
    ):
        raise ValueError(
            "status job ID does not match rows"
        )


def _compact_precision(
    precision: (
        dict[str, object] | None
    ),
) -> dict[str, object] | None:
    if precision is None:
        return None
    return {
        "replicate_count": int(
            precision[
                "replicate_count"
            ]
        ),
        "maximum_scaled_mcse": float(
            precision[
                "maximum_scaled_mcse"
            ]
        ),
        "target": float(
            precision["target"]
        ),
        "precision_pass": bool(
            precision[
                "precision_pass"
            ]
        ),
    }


def _write_precision(
    directory: Path,
    precision: (
        dict[str, object] | None
    ),
) -> None:
    if precision is None:
        return
    atomic_write_json(
        directory
        / "PRECISION_STATUS.json",
        precision,
    )


def run_family_job(
    *,
    job: dict[str, object],
    class_record: dict[str, object],
    seed_inventory: object,
    run_root: Path,
    schedule: StoppingSchedule,
    precision_target: float,
    label: str,
    allow_scientific: bool,
    max_new_batches: int | None = None,
) -> dict[str, object]:
    validate_execution_label(
        label,
        allow_scientific=(
            allow_scientific
        ),
    )

    if precision_target <= 0.0:
        raise ValueError(
            "precision_target must be positive"
        )
    if (
        max_new_batches is not None
        and max_new_batches < 0
    ):
        raise ValueError(
            "max_new_batches must be nonnegative"
        )

    job_id = str(job["job_id"])
    family = str(job["family"])
    class_id = str(job["class_id"])
    class_role = str(
        class_record["class_role"]
    )
    directory = job_directory(
        run_root,
        job_id,
    )
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = load_committed_rows(
        run_root,
        job_id,
    )

    existing_status_path = status_path(
        run_root,
        job_id,
    )
    if existing_status_path.is_file():
        existing_status = json.loads(
            existing_status_path.read_text(
                encoding="utf-8"
            )
        )
        validate_status_against_rows(
            existing_status,
            rows,
        )
        if bool(
            existing_status.get(
                "complete",
                False,
            )
        ):
            return existing_status

    new_batches = 0
    precision = None
    scale_spec = None

    while True:
        completed = len(rows)

        if rows:
            scale_spec = build_job_scale_spec(
                job,
                class_record,
                rows[0],
            )

        if (
            completed
            >= schedule.initial_replicates
            and rows
        ):
            precision = evaluate_job_precision(
                rows,
                scale_spec,
                target=precision_target,
            )
            _write_precision(
                directory,
                precision,
            )

        if (
            precision is not None
            and bool(
                precision[
                    "precision_pass"
                ]
            )
        ):
            stop_reason = (
                "precision_target_met"
            )
            complete = True
            break

        if (
            completed
            >= schedule.maximum_replicates
        ):
            stop_reason = (
                "maximum_replicates_reached"
            )
            complete = True
            break

        if (
            max_new_batches is not None
            and new_batches
            >= max_new_batches
        ):
            stop_reason = (
                "engineering_batch_limit_reached"
            )
            complete = False
            break

        if (
            completed
            < schedule.initial_replicates
        ):
            next_batch_size = min(
                max(
                    schedule.batch_size,
                    (
                        schedule.initial_replicates
                        - completed
                    ),
                ),
                (
                    schedule.maximum_replicates
                    - completed
                ),
            )
        else:
            next_batch_size = min(
                schedule.batch_size,
                (
                    schedule.maximum_replicates
                    - completed
                ),
            )

        if next_batch_size <= 0:
            raise RuntimeError(
                "nonpositive next batch size"
            )

        new_rows = []
        for replicate_index in range(
            completed,
            completed + next_batch_size,
        ):
            row = simulate_job_replicate(
                job,
                class_record,
                seed_inventory,
                replicate_index,
            )
            row["label"] = str(label)
            row[
                "scientific_simulation_run"
            ] = bool(
                label == "SCIENTIFIC"
            )
            new_rows.append(row)

        atomic_write_jsonl_batch(
            directory,
            job_id,
            new_rows,
        )
        rows.extend(new_rows)
        new_batches += 1

        intermediate = {
            "schema_version": "1.0",
            "label": str(label),
            "job_id": job_id,
            "class_id": class_id,
            "class_role": class_role,
            "family": family,
            "replicate_count": len(rows),
            "complete": False,
            "stop_reason": (
                "batch_committed"
            ),
            "new_batches_this_call": (
                new_batches
            ),
            "precision": (
                _compact_precision(
                    precision
                )
            ),
            "precision_limited": False,
            "scientific_simulation_run": (
                bool(
                    label == "SCIENTIFIC"
                )
            ),
        }
        write_job_status(
            run_root,
            job_id,
            intermediate,
        )

    if rows and scale_spec is None:
        scale_spec = build_job_scale_spec(
            job,
            class_record,
            rows[0],
        )

    if (
        rows
        and precision is None
        and len(rows) >= 2
    ):
        precision = evaluate_job_precision(
            rows,
            scale_spec,
            target=precision_target,
        )
        _write_precision(
            directory,
            precision,
        )

    precision_pass = bool(
        precision is not None
        and precision[
            "precision_pass"
        ]
    )
    precision_limited = bool(
        complete
        and stop_reason
        == "maximum_replicates_reached"
        and not precision_pass
        and class_role == "primary"
    )

    status = {
        "schema_version": "1.0",
        "label": str(label),
        "job_id": job_id,
        "class_id": class_id,
        "class_role": class_role,
        "family": family,
        "replicate_count": len(rows),
        "complete": bool(complete),
        "stop_reason": stop_reason,
        "new_batches_this_call": (
            new_batches
        ),
        "precision": (
            _compact_precision(
                precision
            )
        ),
        "precision_limited": (
            precision_limited
        ),
        "scientific_simulation_run": (
            bool(
                label == "SCIENTIFIC"
            )
        ),
    }
    write_job_status(
        run_root,
        job_id,
        status,
    )

    if complete and rows:
        summary = summarize_job_rows(
            rows,
            scale_spec,
        )
        summary["label"] = str(label)
        summary[
            "scientific_simulation_run"
        ] = bool(
            label == "SCIENTIFIC"
        )
        atomic_write_json(
            directory
            / "JOB_SUMMARY.json",
            summary,
        )

    validate_status_against_rows(
        status,
        rows,
    )
    return status
