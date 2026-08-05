from __future__ import annotations

import math

import numpy as np


def tess_value(
    probability: float,
    alpha: float,
) -> float | None:
    p = float(probability)
    a = float(alpha)

    if not 0.0 < a < 1.0:
        raise ValueError(
            "alpha must lie in (0,1)"
        )
    if p < 0.0 or p > 1.0:
        raise ValueError(
            "probability must lie in [0,1]"
        )
    if p == 1.0:
        return None

    return float(
        math.log1p(-p)
        / math.log1p(-a)
    )


def tess_contrast(
    adaptive_probability: float,
    comparator_probability: float,
    alpha: float,
) -> float | None:
    adaptive = tess_value(
        adaptive_probability,
        alpha,
    )
    comparator = tess_value(
        comparator_probability,
        alpha,
    )
    if adaptive is None or comparator is None:
        return None
    return float(
        adaptive - comparator
    )


def finite_n_delta_target(
    population_delta: float,
    evaluation_size: int,
) -> float:
    if evaluation_size < 1:
        raise ValueError(
            "evaluation_size must be positive"
        )
    return float(
        (
            1.0
            - 1.0
            / evaluation_size
        )
        * population_delta
    )


def ensure_json_scalar(
    value: object,
) -> object:
    if isinstance(
        value,
        (np.floating, np.integer),
    ):
        return value.item()
    return value

# ---------------------------------------------------------------------------
# Structured TESS boundary policy for JSON-safe scientific output.
# ---------------------------------------------------------------------------

def tess_value_record(
    probability: float,
    alpha: float,
) -> dict[str, object]:
    p = float(probability)
    a = float(alpha)

    if not 0.0 < a < 1.0:
        raise ValueError(
            "alpha must lie in (0,1)"
        )
    if p < 0.0 or p > 1.0:
        raise ValueError(
            "probability must lie in [0,1]"
        )

    if p == 1.0:
        return {
            "status": "positive_infinity",
            "value": None,
            "probability": p,
            "alpha": a,
        }

    return {
        "status": "finite",
        "value": float(
            math.log1p(-p)
            / math.log1p(-a)
        ),
        "probability": p,
        "alpha": a,
    }


def tess_contrast_record(
    adaptive_probability: float,
    comparator_probability: float,
    alpha: float,
) -> dict[str, object]:
    adaptive = tess_value_record(
        adaptive_probability,
        alpha,
    )
    comparator = tess_value_record(
        comparator_probability,
        alpha,
    )

    adaptive_status = str(
        adaptive["status"]
    )
    comparator_status = str(
        comparator["status"]
    )

    if (
        adaptive_status == "finite"
        and comparator_status == "finite"
    ):
        return {
            "status": "finite",
            "value": float(
                adaptive["value"]
                - comparator["value"]
            ),
            "adaptive": adaptive,
            "comparator": comparator,
        }

    if (
        adaptive_status
        == "positive_infinity"
        and comparator_status == "finite"
    ):
        status = "positive_infinity"
    elif (
        adaptive_status == "finite"
        and comparator_status
        == "positive_infinity"
    ):
        status = "negative_infinity"
    else:
        status = "indeterminate_both_one"

    return {
        "status": status,
        "value": None,
        "adaptive": adaptive,
        "comparator": comparator,
    }


def tess_status_is_valid(
    record: object,
) -> bool:
    if not isinstance(record, dict):
        return False

    status = record.get("status")
    allowed = {
        "finite",
        "positive_infinity",
        "negative_infinity",
        "indeterminate_both_one",
    }
    if status not in allowed:
        return False

    value = record.get("value")
    if status == "finite":
        return isinstance(
            value,
            (int, float),
        ) and math.isfinite(float(value))
    return value is None
