from __future__ import annotations

from typing import Iterable

import numpy as np


TESS_STATUSES = (
    "finite",
    "positive_infinity",
    "negative_infinity",
    "indeterminate_both_one",
)


def scalar_summary(
    values: Iterable[float],
    *,
    target: float,
) -> dict[str, object]:
    sample = np.asarray(
        list(values),
        dtype=float,
    )
    if sample.ndim != 1:
        raise ValueError(
            "values must be one-dimensional"
        )
    if sample.size < 2:
        raise ValueError(
            "at least two replicates are required"
        )
    if not np.all(np.isfinite(sample)):
        raise ValueError(
            "values must be finite"
        )

    mean = float(np.mean(sample))
    sample_sd = float(
        np.std(sample, ddof=1)
    )
    mcse = float(
        sample_sd
        / np.sqrt(sample.size)
    )
    population_target = float(target)

    return {
        "replicate_count": int(sample.size),
        "mean": mean,
        "sample_sd": sample_sd,
        "mcse": mcse,
        "target": population_target,
        "bias": float(
            mean - population_target
        ),
    }


def tess_summary(
    records: Iterable[dict[str, object]],
    *,
    target: float,
) -> dict[str, object]:
    items = list(records)
    if len(items) < 2:
        raise ValueError(
            "at least two TESS records are required"
        )

    statuses = []
    finite_values = []

    for record in items:
        status = str(record.get("status"))
        if status not in TESS_STATUSES:
            raise ValueError(
                f"invalid TESS status: {status}"
            )
        statuses.append(status)
        if status == "finite":
            value = float(record["value"])
            if not np.isfinite(value):
                raise ValueError(
                    "finite TESS value is not finite"
                )
            finite_values.append(value)

    counts = {
        status: statuses.count(status)
        for status in TESS_STATUSES
    }
    fractions = {
        status: float(
            counts[status] / len(items)
        )
        for status in TESS_STATUSES
    }

    if len(finite_values) >= 2:
        finite = scalar_summary(
            finite_values,
            target=target,
        )
    elif len(finite_values) == 1:
        finite = {
            "status": (
                "insufficient_finite_replicates"
            ),
            "replicate_count": 1,
            "target": float(target),
        }
    else:
        finite = {
            "status": (
                "not_applicable_no_finite_values"
            ),
            "replicate_count": 0,
            "target": float(target),
        }

    return {
        "record_count": len(items),
        "status_counts": counts,
        "status_fractions": fractions,
        "nonfinite_count": int(
            len(items) - len(finite_values)
        ),
        "any_nonfinite": bool(
            len(finite_values) != len(items)
        ),
        "finite_summary": finite,
    }


def summarize_job_rows(
    rows: Iterable[dict[str, object]],
    scale_spec: dict[str, object],
) -> dict[str, object]:
    items = list(rows)
    if not items:
        raise ValueError(
            "rows must not be empty"
        )

    job_ids = {
        str(item["job_id"])
        for item in items
    }
    families = {
        str(item["family"])
        for item in items
    }
    if len(job_ids) != 1:
        raise ValueError(
            "multiple job IDs"
        )
    if len(families) != 1:
        raise ValueError(
            "multiple families"
        )

    job_id = next(iter(job_ids))
    family = next(iter(families))
    if scale_spec["job_id"] != job_id:
        raise ValueError(
            "scale-spec job mismatch"
        )
    if scale_spec["family"] != family:
        raise ValueError(
            "scale-spec family mismatch"
        )

    point_count = len(
        items[0]["points"]
    )
    if any(
        len(item["points"]) != point_count
        for item in items
    ):
        raise ValueError(
            "point counts differ"
        )
    if len(scale_spec["points"]) != point_count:
        raise ValueError(
            "scale-spec point count differs"
        )

    points = []

    for point_index in range(point_count):
        target_map = scale_spec[
            "points"
        ][point_index][
            "population_targets"
        ]

        scalar_fields = [
            key
            for key in target_map
            if not key.startswith("tess::")
        ]
        scalar = {
            field: scalar_summary(
                [
                    float(
                        item["points"][
                            point_index
                        ][field]
                    )
                    for item in items
                ],
                target=float(
                    target_map[field]
                ),
            )
            for field in scalar_fields
        }

        tess = {}
        for target_key, target in (
            target_map.items()
        ):
            if not target_key.startswith(
                "tess::"
            ):
                continue
            alpha_key = target_key.split(
                "::",
                1,
            )[1]
            tess[alpha_key] = tess_summary(
                [
                    item["points"][
                        point_index
                    ]["tess_contrasts"][
                        alpha_key
                    ]
                    for item in items
                ],
                target=float(target),
            )

        first_point = items[0][
            "points"
        ][point_index]
        coordinates = {
            key: first_point[key]
            for key in (
                "reference_B",
                "evaluation_n",
            )
            if key in first_point
        }

        points.append(
            {
                "point_index": point_index,
                "coordinates": coordinates,
                "scalar": scalar,
                "tess": tess,
            }
        )

    return {
        "job_id": job_id,
        "family": family,
        "replicate_count": len(items),
        "points": points,
    }
