from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class D7Pools:
    base: tuple[int, ...]
    full: tuple[int, ...]


@dataclass(frozen=True)
class D7PolicyState:
    base_winner: IntArray
    full_winner: IntArray
    base_maximum: FloatArray
    base_reject: BoolArray
    full_reject: BoolArray
    activation: BoolArray
    incremental: BoolArray
    adaptive_reject: BoolArray


@dataclass(frozen=True)
class D7ContrastSummary:
    e0: float
    rho: float
    mu: float
    nu: float
    pi_adaptive: float
    pi_comparator: float
    delta_pi: float


@dataclass(frozen=True)
class D7Separation:
    differences: FloatArray
    minimum_absolute_separation: float
    separated: bool


def _score_matrix(scores: ArrayLike) -> FloatArray:
    matrix = np.asarray(scores, dtype=float)
    if matrix.ndim != 2:
        raise ValueError("scores must be a two-dimensional array")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("scores must be nonempty")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("D7 requires finite candidate scores")
    return matrix


def _vector(values: ArrayLike, length: int, label: str) -> FloatArray:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (length,):
        raise ValueError(f"{label} must have shape ({length},)")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{label} must be finite")
    return vector


def _pool(
    indices: Iterable[int],
    candidate_count: int,
    label: str,
) -> tuple[int, ...]:
    pool = tuple(int(index) for index in indices)
    if not pool:
        raise ValueError(f"{label} must be nonempty")
    if len(set(pool)) != len(pool):
        raise ValueError(f"{label} contains duplicate candidate indices")
    if any(index < 0 or index >= candidate_count for index in pool):
        raise ValueError(f"{label} contains an out-of-range candidate index")
    return pool


def validate_nested_pools(
    base_pool: Iterable[int],
    full_pool: Iterable[int],
    candidate_count: int,
) -> D7Pools:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    base = _pool(base_pool, candidate_count, "base_pool")
    full = _pool(full_pool, candidate_count, "full_pool")
    if not set(base).issubset(full):
        raise ValueError("base_pool must be a subset of full_pool")
    return D7Pools(base=base, full=full)


def winner_indices(
    scores: ArrayLike,
    pool: Iterable[int],
    *,
    require_unique: bool = True,
) -> IntArray:
    matrix = _score_matrix(scores)
    selected_pool = _pool(pool, matrix.shape[1], "pool")
    pool_array = np.asarray(selected_pool, dtype=np.int64)
    subset = matrix[:, pool_array]
    maxima = np.max(subset, axis=1)

    if require_unique:
        tie_counts = np.sum(subset == maxima[:, None], axis=1)
        tied_rows = np.flatnonzero(tie_counts != 1)
        if tied_rows.size:
            preview = ", ".join(map(str, tied_rows[:10]))
            raise ValueError(f"winner is not unique in row(s): {preview}")

    local = np.argmax(subset, axis=1)
    return pool_array[local]


def maximum_trigger_score(
    scores: ArrayLike,
    base_pool: Iterable[int],
) -> tuple[IntArray, FloatArray]:
    matrix = _score_matrix(scores)
    winners = winner_indices(matrix, base_pool)
    rows = np.arange(matrix.shape[0])
    maxima = matrix[rows, winners]
    return winners, maxima.astype(float)


def branch_rejection(
    scores: ArrayLike,
    winners: ArrayLike,
    thresholds: ArrayLike,
) -> BoolArray:
    matrix = _score_matrix(scores)
    winner_array = np.asarray(winners, dtype=np.int64)
    if winner_array.shape != (matrix.shape[0],):
        raise ValueError("winners must have one entry per score row")
    if np.any(winner_array < 0) or np.any(
        winner_array >= matrix.shape[1]
    ):
        raise ValueError("winners contains an out-of-range candidate index")
    threshold_array = _vector(
        thresholds,
        matrix.shape[1],
        "thresholds",
    )
    rows = np.arange(matrix.shape[0])
    return matrix[rows, winner_array] > threshold_array[winner_array]


def generalized_inverse_quantile(
    values: ArrayLike,
    probability: float,
) -> float:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(vector)):
        raise ValueError("values must be finite")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    ordered = np.sort(vector)
    index = int(np.ceil(vector.size * probability)) - 1
    index = min(max(index, 0), vector.size - 1)
    return float(ordered[index])


def maximum_trigger_quantile(
    scores: ArrayLike,
    base_pool: Iterable[int],
    probability: float,
) -> float:
    _, maxima = maximum_trigger_score(scores, base_pool)
    return generalized_inverse_quantile(maxima, probability)


def threshold_separation(
    candidate_thresholds: ArrayLike,
    trigger_threshold: float,
    base_pool: Iterable[int],
    *,
    tolerance: float = 0.0,
) -> D7Separation:
    thresholds = np.asarray(candidate_thresholds, dtype=float)
    if thresholds.ndim != 1 or thresholds.size == 0:
        raise ValueError(
            "candidate_thresholds must be a nonempty one-dimensional array"
        )
    if not np.all(np.isfinite(thresholds)):
        raise ValueError("candidate_thresholds must be finite")
    if not np.isfinite(trigger_threshold):
        raise ValueError("trigger_threshold must be finite")
    if tolerance < 0.0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be nonnegative and finite")

    base = _pool(base_pool, thresholds.size, "base_pool")
    differences = (
        thresholds[np.asarray(base, dtype=np.int64)]
        - float(trigger_threshold)
    )
    minimum = float(np.min(np.abs(differences)))
    return D7Separation(
        differences=differences.astype(float),
        minimum_absolute_separation=minimum,
        separated=bool(minimum > tolerance),
    )


def policy_state(
    scores: ArrayLike,
    thresholds: ArrayLike,
    base_pool: Iterable[int],
    full_pool: Iterable[int],
    trigger_threshold: float,
) -> D7PolicyState:
    matrix = _score_matrix(scores)
    pools = validate_nested_pools(
        base_pool,
        full_pool,
        matrix.shape[1],
    )
    threshold_array = _vector(
        thresholds,
        matrix.shape[1],
        "thresholds",
    )
    if not np.isfinite(trigger_threshold):
        raise ValueError("trigger_threshold must be finite")

    base_winner, base_maximum = maximum_trigger_score(
        matrix,
        pools.base,
    )
    full_winner = winner_indices(matrix, pools.full)
    base_reject = branch_rejection(
        matrix,
        base_winner,
        threshold_array,
    )
    full_reject = branch_rejection(
        matrix,
        full_winner,
        threshold_array,
    )
    activation = base_maximum > float(trigger_threshold)
    incremental = (~base_reject) & full_reject
    adaptive_reject = base_reject | (activation & incremental)

    return D7PolicyState(
        base_winner=base_winner,
        full_winner=full_winner,
        base_maximum=base_maximum,
        base_reject=base_reject,
        full_reject=full_reject,
        activation=activation,
        incremental=incremental,
        adaptive_reject=adaptive_reject,
    )


def contrast_summary(state: D7PolicyState) -> D7ContrastSummary:
    r0 = state.base_reject.astype(float)
    a = state.activation.astype(float)
    m = state.incremental.astype(float)

    e0 = float(np.mean(r0))
    rho = float(np.mean(a))
    mu = float(np.mean(m))
    nu = float(np.mean(a * m))
    pi_adaptive = float(np.mean(state.adaptive_reject))
    pi_comparator = float(e0 + rho * mu)
    delta_pi = float(pi_adaptive - pi_comparator)

    covariance_identity = float(nu - rho * mu)
    if not np.isclose(
        delta_pi,
        covariance_identity,
        atol=1e-15,
        rtol=0.0,
    ):
        raise RuntimeError("contrast covariance identity failed")

    return D7ContrastSummary(
        e0=e0,
        rho=rho,
        mu=mu,
        nu=nu,
        pi_adaptive=pi_adaptive,
        pi_comparator=pi_comparator,
        delta_pi=delta_pi,
    )


def evaluation_influence_contrast(
    state: D7PolicyState,
    summary: D7ContrastSummary | None = None,
) -> FloatArray:
    target = summary if summary is not None else contrast_summary(state)
    a = state.activation.astype(float)
    m = state.incremental.astype(float)
    return (
        (a - target.rho) * (m - target.mu)
        - target.delta_pi
    )


def candidate_threshold_jump_field(
    state: D7PolicyState,
    candidate: int,
    base_pool: Iterable[int],
    full_pool: Iterable[int],
) -> IntArray:
    base_tuple = tuple(int(index) for index in base_pool)
    full_tuple = tuple(int(index) for index in full_pool)
    if not full_tuple:
        raise ValueError("full_pool must be nonempty")
    candidate_count = max(full_tuple) + 1
    pools = validate_nested_pools(
        base_tuple,
        full_tuple,
        candidate_count,
    )
    if candidate not in pools.full:
        raise ValueError("candidate must belong to full_pool")

    base_wins = state.base_winner == candidate
    full_wins = state.full_winner == candidate
    positive = (
        (candidate in pools.base)
        & base_wins
        & (~full_wins)
        & state.full_reject
    )
    negative = (
        (candidate not in pools.base)
        & full_wins
        & (~state.base_reject)
    )
    return positive.astype(np.int64) - negative.astype(np.int64)


def coincidence_relevance_field(
    state: D7PolicyState,
    candidate: int,
    base_pool: Iterable[int],
) -> BoolArray:
    base_tuple = tuple(int(index) for index in base_pool)
    if candidate not in base_tuple:
        raise ValueError(
            "coincidence candidate must belong to the base pool"
        )
    return (
        (state.base_winner == candidate)
        & (state.full_winner != candidate)
        & state.full_reject
    )


def positive_part(value: float) -> float:
    if not np.isfinite(value):
        raise ValueError("value must be finite")
    return float(max(value, 0.0))


def coincidence_directional_term(
    kappa: float,
    candidate_direction: float,
    trigger_direction: float,
) -> float:
    if not np.isfinite(kappa) or kappa < 0.0:
        raise ValueError("kappa must be nonnegative and finite")
    if not np.isfinite(candidate_direction):
        raise ValueError("candidate_direction must be finite")
    if not np.isfinite(trigger_direction):
        raise ValueError("trigger_direction must be finite")
    return float(
        kappa
        * positive_part(candidate_direction - trigger_direction)
    )


def complete_replication_resample(
    scores: ArrayLike,
    indices: ArrayLike,
) -> FloatArray:
    matrix = _score_matrix(scores)
    index_array = np.asarray(indices, dtype=np.int64)
    if index_array.ndim != 1:
        raise ValueError("indices must be one-dimensional")
    if np.any(index_array < 0) or np.any(
        index_array >= matrix.shape[0]
    ):
        raise ValueError("indices contains an out-of-range row")
    return matrix[index_array, :].copy()
