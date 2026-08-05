from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import multivariate_normal, norm


FloatArray = np.ndarray


def transform_scores(
    latent: FloatArray,
    transform_name: str,
) -> FloatArray:
    values = np.asarray(latent, dtype=float)
    if transform_name == "identity":
        return values.copy()
    if transform_name == "exp_0_35":
        return np.exp(0.35 * values)
    if transform_name == "sinh_0_5":
        return np.sinh(0.5 * values)
    raise ValueError(
        f"unknown transform: {transform_name}"
    )


def quantile_order_index(
    sample_size: int,
    probability: float,
) -> int:
    if sample_size < 1:
        raise ValueError(
            "sample_size must be positive"
        )
    if not 0.0 < probability < 1.0:
        raise ValueError(
            "probability must lie in (0,1)"
        )
    return int(math.ceil(sample_size * probability))


def empirical_order_quantile(
    values: FloatArray,
    probability: float,
) -> float:
    sample = np.asarray(values, dtype=float)
    if sample.ndim != 1 or sample.size == 0:
        raise ValueError(
            "values must be a nonempty vector"
        )
    order_index = quantile_order_index(
        sample.size,
        probability,
    )
    return float(
        np.partition(
            sample,
            order_index - 1,
        )[order_index - 1]
    )


def reference_thresholds(
    reference_bank: FloatArray,
    candidate_probability: float,
    trigger_probability: float,
) -> FloatArray:
    bank = np.asarray(
        reference_bank,
        dtype=float,
    )
    if bank.ndim != 2 or bank.shape[1] != 3:
        raise ValueError(
            "reference_bank must have shape (B,3)"
        )

    candidate_thresholds = np.array(
        [
            empirical_order_quantile(
                bank[:, index],
                candidate_probability,
            )
            for index in range(3)
        ],
        dtype=float,
    )
    base_maximum = np.maximum(
        bank[:, 0],
        bank[:, 1],
    )
    trigger_threshold = empirical_order_quantile(
        base_maximum,
        trigger_probability,
    )
    return np.concatenate(
        [
            candidate_thresholds,
            np.array(
                [trigger_threshold],
                dtype=float,
            ),
        ]
    )


def policy_fields(
    evaluation_bank: FloatArray,
    thresholds: FloatArray,
) -> dict[str, FloatArray]:
    bank = np.asarray(
        evaluation_bank,
        dtype=float,
    )
    theta = np.asarray(
        thresholds,
        dtype=float,
    )
    if bank.ndim != 2 or bank.shape[1] != 3:
        raise ValueError(
            "evaluation_bank must have shape (n,3)"
        )
    if theta.shape != (4,):
        raise ValueError(
            "thresholds must have shape (4,)"
        )

    q = theta[:3]
    trigger = float(theta[3])

    base_winner = np.argmax(
        bank[:, :2],
        axis=1,
    )
    full_winner = np.argmax(
        bank,
        axis=1,
    )
    row_index = np.arange(bank.shape[0])

    base_reject = (
        bank[
            row_index,
            base_winner,
        ]
        > q[base_winner]
    )
    full_reject = (
        bank[
            row_index,
            full_winner,
        ]
        > q[full_winner]
    )
    activation = (
        np.maximum(
            bank[:, 0],
            bank[:, 1],
        )
        > trigger
    )
    incremental = (
        (~base_reject)
        & full_reject
    )
    adaptive = (
        base_reject
        | (
            activation
            & incremental
        )
    )

    return {
        "base_winner": base_winner,
        "full_winner": full_winner,
        "R0": base_reject.astype(float),
        "R1": full_reject.astype(float),
        "A": activation.astype(float),
        "M": incremental.astype(float),
        "H": adaptive.astype(float),
    }


def policy_estimators(
    fields: dict[str, FloatArray],
) -> dict[str, float]:
    r0 = np.asarray(fields["R0"], dtype=float)
    a = np.asarray(fields["A"], dtype=float)
    m = np.asarray(fields["M"], dtype=float)
    h = np.asarray(fields["H"], dtype=float)
    if not (
        r0.shape == a.shape == m.shape == h.shape
    ):
        raise ValueError(
            "field shapes must match"
        )

    adaptive_probability = float(np.mean(h))
    comparator_probability = float(
        np.mean(r0)
        + np.mean(a)
        * np.mean(m)
    )
    delta_hat = float(
        adaptive_probability
        - comparator_probability
    )
    return {
        "adaptive_probability": adaptive_probability,
        "comparator_probability": comparator_probability,
        "delta_hat": delta_hat,
        "base_probability": float(np.mean(r0)),
        "activation_probability": float(np.mean(a)),
        "incremental_probability": float(np.mean(m)),
        "joint_am_probability": float(
            np.mean(a * m)
        ),
    }


def bvn_cdf(
    upper_left: float,
    upper_right: float,
    correlation: float,
) -> float:
    if correlation >= 1.0:
        return float(
            norm.cdf(
                min(
                    upper_left,
                    upper_right,
                )
            )
        )
    if correlation <= -1.0:
        lower = -upper_right
        if upper_left <= lower:
            return 0.0
        return float(
            norm.cdf(upper_left)
            - norm.cdf(lower)
        )

    return float(
        multivariate_normal.cdf(
            np.array(
                [
                    upper_left,
                    upper_right,
                ],
                dtype=float,
            ),
            mean=np.zeros(2),
            cov=np.array(
                [
                    [1.0, correlation],
                    [correlation, 1.0],
                ],
                dtype=float,
            ),
            maxpts=100000,
            abseps=1e-10,
            releps=1e-10,
            rng=np.random.default_rng(1729),
        )
    )


def mvn3_cdf(
    upper: FloatArray,
    correlation_matrix: FloatArray,
) -> float:
    bounds = np.asarray(
        upper,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    if bounds.shape != (3,):
        raise ValueError(
            "upper must have shape (3,)"
        )
    if correlation.shape != (3, 3):
        raise ValueError(
            "correlation_matrix must have shape (3,3)"
        )

    return float(
        multivariate_normal.cdf(
            bounds,
            mean=np.zeros(3),
            cov=correlation,
            maxpts=300000,
            abseps=2e-9,
            releps=2e-9,
            rng=np.random.default_rng(1729),
        )
    )


def base_max_cdf(
    threshold: float,
    base_correlation: float,
) -> float:
    return bvn_cdf(
        threshold,
        threshold,
        base_correlation,
    )


def base_max_density(
    threshold: float,
    base_correlation: float,
) -> float:
    scale = math.sqrt(
        (1.0 - base_correlation)
        / (1.0 + base_correlation)
    )
    return float(
        2.0
        * norm.pdf(threshold)
        * norm.cdf(scale * threshold)
    )


def base_max_density_derivative(
    threshold: float,
    base_correlation: float,
) -> float:
    scale = math.sqrt(
        (1.0 - base_correlation)
        / (1.0 + base_correlation)
    )
    phi = float(norm.pdf(threshold))
    return float(
        2.0
        * (
            -threshold
            * phi
            * norm.cdf(scale * threshold)
            + phi
            * norm.pdf(scale * threshold)
            * scale
        )
    )


@lru_cache(maxsize=128)
def base_max_quantile(
    probability: float,
    base_correlation: float,
) -> float:
    return float(
        brentq(
            lambda threshold: (
                base_max_cdf(
                    threshold,
                    base_correlation,
                )
                - probability
            ),
            -8.0,
            8.0,
            xtol=1e-11,
            rtol=1e-11,
        )
    )


def _conditional_loser_probability(
    winner_value: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    loser_index = 1 - winner_index
    correlation = float(
        correlation_matrix[
            winner_index,
            loser_index,
        ]
    )
    conditional_sd = math.sqrt(
        1.0 - correlation**2
    )
    return float(
        norm.cdf(
            (
                winner_value
                - correlation * winner_value
            )
            / conditional_sd
        )
    )


def _conditional_branch_probability(
    winner_value: float,
    added_cutoff: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    loser_index = 1 - winner_index
    indices = [loser_index, 2]
    r_to_winner = correlation_matrix[
        indices,
        winner_index,
    ]
    conditional_mean = (
        r_to_winner * winner_value
    )
    conditional_covariance = (
        correlation_matrix[
            np.ix_(indices, indices)
        ]
        - np.outer(
            r_to_winner,
            r_to_winner,
        )
    )
    sd_loser = math.sqrt(
        conditional_covariance[0, 0]
    )
    sd_added = math.sqrt(
        conditional_covariance[1, 1]
    )
    conditional_correlation = float(
        conditional_covariance[0, 1]
        / (sd_loser * sd_added)
    )

    loser_upper = (
        winner_value
        - conditional_mean[0]
    ) / sd_loser
    added_upper = (
        added_cutoff
        - conditional_mean[1]
    ) / sd_added

    loser_probability = float(
        norm.cdf(loser_upper)
    )
    joint_lower = bvn_cdf(
        loser_upper,
        added_upper,
        conditional_correlation,
    )
    return float(
        max(
            loser_probability
            - joint_lower,
            0.0,
        )
    )


def _winner_rejection_probability(
    threshold: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    value, _ = quad(
        lambda winner: (
            norm.pdf(winner)
            * _conditional_loser_probability(
                winner,
                winner_index,
                correlation_matrix,
            )
        ),
        threshold,
        math.inf,
        epsabs=3e-9,
        epsrel=3e-9,
        limit=120,
    )
    return float(value)


def _incremental_branch_probability(
    lower_winner: float,
    upper_winner: float,
    added_threshold: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    if upper_winner <= lower_winner:
        return 0.0
    value, _ = quad(
        lambda winner: (
            norm.pdf(winner)
            * _conditional_branch_probability(
                winner,
                max(
                    winner,
                    added_threshold,
                ),
                winner_index,
                correlation_matrix,
            )
        ),
        lower_winner,
        upper_winner,
        epsabs=4e-8,
        epsrel=4e-8,
        limit=100,
    )
    return float(value)


def policy_population_probabilities(
    thresholds: FloatArray,
    correlation_matrix: FloatArray,
) -> dict[str, float]:
    theta = np.asarray(
        thresholds,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    if theta.shape != (4,):
        raise ValueError(
            "thresholds must have shape (4,)"
        )
    if correlation.shape != (3, 3):
        raise ValueError(
            "correlation_matrix must have shape (3,3)"
        )

    q0, q1, q2, trigger = map(
        float,
        theta,
    )
    base_probability = (
        _winner_rejection_probability(
            q0,
            0,
            correlation,
        )
        + _winner_rejection_probability(
            q1,
            1,
            correlation,
        )
    )
    activation_probability = float(
        1.0
        - base_max_cdf(
            trigger,
            float(correlation[0, 1]),
        )
    )

    incremental_parts = [
        _incremental_branch_probability(
            -math.inf,
            q0,
            q2,
            0,
            correlation,
        ),
        _incremental_branch_probability(
            -math.inf,
            q1,
            q2,
            1,
            correlation,
        ),
    ]
    joint_parts = [
        _incremental_branch_probability(
            trigger,
            q0,
            q2,
            0,
            correlation,
        ),
        _incremental_branch_probability(
            trigger,
            q1,
            q2,
            1,
            correlation,
        ),
    ]

    incremental_probability = float(
        sum(incremental_parts)
    )
    joint_am_probability = float(
        sum(joint_parts)
    )
    adaptive_probability = float(
        base_probability
        + joint_am_probability
    )
    comparator_probability = float(
        base_probability
        + activation_probability
        * incremental_probability
    )
    delta = float(
        adaptive_probability
        - comparator_probability
    )

    return {
        "base_probability": base_probability,
        "activation_probability": activation_probability,
        "incremental_probability": incremental_probability,
        "joint_am_probability": joint_am_probability,
        "adaptive_probability": adaptive_probability,
        "comparator_probability": comparator_probability,
        "delta_pi": delta,
        "incremental_parts": incremental_parts,
        "joint_parts": joint_parts,
    }

# ---------------------------------------------------------------------------
# Direct polyhedral-Gaussian policy probability implementation.
# This later definition intentionally supersedes the earlier integral form.
# ---------------------------------------------------------------------------

def _linear_gaussian_cdf(
    linear_map: FloatArray,
    upper: FloatArray,
    correlation_matrix: FloatArray,
) -> float:
    matrix = np.asarray(
        linear_map,
        dtype=float,
    )
    bounds = np.asarray(
        upper,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )

    covariance = (
        matrix
        @ correlation
        @ matrix.T
    )
    covariance = (
        covariance
        + covariance.T
    ) / 2.0

    return float(
        multivariate_normal.cdf(
            bounds,
            mean=np.zeros(bounds.size),
            cov=covariance,
            maxpts=500000,
            abseps=1e-11,
            releps=1e-11,
            rng=np.random.default_rng(271828),
        )
    )


def _base_reject_cell_probability_direct(
    candidate_threshold: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    loser_index = 1 - winner_index
    first = np.zeros(3, dtype=float)
    first[loser_index] = 1.0
    first[winner_index] = -1.0

    second = np.zeros(3, dtype=float)
    second[winner_index] = -1.0

    return _linear_gaussian_cdf(
        np.vstack([first, second]),
        np.array(
            [0.0, -candidate_threshold],
            dtype=float,
        ),
        correlation_matrix,
    )


def _incremental_cumulative_direct(
    winner_upper: float,
    added_threshold: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    loser_index = 1 - winner_index

    loser_minus_winner = np.zeros(
        3,
        dtype=float,
    )
    loser_minus_winner[loser_index] = 1.0
    loser_minus_winner[winner_index] = -1.0

    winner = np.zeros(3, dtype=float)
    winner[winner_index] = 1.0

    minus_added = np.zeros(3, dtype=float)
    minus_added[2] = -1.0

    winner_minus_added = np.zeros(
        3,
        dtype=float,
    )
    winner_minus_added[winner_index] = 1.0
    winner_minus_added[2] = -1.0

    if winner_upper <= added_threshold:
        return _linear_gaussian_cdf(
            np.vstack(
                [
                    loser_minus_winner,
                    winner,
                    minus_added,
                ]
            ),
            np.array(
                [
                    0.0,
                    winner_upper,
                    -added_threshold,
                ],
                dtype=float,
            ),
            correlation_matrix,
        )

    below_added = _linear_gaussian_cdf(
        np.vstack(
            [
                loser_minus_winner,
                winner,
                minus_added,
            ]
        ),
        np.array(
            [
                0.0,
                added_threshold,
                -added_threshold,
            ],
            dtype=float,
        ),
        correlation_matrix,
    )
    moving_upper = _linear_gaussian_cdf(
        np.vstack(
            [
                loser_minus_winner,
                winner,
                winner_minus_added,
            ]
        ),
        np.array(
            [
                0.0,
                winner_upper,
                0.0,
            ],
            dtype=float,
        ),
        correlation_matrix,
    )
    moving_lower = _linear_gaussian_cdf(
        np.vstack(
            [
                loser_minus_winner,
                winner,
                winner_minus_added,
            ]
        ),
        np.array(
            [
                0.0,
                added_threshold,
                0.0,
            ],
            dtype=float,
        ),
        correlation_matrix,
    )
    return float(
        below_added
        + moving_upper
        - moving_lower
    )


def policy_population_probabilities(
    thresholds: FloatArray,
    correlation_matrix: FloatArray,
) -> dict[str, float]:
    theta = np.asarray(
        thresholds,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    if theta.shape != (4,):
        raise ValueError(
            "thresholds must have shape (4,)"
        )
    if correlation.shape != (3, 3):
        raise ValueError(
            "correlation_matrix must have shape (3,3)"
        )

    q0, q1, q2, trigger = map(float, theta)

    base_parts = [
        _base_reject_cell_probability_direct(
            q0,
            0,
            correlation,
        ),
        _base_reject_cell_probability_direct(
            q1,
            1,
            correlation,
        ),
    ]
    incremental_parts = [
        _incremental_cumulative_direct(
            q0,
            q2,
            0,
            correlation,
        ),
        _incremental_cumulative_direct(
            q1,
            q2,
            1,
            correlation,
        ),
    ]
    joint_parts = [
        (
            _incremental_cumulative_direct(
                q0,
                q2,
                0,
                correlation,
            )
            - _incremental_cumulative_direct(
                trigger,
                q2,
                0,
                correlation,
            )
            if q0 > trigger
            else 0.0
        ),
        (
            _incremental_cumulative_direct(
                q1,
                q2,
                1,
                correlation,
            )
            - _incremental_cumulative_direct(
                trigger,
                q2,
                1,
                correlation,
            )
            if q1 > trigger
            else 0.0
        ),
    ]

    base_probability = float(sum(base_parts))
    activation_probability = float(
        1.0
        - bvn_cdf(
            trigger,
            trigger,
            float(correlation[0, 1]),
        )
    )
    incremental_probability = float(
        sum(incremental_parts)
    )
    joint_am_probability = float(
        sum(joint_parts)
    )
    adaptive_probability = float(
        base_probability
        + joint_am_probability
    )
    comparator_probability = float(
        base_probability
        + activation_probability
        * incremental_probability
    )
    delta = float(
        adaptive_probability
        - comparator_probability
    )

    return {
        "base_probability": base_probability,
        "activation_probability": activation_probability,
        "incremental_probability": incremental_probability,
        "joint_am_probability": joint_am_probability,
        "adaptive_probability": adaptive_probability,
        "comparator_probability": comparator_probability,
        "delta_pi": delta,
        "base_parts": base_parts,
        "incremental_parts": incremental_parts,
        "joint_parts": joint_parts,
    }

# ---------------------------------------------------------------------------
# Deterministic Gaussian-probability backend candidate.
# The fixed-RNG Genz backend is retained as a named legacy diagnostic.
# ---------------------------------------------------------------------------

_genz_linear_gaussian_cdf_legacy = (
    _linear_gaussian_cdf
)
_genz_bvn_cdf_legacy = bvn_cdf
_genz_mvn3_cdf_legacy = mvn3_cdf

from d8a_deterministic_gaussian import (  # noqa: E402
    bvn_cdf as bvn_cdf,
    linear_gaussian_cdf as _linear_gaussian_cdf,
    mvn3_cdf as mvn3_cdf,
)
