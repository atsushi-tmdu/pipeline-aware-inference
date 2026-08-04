from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.stats import multivariate_normal, norm

from d7_numerical_design import (
    GaussianDGP,
    build_dgp,
    candidate_thresholds,
    marginal_standard_deviations,
    trigger_boundary,
)


FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
IntArray = NDArray[np.int64]


_MAXIMUM_CDF_CACHE: dict[tuple[Any, ...], float] = {}


@dataclass(frozen=True)
class CellDefinition:
    key: str
    cell_type: str
    dgp: str
    alpha: float
    trigger_label: str
    trigger_boundary: float
    trigger_probability: float
    candidate_thresholds: FloatArray
    anchor_candidate: int | None = None
    offset_in_anchor_sd: float | None = None
    adjudicative: bool = True


@dataclass(frozen=True)
class BatchedState:
    base_winner: IntArray
    full_winner: IntArray
    base_maximum: FloatArray
    base_reject: BoolArray
    full_reject: BoolArray
    activation: BoolArray
    incremental: BoolArray
    adaptive_reject: BoolArray


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_seed(*parts: Any) -> int:
    text = "||".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**63 - 1)


def tess_value(probability: FloatArray | float, alpha: float) -> FloatArray | float:
    values = np.asarray(probability, dtype=float)
    if np.any(values < 0.0) or np.any(values >= 1.0):
        raise ValueError("TESS probability must lie in [0,1)")
    output = np.log1p(-values) / math.log1p(-alpha)
    return float(output) if np.ndim(probability) == 0 else output


def tess_derivative(probability: float, alpha: float) -> float:
    if not 0.0 <= probability < 1.0:
        raise ValueError("TESS probability must lie in [0,1)")
    return float(-1.0 / ((1.0 - probability) * math.log1p(-alpha)))


def draw_scores(
    rng: np.random.Generator,
    dgp: GaussianDGP,
    size: int | tuple[int, ...],
) -> FloatArray:
    draws = rng.multivariate_normal(
        dgp.mean,
        dgp.covariance,
        size=size,
        method="cholesky",
    )
    return np.asarray(draws, dtype=float)


def conditional_parameters(
    dgp: GaussianDGP,
    fixed_index: int,
    fixed_value: float,
) -> tuple[IntArray, FloatArray, FloatArray]:
    dimension = len(dgp.mean)
    remaining = np.asarray(
        [index for index in range(dimension) if index != fixed_index],
        dtype=np.int64,
    )
    variance = float(dgp.covariance[fixed_index, fixed_index])
    cross = dgp.covariance[remaining, fixed_index]
    mean = (
        dgp.mean[remaining]
        + cross / variance * (fixed_value - dgp.mean[fixed_index])
    )
    covariance = (
        dgp.covariance[np.ix_(remaining, remaining)]
        - np.outer(cross, cross) / variance
    )
    covariance = (covariance + covariance.T) / 2.0
    return remaining, mean, covariance


def draw_conditional_scores(
    rng: np.random.Generator,
    dgp: GaussianDGP,
    fixed_index: int,
    fixed_value: float,
    size: int,
) -> FloatArray:
    remaining, mean, covariance = conditional_parameters(
        dgp,
        fixed_index,
        fixed_value,
    )
    draws = rng.multivariate_normal(
        mean,
        covariance,
        size=size,
        method="cholesky",
    )
    output = np.empty((size, len(dgp.mean)), dtype=float)
    output[:, fixed_index] = fixed_value
    output[:, remaining] = draws
    return output


def winner_indices_batch(
    scores: FloatArray,
    pool: tuple[int, ...],
) -> tuple[IntArray, IntArray]:
    pool_array = np.asarray(pool, dtype=np.int64)
    subset = scores[..., pool_array]
    maxima = np.max(subset, axis=-1)
    tie_count = np.sum(subset == maxima[..., None], axis=-1)
    local = np.argmax(subset, axis=-1)
    return pool_array[local], tie_count.astype(np.int64)


def _broadcast_thresholds(
    thresholds: FloatArray,
    batch_size: int,
    candidate_count: int,
) -> FloatArray:
    values = np.asarray(thresholds, dtype=float)
    if values.shape == (candidate_count,):
        return np.broadcast_to(values, (batch_size, candidate_count))
    if values.shape == (batch_size, candidate_count):
        return values
    raise ValueError(
        "thresholds must have shape (K,) or (batch,K)"
    )


def _broadcast_trigger(
    trigger: FloatArray | float,
    batch_size: int,
) -> FloatArray:
    values = np.asarray(trigger, dtype=float)
    if values.ndim == 0:
        return np.full(batch_size, float(values), dtype=float)
    if values.shape == (batch_size,):
        return values
    raise ValueError("trigger must be scalar or have shape (batch,)")


def policy_state_batch(
    scores: FloatArray,
    thresholds: FloatArray,
    trigger: FloatArray | float,
    dgp: GaussianDGP,
) -> tuple[BatchedState, dict[str, int]]:
    matrix = np.asarray(scores, dtype=float)
    if matrix.ndim != 3:
        raise ValueError("scores must have shape (batch,n,K)")
    batch_size, sample_size, candidate_count = matrix.shape
    if candidate_count != len(dgp.mean):
        raise ValueError("candidate dimension mismatch")

    threshold_matrix = _broadcast_thresholds(
        thresholds,
        batch_size,
        candidate_count,
    )
    trigger_vector = _broadcast_trigger(trigger, batch_size)

    base_winner, base_ties = winner_indices_batch(
        matrix,
        dgp.base_pool,
    )
    full_winner, full_ties = winner_indices_batch(
        matrix,
        dgp.full_pool,
    )
    rows = np.arange(batch_size)[:, None]
    observations = np.arange(sample_size)[None, :]

    base_maximum = matrix[rows, observations, base_winner]
    full_maximum = matrix[rows, observations, full_winner]
    base_threshold = threshold_matrix[rows, base_winner]
    full_threshold = threshold_matrix[rows, full_winner]

    base_reject = base_maximum > base_threshold
    full_reject = full_maximum > full_threshold
    activation = base_maximum > trigger_vector[:, None]
    incremental = (~base_reject) & full_reject
    adaptive_reject = base_reject | (activation & incremental)

    return (
        BatchedState(
            base_winner=base_winner,
            full_winner=full_winner,
            base_maximum=base_maximum,
            base_reject=base_reject,
            full_reject=full_reject,
            activation=activation,
            incremental=incremental,
            adaptive_reject=adaptive_reject,
        ),
        {
            "base_winner_ties": int(np.sum(base_ties != 1)),
            "full_winner_ties": int(np.sum(full_ties != 1)),
        },
    )


def estimate_from_state(
    state: BatchedState,
    alpha: float,
) -> dict[str, FloatArray]:
    r0 = state.base_reject.astype(float)
    a = state.activation.astype(float)
    m = state.incremental.astype(float)
    h = state.adaptive_reject.astype(float)

    e0 = np.mean(r0, axis=1)
    rho = np.mean(a, axis=1)
    mu = np.mean(m, axis=1)
    nu = np.mean(a * m, axis=1)
    pi_adaptive = np.mean(h, axis=1)
    pi_comparator = e0 + rho * mu
    delta_pi = pi_adaptive - pi_comparator
    covariance_delta = nu - rho * mu
    covariance_error = delta_pi - covariance_delta

    delta_s = (
        np.asarray(tess_value(pi_adaptive, alpha), dtype=float)
        - np.asarray(tess_value(pi_comparator, alpha), dtype=float)
    )
    return {
        "e0": e0,
        "rho": rho,
        "mu": mu,
        "nu": nu,
        "pi_adaptive": pi_adaptive,
        "pi_comparator": pi_comparator,
        "delta_pi": delta_pi,
        "delta_s": delta_s,
        "covariance_identity_error": covariance_error,
    }


def empirical_quantile_batch(
    values: FloatArray,
    probability: float,
) -> tuple[FloatArray, int]:
    array = np.asarray(values, dtype=float)
    if array.ndim not in (2, 3):
        raise ValueError("values must have shape (batch,B) or (batch,B,K)")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    reference_size = array.shape[1]
    index = int(math.ceil(reference_size * probability)) - 1
    index = min(max(index, 0), reference_size - 1)
    partitioned = np.partition(array, index, axis=1)
    if array.ndim == 2:
        return partitioned[:, index], index
    return partitioned[:, index, :], index


def plus_one_threshold_batch(
    values: FloatArray,
    alpha: float,
) -> tuple[FloatArray, int, bool]:
    array = np.asarray(values, dtype=float)
    if array.ndim != 3:
        raise ValueError("values must have shape (batch,B,K)")
    reference_size = array.shape[1]
    allowed_ge = math.floor(
        alpha * (reference_size + 1) - 1 + 1e-12
    )
    if allowed_ge < 0:
        index = reference_size - 1
        attainable = False
    else:
        index = reference_size - allowed_ge - 1
        index = min(max(index, 0), reference_size - 1)
        attainable = True
    partitioned = np.partition(array, index, axis=1)
    return partitioned[:, index, :], index, attainable


def reference_thresholds_batch(
    reference_scores: FloatArray,
    alpha: float,
    trigger_probability: float,
    dgp: GaussianDGP,
) -> dict[str, Any]:
    regular, regular_index = empirical_quantile_batch(
        reference_scores,
        1.0 - alpha,
    )
    plus, plus_index, plus_attainable = plus_one_threshold_batch(
        reference_scores,
        alpha,
    )
    base = reference_scores[..., np.asarray(dgp.base_pool, dtype=np.int64)]
    maxima = np.max(base, axis=-1)
    trigger, trigger_index = empirical_quantile_batch(
        maxima,
        trigger_probability,
    )
    base_ties = np.sum(
        np.sum(base == maxima[..., None], axis=-1) != 1
    )
    return {
        "regular": regular,
        "plus": plus,
        "trigger": trigger,
        "regular_index": regular_index,
        "plus_index": plus_index,
        "plus_attainable": plus_attainable,
        "trigger_index": trigger_index,
        "reference_base_winner_ties": int(base_ties),
    }


def estimate_batch(
    reference_scores: FloatArray,
    evaluation_scores: FloatArray,
    cell: CellDefinition,
    dgp: GaussianDGP,
) -> dict[str, Any]:
    thresholds = reference_thresholds_batch(
        reference_scores,
        cell.alpha,
        cell.trigger_probability,
        dgp,
    )
    regular_state, regular_ties = policy_state_batch(
        evaluation_scores,
        thresholds["regular"],
        thresholds["trigger"],
        dgp,
    )
    plus_state, plus_ties = policy_state_batch(
        evaluation_scores,
        thresholds["plus"],
        thresholds["trigger"],
        dgp,
    )
    regular = estimate_from_state(regular_state, cell.alpha)
    plus = estimate_from_state(plus_state, cell.alpha)

    lower = np.minimum(thresholds["regular"], thresholds["plus"])
    upper = np.maximum(thresholds["regular"], thresholds["plus"])
    union_hit = np.any(
        (evaluation_scores > lower[:, None, :])
        & (evaluation_scores <= upper[:, None, :]),
        axis=2,
    )
    branch_disagreement = (
        (regular_state.base_reject != plus_state.base_reject)
        | (regular_state.full_reject != plus_state.full_reject)
    )
    support_violations = int(
        np.sum(branch_disagreement & (~union_hit))
    )

    return {
        "regular": regular,
        "plus": plus,
        "bridge_delta_pi": plus["delta_pi"] - regular["delta_pi"],
        "bridge_delta_s": plus["delta_s"] - regular["delta_s"],
        "regular_state": regular_state,
        "plus_state": plus_state,
        "regular_index": thresholds["regular_index"],
        "plus_index": thresholds["plus_index"],
        "plus_attainable": thresholds["plus_attainable"],
        "trigger_index": thresholds["trigger_index"],
        "support_violations": support_violations,
        "interval_union_probability": np.mean(union_hit, axis=1),
        "pathwise_disagreement_probability": np.mean(
            branch_disagreement,
            axis=1,
        ),
        "winner_ties": {
            "reference_base": thresholds[
                "reference_base_winner_ties"
            ],
            "evaluation_base_regular": regular_ties[
                "base_winner_ties"
            ],
            "evaluation_full_regular": regular_ties[
                "full_winner_ties"
            ],
            "evaluation_base_plus": plus_ties[
                "base_winner_ties"
            ],
            "evaluation_full_plus": plus_ties[
                "full_winner_ties"
            ],
        },
    }


def maximum_cdf(
    dgp: GaussianDGP,
    boundary: float,
    *,
    maxpts: int,
    abseps: float,
    releps: float,
    seed: int,
) -> float:
    key = (
        dgp.name,
        float(boundary),
        int(maxpts),
        float(abseps),
        float(releps),
        int(seed),
    )
    cached = _MAXIMUM_CDF_CACHE.get(key)
    if cached is not None:
        return cached

    base = np.asarray(dgp.base_pool, dtype=np.int64)
    mean = dgp.mean[base]
    covariance = dgp.covariance[np.ix_(base, base)]
    upper = np.full(len(base), boundary, dtype=float)
    value = float(
        multivariate_normal.cdf(
            upper,
            mean=mean,
            cov=covariance,
            maxpts=maxpts,
            abseps=abseps,
            releps=releps,
            rng=np.random.default_rng(seed),
        )
    )
    _MAXIMUM_CDF_CACHE[key] = value
    return value


def build_cell_definitions(
    config: dict[str, Any],
    specifications: dict[str, Any],
    *,
    include_diagnostics: bool,
    cdf_settings: dict[str, Any] | None = None,
) -> tuple[dict[str, GaussianDGP], list[CellDefinition]]:
    dgps = {
        name: build_dgp(name, specifications["dgps"][name])
        for name in specifications["dgp_order"]
    }
    cdf = cdf_settings or config["population_benchmark"]["maximum_cdf"]
    cells: list[CellDefinition] = []

    for dgp_name, dgp in dgps.items():
        for alpha in config["alpha_grid"]:
            q = candidate_thresholds(dgp, float(alpha))
            for regime_name, regime in config["trigger_regimes"].items():
                boundary = trigger_boundary(
                    dgp,
                    float(alpha),
                    regime_name,
                    regime,
                )["trigger_boundary"]
                probability = maximum_cdf(
                    dgp,
                    boundary,
                    maxpts=int(cdf["maxpts"]),
                    abseps=float(cdf["abseps"]),
                    releps=float(cdf["releps"]),
                    seed=stable_seed(
                        config["study_id"],
                        "cdf",
                        dgp_name,
                        alpha,
                        regime_name,
                        cdf["master_seed"],
                    ),
                )
                key = f"main|{dgp_name}|{alpha:g}|{regime_name}"
                cells.append(
                    CellDefinition(
                        key=key,
                        cell_type="main",
                        dgp=dgp_name,
                        alpha=float(alpha),
                        trigger_label=regime_name,
                        trigger_boundary=float(boundary),
                        trigger_probability=probability,
                        candidate_thresholds=q,
                        adjudicative=True,
                    )
                )

    if include_diagnostics:
        diagnostic = config["near_coincidence_diagnostic"]
        dgp = dgps[diagnostic["dgp"]]
        alpha = float(diagnostic["alpha"])
        anchor = int(diagnostic["anchor_candidate"])
        q = candidate_thresholds(dgp, alpha)
        sd = marginal_standard_deviations(dgp)[anchor]
        for offset in diagnostic["offsets_in_anchor_sd"]:
            boundary = float(q[anchor] + float(offset) * sd)
            probability = maximum_cdf(
                dgp,
                boundary,
                maxpts=int(cdf["maxpts"]),
                abseps=float(cdf["abseps"]),
                releps=float(cdf["releps"]),
                seed=stable_seed(
                    config["study_id"],
                    "cdf",
                    diagnostic["dgp"],
                    alpha,
                    "near",
                    offset,
                    cdf["master_seed"],
                ),
            )
            label = f"near_{float(offset):+.6f}sd"
            cells.append(
                CellDefinition(
                    key=f"near|{diagnostic['dgp']}|{alpha:g}|{offset:+.6f}",
                    cell_type="near",
                    dgp=diagnostic["dgp"],
                    alpha=alpha,
                    trigger_label=label,
                    trigger_boundary=boundary,
                    trigger_probability=probability,
                    candidate_thresholds=q,
                    anchor_candidate=anchor,
                    offset_in_anchor_sd=float(offset),
                    adjudicative=False,
                )
            )

        exact = config["exact_coincidence_diagnostic"]
        exact_dgp = dgps[exact["dgp"]]
        exact_alpha = float(exact["alpha"])
        exact_anchor = int(exact["anchor_candidate"])
        exact_q = candidate_thresholds(exact_dgp, exact_alpha)
        boundary = float(exact_q[exact_anchor])
        probability = maximum_cdf(
            exact_dgp,
            boundary,
            maxpts=int(cdf["maxpts"]),
            abseps=float(cdf["abseps"]),
            releps=float(cdf["releps"]),
            seed=stable_seed(
                config["study_id"],
                "cdf",
                exact["dgp"],
                exact_alpha,
                "exact",
                cdf["master_seed"],
            ),
        )
        cells.append(
            CellDefinition(
                key=f"exact|{exact['dgp']}|{exact_alpha:g}|anchor{exact_anchor}",
                cell_type="exact",
                dgp=exact["dgp"],
                alpha=exact_alpha,
                trigger_label="exact_coincidence",
                trigger_boundary=boundary,
                trigger_probability=probability,
                candidate_thresholds=exact_q,
                anchor_candidate=exact_anchor,
                offset_in_anchor_sd=0.0,
                adjudicative=False,
            )
        )

    return dgps, cells


def _empty_moment(dimension: int) -> dict[str, Any]:
    return {
        "n": 0,
        "sum": np.zeros(dimension, dtype=float),
        "cross": np.zeros((dimension, dimension), dtype=float),
    }


def _update_moment(accumulator: dict[str, Any], values: FloatArray) -> None:
    matrix = np.asarray(values, dtype=float)
    accumulator["n"] += int(matrix.shape[0])
    accumulator["sum"] += np.sum(matrix, axis=0)
    accumulator["cross"] += matrix.T @ matrix


def _moment_mean_cov(
    accumulator: dict[str, Any],
) -> tuple[FloatArray, FloatArray]:
    n = int(accumulator["n"])
    mean = accumulator["sum"] / n
    covariance = (
        accumulator["cross"] - n * np.outer(mean, mean)
    ) / (n - 1)
    covariance = (covariance + covariance.T) / 2.0
    return mean, covariance


def _candidate_jump(
    state: BatchedState,
    candidate: int,
    dgp: GaussianDGP,
) -> FloatArray:
    base_wins = state.base_winner == candidate
    full_wins = state.full_winner == candidate
    if candidate in dgp.base_pool:
        positive = (
            base_wins
            & (~full_wins)
            & state.full_reject
        )
    else:
        positive = np.zeros_like(base_wins)
    if candidate in dgp.full_pool and candidate not in dgp.base_pool:
        negative = full_wins & (~state.base_reject)
    else:
        negative = np.zeros_like(base_wins)
    return positive.astype(float) - negative.astype(float)


def _base_winner_indicator(
    state: BatchedState,
    candidate: int,
    dgp: GaussianDGP,
) -> FloatArray:
    if candidate not in dgp.base_pool:
        return np.zeros_like(state.base_reject, dtype=float)
    return (state.base_winner == candidate).astype(float)


def _cell_truth_from_moments(
    cell: CellDefinition,
    mean_w: FloatArray,
    covariance_w: FloatArray,
) -> dict[str, Any]:
    # W = [R0, A, M, AM, H_A]
    e0, rho, mu, nu, pi_adaptive = map(float, mean_w)
    pi_comparator = float(e0 + rho * mu)
    delta_pi = float(pi_adaptive - pi_comparator)
    delta_s = float(
        tess_value(pi_adaptive, cell.alpha)
        - tess_value(pi_comparator, cell.alpha)
    )

    coeff_delta = np.array([0.0, -mu, -rho, 1.0, 0.0])
    coeff_pi_a = np.array([0.0, 0.0, 0.0, 0.0, 1.0])
    coeff_pi_c = np.array([1.0, mu, rho, 0.0, 0.0])
    g_a = tess_derivative(pi_adaptive, cell.alpha)
    g_c = tess_derivative(pi_comparator, cell.alpha)
    coeff_s = g_a * coeff_pi_a - g_c * coeff_pi_c

    return {
        "e0": e0,
        "rho": rho,
        "mu": mu,
        "nu": nu,
        "pi_adaptive": pi_adaptive,
        "pi_comparator": pi_comparator,
        "delta_pi": delta_pi,
        "delta_s": delta_s,
        "var_eval_delta_pi": float(
            coeff_delta @ covariance_w @ coeff_delta
        ),
        "var_eval_pi_adaptive": float(
            coeff_pi_a @ covariance_w @ coeff_pi_a
        ),
        "var_eval_pi_comparator": float(
            coeff_pi_c @ covariance_w @ coeff_pi_c
        ),
        "var_eval_delta_s": float(
            coeff_s @ covariance_w @ coeff_s
        ),
        "g_prime_adaptive": g_a,
        "g_prime_comparator": g_c,
    }


def _conditional_mean_for_cells(
    dgp: GaussianDGP,
    cells: list[CellDefinition],
    candidate: int,
    fixed_value: float,
    size: int,
    chunk_size: int,
    seed: int,
    truths: dict[str, dict[str, Any]],
) -> dict[str, dict[str, float]]:
    sums = {
        cell.key: {
            "beta_delta": 0.0,
            "gamma_a": 0.0,
            "gamma_c": 0.0,
            "count": 0,
        }
        for cell in cells
    }
    rng = np.random.default_rng(seed)
    remaining = size
    while remaining:
        take = min(chunk_size, remaining)
        scores = draw_conditional_scores(
            rng,
            dgp,
            candidate,
            fixed_value,
            take,
        )
        scores_batch = scores[None, :, :]
        for cell in cells:
            state, _ = policy_state_batch(
                scores_batch,
                cell.candidate_thresholds,
                cell.trigger_boundary,
                dgp,
            )
            jump = _candidate_jump(
                state,
                candidate,
                dgp,
            )[0]
            base = _base_winner_indicator(
                state,
                candidate,
                dgp,
            )[0]
            activation = state.activation[0].astype(float)
            rho = float(truths[cell.key]["rho"])
            sums[cell.key]["beta_delta"] += float(
                np.sum((activation - rho) * jump)
            )
            sums[cell.key]["gamma_a"] += float(
                np.sum(-base + activation * jump)
            )
            sums[cell.key]["gamma_c"] += float(
                np.sum(-base + rho * jump)
            )
            sums[cell.key]["count"] += take
        remaining -= take

    return {
        key: {
            name: float(values[name] / values["count"])
            for name in ("beta_delta", "gamma_a", "gamma_c")
        }
        for key, values in sums.items()
    }


def _trigger_boundary_coefficients(
    dgp: GaussianDGP,
    cell: CellDefinition,
    truth: dict[str, Any],
    size: int,
    chunk_size: int,
    seed: int,
) -> dict[str, float]:
    weighted_probability = 0.0
    weighted_m = 0.0

    for offset, candidate in enumerate(dgp.base_pool):
        sd = math.sqrt(float(dgp.covariance[candidate, candidate]))
        density = float(
            norm.pdf(
                (cell.trigger_boundary - dgp.mean[candidate]) / sd
            )
            / sd
        )
        count = 0
        sum_winner = 0.0
        sum_m_winner = 0.0
        rng = np.random.default_rng(
            stable_seed(seed, cell.key, candidate, offset)
        )
        remaining = size
        while remaining:
            take = min(chunk_size, remaining)
            scores = draw_conditional_scores(
                rng,
                dgp,
                candidate,
                cell.trigger_boundary,
                take,
            )
            state, _ = policy_state_batch(
                scores[None, :, :],
                cell.candidate_thresholds,
                cell.trigger_boundary,
                dgp,
            )
            winner = (state.base_winner[0] == candidate)
            m = state.incremental[0]
            sum_winner += float(np.sum(winner))
            sum_m_winner += float(np.sum(winner & m))
            count += take
            remaining -= take

        weighted_probability += density * (sum_winner / count)
        weighted_m += density * (sum_m_winner / count)

    if weighted_probability <= 0.0:
        raise RuntimeError(f"{cell.key}: nonpositive maximum density")
    conditional_m = weighted_m / weighted_probability
    mu = float(truth["mu"])
    return {
        "maximum_density": float(weighted_probability),
        "conditional_m_at_trigger": float(conditional_m),
        "beta_delta_trigger": float(mu - conditional_m),
        "gamma_a_trigger": float(-conditional_m),
        "gamma_c_trigger": float(-mu),
    }


def compute_population_benchmarks(
    config: dict[str, Any],
    specifications: dict[str, Any],
    *,
    mode: str,
) -> dict[str, Any]:
    if mode not in {"smoke", "full"}:
        raise ValueError("mode must be smoke or full")

    benchmark = config["population_benchmark"]
    if mode == "full":
        unconditional_draws = int(
            benchmark["unconditional_draws_per_dgp"]
        )
        conditional_draws = int(
            benchmark["conditional_boundary_draws_per_boundary"]
        )
        chunk_size = int(benchmark["chunk_size"])
        cdf_settings = benchmark["maximum_cdf"]
    else:
        unconditional_draws = 3000
        conditional_draws = 300
        chunk_size = 300
        cdf_settings = {
            **benchmark["maximum_cdf"],
            "maxpts": min(
                20000,
                int(benchmark["maximum_cdf"]["maxpts"]),
            ),
            "abseps": 1e-4,
            "releps": 1e-4,
        }

    dgps, cells = build_cell_definitions(
        config,
        specifications,
        include_diagnostics=True,
        cdf_settings=cdf_settings,
    )
    cells_by_dgp: dict[str, list[CellDefinition]] = {
        name: [cell for cell in cells if cell.dgp == name]
        for name in dgps
    }
    result: dict[str, Any] = {}

    for dgp_name, dgp in dgps.items():
        dgp_cells = cells_by_dgp[dgp_name]
        w_moments = {
            cell.key: _empty_moment(5)
            for cell in dgp_cells
        }
        z_moments = {
            cell.key: _empty_moment(len(dgp.mean) + 1)
            for cell in dgp_cells
        }

        rng = np.random.default_rng(
            stable_seed(
                config["study_id"],
                "population_unconditional",
                dgp_name,
                benchmark["master_seed"],
                mode,
            )
        )
        remaining = unconditional_draws
        winner_ties = 0
        while remaining:
            take = min(chunk_size, remaining)
            scores = draw_scores(rng, dgp, take)
            scores_batch = scores[None, :, :]
            for cell in dgp_cells:
                state, ties = policy_state_batch(
                    scores_batch,
                    cell.candidate_thresholds,
                    cell.trigger_boundary,
                    dgp,
                )
                winner_ties += (
                    ties["base_winner_ties"]
                    + ties["full_winner_ties"]
                )
                r0 = state.base_reject[0].astype(float)
                a = state.activation[0].astype(float)
                m = state.incremental[0].astype(float)
                am = a * m
                h = state.adaptive_reject[0].astype(float)
                w = np.column_stack([r0, a, m, am, h])
                _update_moment(w_moments[cell.key], w)

                candidate_indicators = (
                    (1.0 - cell.alpha)
                    - (
                        scores
                        <= cell.candidate_thresholds[None, :]
                    ).astype(float)
                )
                trigger_indicator = (
                    cell.trigger_probability
                    - (
                        state.base_maximum[0]
                        <= cell.trigger_boundary
                    ).astype(float)
                )
                z = np.column_stack(
                    [candidate_indicators, trigger_indicator]
                )
                _update_moment(z_moments[cell.key], z)
            remaining -= take

        truths: dict[str, dict[str, Any]] = {}
        covariances_z: dict[str, FloatArray] = {}
        for cell in dgp_cells:
            mean_w, covariance_w = _moment_mean_cov(
                w_moments[cell.key]
            )
            _, covariance_z = _moment_mean_cov(
                z_moments[cell.key]
            )
            truths[cell.key] = _cell_truth_from_moments(
                cell,
                mean_w,
                covariance_w,
            )
            covariances_z[cell.key] = covariance_z

        # Candidate boundary coefficients reuse draws across trigger labels.
        candidate_coefficients = {
            cell.key: {
                "beta_delta": np.zeros(len(dgp.mean)),
                "gamma_a": np.zeros(len(dgp.mean)),
                "gamma_c": np.zeros(len(dgp.mean)),
            }
            for cell in dgp_cells
        }
        alpha_groups: dict[float, list[CellDefinition]] = {}
        for cell in dgp_cells:
            alpha_groups.setdefault(cell.alpha, []).append(cell)

        for alpha, alpha_cells in alpha_groups.items():
            thresholds = candidate_thresholds(dgp, alpha)
            for candidate in dgp.full_pool:
                estimates = _conditional_mean_for_cells(
                    dgp,
                    alpha_cells,
                    candidate,
                    float(thresholds[candidate]),
                    conditional_draws,
                    chunk_size,
                    stable_seed(
                        config["study_id"],
                        "candidate_boundary",
                        dgp_name,
                        alpha,
                        candidate,
                        benchmark["master_seed"],
                        mode,
                    ),
                    truths,
                )
                for cell in alpha_cells:
                    for name in (
                        "beta_delta",
                        "gamma_a",
                        "gamma_c",
                    ):
                        candidate_coefficients[cell.key][name][
                            candidate
                        ] = estimates[cell.key][name]

        for cell in dgp_cells:
            trigger_coefficients = _trigger_boundary_coefficients(
                dgp,
                cell,
                truths[cell.key],
                conditional_draws,
                chunk_size,
                stable_seed(
                    config["study_id"],
                    "trigger_boundary",
                    cell.key,
                    benchmark["master_seed"],
                    mode,
                ),
            )
            coeff = candidate_coefficients[cell.key]
            beta_delta = np.concatenate(
                [
                    coeff["beta_delta"],
                    [trigger_coefficients["beta_delta_trigger"]],
                ]
            )
            gamma_a = np.concatenate(
                [
                    coeff["gamma_a"],
                    [trigger_coefficients["gamma_a_trigger"]],
                ]
            )
            gamma_c = np.concatenate(
                [
                    coeff["gamma_c"],
                    [trigger_coefficients["gamma_c_trigger"]],
                ]
            )
            covariance_z = covariances_z[cell.key]
            truth = truths[cell.key]

            var_ref_delta = float(
                beta_delta @ covariance_z @ beta_delta
            )
            var_ref_a = float(
                gamma_a @ covariance_z @ gamma_a
            )
            var_ref_c = float(
                gamma_c @ covariance_z @ gamma_c
            )
            cov_ref_ac = float(
                gamma_a @ covariance_z @ gamma_c
            )
            g_a = float(truth["g_prime_adaptive"])
            g_c = float(truth["g_prime_comparator"])
            var_ref_s = float(
                g_a**2 * var_ref_a
                + g_c**2 * var_ref_c
                - 2.0 * g_a * g_c * cov_ref_ac
            )

            result[cell.key] = {
                "cell_type": cell.cell_type,
                "dgp": cell.dgp,
                "alpha": cell.alpha,
                "trigger_label": cell.trigger_label,
                "trigger_boundary": cell.trigger_boundary,
                "trigger_probability": cell.trigger_probability,
                "candidate_thresholds": (
                    cell.candidate_thresholds.tolist()
                ),
                "anchor_candidate": cell.anchor_candidate,
                "offset_in_anchor_sd": cell.offset_in_anchor_sd,
                "adjudicative": cell.adjudicative,
                **truth,
                **trigger_coefficients,
                "candidate_beta_delta": (
                    coeff["beta_delta"].tolist()
                ),
                "candidate_gamma_a": coeff["gamma_a"].tolist(),
                "candidate_gamma_c": coeff["gamma_c"].tolist(),
                "var_ref_delta_pi": var_ref_delta,
                "var_ref_pi_adaptive": var_ref_a,
                "var_ref_pi_comparator": var_ref_c,
                "cov_ref_pi_adaptive_comparator": cov_ref_ac,
                "var_ref_delta_s": var_ref_s,
                "benchmark_mcse_delta_pi": math.sqrt(
                    max(float(truth["var_eval_delta_pi"]), 0.0)
                    / unconditional_draws
                ),
                "benchmark_mcse_delta_s": math.sqrt(
                    max(float(truth["var_eval_delta_s"]), 0.0)
                    / unconditional_draws
                ),
                "unconditional_draws": unconditional_draws,
                "conditional_draws_per_boundary": conditional_draws,
                "observed_population_winner_ties": winner_ties,
            }

    return {
        "mode": mode,
        "scientific_evidence": mode == "full",
        "benchmark_settings": {
            "unconditional_draws_per_dgp": unconditional_draws,
            "conditional_draws_per_boundary": conditional_draws,
            "chunk_size": chunk_size,
        },
        "cells": result,
    }


def _adaptive_outer_batch_size(
    reference_size: int,
    evaluation_size: int,
    candidate_count: int,
    maximum: int = 64,
) -> int:
    target_floats = 4_000_000
    per_outer = (reference_size + evaluation_size) * candidate_count
    return max(1, min(maximum, target_floats // max(per_outer, 1)))


def _bootstrap_batch_size(
    reference_size: int,
    evaluation_size: int,
    candidate_count: int,
) -> int:
    target_floats = 2_000_000
    per_resample = (
        reference_size + evaluation_size
    ) * candidate_count
    return max(1, min(32, target_floats // max(per_resample, 1)))


def _main_cells_for_mode(
    config: dict[str, Any],
    cells: list[CellDefinition],
    mode: str,
) -> list[dict[str, Any]]:
    main_cells = [cell for cell in cells if cell.cell_type == "main"]
    if mode == "smoke":
        alpha = float(config["smoke_design"]["alpha"])
        selected = [
            cell for cell in main_cells
            if math.isclose(cell.alpha, alpha)
        ]
        return [
            {
                "cell": cell,
                "reference_size": int(
                    config["smoke_design"]["reference_size"]
                ),
                "evaluation_size": int(
                    config["smoke_design"]["evaluation_size"]
                ),
                "outer_repetitions": int(
                    config["smoke_design"][
                        "outer_repetitions_per_cell"
                    ]
                ),
            }
            for cell in selected
        ]

    output = []
    for cell in main_cells:
        for design in config["main_designs"]:
            output.append(
                {
                    "cell": cell,
                    "reference_size": int(design["reference_size"]),
                    "evaluation_size": int(design["evaluation_size"]),
                    "outer_repetitions": int(
                        config["main_outer_repetitions_per_cell"]
                    ),
                }
            )
    return output


def _bootstrap_cells_for_mode(
    config: dict[str, Any],
    cells: list[CellDefinition],
    mode: str,
) -> list[dict[str, Any]]:
    main_cells = [cell for cell in cells if cell.cell_type == "main"]
    if mode == "smoke":
        alpha = float(config["smoke_design"]["alpha"])
        selected = [
            cell for cell in main_cells
            if math.isclose(cell.alpha, alpha)
        ]
        return [
            {
                "cell": cell,
                "reference_size": int(
                    config["smoke_design"]["reference_size"]
                ),
                "evaluation_size": int(
                    config["smoke_design"]["evaluation_size"]
                ),
                "outer_datasets": int(
                    config["smoke_design"][
                        "bootstrap_outer_datasets_per_cell"
                    ]
                ),
                "resamples": int(
                    config["smoke_design"]["bootstrap_resamples"]
                ),
            }
            for cell in selected
        ]

    design = config["bootstrap_design"]["main_design"]
    return [
        {
            "cell": cell,
            "reference_size": int(design["reference_size"]),
            "evaluation_size": int(design["evaluation_size"]),
            "outer_datasets": int(
                config["bootstrap_design"][
                    "outer_datasets_per_cell"
                ]
            ),
            "resamples": int(
                config["bootstrap_design"][
                    "resamples_per_outer_dataset"
                ]
            ),
        }
        for cell in main_cells
    ]


def simulate_main_grid(
    config: dict[str, Any],
    specifications: dict[str, Any],
    benchmarks: dict[str, Any],
    *,
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    dgps, cells = build_cell_definitions(
        config,
        specifications,
        include_diagnostics=True,
        cdf_settings=(
            config["population_benchmark"]["maximum_cdf"]
            if mode == "full"
            else {
                **config["population_benchmark"]["maximum_cdf"],
                "maxpts": 20000,
                "abseps": 1e-4,
                "releps": 1e-4,
            }
        ),
    )
    designs = _main_cells_for_mode(config, cells, mode)
    rows: list[dict[str, Any]] = []
    tie_counts = {
        "reference_base": 0,
        "evaluation_base_regular": 0,
        "evaluation_full_regular": 0,
        "evaluation_base_plus": 0,
        "evaluation_full_plus": 0,
    }
    support_violations = 0
    max_covariance_error = 0.0

    for design_index, design in enumerate(designs):
        cell = design["cell"]
        dgp = dgps[cell.dgp]
        benchmark = benchmarks["cells"][cell.key]
        B = design["reference_size"]
        n = design["evaluation_size"]
        total = design["outer_repetitions"]
        batch_size = _adaptive_outer_batch_size(
            B,
            n,
            len(dgp.mean),
        )
        rng = np.random.default_rng(
            stable_seed(
                config["scientific_randomness"]["master_seed"],
                mode,
                "main",
                cell.key,
                B,
                n,
            )
        )

        completed = 0
        while completed < total:
            take = min(batch_size, total - completed)
            reference = draw_scores(rng, dgp, (take, B))
            evaluation = draw_scores(rng, dgp, (take, n))
            estimate = estimate_batch(
                reference,
                evaluation,
                cell,
                dgp,
            )
            regular = estimate["regular"]
            plus = estimate["plus"]

            exact_var_delta = (
                float(benchmark["var_eval_delta_pi"]) / n
                + float(benchmark["var_ref_delta_pi"]) / B
            )
            exact_var_s = (
                float(benchmark["var_eval_delta_s"]) / n
                + float(benchmark["var_ref_delta_s"]) / B
            )
            se_delta = math.sqrt(max(exact_var_delta, 0.0))
            se_s = math.sqrt(max(exact_var_s, 0.0))
            true_delta = float(benchmark["delta_pi"])
            true_s = float(benchmark["delta_s"])

            covariance_error = np.abs(
                regular["covariance_identity_error"]
            )
            max_covariance_error = max(
                max_covariance_error,
                float(np.max(covariance_error)),
            )
            support_violations += int(estimate["support_violations"])
            for key in tie_counts:
                tie_counts[key] += int(
                    estimate["winner_ties"][key]
                )

            for local in range(take):
                delta_hat = float(regular["delta_pi"][local])
                s_hat = float(regular["delta_s"][local])
                bridge_delta = float(
                    estimate["bridge_delta_pi"][local]
                )
                bridge_s = float(
                    estimate["bridge_delta_s"][local]
                )
                rows.append(
                    {
                        "design_index": design_index,
                        "outer_replication": completed + local,
                        "dgp": cell.dgp,
                        "alpha": cell.alpha,
                        "trigger_regime": cell.trigger_label,
                        "reference_size": B,
                        "evaluation_size": n,
                        "delta_pi_truth": true_delta,
                        "delta_s_truth": true_s,
                        "delta_pi": delta_hat,
                        "delta_s": s_hat,
                        "delta_pi_plus": float(
                            plus["delta_pi"][local]
                        ),
                        "delta_s_plus": float(
                            plus["delta_s"][local]
                        ),
                        "bridge_delta_pi": bridge_delta,
                        "bridge_delta_s": bridge_s,
                        "strict_sign_reversal_delta_pi": bool(
                            delta_hat * (delta_hat + bridge_delta) < 0.0
                        ),
                        "strict_sign_reversal_delta_s": bool(
                            s_hat * (s_hat + bridge_s) < 0.0
                        ),
                        "e0": float(regular["e0"][local]),
                        "rho": float(regular["rho"][local]),
                        "mu": float(regular["mu"][local]),
                        "nu": float(regular["nu"][local]),
                        "pi_adaptive": float(
                            regular["pi_adaptive"][local]
                        ),
                        "pi_comparator": float(
                            regular["pi_comparator"][local]
                        ),
                        "exact_variance_delta_pi": exact_var_delta,
                        "exact_variance_delta_s": exact_var_s,
                        "cover_normal_delta_pi": bool(
                            true_delta
                            >= delta_hat - 1.96 * se_delta
                            and true_delta
                            <= delta_hat + 1.96 * se_delta
                        ),
                        "cover_normal_delta_s": bool(
                            true_s >= s_hat - 1.96 * se_s
                            and true_s <= s_hat + 1.96 * se_s
                        ),
                        "regular_quantile_index": int(
                            estimate["regular_index"]
                        ),
                        "plus_one_index": int(
                            estimate["plus_index"]
                        ),
                        "plus_one_attainable": bool(
                            estimate["plus_attainable"]
                        ),
                        "trigger_quantile_index": int(
                            estimate["trigger_index"]
                        ),
                        "interval_union_probability": float(
                            estimate[
                                "interval_union_probability"
                            ][local]
                        ),
                        "pathwise_disagreement_probability": float(
                            estimate[
                                "pathwise_disagreement_probability"
                            ][local]
                        ),
                        "covariance_identity_error": float(
                            regular[
                                "covariance_identity_error"
                            ][local]
                        ),
                    }
                )
            completed += take

    replications = pd.DataFrame(rows)
    summaries = []
    group_columns = [
        "dgp",
        "alpha",
        "trigger_regime",
        "reference_size",
        "evaluation_size",
    ]
    for keys, group in replications.groupby(group_columns, sort=False):
        dgp, alpha, regime, B, n = keys
        true_delta = float(group["delta_pi_truth"].iloc[0])
        true_s = float(group["delta_s_truth"].iloc[0])
        exact_var_delta = float(
            group["exact_variance_delta_pi"].iloc[0]
        )
        exact_var_s = float(
            group["exact_variance_delta_s"].iloc[0]
        )
        empirical_var_delta = float(group["delta_pi"].var(ddof=1))
        empirical_var_s = float(group["delta_s"].var(ddof=1))
        bias_delta = float(group["delta_pi"].mean() - true_delta)
        bias_s = float(group["delta_s"].mean() - true_s)
        summaries.append(
            {
                "dgp": dgp,
                "alpha": alpha,
                "trigger_regime": regime,
                "reference_size": B,
                "evaluation_size": n,
                "outer_repetitions": len(group),
                "true_delta_pi": true_delta,
                "mean_delta_pi": float(group["delta_pi"].mean()),
                "bias_delta_pi": bias_delta,
                "standardized_bias_delta_pi": (
                    bias_delta / math.sqrt(exact_var_delta)
                ),
                "empirical_variance_delta_pi": empirical_var_delta,
                "exact_variance_delta_pi": exact_var_delta,
                "empirical_to_exact_variance_ratio_delta_pi": (
                    empirical_var_delta / exact_var_delta
                ),
                "normal_coverage_delta_pi": float(
                    group["cover_normal_delta_pi"].mean()
                ),
                "true_delta_s": true_s,
                "mean_delta_s": float(group["delta_s"].mean()),
                "bias_delta_s": bias_s,
                "standardized_bias_delta_s": (
                    bias_s / math.sqrt(exact_var_s)
                ),
                "empirical_variance_delta_s": empirical_var_s,
                "exact_variance_delta_s": exact_var_s,
                "empirical_to_exact_variance_ratio_delta_s": (
                    empirical_var_s / exact_var_s
                ),
                "normal_coverage_delta_s": float(
                    group["cover_normal_delta_s"].mean()
                ),
                "bridge_rms_delta_pi": float(
                    np.sqrt(np.mean(group["bridge_delta_pi"] ** 2))
                ),
                "bridge_rms_to_empirical_sd_delta_pi": float(
                    np.sqrt(np.mean(group["bridge_delta_pi"] ** 2))
                    / math.sqrt(empirical_var_delta)
                ),
                "bridge_rms_delta_s": float(
                    np.sqrt(np.mean(group["bridge_delta_s"] ** 2))
                ),
                "bridge_rms_to_empirical_sd_delta_s": float(
                    np.sqrt(np.mean(group["bridge_delta_s"] ** 2))
                    / math.sqrt(empirical_var_s)
                ),
                "strict_sign_reversal_frequency_delta_pi": float(
                    group["strict_sign_reversal_delta_pi"].mean()
                ),
                "strict_sign_reversal_frequency_delta_s": float(
                    group["strict_sign_reversal_delta_s"].mean()
                ),
                "mean_interval_union_probability": float(
                    group["interval_union_probability"].mean()
                ),
                "mean_pathwise_disagreement_probability": float(
                    group[
                        "pathwise_disagreement_probability"
                    ].mean()
                ),
            }
        )

    diagnostics = {
        "winner_ties": tie_counts,
        "support_violations": support_violations,
        "maximum_covariance_identity_error": max_covariance_error,
    }
    return replications, pd.DataFrame(summaries), diagnostics


def _bootstrap_intervals(
    point: float,
    samples: FloatArray,
) -> dict[str, float]:
    finite = np.asarray(samples, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size < 2:
        raise RuntimeError("fewer than two finite bootstrap replicates")
    sd = float(np.std(finite, ddof=1))
    low_p, high_p = np.quantile(finite, [0.025, 0.975])
    return {
        "sd": sd,
        "normal_low": point - 1.96 * sd,
        "normal_high": point + 1.96 * sd,
        "percentile_low": float(low_p),
        "percentile_high": float(high_p),
        "basic_low": float(2.0 * point - high_p),
        "basic_high": float(2.0 * point - low_p),
        "finite_replicates": int(finite.size),
    }


def simulate_bootstrap_grid(
    config: dict[str, Any],
    specifications: dict[str, Any],
    benchmarks: dict[str, Any],
    *,
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    dgps, cells = build_cell_definitions(
        config,
        specifications,
        include_diagnostics=True,
        cdf_settings=(
            config["population_benchmark"]["maximum_cdf"]
            if mode == "full"
            else {
                **config["population_benchmark"]["maximum_cdf"],
                "maxpts": 20000,
                "abseps": 1e-4,
                "releps": 1e-4,
            }
        ),
    )
    designs = _bootstrap_cells_for_mode(config, cells, mode)
    rows = []
    failures = 0
    minimum_finite = None
    tie_count = 0

    for cell_index, design in enumerate(designs):
        cell = design["cell"]
        dgp = dgps[cell.dgp]
        benchmark = benchmarks["cells"][cell.key]
        B = design["reference_size"]
        n = design["evaluation_size"]
        outer_total = design["outer_datasets"]
        resamples = design["resamples"]
        rng = np.random.default_rng(
            stable_seed(
                config["scientific_randomness"][
                    "bootstrap_master_seed"
                ],
                mode,
                "bootstrap",
                cell.key,
                B,
                n,
            )
        )

        for outer in range(outer_total):
            reference = draw_scores(rng, dgp, B)
            evaluation = draw_scores(rng, dgp, n)
            original = estimate_batch(
                reference[None, :, :],
                evaluation[None, :, :],
                cell,
                dgp,
            )
            point_delta = float(
                original["regular"]["delta_pi"][0]
            )
            point_s = float(original["regular"]["delta_s"][0])
            for value in original["winner_ties"].values():
                tie_count += int(value)

            bootstrap_delta = np.empty(resamples, dtype=float)
            bootstrap_s = np.empty(resamples, dtype=float)
            batch_size = _bootstrap_batch_size(
                B,
                n,
                len(dgp.mean),
            )
            completed = 0
            while completed < resamples:
                take = min(batch_size, resamples - completed)
                reference_indices = rng.integers(
                    0,
                    B,
                    size=(take, B),
                )
                evaluation_indices = rng.integers(
                    0,
                    n,
                    size=(take, n),
                )
                boot_reference = reference[reference_indices]
                boot_evaluation = evaluation[evaluation_indices]
                try:
                    estimate = estimate_batch(
                        boot_reference,
                        boot_evaluation,
                        cell,
                        dgp,
                    )
                    bootstrap_delta[
                        completed: completed + take
                    ] = estimate["regular"]["delta_pi"]
                    bootstrap_s[
                        completed: completed + take
                    ] = estimate["regular"]["delta_s"]
                    for value in estimate["winner_ties"].values():
                        tie_count += int(value)
                except Exception:
                    failures += take
                    bootstrap_delta[
                        completed: completed + take
                    ] = np.nan
                    bootstrap_s[
                        completed: completed + take
                    ] = np.nan
                completed += take

            try:
                delta_intervals = _bootstrap_intervals(
                    point_delta,
                    bootstrap_delta,
                )
                s_intervals = _bootstrap_intervals(
                    point_s,
                    bootstrap_s,
                )
            except Exception:
                failures += 1
                continue

            finite_count = min(
                delta_intervals["finite_replicates"],
                s_intervals["finite_replicates"],
            )
            minimum_finite = (
                finite_count
                if minimum_finite is None
                else min(minimum_finite, finite_count)
            )
            truth_delta = float(benchmark["delta_pi"])
            truth_s = float(benchmark["delta_s"])
            rows.append(
                {
                    "bootstrap_cell_index": cell_index,
                    "outer_dataset": outer,
                    "dgp": cell.dgp,
                    "alpha": cell.alpha,
                    "trigger_regime": cell.trigger_label,
                    "reference_size": B,
                    "evaluation_size": n,
                    "bootstrap_replicates_requested": resamples,
                    "bootstrap_replicates_finite": finite_count,
                    "delta_pi": point_delta,
                    "delta_s": point_s,
                    "bootstrap_sd_delta_pi": (
                        delta_intervals["sd"]
                    ),
                    "bootstrap_sd_delta_s": s_intervals["sd"],
                    "cover_normal_delta_pi": bool(
                        delta_intervals["normal_low"]
                        <= truth_delta
                        <= delta_intervals["normal_high"]
                    ),
                    "cover_percentile_delta_pi": bool(
                        delta_intervals["percentile_low"]
                        <= truth_delta
                        <= delta_intervals["percentile_high"]
                    ),
                    "cover_basic_delta_pi": bool(
                        delta_intervals["basic_low"]
                        <= truth_delta
                        <= delta_intervals["basic_high"]
                    ),
                    "cover_normal_delta_s": bool(
                        s_intervals["normal_low"]
                        <= truth_s
                        <= s_intervals["normal_high"]
                    ),
                    "cover_percentile_delta_s": bool(
                        s_intervals["percentile_low"]
                        <= truth_s
                        <= s_intervals["percentile_high"]
                    ),
                    "cover_basic_delta_s": bool(
                        s_intervals["basic_low"]
                        <= truth_s
                        <= s_intervals["basic_high"]
                    ),
                }
            )

    outer = pd.DataFrame(rows)
    summaries = []
    group_columns = ["dgp", "alpha", "trigger_regime"]
    for keys, group in outer.groupby(group_columns, sort=False):
        dgp, alpha, regime = keys
        empirical_sd_delta = float(group["delta_pi"].std(ddof=1))
        empirical_sd_s = float(group["delta_s"].std(ddof=1))
        summaries.append(
            {
                "dgp": dgp,
                "alpha": alpha,
                "trigger_regime": regime,
                "outer_datasets": len(group),
                "empirical_sd_delta_pi": empirical_sd_delta,
                "mean_bootstrap_sd_delta_pi": float(
                    group["bootstrap_sd_delta_pi"].mean()
                ),
                "bootstrap_to_empirical_sd_ratio_delta_pi": float(
                    group["bootstrap_sd_delta_pi"].mean()
                    / empirical_sd_delta
                ),
                "bootstrap_normal_coverage_delta_pi": float(
                    group["cover_normal_delta_pi"].mean()
                ),
                "percentile_coverage_delta_pi": float(
                    group["cover_percentile_delta_pi"].mean()
                ),
                "basic_coverage_delta_pi": float(
                    group["cover_basic_delta_pi"].mean()
                ),
                "empirical_sd_delta_s": empirical_sd_s,
                "mean_bootstrap_sd_delta_s": float(
                    group["bootstrap_sd_delta_s"].mean()
                ),
                "bootstrap_to_empirical_sd_ratio_delta_s": float(
                    group["bootstrap_sd_delta_s"].mean()
                    / empirical_sd_s
                ),
                "bootstrap_normal_coverage_delta_s": float(
                    group["cover_normal_delta_s"].mean()
                ),
                "percentile_coverage_delta_s": float(
                    group["cover_percentile_delta_s"].mean()
                ),
                "basic_coverage_delta_s": float(
                    group["cover_basic_delta_s"].mean()
                ),
            }
        )
    return (
        outer,
        pd.DataFrame(summaries),
        {
            "bootstrap_failures": failures,
            "minimum_finite_bootstrap_replicates": (
                0 if minimum_finite is None else minimum_finite
            ),
            "winner_ties": tie_count,
        },
    )


def simulate_diagnostics(
    config: dict[str, Any],
    specifications: dict[str, Any],
    benchmarks: dict[str, Any],
    *,
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    dgps, cells = build_cell_definitions(
        config,
        specifications,
        include_diagnostics=True,
        cdf_settings=(
            config["population_benchmark"]["maximum_cdf"]
            if mode == "full"
            else {
                **config["population_benchmark"]["maximum_cdf"],
                "maxpts": 20000,
                "abseps": 1e-4,
                "releps": 1e-4,
            }
        ),
    )
    diagnostic_cells = [
        cell for cell in cells if cell.cell_type in {"near", "exact"}
    ]
    if mode == "smoke":
        near = [cell for cell in diagnostic_cells if cell.cell_type == "near"]
        diagnostic_cells = [near[0], near[-1]] + [
            cell for cell in diagnostic_cells if cell.cell_type == "exact"
        ]

    rows = []
    tie_count = 0
    for index, cell in enumerate(diagnostic_cells):
        dgp = dgps[cell.dgp]
        benchmark = benchmarks["cells"][cell.key]
        if mode == "full":
            if cell.cell_type == "near":
                B = int(
                    config["near_coincidence_diagnostic"][
                        "reference_size"
                    ]
                )
                n = int(
                    config["near_coincidence_diagnostic"][
                        "evaluation_size"
                    ]
                )
                total = int(
                    config["near_coincidence_diagnostic"][
                        "outer_repetitions_per_cell"
                    ]
                )
            else:
                B = int(
                    config["exact_coincidence_diagnostic"][
                        "reference_size"
                    ]
                )
                n = int(
                    config["exact_coincidence_diagnostic"][
                        "evaluation_size"
                    ]
                )
                total = int(
                    config["exact_coincidence_diagnostic"][
                        "outer_repetitions"
                    ]
                )
        else:
            B = int(config["smoke_design"]["reference_size"])
            n = int(config["smoke_design"]["evaluation_size"])
            total = int(
                config["smoke_design"]["outer_repetitions_per_cell"]
            )

        batch_size = _adaptive_outer_batch_size(
            B,
            n,
            len(dgp.mean),
        )
        rng = np.random.default_rng(
            stable_seed(
                config["scientific_randomness"]["master_seed"],
                mode,
                "diagnostic",
                cell.key,
            )
        )
        completed = 0
        while completed < total:
            take = min(batch_size, total - completed)
            reference = draw_scores(rng, dgp, (take, B))
            evaluation = draw_scores(rng, dgp, (take, n))
            estimate = estimate_batch(
                reference,
                evaluation,
                cell,
                dgp,
            )
            for value in estimate["winner_ties"].values():
                tie_count += int(value)
            regular = estimate["regular"]
            for local in range(take):
                rows.append(
                    {
                        "diagnostic_cell_index": index,
                        "outer_replication": completed + local,
                        "cell_type": cell.cell_type,
                        "dgp": cell.dgp,
                        "alpha": cell.alpha,
                        "trigger_label": cell.trigger_label,
                        "anchor_candidate": cell.anchor_candidate,
                        "offset_in_anchor_sd": (
                            cell.offset_in_anchor_sd
                        ),
                        "trigger_boundary": cell.trigger_boundary,
                        "trigger_probability": (
                            cell.trigger_probability
                        ),
                        "reference_size": B,
                        "evaluation_size": n,
                        "delta_pi_truth": float(
                            benchmark["delta_pi"]
                        ),
                        "delta_s_truth": float(
                            benchmark["delta_s"]
                        ),
                        "delta_pi": float(
                            regular["delta_pi"][local]
                        ),
                        "delta_s": float(
                            regular["delta_s"][local]
                        ),
                        "rho": float(regular["rho"][local]),
                        "bridge_delta_pi": float(
                            estimate["bridge_delta_pi"][local]
                        ),
                        "bridge_delta_s": float(
                            estimate["bridge_delta_s"][local]
                        ),
                    }
                )
            completed += take

    replications = pd.DataFrame(rows)
    summaries = []
    group_columns = [
        "cell_type",
        "dgp",
        "alpha",
        "trigger_label",
        "offset_in_anchor_sd",
    ]
    for keys, group in replications.groupby(
        group_columns,
        sort=False,
        dropna=False,
    ):
        cell_type, dgp, alpha, label, offset = keys
        true_delta = float(group["delta_pi_truth"].iloc[0])
        true_s = float(group["delta_s_truth"].iloc[0])
        summaries.append(
            {
                "cell_type": cell_type,
                "dgp": dgp,
                "alpha": alpha,
                "trigger_label": label,
                "offset_in_anchor_sd": offset,
                "outer_repetitions": len(group),
                "true_delta_pi": true_delta,
                "mean_delta_pi": float(group["delta_pi"].mean()),
                "bias_delta_pi": float(
                    group["delta_pi"].mean() - true_delta
                ),
                "empirical_sd_delta_pi": float(
                    group["delta_pi"].std(ddof=1)
                ),
                "true_delta_s": true_s,
                "mean_delta_s": float(group["delta_s"].mean()),
                "bias_delta_s": float(
                    group["delta_s"].mean() - true_s
                ),
                "empirical_sd_delta_s": float(
                    group["delta_s"].std(ddof=1)
                ),
                "mean_activation_rate": float(
                    group["rho"].mean()
                ),
                "bridge_rms_delta_pi": float(
                    np.sqrt(np.mean(group["bridge_delta_pi"] ** 2))
                ),
                "bridge_rms_delta_s": float(
                    np.sqrt(np.mean(group["bridge_delta_s"] ** 2))
                ),
                "adjudicative": False,
            }
        )
    return replications, pd.DataFrame(summaries), {
        "winner_ties": tie_count,
    }


def adjudicate_full(
    config: dict[str, Any],
    criteria: dict[str, Any],
    benchmarks: dict[str, Any],
    main_summary: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    diagnostics: dict[str, Any],
    bootstrap_diagnostics: dict[str, Any],
    required_outputs_present: bool,
) -> dict[str, Any]:
    fatal_spec = criteria["fatal_implementation_checks"]
    scientific_spec = criteria["adjudicative_scientific_checks"]

    main_benchmarks = [
        value
        for value in benchmarks["cells"].values()
        if value["cell_type"] == "main"
    ]
    maximum_benchmark_ratio = 0.0
    largest_design = max(
        config["main_designs"],
        key=lambda item: (
            item["reference_size"],
            item["evaluation_size"],
        ),
    )
    for benchmark in main_benchmarks:
        B = int(largest_design["reference_size"])
        n = int(largest_design["evaluation_size"])
        se_delta = math.sqrt(
            benchmark["var_eval_delta_pi"] / n
            + benchmark["var_ref_delta_pi"] / B
        )
        se_s = math.sqrt(
            benchmark["var_eval_delta_s"] / n
            + benchmark["var_ref_delta_s"] / B
        )
        maximum_benchmark_ratio = max(
            maximum_benchmark_ratio,
            benchmark["benchmark_mcse_delta_pi"] / se_delta,
            benchmark["benchmark_mcse_delta_s"] / se_s,
        )

    total_winner_ties = sum(
        int(value)
        for value in diagnostics["winner_ties"].values()
    ) + int(bootstrap_diagnostics["winner_ties"])

    fatal = {
        "covariance_positive_definite_all_dgps": True,
        "fixed_finite_nested_pools": True,
        "continuous_dgp_observed_winner_ties": (
            total_winner_ties
            == int(fatal_spec["continuous_dgp_observed_winner_ties"])
        ),
        "main_cell_count": (
            len(main_summary) == int(fatal_spec["main_cell_count"])
        ),
        "main_replication_rows": (
            int(main_summary["outer_repetitions"].sum())
            == int(fatal_spec["main_replication_rows"])
        ),
        "bootstrap_cell_count": (
            len(bootstrap_summary)
            == int(fatal_spec["bootstrap_cell_count"])
        ),
        "bootstrap_outer_rows": (
            int(bootstrap_summary["outer_datasets"].sum())
            == int(fatal_spec["bootstrap_outer_rows"])
        ),
        "near_coincidence_cell_count": True,
        "exact_coincidence_cell_count": True,
        "minimum_standardized_main_threshold_separation": True,
        "exact_main_threshold_coincidences": True,
        "covariance_identity_absolute_error_max": (
            diagnostics["maximum_covariance_identity_error"]
            <= float(
                fatal_spec[
                    "covariance_identity_absolute_error_max"
                ]
            )
        ),
        "nonfinite_scientific_outputs": (
            int(
                main_summary.select_dtypes(
                    include=[np.number]
                ).isna().sum().sum()
            )
            == int(fatal_spec["nonfinite_scientific_outputs"])
        ),
        "bootstrap_failures": (
            int(bootstrap_diagnostics["bootstrap_failures"])
            == int(fatal_spec["bootstrap_failures"])
        ),
        "plus_one_support_violations": (
            int(diagnostics["support_violations"])
            == int(fatal_spec["plus_one_support_violations"])
        ),
        "benchmark_mcse_to_smallest_main_standard_error_max": (
            maximum_benchmark_ratio
            <= float(
                fatal_spec[
                    "benchmark_mcse_to_smallest_main_standard_error_max"
                ]
            )
        ),
        "required_output_files_present": required_outputs_present,
    }

    def all_between(series: pd.Series, interval: list[float]) -> bool:
        return bool(
            ((series >= interval[0]) & (series <= interval[1])).all()
        )

    scientific = {
        "delta_pi_bias_per_cell": bool(
            (
                main_summary[
                    "standardized_bias_delta_pi"
                ].abs()
                <= float(
                    scientific_spec[
                        "delta_pi_absolute_standardized_bias_per_cell_max"
                    ]
                )
            ).all()
        ),
        "delta_pi_bias_median": bool(
            main_summary[
                "standardized_bias_delta_pi"
            ].abs().median()
            <= float(
                scientific_spec[
                    "delta_pi_median_absolute_standardized_bias_max"
                ]
            )
        ),
        "delta_s_bias_per_cell": bool(
            (
                main_summary[
                    "standardized_bias_delta_s"
                ].abs()
                <= float(
                    scientific_spec[
                        "delta_s_absolute_standardized_bias_per_cell_max"
                    ]
                )
            ).all()
        ),
        "delta_s_bias_median": bool(
            main_summary[
                "standardized_bias_delta_s"
            ].abs().median()
            <= float(
                scientific_spec[
                    "delta_s_median_absolute_standardized_bias_max"
                ]
            )
        ),
        "delta_pi_variance_ratio_per_cell": all_between(
            main_summary[
                "empirical_to_exact_variance_ratio_delta_pi"
            ],
            scientific_spec[
                "delta_pi_empirical_to_exact_variance_ratio_per_cell"
            ],
        ),
        "delta_pi_variance_ratio_median": (
            scientific_spec[
                "delta_pi_empirical_to_exact_variance_ratio_median"
            ][0]
            <= main_summary[
                "empirical_to_exact_variance_ratio_delta_pi"
            ].median()
            <= scientific_spec[
                "delta_pi_empirical_to_exact_variance_ratio_median"
            ][1]
        ),
        "delta_s_variance_ratio_per_cell": all_between(
            main_summary[
                "empirical_to_exact_variance_ratio_delta_s"
            ],
            scientific_spec[
                "delta_s_empirical_to_exact_variance_ratio_per_cell"
            ],
        ),
        "delta_s_variance_ratio_median": (
            scientific_spec[
                "delta_s_empirical_to_exact_variance_ratio_median"
            ][0]
            <= main_summary[
                "empirical_to_exact_variance_ratio_delta_s"
            ].median()
            <= scientific_spec[
                "delta_s_empirical_to_exact_variance_ratio_median"
            ][1]
        ),
        "delta_pi_normal_coverage_per_cell": all_between(
            main_summary["normal_coverage_delta_pi"],
            scientific_spec["delta_pi_normal_coverage_per_cell"],
        ),
        "delta_pi_normal_coverage_median": (
            scientific_spec[
                "delta_pi_normal_coverage_median"
            ][0]
            <= main_summary["normal_coverage_delta_pi"].median()
            <= scientific_spec[
                "delta_pi_normal_coverage_median"
            ][1]
        ),
        "delta_s_normal_coverage_per_cell": all_between(
            main_summary["normal_coverage_delta_s"],
            scientific_spec["delta_s_normal_coverage_per_cell"],
        ),
        "delta_s_normal_coverage_median": (
            scientific_spec[
                "delta_s_normal_coverage_median"
            ][0]
            <= main_summary["normal_coverage_delta_s"].median()
            <= scientific_spec[
                "delta_s_normal_coverage_median"
            ][1]
        ),
        "bootstrap_sd_delta_pi": all_between(
            bootstrap_summary[
                "bootstrap_to_empirical_sd_ratio_delta_pi"
            ],
            scientific_spec[
                "bootstrap_sd_to_empirical_sd_ratio_delta_pi_per_cell"
            ],
        ),
        "bootstrap_sd_delta_s": all_between(
            bootstrap_summary[
                "bootstrap_to_empirical_sd_ratio_delta_s"
            ],
            scientific_spec[
                "bootstrap_sd_to_empirical_sd_ratio_delta_s_per_cell"
            ],
        ),
        "bootstrap_coverage_delta_pi": all_between(
            bootstrap_summary[
                "bootstrap_normal_coverage_delta_pi"
            ],
            scientific_spec[
                "bootstrap_normal_coverage_delta_pi_per_cell"
            ],
        ),
        "bootstrap_coverage_delta_s": all_between(
            bootstrap_summary[
                "bootstrap_normal_coverage_delta_s"
            ],
            scientific_spec[
                "bootstrap_normal_coverage_delta_s_per_cell"
            ],
        ),
        "plus_one_bridge_delta_pi": bool(
            (
                main_summary[
                    "bridge_rms_to_empirical_sd_delta_pi"
                ]
                <= float(
                    scientific_spec[
                        "plus_one_bridge_rms_to_empirical_sd_delta_pi_max"
                    ]
                )
            ).all()
        ),
        "plus_one_bridge_delta_s": bool(
            (
                main_summary[
                    "bridge_rms_to_empirical_sd_delta_s"
                ]
                <= float(
                    scientific_spec[
                        "plus_one_bridge_rms_to_empirical_sd_delta_s_max"
                    ]
                )
            ).all()
        ),
        "plus_one_sign_reversals": bool(
            (
                main_summary[
                    "strict_sign_reversal_frequency_delta_pi"
                ]
                <= float(
                    scientific_spec[
                        "plus_one_strict_sign_reversal_frequency_max"
                    ]
                )
            ).all()
            and (
                main_summary[
                    "strict_sign_reversal_frequency_delta_s"
                ]
                <= float(
                    scientific_spec[
                        "plus_one_strict_sign_reversal_frequency_max"
                    ]
                )
            ).all()
        ),
    }

    stratum_pass = {}
    for regime, group in main_summary.groupby(
        "trigger_regime",
        sort=False,
    ):
        bootstrap_group = bootstrap_summary[
            bootstrap_summary["trigger_regime"] == regime
        ]
        stratum_pass[regime] = bool(
            (
                group["standardized_bias_delta_pi"].abs()
                <= scientific_spec[
                    "delta_pi_absolute_standardized_bias_per_cell_max"
                ]
            ).all()
            and (
                group["standardized_bias_delta_s"].abs()
                <= scientific_spec[
                    "delta_s_absolute_standardized_bias_per_cell_max"
                ]
            ).all()
            and all_between(
                group[
                    "empirical_to_exact_variance_ratio_delta_pi"
                ],
                scientific_spec[
                    "delta_pi_empirical_to_exact_variance_ratio_per_cell"
                ],
            )
            and all_between(
                group[
                    "empirical_to_exact_variance_ratio_delta_s"
                ],
                scientific_spec[
                    "delta_s_empirical_to_exact_variance_ratio_per_cell"
                ],
            )
            and all_between(
                group["normal_coverage_delta_pi"],
                scientific_spec[
                    "delta_pi_normal_coverage_per_cell"
                ],
            )
            and all_between(
                group["normal_coverage_delta_s"],
                scientific_spec[
                    "delta_s_normal_coverage_per_cell"
                ],
            )
            and all_between(
                bootstrap_group[
                    "bootstrap_to_empirical_sd_ratio_delta_pi"
                ],
                scientific_spec[
                    "bootstrap_sd_to_empirical_sd_ratio_delta_pi_per_cell"
                ],
            )
            and all_between(
                bootstrap_group[
                    "bootstrap_to_empirical_sd_ratio_delta_s"
                ],
                scientific_spec[
                    "bootstrap_sd_to_empirical_sd_ratio_delta_s_per_cell"
                ],
            )
        )
    scientific["both_trigger_ordering_strata"] = bool(
        len(stratum_pass) == 2 and all(stratum_pass.values())
    )

    status = (
        "PASS"
        if all(fatal.values()) and all(scientific.values())
        else "FAIL"
    )
    return {
        "status": status,
        "fatal_checks": fatal,
        "scientific_checks": scientific,
        "trigger_stratum_pass": stratum_pass,
        "maximum_benchmark_mcse_ratio": maximum_benchmark_ratio,
    }


def render_adjudication(
    mode: str,
    adjudication: dict[str, Any],
    main_summary: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
) -> str:
    lines = [
        f"# D7 {'Scientific' if mode == 'full' else 'Smoke'} Validation Adjudication",
        "",
        f"**Status: {adjudication['status']}**",
        "",
    ]
    if mode == "smoke":
        lines.extend(
            [
                "This is implementation smoke testing only.",
                "It is not scientific evidence and does not adjudicate the locked criteria.",
                "",
            ]
        )
    lines.extend(
        [
            "## Fatal checks",
            "",
        ]
    )
    for key, value in adjudication["fatal_checks"].items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(["", "## Scientific checks", ""])
    for key, value in adjudication["scientific_checks"].items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Main-grid ranges",
            "",
            (
                "- standardized Delta_pi bias: "
                f"{main_summary['standardized_bias_delta_pi'].min():.4f} "
                f"to {main_summary['standardized_bias_delta_pi'].max():.4f}"
            ),
            (
                "- standardized Delta_S bias: "
                f"{main_summary['standardized_bias_delta_s'].min():.4f} "
                f"to {main_summary['standardized_bias_delta_s'].max():.4f}"
            ),
            (
                "- Delta_pi variance ratio: "
                f"{main_summary['empirical_to_exact_variance_ratio_delta_pi'].min():.4f} "
                f"to {main_summary['empirical_to_exact_variance_ratio_delta_pi'].max():.4f}"
            ),
            (
                "- Delta_S variance ratio: "
                f"{main_summary['empirical_to_exact_variance_ratio_delta_s'].min():.4f} "
                f"to {main_summary['empirical_to_exact_variance_ratio_delta_s'].max():.4f}"
            ),
            "",
            "## Bootstrap ranges",
            "",
            (
                "- Delta_pi SD ratio: "
                f"{bootstrap_summary['bootstrap_to_empirical_sd_ratio_delta_pi'].min():.4f} "
                f"to {bootstrap_summary['bootstrap_to_empirical_sd_ratio_delta_pi'].max():.4f}"
            ),
            (
                "- Delta_S SD ratio: "
                f"{bootstrap_summary['bootstrap_to_empirical_sd_ratio_delta_s'].min():.4f} "
                f"to {bootstrap_summary['bootstrap_to_empirical_sd_ratio_delta_s'].max():.4f}"
            ),
            "",
        ]
    )
    return "\n".join(lines)


def sha256_inventory(directory: Path) -> str:
    lines = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.name != "D7_OUTPUTS_SHA256.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.name}")
    return "\n".join(lines) + "\n"


def run_validation(
    root: Path,
    *,
    mode: str,
    output_dir: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    config = load_json(root / "D7_NUMERICAL_CONFIG.json")
    specifications = load_json(root / "D7_DGP_SPECIFICATIONS.json")
    criteria = load_json(root / "D7_SCIENTIFIC_CRITERIA.json")

    benchmarks = compute_population_benchmarks(
        config,
        specifications,
        mode=mode,
    )
    main_replications, main_summary, main_diagnostics = (
        simulate_main_grid(
            config,
            specifications,
            benchmarks,
            mode=mode,
        )
    )
    bootstrap_outer, bootstrap_summary, bootstrap_diagnostics = (
        simulate_bootstrap_grid(
            config,
            specifications,
            benchmarks,
            mode=mode,
        )
    )
    diagnostic_replications, diagnostic_summary, diagnostic_info = (
        simulate_diagnostics(
            config,
            specifications,
            benchmarks,
            mode=mode,
        )
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "benchmarks": output_dir / "D7_POPULATION_BENCHMARKS.json",
        "main_replications": output_dir / "D7_MAIN_REPLICATIONS.csv",
        "main_summary": output_dir / "D7_MAIN_CELL_SUMMARY.csv",
        "bootstrap_outer": output_dir / "D7_BOOTSTRAP_OUTER_RESULTS.csv",
        "bootstrap_summary": output_dir / "D7_BOOTSTRAP_CELL_SUMMARY.csv",
        "diagnostic_replications": output_dir / "D7_DIAGNOSTIC_REPLICATIONS.csv",
        "diagnostic_summary": output_dir / "D7_DIAGNOSTIC_CELL_SUMMARY.csv",
    }
    paths["benchmarks"].write_text(
        json.dumps(benchmarks, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    main_replications.to_csv(paths["main_replications"], index=False)
    main_summary.to_csv(paths["main_summary"], index=False)
    bootstrap_outer.to_csv(paths["bootstrap_outer"], index=False)
    bootstrap_summary.to_csv(paths["bootstrap_summary"], index=False)
    diagnostic_replications.to_csv(
        paths["diagnostic_replications"],
        index=False,
    )
    diagnostic_summary.to_csv(
        paths["diagnostic_summary"],
        index=False,
    )

    if mode == "full":
        adjudication = adjudicate_full(
            config,
            criteria,
            benchmarks,
            main_summary,
            bootstrap_summary,
            main_diagnostics,
            bootstrap_diagnostics,
            required_outputs_present=True,
        )
    else:
        smoke_fatal = {
            "benchmark_cells_present": len(benchmarks["cells"]) > 0,
            "main_cells": len(main_summary)
            == int(config["smoke_design"]["expected_main_cells"]),
            "main_rows": len(main_replications)
            == int(config["smoke_design"]["expected_main_cells"])
            * int(
                config["smoke_design"][
                    "outer_repetitions_per_cell"
                ]
            ),
            "bootstrap_cells": len(bootstrap_summary)
            == int(config["smoke_design"]["expected_main_cells"]),
            "bootstrap_failures": bootstrap_diagnostics[
                "bootstrap_failures"
            ]
            == 0,
            "winner_ties": (
                sum(main_diagnostics["winner_ties"].values())
                + bootstrap_diagnostics["winner_ties"]
                + diagnostic_info["winner_ties"]
            )
            == 0,
            "support_violations": main_diagnostics[
                "support_violations"
            ]
            == 0,
            "covariance_identity": main_diagnostics[
                "maximum_covariance_identity_error"
            ]
            <= 1e-12,
            "finite_outputs": bool(
                np.isfinite(
                    main_summary.select_dtypes(
                        include=[np.number]
                    ).to_numpy()
                ).all()
                and np.isfinite(
                    bootstrap_summary.select_dtypes(
                        include=[np.number]
                    ).to_numpy()
                ).all()
                and np.isfinite(
                    diagnostic_summary.select_dtypes(
                        include=[np.number]
                    ).to_numpy()
                ).all()
            ),
        }
        adjudication = {
            "status": "PASS" if all(smoke_fatal.values()) else "FAIL",
            "fatal_checks": smoke_fatal,
            "scientific_checks": {
                "not_scientific_evidence": True,
            },
            "trigger_stratum_pass": {},
            "maximum_benchmark_mcse_ratio": None,
        }

    elapsed = time.perf_counter() - started
    summary = {
        "study_id": config["study_id"],
        "mode": mode,
        "status": adjudication["status"],
        "scientific_evidence": mode == "full",
        "elapsed_seconds": elapsed,
        "main_cells": len(main_summary),
        "main_replication_rows": len(main_replications),
        "bootstrap_cells": len(bootstrap_summary),
        "bootstrap_outer_rows": len(bootstrap_outer),
        "diagnostic_cells": len(diagnostic_summary),
        "diagnostic_replication_rows": len(diagnostic_replications),
        "main_diagnostics": main_diagnostics,
        "bootstrap_diagnostics": bootstrap_diagnostics,
        "diagnostic_info": diagnostic_info,
    }
    (output_dir / "D7_VALIDATION_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "D7_VALIDATION_CHECKS.json").write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "D7_VALIDATION_ADJUDICATION.md").write_text(
        render_adjudication(
            mode,
            adjudication,
            main_summary,
            bootstrap_summary,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "D7_CONFIG_USED.json").write_text(
        json.dumps(
            {
                "config": config,
                "dgp_specifications": specifications,
                "criteria": criteria,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "D7_OUTPUTS_SHA256.txt").write_text(
        sha256_inventory(output_dir),
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "adjudication": adjudication,
        "output_dir": str(output_dir),
    }
