from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


ALLOWED_TESS_STATUSES = (
    "finite",
    "positive_infinity",
    "negative_infinity",
    "indeterminate_both_one",
)


@dataclass(frozen=True)
class ScalarPrecision:
    status: str
    replicate_count: int
    mean: float | None
    sample_sd: float | None
    mcse: float | None
    scale_denominator: float
    scaled_mcse: float | None
    target: float
    precision_pass: bool


def scalar_mean_precision(
    values: Iterable[float],
    *,
    scale_denominator: float,
    target: float,
) -> ScalarPrecision:
    denominator = float(
        scale_denominator
    )
    if denominator <= 0.0:
        raise ValueError(
            "scale_denominator must be positive"
        )
    if target <= 0.0:
        raise ValueError(
            "target must be positive"
        )

    sample = np.asarray(
        list(values),
        dtype=float,
    )
    if sample.ndim != 1:
        raise ValueError(
            "values must be one-dimensional"
        )
    if not np.all(np.isfinite(sample)):
        raise ValueError(
            "values must be finite"
        )

    count = int(sample.size)
    if count < 2:
        return ScalarPrecision(
            status="insufficient_replicates",
            replicate_count=count,
            mean=(
                float(sample[0])
                if count == 1
                else None
            ),
            sample_sd=None,
            mcse=None,
            scale_denominator=denominator,
            scaled_mcse=None,
            target=float(target),
            precision_pass=False,
        )

    mean = float(np.mean(sample))
    sample_sd = float(
        np.std(sample, ddof=1)
    )
    mcse = float(
        sample_sd
        / np.sqrt(count)
    )
    scaled = float(
        mcse / denominator
    )

    return ScalarPrecision(
        status=(
            "zero_variance"
            if sample_sd == 0.0
            else "finite"
        ),
        replicate_count=count,
        mean=mean,
        sample_sd=sample_sd,
        mcse=mcse,
        scale_denominator=denominator,
        scaled_mcse=scaled,
        target=float(target),
        precision_pass=(
            scaled <= target
        ),
    )


def tess_contrast_precision(
    records: Iterable[dict[str, object]],
    *,
    finite_scale_denominator: float,
    target: float,
) -> dict[str, object]:
    items = list(records)
    statuses = []

    for record in items:
        status = str(record.get("status"))
        if status not in ALLOWED_TESS_STATUSES:
            raise ValueError(
                f"invalid TESS status: {status}"
            )
        statuses.append(status)

    status_precision = {
        status: scalar_mean_precision(
            [
                float(observed == status)
                for observed in statuses
            ],
            scale_denominator=1.0,
            target=target,
        )
        for status in ALLOWED_TESS_STATUSES
    }

    finite_values = [
        float(record["value"])
        for record in items
        if record["status"] == "finite"
    ]

    if len(finite_values) == 0:
        finite_precision: (
            ScalarPrecision
            | dict[str, object]
        ) = {
            "status": (
                "not_applicable_no_finite_values"
            ),
            "replicate_count": 0,
            "scale_denominator": (
                float(
                    finite_scale_denominator
                )
            ),
            "precision_pass": True,
        }
    else:
        finite_precision = scalar_mean_precision(
            finite_values,
            scale_denominator=(
                finite_scale_denominator
            ),
            target=target,
        )

    status_pass = all(
        item.precision_pass
        for item in status_precision.values()
    )
    finite_pass = (
        finite_precision.precision_pass
        if isinstance(
            finite_precision,
            ScalarPrecision,
        )
        else bool(
            finite_precision[
                "precision_pass"
            ]
        )
    )

    scaled_values = [
        item.scaled_mcse
        for item in status_precision.values()
        if item.scaled_mcse is not None
    ]
    if isinstance(
        finite_precision,
        ScalarPrecision,
    ) and finite_precision.scaled_mcse is not None:
        scaled_values.append(
            finite_precision.scaled_mcse
        )

    return {
        "record_count": len(items),
        "status_counts": {
            status: statuses.count(status)
            for status in ALLOWED_TESS_STATUSES
        },
        "status_precision": {
            status: item.__dict__
            for status, item
            in status_precision.items()
        },
        "finite_value_precision": (
            finite_precision.__dict__
            if isinstance(
                finite_precision,
                ScalarPrecision,
            )
            else finite_precision
        ),
        "maximum_scaled_mcse": (
            max(scaled_values)
            if scaled_values
            else 0.0
        ),
        "precision_pass": (
            status_pass and finite_pass
        ),
    }


def evaluate_job_precision(
    rows: Iterable[dict[str, object]],
    scale_spec: dict[str, object],
    *,
    target: float,
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
            "rows contain multiple job IDs"
        )
    if len(families) != 1:
        raise ValueError(
            "rows contain multiple families"
        )

    job_id = next(iter(job_ids))
    family = next(iter(families))
    if str(scale_spec["job_id"]) != job_id:
        raise ValueError(
            "scale spec job ID mismatch"
        )
    if str(scale_spec["family"]) != family:
        raise ValueError(
            "scale spec family mismatch"
        )

    point_count = len(
        items[0]["points"]
    )
    if len(scale_spec["points"]) != point_count:
        raise ValueError(
            "scale point count mismatch"
        )
    if any(
        len(item["points"]) != point_count
        for item in items
    ):
        raise ValueError(
            "row point counts differ"
        )

    scalar_results = {}
    tess_results = {}
    scaled_values = []
    all_pass = True

    for point_index in range(point_count):
        point_scale = scale_spec[
            "points"
        ][point_index]

        for field, denominator in point_scale[
            "scalar_denominators"
        ].items():
            key = (
                f"point_{point_index}::{field}"
            )
            precision = scalar_mean_precision(
                [
                    float(
                        item["points"][
                            point_index
                        ][field]
                    )
                    for item in items
                ],
                scale_denominator=float(
                    denominator
                ),
                target=target,
            )
            scalar_results[key] = (
                precision.__dict__
            )
            all_pass = (
                all_pass
                and precision.precision_pass
            )
            if precision.scaled_mcse is not None:
                scaled_values.append(
                    precision.scaled_mcse
                )

        for alpha_key, denominator in point_scale[
            "tess_denominators"
        ].items():
            key = (
                f"point_{point_index}::"
                f"tess::{alpha_key}"
            )
            precision = (
                tess_contrast_precision(
                    [
                        item["points"][
                            point_index
                        ]["tess_contrasts"][
                            alpha_key
                        ]
                        for item in items
                    ],
                    finite_scale_denominator=(
                        float(denominator)
                    ),
                    target=target,
                )
            )
            tess_results[key] = precision
            all_pass = (
                all_pass
                and bool(
                    precision[
                        "precision_pass"
                    ]
                )
            )
            scaled_values.append(
                float(
                    precision[
                        "maximum_scaled_mcse"
                    ]
                )
            )

    return {
        "job_id": job_id,
        "family": family,
        "replicate_count": len(items),
        "target": float(target),
        "scalar_precision": scalar_results,
        "tess_precision": tess_results,
        "maximum_scaled_mcse": (
            max(scaled_values)
            if scaled_values
            else 0.0
        ),
        "precision_pass": all_pass,
    }
