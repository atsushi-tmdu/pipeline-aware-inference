from __future__ import annotations

from typing import Iterable

import numpy as np

from d8a_generalized_oracle import (
    theta_from_class,
)
from d8a_policy_engine import (
    policy_estimators,
    policy_fields,
    policy_population_probabilities,
    reference_thresholds,
)
from d8a_runner_seed import (
    SeedInventory,
)
from d8a_runner_statistics import (
    finite_n_delta_target,
    tess_contrast,
)


def _sorted_unique_positive(
    values: Iterable[int],
) -> list[int]:
    result = sorted(
        {
            int(value)
            for value in values
        }
    )
    if not result or result[0] < 1:
        raise ValueError(
            "sample sizes must be positive"
        )
    return result


def _tess_map(
    adaptive: float,
    comparator: float,
    alpha_values: Iterable[float],
) -> dict[str, float | None]:
    return {
        f"alpha_{float(alpha):.2f}": (
            tess_contrast(
                adaptive,
                comparator,
                float(alpha),
            )
        )
        for alpha in alpha_values
    }


def simulate_reference_only(
    job: dict[str, object],
    class_record: dict[str, object],
    seed_inventory: SeedInventory,
    replicate_index: int,
    *,
    sample_sizes: Iterable[int] | None = None,
) -> dict[str, object]:
    if job["family"] != "reference_only":
        raise ValueError(
            "job is not reference_only"
        )

    sizes = _sorted_unique_positive(
        sample_sizes
        if sample_sizes is not None
        else job[
            "sample_specification"
        ]["reference_B"]
    )
    correlation = np.asarray(
        class_record[
            "correlation_matrix"
        ],
        dtype=float,
    )
    rng = seed_inventory.make_rng(
        str(job["job_id"]),
        "scientific_reference",
        replicate_index,
    )
    bank = rng.multivariate_normal(
        np.zeros(3),
        correlation,
        size=max(sizes),
    )

    candidate_probability = float(
        class_record[
            "candidate_probability"
        ]
    )
    trigger_probability = float(
        class_record[
            "trigger_probability"
        ]
    )
    alpha_values = [
        float(value)
        for value in job[
            "tess_alpha_values"
        ]
    ]

    population_theta = theta_from_class(
        class_record
    )
    population = (
        policy_population_probabilities(
            population_theta,
            correlation,
        )
    )

    points = []
    for size in sizes:
        thresholds = reference_thresholds(
            bank[:size],
            candidate_probability,
            trigger_probability,
        )
        probabilities = (
            policy_population_probabilities(
                thresholds,
                correlation,
            )
        )
        points.append(
            {
                "reference_B": size,
                "thresholds": [
                    float(value)
                    for value in thresholds
                ],
                "adaptive_probability": float(
                    probabilities[
                        "adaptive_probability"
                    ]
                ),
                "comparator_probability": float(
                    probabilities[
                        "comparator_probability"
                    ]
                ),
                "delta_pi": float(
                    probabilities[
                        "delta_pi"
                    ]
                ),
                "delta_reference_bias": float(
                    probabilities[
                        "delta_pi"
                    ]
                    - population[
                        "delta_pi"
                    ]
                ),
                "tess_contrasts": _tess_map(
                    float(
                        probabilities[
                            "adaptive_probability"
                        ]
                    ),
                    float(
                        probabilities[
                            "comparator_probability"
                        ]
                    ),
                    alpha_values,
                ),
            }
        )

    return {
        "job_id": job["job_id"],
        "family": "reference_only",
        "class_id": class_record[
            "class_id"
        ],
        "replicate_index": replicate_index,
        "points": points,
    }


def simulate_evaluation_only(
    job: dict[str, object],
    class_record: dict[str, object],
    seed_inventory: SeedInventory,
    replicate_index: int,
    *,
    sample_sizes: Iterable[int] | None = None,
) -> dict[str, object]:
    if job["family"] != "evaluation_only":
        raise ValueError(
            "job is not evaluation_only"
        )

    sizes = _sorted_unique_positive(
        sample_sizes
        if sample_sizes is not None
        else job[
            "sample_specification"
        ]["evaluation_n"]
    )
    correlation = np.asarray(
        class_record[
            "correlation_matrix"
        ],
        dtype=float,
    )
    theta = theta_from_class(
        class_record
    )
    population = (
        policy_population_probabilities(
            theta,
            correlation,
        )
    )

    rng = seed_inventory.make_rng(
        str(job["job_id"]),
        "scientific_evaluation",
        replicate_index,
    )
    bank = rng.multivariate_normal(
        np.zeros(3),
        correlation,
        size=max(sizes),
    )
    alpha_values = [
        float(value)
        for value in job[
            "tess_alpha_values"
        ]
    ]

    points = []
    for size in sizes:
        estimates = policy_estimators(
            policy_fields(
                bank[:size],
                theta,
            )
        )
        points.append(
            {
                "evaluation_n": size,
                "adaptive_estimate": float(
                    estimates[
                        "adaptive_probability"
                    ]
                ),
                "comparator_estimate": float(
                    estimates[
                        "comparator_probability"
                    ]
                ),
                "delta_hat": float(
                    estimates["delta_hat"]
                ),
                "finite_n_delta_target": (
                    finite_n_delta_target(
                        float(
                            population[
                                "delta_pi"
                            ]
                        ),
                        size,
                    )
                ),
                "tess_contrasts": _tess_map(
                    float(
                        estimates[
                            "adaptive_probability"
                        ]
                    ),
                    float(
                        estimates[
                            "comparator_probability"
                        ]
                    ),
                    alpha_values,
                ),
            }
        )

    return {
        "job_id": job["job_id"],
        "family": "evaluation_only",
        "class_id": class_record[
            "class_id"
        ],
        "replicate_index": replicate_index,
        "points": points,
    }


def _normalize_pairs(
    pairs: Iterable[Iterable[int]],
) -> list[tuple[int, int]]:
    result = []
    for pair in pairs:
        values = list(pair)
        if len(values) != 2:
            raise ValueError(
                "combined pair must have length 2"
            )
        reference_size = int(
            values[0]
        )
        evaluation_size = int(
            values[1]
        )
        if (
            reference_size < 1
            or evaluation_size < 1
        ):
            raise ValueError(
                "combined sizes must be positive"
            )
        result.append(
            (
                reference_size,
                evaluation_size,
            )
        )
    if not result:
        raise ValueError(
            "combined pair list is empty"
        )
    return result


def simulate_combined(
    job: dict[str, object],
    class_record: dict[str, object],
    seed_inventory: SeedInventory,
    replicate_index: int,
    *,
    pairs: Iterable[Iterable[int]] | None = None,
) -> dict[str, object]:
    if job["family"] != "combined":
        raise ValueError(
            "job is not combined"
        )

    combined_pairs = _normalize_pairs(
        pairs
        if pairs is not None
        else job[
            "sample_specification"
        ]["combined_pairs"]
    )
    correlation = np.asarray(
        class_record[
            "correlation_matrix"
        ],
        dtype=float,
    )
    reference_rng = (
        seed_inventory.make_rng(
            str(job["job_id"]),
            "scientific_reference",
            replicate_index,
        )
    )
    evaluation_rng = (
        seed_inventory.make_rng(
            str(job["job_id"]),
            "scientific_evaluation",
            replicate_index,
        )
    )
    reference_bank = (
        reference_rng.multivariate_normal(
            np.zeros(3),
            correlation,
            size=max(
                reference_size
                for (
                    reference_size,
                    _,
                ) in combined_pairs
            ),
        )
    )
    evaluation_bank = (
        evaluation_rng.multivariate_normal(
            np.zeros(3),
            correlation,
            size=max(
                evaluation_size
                for (
                    _,
                    evaluation_size,
                ) in combined_pairs
            ),
        )
    )

    candidate_probability = float(
        class_record[
            "candidate_probability"
        ]
    )
    trigger_probability = float(
        class_record[
            "trigger_probability"
        ]
    )
    alpha_values = [
        float(value)
        for value in job[
            "tess_alpha_values"
        ]
    ]

    points = []
    for (
        reference_size,
        evaluation_size,
    ) in combined_pairs:
        thresholds = reference_thresholds(
            reference_bank[
                :reference_size
            ],
            candidate_probability,
            trigger_probability,
        )
        population_at_reference = (
            policy_population_probabilities(
                thresholds,
                correlation,
            )
        )
        estimates = policy_estimators(
            policy_fields(
                evaluation_bank[
                    :evaluation_size
                ],
                thresholds,
            )
        )

        points.append(
            {
                "reference_B": (
                    reference_size
                ),
                "evaluation_n": (
                    evaluation_size
                ),
                "thresholds": [
                    float(value)
                    for value in thresholds
                ],
                "adaptive_estimate": float(
                    estimates[
                        "adaptive_probability"
                    ]
                ),
                "comparator_estimate": float(
                    estimates[
                        "comparator_probability"
                    ]
                ),
                "delta_hat": float(
                    estimates["delta_hat"]
                ),
                "conditional_finite_n_delta_target": (
                    finite_n_delta_target(
                        float(
                            population_at_reference[
                                "delta_pi"
                            ]
                        ),
                        evaluation_size,
                    )
                ),
                "tess_contrasts": _tess_map(
                    float(
                        estimates[
                            "adaptive_probability"
                        ]
                    ),
                    float(
                        estimates[
                            "comparator_probability"
                        ]
                    ),
                    alpha_values,
                ),
            }
        )

    return {
        "job_id": job["job_id"],
        "family": "combined",
        "class_id": class_record[
            "class_id"
        ],
        "replicate_index": replicate_index,
        "points": points,
    }


def simulate_job_replicate(
    job: dict[str, object],
    class_record: dict[str, object],
    seed_inventory: SeedInventory,
    replicate_index: int,
    *,
    engineering_override: dict[
        str, object
    ] | None = None,
) -> dict[str, object]:
    override = (
        engineering_override or {}
    )
    family = str(job["family"])

    if family == "reference_only":
        return simulate_reference_only(
            job,
            class_record,
            seed_inventory,
            replicate_index,
            sample_sizes=override.get(
                "reference_sizes"
            ),
        )
    if family == "evaluation_only":
        return simulate_evaluation_only(
            job,
            class_record,
            seed_inventory,
            replicate_index,
            sample_sizes=override.get(
                "evaluation_sizes"
            ),
        )
    if family == "combined":
        return simulate_combined(
            job,
            class_record,
            seed_inventory,
            replicate_index,
            pairs=override.get(
                "combined_pairs"
            ),
        )
    raise ValueError(
        f"unknown family: {family}"
    )

# ---------------------------------------------------------------------------
# Structured TESS output. Boundary events are never silently dropped.
# ---------------------------------------------------------------------------

from d8a_runner_statistics import (  # noqa: E402
    tess_contrast_record,
)


def _tess_map(
    adaptive: float,
    comparator: float,
    alpha_values: Iterable[float],
) -> dict[str, dict[str, object]]:
    return {
        f"alpha_{float(alpha):.2f}": (
            tess_contrast_record(
                adaptive,
                comparator,
                float(alpha),
            )
        )
        for alpha in alpha_values
    }
