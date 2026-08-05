from __future__ import annotations

from collections import defaultdict
from typing import Iterable

import numpy as np


PRIMARY_CLASS_COUNT = 17
REFERENCE_MEDIAN_MAXIMUM = 0.15
REFERENCE_P90_MAXIMUM = 0.40
REFERENCE_MEDIAN_IMPROVEMENT_MINIMUM = 0.40
COMBINED_POLICY_MEDIAN_MAXIMUM = 0.15
COMBINED_POLICY_P90_MAXIMUM = 0.40
TESS_MEDIAN_MAXIMUM = 0.25
TESS_P90_MAXIMUM = 0.60
SECOND_ORDER_IMPROVED_FRACTION_MINIMUM = 0.75
PRECISION_LIMITED_FRACTION_MAXIMUM = 0.10


def _finite(
    value: float,
    name: str,
) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError(
            f"{name} must be finite"
        )
    return result


def adjusted_normalized_residual(
    *,
    observed_mean: float,
    target: float,
    predicted_bias: float,
    mcse: float,
    scale: float,
    z_star: float,
) -> dict[str, float]:
    denominator = _finite(
        scale,
        "scale",
    )
    if denominator <= 0.0:
        raise ValueError(
            "scale must be positive"
        )

    standard_error = _finite(
        mcse,
        "mcse",
    )
    if standard_error < 0.0:
        raise ValueError(
            "mcse must be nonnegative"
        )

    bias = (
        _finite(
            observed_mean,
            "observed_mean",
        )
        - _finite(target, "target")
    )
    prediction = _finite(
        predicted_bias,
        "predicted_bias",
    )
    raw_residual = float(
        bias - prediction
    )
    adjusted_absolute = float(
        max(
            abs(raw_residual)
            - _finite(
                z_star,
                "z_star",
            )
            * standard_error,
            0.0,
        )
    )

    return {
        "observed_bias": float(bias),
        "predicted_bias": prediction,
        "raw_residual": raw_residual,
        "mcse_adjusted_absolute_residual": (
            adjusted_absolute
        ),
        "scale": denominator,
        "normalized_residual": float(
            adjusted_absolute
            / denominator
        ),
    }


def reference_policy_metric(
    *,
    observed_mean: float,
    mcse: float,
    population_delta: float,
    reference_coefficient: float,
    reference_size: int,
    z_star: float,
) -> dict[str, float]:
    B = int(reference_size)
    if B < 1:
        raise ValueError(
            "reference_size must be positive"
        )
    coefficient = _finite(
        reference_coefficient,
        "reference_coefficient",
    )
    return adjusted_normalized_residual(
        observed_mean=observed_mean,
        target=population_delta,
        predicted_bias=coefficient / B,
        mcse=mcse,
        scale=(
            (1.0 / B)
            * (
                1.0
                + abs(coefficient)
            )
        ),
        z_star=z_star,
    )


def combined_policy_metric(
    *,
    observed_mean: float,
    mcse: float,
    population_delta: float,
    reference_coefficient: float,
    reference_size: int,
    evaluation_size: int,
    z_star: float,
) -> dict[str, float]:
    B = int(reference_size)
    n = int(evaluation_size)
    if B < 1 or n < 1:
        raise ValueError(
            "sample sizes must be positive"
        )
    delta = _finite(
        population_delta,
        "population_delta",
    )
    coefficient = _finite(
        reference_coefficient,
        "reference_coefficient",
    )
    prediction = (
        coefficient / B
        - delta / n
        - coefficient / (B * n)
    )
    scale = (
        1.0 / B
        + 1.0 / n
    ) * (
        1.0
        + abs(coefficient)
        + abs(delta)
    )
    return adjusted_normalized_residual(
        observed_mean=observed_mean,
        target=delta,
        predicted_bias=prediction,
        mcse=mcse,
        scale=scale,
        z_star=z_star,
    )


def combined_tess_metric(
    *,
    observed_mean: float,
    mcse: float,
    population_tess: float,
    reference_coefficient: float,
    evaluation_coefficient: float,
    reference_size: int,
    evaluation_size: int,
    z_star: float,
) -> dict[str, float]:
    B = int(reference_size)
    n = int(evaluation_size)
    if B < 1 or n < 1:
        raise ValueError(
            "sample sizes must be positive"
        )
    reference = _finite(
        reference_coefficient,
        "reference_coefficient",
    )
    evaluation = _finite(
        evaluation_coefficient,
        "evaluation_coefficient",
    )
    prediction = (
        reference / B
        + evaluation / n
    )
    scale = (
        1.0 / B
        + 1.0 / n
    ) * (
        1.0
        + abs(reference)
        + abs(evaluation)
    )
    return adjusted_normalized_residual(
        observed_mean=observed_mean,
        target=population_tess,
        predicted_bias=prediction,
        mcse=mcse,
        scale=scale,
        z_star=z_star,
    )


def exact_identity_check(
    *,
    observed_mean: float,
    target: float,
    mcse: float,
    z_star: float,
) -> dict[str, object]:
    difference = abs(
        _finite(
            observed_mean,
            "observed_mean",
        )
        - _finite(target, "target")
    )
    standard_error = _finite(
        mcse,
        "mcse",
    )
    if standard_error < 0.0:
        raise ValueError(
            "mcse must be nonnegative"
        )
    tolerance = (
        _finite(z_star, "z_star")
        * standard_error
    )
    if standard_error == 0.0:
        passed = bool(
            difference <= 1e-15
        )
    else:
        passed = bool(
            difference <= tolerance
        )
    return {
        "absolute_difference": float(
            difference
        ),
        "simultaneous_tolerance": float(
            tolerance
        ),
        "passed": passed,
    }


def second_order_improved(
    *,
    observed_bias: float,
    first_order_prediction: float,
    second_order_prediction: float,
) -> bool:
    bias = _finite(
        observed_bias,
        "observed_bias",
    )
    first = _finite(
        first_order_prediction,
        "first_order_prediction",
    )
    second = _finite(
        second_order_prediction,
        "second_order_prediction",
    )
    return bool(
        abs(bias - second)
        < abs(bias - first)
    )


def _require_primary_class_values(
    records: Iterable[dict[str, object]],
    *,
    value_key: str,
) -> list[float]:
    items = list(records)
    class_ids = [
        str(item["class_id"])
        for item in items
    ]
    if len(items) != PRIMARY_CLASS_COUNT:
        raise ValueError(
            "exactly 17 primary class records "
            "are required"
        )
    if len(set(class_ids)) != PRIMARY_CLASS_COUNT:
        raise ValueError(
            "primary class IDs must be unique"
        )
    return [
        _finite(
            item[value_key],
            value_key,
        )
        for item in items
    ]


def _distribution_summary(
    values: Iterable[float],
) -> dict[str, float]:
    sample = np.asarray(
        list(values),
        dtype=float,
    )
    if sample.size == 0:
        raise ValueError(
            "values must not be empty"
        )
    if not np.all(np.isfinite(sample)):
        raise ValueError(
            "values must be finite"
        )
    return {
        "median": float(
            np.quantile(
                sample,
                0.5,
                method="linear",
            )
        ),
        "p90": float(
            np.quantile(
                sample,
                0.9,
                method="linear",
            )
        ),
    }


def aggregate_reference_acceptance(
    records: Iterable[dict[str, object]],
) -> dict[str, object]:
    items = list(records)
    largest = _require_primary_class_values(
        items,
        value_key=(
            "normalized_residual_B10000"
        ),
    )
    smaller = _require_primary_class_values(
        items,
        value_key=(
            "normalized_residual_B500"
        ),
    )

    largest_summary = (
        _distribution_summary(largest)
    )
    smaller_summary = (
        _distribution_summary(smaller)
    )

    baseline = smaller_summary["median"]
    final = largest_summary["median"]
    if baseline == 0.0:
        improvement = (
            1.0
            if final == 0.0
            else float("-inf")
        )
    else:
        improvement = float(
            (baseline - final)
            / baseline
        )

    second_order_count = sum(
        bool(
            item[
                "second_order_improved"
            ]
        )
        for item in items
    )
    second_order_fraction = float(
        second_order_count
        / PRIMARY_CLASS_COUNT
    )

    passed = bool(
        largest_summary["median"]
        <= REFERENCE_MEDIAN_MAXIMUM
        and largest_summary["p90"]
        <= REFERENCE_P90_MAXIMUM
        and improvement
        >= REFERENCE_MEDIAN_IMPROVEMENT_MINIMUM
        and second_order_fraction
        >= SECOND_ORDER_IMPROVED_FRACTION_MINIMUM
    )

    return {
        "largest_B": 10000,
        "comparison_B": 500,
        "largest_B_distribution": (
            largest_summary
        ),
        "comparison_B_distribution": (
            smaller_summary
        ),
        "median_improvement": improvement,
        "second_order_improved_count": (
            second_order_count
        ),
        "second_order_improved_fraction": (
            second_order_fraction
        ),
        "passed": passed,
    }


def aggregate_combined_policy_acceptance(
    records: Iterable[dict[str, object]],
) -> dict[str, object]:
    values = _require_primary_class_values(
        records,
        value_key="normalized_residual",
    )
    summary = _distribution_summary(
        values
    )
    return {
        "largest_pair": [10000, 10000],
        "distribution": summary,
        "passed": bool(
            summary["median"]
            <= COMBINED_POLICY_MEDIAN_MAXIMUM
            and summary["p90"]
            <= COMBINED_POLICY_P90_MAXIMUM
        ),
    }


def aggregate_tess_acceptance(
    records: Iterable[dict[str, object]],
    *,
    alpha_values: Iterable[float],
) -> dict[str, object]:
    items = list(records)
    grouped: dict[float, list[dict[str, object]]] = (
        defaultdict(list)
    )
    for item in items:
        grouped[
            float(item["alpha"])
        ].append(item)

    alpha_results = {}
    all_pass = True

    for alpha in [
        float(value)
        for value in alpha_values
    ]:
        group = grouped.get(
            alpha,
            [],
        )
        values = (
            _require_primary_class_values(
                group,
                value_key=(
                    "normalized_residual"
                ),
            )
        )
        summary = _distribution_summary(
            values
        )
        nonfinite_count = sum(
            int(
                item[
                    "nonfinite_record_count"
                ]
            )
            for item in group
        )
        passed = bool(
            nonfinite_count == 0
            and summary["median"]
            <= TESS_MEDIAN_MAXIMUM
            and summary["p90"]
            <= TESS_P90_MAXIMUM
        )
        alpha_results[
            f"{alpha:.2f}"
        ] = {
            "distribution": summary,
            "nonfinite_record_count": (
                nonfinite_count
            ),
            "passed": passed,
        }
        all_pass = (
            all_pass and passed
        )

    if set(grouped) != {
        float(value)
        for value in alpha_values
    }:
        raise ValueError(
            "unexpected or missing TESS alpha"
        )

    return {
        "largest_pair": [10000, 10000],
        "by_alpha": alpha_results,
        "passed": all_pass,
    }


def aggregate_exact_identity(
    records: Iterable[dict[str, object]],
    *,
    expected_comparisons: int,
) -> dict[str, object]:
    items = list(records)
    if len(items) != int(
        expected_comparisons
    ):
        raise ValueError(
            "exact-identity comparison count "
            "does not match the lock"
        )
    passed_count = sum(
        bool(item["passed"])
        for item in items
    )
    return {
        "comparison_count": len(items),
        "passed_count": passed_count,
        "failed_count": (
            len(items) - passed_count
        ),
        "passed": bool(
            passed_count == len(items)
        ),
    }


def aggregate_precision_limited(
    primary_class_ids: Iterable[str],
) -> dict[str, object]:
    unique = {
        str(value)
        for value in primary_class_ids
    }
    if not unique.issubset(
        {
            f"d8a-primary-{index:03d}"
            for index in range(
                PRIMARY_CLASS_COUNT
            )
        }
    ):
        # The scientific adapter may use the registered
        # d8a-generalized IDs instead. Only the count is
        # scientifically operative here.
        if len(unique) > PRIMARY_CLASS_COUNT:
            raise ValueError(
                "too many precision-limited classes"
            )

    count = len(unique)
    fraction = float(
        count / PRIMARY_CLASS_COUNT
    )
    return {
        "precision_limited_class_count": (
            count
        ),
        "primary_class_denominator": (
            PRIMARY_CLASS_COUNT
        ),
        "fraction": fraction,
        "maximum_fraction": (
            PRECISION_LIMITED_FRACTION_MAXIMUM
        ),
        "maximum_allowed_class_count": 1,
        "passed": bool(count <= 1),
    }


def formal_acceptance(
    *,
    reference: dict[str, object],
    combined_policy: dict[str, object],
    tess: dict[str, object],
    exact_identity: dict[str, object],
    precision_limited: dict[str, object],
    fatal_checks_pass: bool,
) -> dict[str, object]:
    components = {
        "reference": bool(
            reference["passed"]
        ),
        "combined_policy": bool(
            combined_policy["passed"]
        ),
        "tess": bool(tess["passed"]),
        "exact_identity": bool(
            exact_identity["passed"]
        ),
        "precision_limited": bool(
            precision_limited["passed"]
        ),
        "fatal_checks": bool(
            fatal_checks_pass
        ),
    }
    return {
        "components": components,
        "formal_status": (
            "PASS"
            if all(
                components.values()
            )
            else "FAIL"
        ),
    }
