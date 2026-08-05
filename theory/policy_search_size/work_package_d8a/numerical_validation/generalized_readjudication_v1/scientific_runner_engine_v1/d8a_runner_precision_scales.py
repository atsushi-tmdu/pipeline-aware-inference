from __future__ import annotations

from functools import lru_cache

from d8a_generalized_oracle import (
    full_oracle_summary,
)
from d8a_runner_statistics import (
    tess_contrast_record,
)


def natural_scale(
    population_target: float,
) -> float:
    value = float(population_target)
    return float(
        1.0 + abs(value)
    )


def _class_key(
    class_record: dict[str, object],
) -> tuple[object, ...]:
    return (
        str(class_record["class_id"]),
        str(class_record["dependence"]),
        float(
            class_record[
                "candidate_probability"
            ]
        ),
        float(
            class_record[
                "trigger_probability"
            ]
        ),
        tuple(
            tuple(float(value) for value in row)
            for row in class_record[
                "correlation_matrix"
            ]
        ),
    )


@lru_cache(maxsize=4096)
def _population_targets_cached(
    class_key: tuple[object, ...],
    alpha: float,
) -> dict[str, float]:
    (
        class_id,
        dependence,
        candidate_probability,
        trigger_probability,
        correlation_rows,
    ) = class_key

    class_record = {
        "class_id": class_id,
        "dependence": dependence,
        "candidate_probability": (
            candidate_probability
        ),
        "trigger_probability": (
            trigger_probability
        ),
        "correlation_matrix": [
            list(row)
            for row in correlation_rows
        ],
    }

    # Population probabilities are independent of the reference-size
    # lattice term. A registered reference size is supplied only because
    # the locked full-oracle interface also returns reference coefficients.
    summary = full_oracle_summary(
        class_record,
        500,
        float(alpha),
    )
    probabilities = summary[
        "probabilities"
    ]

    adaptive = float(
        probabilities[
            "adaptive_probability"
        ]
    )
    comparator = float(
        probabilities[
            "comparator_probability"
        ]
    )
    delta = float(
        probabilities["delta_pi"]
    )

    tess = tess_contrast_record(
        adaptive,
        comparator,
        float(alpha),
    )
    if tess["status"] != "finite":
        raise ValueError(
            "locked population TESS target "
            "is not finite"
        )

    return {
        "adaptive": adaptive,
        "comparator": comparator,
        "delta": delta,
        "tess": float(tess["value"]),
    }


def population_targets(
    class_record: dict[str, object],
    alpha: float,
) -> dict[str, float]:
    return _population_targets_cached(
        _class_key(class_record),
        float(alpha),
    )


def build_job_scale_spec(
    job: dict[str, object],
    class_record: dict[str, object],
    example_row: dict[str, object],
) -> dict[str, object]:
    family = str(job["family"])
    alpha_values = [
        float(value)
        for value in job[
            "tess_alpha_values"
        ]
    ]

    base_targets = population_targets(
        class_record,
        alpha_values[0],
    )
    tess_targets = {
        f"alpha_{alpha:.2f}": (
            population_targets(
                class_record,
                alpha,
            )["tess"]
        )
        for alpha in alpha_values
    }

    if family == "reference_only":
        scalar_fields = {
            "adaptive_probability": (
                base_targets["adaptive"]
            ),
            "comparator_probability": (
                base_targets["comparator"]
            ),
            "delta_pi": (
                base_targets["delta"]
            ),
        }
    elif family in {
        "evaluation_only",
        "combined",
    }:
        scalar_fields = {
            "adaptive_estimate": (
                base_targets["adaptive"]
            ),
            "comparator_estimate": (
                base_targets["comparator"]
            ),
            "delta_hat": (
                base_targets["delta"]
            ),
        }
    else:
        raise ValueError(
            f"unknown family: {family}"
        )

    point_spec = {
        "population_targets": {
            **scalar_fields,
            **{
                f"tess::{key}": value
                for key, value
                in tess_targets.items()
            },
        },
        "scalar_denominators": {
            field: natural_scale(target)
            for field, target
            in scalar_fields.items()
        },
        "tess_denominators": {
            key: natural_scale(target)
            for key, target
            in tess_targets.items()
        },
    }

    return {
        "job_id": str(job["job_id"]),
        "family": family,
        "scale_source": (
            "locked_population_oracle_target"
        ),
        "points": [
            point_spec
            for _ in example_row["points"]
        ],
    }
