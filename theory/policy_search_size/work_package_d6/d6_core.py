from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class D6Pools:
    base: tuple[int, ...]
    full: tuple[int, ...]


@dataclass(frozen=True)
class D6PolicyState:
    base_winner: IntArray
    full_winner: IntArray
    base_reject: BoolArray
    full_reject: BoolArray
    activation: BoolArray
    incremental: BoolArray
    adaptive_reject: BoolArray


@dataclass(frozen=True)
class D6ContrastSummary:
    e0: float
    rho: float
    mu: float
    nu: float
    pi_adaptive: float
    pi_comparator: float
    delta_pi: float


def _score_matrix(scores: ArrayLike) -> FloatArray:
    matrix = np.asarray(scores, dtype=float)
    if matrix.ndim != 2:
        raise ValueError("scores must be a two-dimensional array")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("scores must be nonempty")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("D6 requires finite candidate scores")
    return matrix


def _vector(values: ArrayLike, length: int, label: str) -> FloatArray:
    vector = np.asarray(values, dtype=float)
    if vector.shape != (length,):
        raise ValueError(f"{label} must have shape ({length},)")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{label} must be finite")
    return vector


def _pool(indices: Iterable[int], candidate_count: int, label: str) -> tuple[int, ...]:
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
) -> D6Pools:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    base = _pool(base_pool, candidate_count, "base_pool")
    full = _pool(full_pool, candidate_count, "full_pool")
    if not set(base).issubset(full):
        raise ValueError("base_pool must be a subset of full_pool")
    return D6Pools(base=base, full=full)


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


def branch_rejection(
    scores: ArrayLike,
    winners: ArrayLike,
    thresholds: ArrayLike,
) -> BoolArray:
    matrix = _score_matrix(scores)
    winner_array = np.asarray(winners, dtype=np.int64)
    if winner_array.shape != (matrix.shape[0],):
        raise ValueError("winners must have one entry per score row")
    if np.any(winner_array < 0) or np.any(winner_array >= matrix.shape[1]):
        raise ValueError("winners contains an out-of-range candidate index")
    threshold_array = _vector(thresholds, matrix.shape[1], "thresholds")
    rows = np.arange(matrix.shape[0])
    return matrix[rows, winner_array] > threshold_array[winner_array]


def policy_state(
    scores: ArrayLike,
    activation_score: ArrayLike,
    thresholds: ArrayLike,
    base_pool: Iterable[int],
    full_pool: Iterable[int],
    activation_threshold: float,
) -> D6PolicyState:
    matrix = _score_matrix(scores)
    pools = validate_nested_pools(base_pool, full_pool, matrix.shape[1])
    activation_values = _vector(
        activation_score,
        matrix.shape[0],
        "activation_score",
    )
    threshold_array = _vector(thresholds, matrix.shape[1], "thresholds")
    if not np.isfinite(activation_threshold):
        raise ValueError("activation_threshold must be finite")

    base_winner = winner_indices(matrix, pools.base)
    full_winner = winner_indices(matrix, pools.full)
    base_reject = branch_rejection(matrix, base_winner, threshold_array)
    full_reject = branch_rejection(matrix, full_winner, threshold_array)
    activation = activation_values > float(activation_threshold)
    incremental = (~base_reject) & full_reject
    adaptive_reject = base_reject | (activation & incremental)

    return D6PolicyState(
        base_winner=base_winner,
        full_winner=full_winner,
        base_reject=base_reject,
        full_reject=full_reject,
        activation=activation,
        incremental=incremental,
        adaptive_reject=adaptive_reject,
    )


def contrast_summary(state: D6PolicyState) -> D6ContrastSummary:
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
    if not np.isclose(delta_pi, covariance_identity, atol=1e-15, rtol=0.0):
        raise RuntimeError("contrast covariance identity failed")

    return D6ContrastSummary(
        e0=e0,
        rho=rho,
        mu=mu,
        nu=nu,
        pi_adaptive=pi_adaptive,
        pi_comparator=pi_comparator,
        delta_pi=delta_pi,
    )


def evaluation_influence_contrast(
    state: D6PolicyState,
    summary: D6ContrastSummary | None = None,
) -> FloatArray:
    target = summary if summary is not None else contrast_summary(state)
    a = state.activation.astype(float)
    m = state.incremental.astype(float)
    return (a - target.rho) * (m - target.mu) - target.delta_pi


def candidate_threshold_jump_field(
    state: D6PolicyState,
    candidate: int,
    base_pool: Iterable[int],
    full_pool: Iterable[int],
) -> IntArray:
    base_tuple = tuple(int(index) for index in base_pool)
    full_tuple = tuple(int(index) for index in full_pool)
    if not full_tuple:
        raise ValueError("full_pool must be nonempty")
    candidate_count = max(full_tuple) + 1
    pools = validate_nested_pools(base_tuple, full_tuple, candidate_count)
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


def direct_incremental_threshold_jump(
    score_row: ArrayLike,
    thresholds: ArrayLike,
    base_pool: Iterable[int],
    full_pool: Iterable[int],
    candidate: int,
    *,
    epsilon: float = 1e-8,
) -> int:
    row = np.asarray(score_row, dtype=float)
    if row.ndim != 1 or row.size == 0:
        raise ValueError("score_row must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(row)):
        raise ValueError("score_row must be finite")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive and finite")

    pools = validate_nested_pools(base_pool, full_pool, row.size)
    if candidate not in pools.full:
        raise ValueError("candidate must belong to full_pool")
    threshold_array = _vector(thresholds, row.size, "thresholds")
    base_winner = int(winner_indices(row[None, :], pools.base)[0])
    full_winner = int(winner_indices(row[None, :], pools.full)[0])

    def incremental(q: FloatArray) -> int:
        r0 = int(row[base_winner] > q[base_winner])
        r1 = int(row[full_winner] > q[full_winner])
        return int((1 - r0) * r1)

    below = threshold_array.copy()
    above = threshold_array.copy()
    below[candidate] = row[candidate] - epsilon
    above[candidate] = row[candidate] + epsilon
    return incremental(above) - incremental(below)


def tess_transform(rejection_probability: float, alpha: float) -> float:
    if not 0.0 <= rejection_probability < 1.0:
        raise ValueError("rejection_probability must lie in [0, 1)")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return float(np.log1p(-rejection_probability) / np.log1p(-alpha))


def tess_derivative(rejection_probability: float, alpha: float) -> float:
    if not 0.0 <= rejection_probability < 1.0:
        raise ValueError("rejection_probability must lie in [0, 1)")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    return float(
        -1.0
        / ((1.0 - rejection_probability) * np.log1p(-alpha))
    )


def complete_replication_resample(
    scores: ArrayLike,
    activation_score: ArrayLike,
    indices: ArrayLike,
) -> tuple[FloatArray, FloatArray]:
    matrix = _score_matrix(scores)
    activation_values = _vector(
        activation_score,
        matrix.shape[0],
        "activation_score",
    )
    index_array = np.asarray(indices, dtype=np.int64)
    if index_array.ndim != 1:
        raise ValueError("indices must be one-dimensional")
    if np.any(index_array < 0) or np.any(index_array >= matrix.shape[0]):
        raise ValueError("indices contains an out-of-range row")
    return matrix[index_array, :].copy(), activation_values[index_array].copy()
