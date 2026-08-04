from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq
from scipy.stats import multivariate_normal, norm

from d7_core import (
    candidate_threshold_jump_field,
    coincidence_relevance_field,
    contrast_summary,
    policy_state,
)


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class D7GaussianDGP:
    mean: FloatArray
    covariance: FloatArray
    base_pool: tuple[int, ...]
    full_pool: tuple[int, ...]
    alpha: float
    activation_rate: float

    @property
    def candidate_count(self) -> int:
        return int(self.mean.size)


def default_dgp() -> D7GaussianDGP:
    mean = np.array([0.0, 0.10, 0.20], dtype=float)
    standard_deviation = np.array([1.0, 0.90, 1.10], dtype=float)
    correlation = np.array(
        [
            [1.00, 0.35, 0.20],
            [0.35, 1.00, -0.10],
            [0.20, -0.10, 1.00],
        ],
        dtype=float,
    )
    covariance = (
        np.diag(standard_deviation)
        @ correlation
        @ np.diag(standard_deviation)
    )
    return D7GaussianDGP(
        mean=mean,
        covariance=covariance,
        base_pool=(0, 1),
        full_pool=(0, 1, 2),
        alpha=0.10,
        activation_rate=0.50,
    )


def validate_dgp(dgp: D7GaussianDGP) -> dict[str, float]:
    dimension = dgp.candidate_count
    if dgp.covariance.shape != (dimension, dimension):
        raise ValueError("covariance has the wrong shape")
    if not np.allclose(dgp.covariance, dgp.covariance.T):
        raise ValueError("covariance must be symmetric")
    eigenvalues = np.linalg.eigvalsh(dgp.covariance)
    if float(np.min(eigenvalues)) <= 0.0:
        raise ValueError("covariance must be positive definite")
    if not set(dgp.base_pool).issubset(dgp.full_pool):
        raise ValueError("base pool must be nested in full pool")
    if not 0.0 < dgp.alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 < dgp.activation_rate < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    return {
        "minimum_covariance_eigenvalue": float(np.min(eigenvalues)),
        "maximum_covariance_eigenvalue": float(np.max(eigenvalues)),
    }


def standard_deviations(dgp: D7GaussianDGP) -> FloatArray:
    return np.sqrt(np.diag(dgp.covariance))


def candidate_thresholds(dgp: D7GaussianDGP) -> FloatArray:
    probability = 1.0 - dgp.alpha
    return (
        dgp.mean
        + standard_deviations(dgp) * norm.ppf(probability)
    ).astype(float)


def base_maximum_cdf(dgp: D7GaussianDGP, value: float) -> float:
    indices = np.asarray(dgp.base_pool, dtype=np.int64)
    mean = dgp.mean[indices]
    covariance = dgp.covariance[np.ix_(indices, indices)]
    upper = np.full(indices.size, float(value), dtype=float)
    return float(
        multivariate_normal.cdf(
            upper,
            mean=mean,
            cov=covariance,
            maxpts=1_000_000,
            abseps=1e-10,
            releps=1e-10,
            rng=np.random.default_rng(20270105),
        )
    )


def trigger_threshold(dgp: D7GaussianDGP) -> float:
    probability = 1.0 - dgp.activation_rate
    sd = standard_deviations(dgp)
    lower = float(np.min(dgp.mean - 8.0 * sd))
    upper = float(np.max(dgp.mean + 8.0 * sd))
    return float(
        brentq(
            lambda value: base_maximum_cdf(dgp, value) - probability,
            lower,
            upper,
            xtol=1e-12,
            rtol=1e-12,
            maxiter=200,
        )
    )


def marginal_density(
    dgp: D7GaussianDGP,
    candidate: int,
    value: float,
) -> float:
    sd = standard_deviations(dgp)[candidate]
    standardized = (value - dgp.mean[candidate]) / sd
    return float(norm.pdf(standardized) / sd)


def conditional_parameters(
    dgp: D7GaussianDGP,
    fixed_index: int,
    fixed_value: float,
) -> tuple[tuple[int, ...], FloatArray, FloatArray]:
    dimension = dgp.candidate_count
    remaining = tuple(
        index for index in range(dimension) if index != fixed_index
    )
    variance = float(dgp.covariance[fixed_index, fixed_index])
    cross = dgp.covariance[np.asarray(remaining), fixed_index]
    conditional_mean = (
        dgp.mean[np.asarray(remaining)]
        + cross / variance * (fixed_value - dgp.mean[fixed_index])
    )
    conditional_covariance = (
        dgp.covariance[np.ix_(remaining, remaining)]
        - np.outer(cross, cross) / variance
    )
    conditional_covariance = (
        conditional_covariance + conditional_covariance.T
    ) / 2.0
    return remaining, conditional_mean, conditional_covariance


def draw_conditional(
    dgp: D7GaussianDGP,
    fixed_index: int,
    fixed_value: float,
    size: int,
    rng: np.random.Generator,
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
    output = np.empty((size, dgp.candidate_count), dtype=float)
    output[:, fixed_index] = fixed_value
    output[:, np.asarray(remaining)] = draws
    return output


def draw_unconditional(
    dgp: D7GaussianDGP,
    size: int,
    rng: np.random.Generator,
) -> FloatArray:
    return rng.multivariate_normal(
        dgp.mean,
        dgp.covariance,
        size=size,
        method="cholesky",
    )


def _batch_slices(size: int, batches: int) -> list[slice]:
    edges = np.linspace(0, size, batches + 1, dtype=int)
    return [
        slice(int(edges[index]), int(edges[index + 1]))
        for index in range(batches)
    ]


def _batch_se(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    return float(np.std(array, ddof=1) / np.sqrt(array.size))


def contrast(
    scores: FloatArray,
    dgp: D7GaussianDGP,
    thresholds: FloatArray,
    trigger: float,
) -> float:
    state = policy_state(
        scores,
        thresholds,
        dgp.base_pool,
        dgp.full_pool,
        trigger,
    )
    return contrast_summary(state).delta_pi


def candidate_finite_difference(
    scores: FloatArray,
    dgp: D7GaussianDGP,
    thresholds: FloatArray,
    trigger: float,
    candidate: int,
    relative_step: float,
    batches: int,
) -> tuple[float, float, float]:
    step = float(relative_step * standard_deviations(dgp)[candidate])
    plus = thresholds.copy()
    minus = thresholds.copy()
    plus[candidate] += step
    minus[candidate] -= step
    estimate = (
        contrast(scores, dgp, plus, trigger)
        - contrast(scores, dgp, minus, trigger)
    ) / (2.0 * step)
    values = []
    for sl in _batch_slices(scores.shape[0], batches):
        values.append(
            (
                contrast(scores[sl], dgp, plus, trigger)
                - contrast(scores[sl], dgp, minus, trigger)
            )
            / (2.0 * step)
        )
    return float(estimate), _batch_se(values), step


def candidate_boundary_derivative(
    dgp: D7GaussianDGP,
    thresholds: FloatArray,
    trigger: float,
    candidate: int,
    size: int,
    seed: int,
    rho: float,
    batches: int,
) -> tuple[float, float, float]:
    scores = draw_conditional(
        dgp,
        candidate,
        float(thresholds[candidate]),
        size,
        np.random.default_rng(seed),
    )
    state = policy_state(
        scores,
        thresholds,
        dgp.base_pool,
        dgp.full_pool,
        trigger,
    )
    jump = candidate_threshold_jump_field(
        state,
        candidate,
        dgp.base_pool,
        dgp.full_pool,
    ).astype(float)
    values = (state.activation.astype(float) - rho) * jump
    density = marginal_density(
        dgp,
        candidate,
        float(thresholds[candidate]),
    )
    derivative = density * float(np.mean(values))
    batch_values = [
        density * float(np.mean(values[sl]))
        for sl in _batch_slices(size, batches)
    ]
    return float(derivative), _batch_se(batch_values), float(np.mean(values))


def trigger_density_decomposition(
    dgp: D7GaussianDGP,
    trigger: float,
) -> tuple[float, list[float]]:
    if len(dgp.base_pool) != 2:
        raise ValueError("preflight density decomposition expects two base candidates")
    terms = []
    for candidate in dgp.base_pool:
        other = next(index for index in dgp.base_pool if index != candidate)
        variance = float(dgp.covariance[candidate, candidate])
        conditional_mean = (
            dgp.mean[other]
            + dgp.covariance[other, candidate] / variance
            * (trigger - dgp.mean[candidate])
        )
        conditional_variance = (
            dgp.covariance[other, other]
            - dgp.covariance[other, candidate] ** 2 / variance
        )
        probability = float(
            norm.cdf(
                (trigger - conditional_mean)
                / np.sqrt(conditional_variance)
            )
        )
        terms.append(
            marginal_density(dgp, candidate, trigger) * probability
        )
    return float(sum(terms)), [float(value) for value in terms]


def trigger_finite_difference(
    scores: FloatArray,
    dgp: D7GaussianDGP,
    thresholds: FloatArray,
    trigger: float,
    relative_step: float,
    batches: int,
) -> tuple[float, float, float]:
    step = float(relative_step * np.mean(standard_deviations(dgp)))
    estimate = (
        contrast(scores, dgp, thresholds, trigger + step)
        - contrast(scores, dgp, thresholds, trigger - step)
    ) / (2.0 * step)
    values = []
    for sl in _batch_slices(scores.shape[0], batches):
        values.append(
            (
                contrast(
                    scores[sl],
                    dgp,
                    thresholds,
                    trigger + step,
                )
                - contrast(
                    scores[sl],
                    dgp,
                    thresholds,
                    trigger - step,
                )
            )
            / (2.0 * step)
        )
    return float(estimate), _batch_se(values), step


def trigger_boundary_derivative(
    dgp: D7GaussianDGP,
    thresholds: FloatArray,
    trigger: float,
    size: int,
    seed: int,
    mu: float,
    batches: int,
) -> tuple[float, float, float, float]:
    density, density_terms = trigger_density_decomposition(dgp, trigger)
    weighted_terms = []
    batch_derivatives = np.zeros(batches, dtype=float)

    for offset, candidate in enumerate(dgp.base_pool):
        scores = draw_conditional(
            dgp,
            candidate,
            trigger,
            size,
            np.random.default_rng(seed + offset),
        )
        state = policy_state(
            scores,
            thresholds,
            dgp.base_pool,
            dgp.full_pool,
            trigger,
        )
        indicator = (
            (state.base_winner == candidate)
            * state.incremental
        ).astype(float)
        candidate_density = marginal_density(dgp, candidate, trigger)
        weighted_terms.append(
            candidate_density * float(np.mean(indicator))
        )
        for batch_index, sl in enumerate(
            _batch_slices(size, batches)
        ):
            batch_derivatives[batch_index] += (
                candidate_density * float(np.mean(indicator[sl]))
            )

    derivative = density * mu - float(sum(weighted_terms))
    batch_values = density * mu - batch_derivatives
    conditional_m = float(sum(weighted_terms) / density)
    return (
        float(derivative),
        _batch_se(batch_values.tolist()),
        float(density),
        conditional_m,
    )


def maximum_density_finite_difference(
    dgp: D7GaussianDGP,
    trigger: float,
    step: float,
) -> float:
    return float(
        (
            base_maximum_cdf(dgp, trigger + step)
            - base_maximum_cdf(dgp, trigger - step)
        )
        / (2.0 * step)
    )


def coincidence_kink_check(
    scores: FloatArray,
    dgp: D7GaussianDGP,
    regular_thresholds: FloatArray,
    trigger: float,
    candidate: int,
    relative_step: float,
    conditional_size: int,
    seed: int,
    batches: int,
) -> dict[str, float]:
    coincident = regular_thresholds.copy()
    coincident[candidate] = trigger
    step = float(relative_step * standard_deviations(dgp)[candidate])
    base_value = contrast(scores, dgp, coincident, trigger)

    q_plus = coincident.copy()
    q_plus[candidate] += step

    d_q = (
        contrast(scores, dgp, q_plus, trigger) - base_value
    ) / step
    d_c = (
        contrast(scores, dgp, coincident, trigger + step) - base_value
    ) / step
    d_both = (
        contrast(scores, dgp, q_plus, trigger + step) - base_value
    ) / step
    empirical_kappa = float(d_q + d_c - d_both)

    conditional = draw_conditional(
        dgp,
        candidate,
        trigger,
        conditional_size,
        np.random.default_rng(seed),
    )
    state = policy_state(
        conditional,
        coincident,
        dgp.base_pool,
        dgp.full_pool,
        trigger,
    )
    relevance = coincidence_relevance_field(
        state,
        candidate,
        dgp.base_pool,
    ).astype(float)
    density = marginal_density(dgp, candidate, trigger)
    boundary_kappa = density * float(np.mean(relevance))

    batch_values = [
        density * float(np.mean(relevance[sl]))
        for sl in _batch_slices(conditional_size, batches)
    ]
    boundary_se = _batch_se(batch_values)

    return {
        "candidate": int(candidate),
        "step": step,
        "direction_q": float(d_q),
        "direction_c": float(d_c),
        "direction_both": float(d_both),
        "empirical_nonadditivity": empirical_kappa,
        "boundary_kappa": float(boundary_kappa),
        "boundary_kappa_se": float(boundary_se),
        "difference": float(empirical_kappa - boundary_kappa),
    }


def derivative_check(
    finite: float,
    finite_se: float,
    boundary: float,
    boundary_se: float,
    absolute_tolerance: float,
    multiplier: float,
) -> dict[str, Any]:
    combined = float(np.sqrt(finite_se**2 + boundary_se**2))
    tolerance = float(max(absolute_tolerance, multiplier * combined))
    difference = float(finite - boundary)
    return {
        "finite_difference": finite,
        "finite_difference_se": finite_se,
        "boundary_derivative": boundary,
        "boundary_derivative_se": boundary_se,
        "difference": difference,
        "combined_se": combined,
        "tolerance": tolerance,
        "pass": bool(abs(difference) <= tolerance),
    }


def run_preflight(
    *,
    unconditional_size: int,
    conditional_size: int,
    seed: int,
    relative_step: float,
    batches: int,
    absolute_tolerance: float,
    standard_error_multiplier: float,
) -> dict[str, Any]:
    dgp = default_dgp()
    validation = validate_dgp(dgp)
    thresholds = candidate_thresholds(dgp)
    trigger = trigger_threshold(dgp)
    separation = thresholds[np.asarray(dgp.base_pool)] - trigger

    scores = draw_unconditional(
        dgp,
        unconditional_size,
        np.random.default_rng(seed),
    )
    state = policy_state(
        scores,
        thresholds,
        dgp.base_pool,
        dgp.full_pool,
        trigger,
    )
    summary = contrast_summary(state)

    candidate_checks = []
    for candidate in dgp.full_pool:
        finite, finite_se, step = candidate_finite_difference(
            scores,
            dgp,
            thresholds,
            trigger,
            candidate,
            relative_step,
            batches,
        )
        boundary, boundary_se, beta = candidate_boundary_derivative(
            dgp,
            thresholds,
            trigger,
            candidate,
            conditional_size,
            seed + 100 + candidate,
            summary.rho,
            batches,
        )
        check = derivative_check(
            finite,
            finite_se,
            boundary,
            boundary_se,
            absolute_tolerance,
            standard_error_multiplier,
        )
        check.update(
            {
                "candidate": int(candidate),
                "step": float(step),
                "beta": float(beta),
            }
        )
        candidate_checks.append(check)

    finite_t, finite_t_se, trigger_step = trigger_finite_difference(
        scores,
        dgp,
        thresholds,
        trigger,
        relative_step,
        batches,
    )
    boundary_t, boundary_t_se, density_t, conditional_m = (
        trigger_boundary_derivative(
            dgp,
            thresholds,
            trigger,
            conditional_size,
            seed + 200,
            summary.mu,
            batches,
        )
    )
    trigger_check = derivative_check(
        finite_t,
        finite_t_se,
        boundary_t,
        boundary_t_se,
        absolute_tolerance,
        standard_error_multiplier,
    )
    trigger_check.update(
        {
            "step": float(trigger_step),
            "maximum_density": float(density_t),
            "conditional_incremental_probability": float(
                conditional_m
            ),
        }
    )

    density_fd = maximum_density_finite_difference(
        dgp,
        trigger,
        trigger_step,
    )
    density_difference = float(density_fd - density_t)
    density_pass = bool(abs(density_difference) <= 0.0025)

    kink = coincidence_kink_check(
        scores,
        dgp,
        thresholds,
        trigger,
        candidate=0,
        relative_step=relative_step,
        conditional_size=conditional_size,
        seed=seed + 300,
        batches=batches,
    )
    kink_tolerance = float(
        max(
            absolute_tolerance,
            standard_error_multiplier
            * float(kink["boundary_kappa_se"]),
        )
    )
    kink["tolerance"] = kink_tolerance
    kink["pass"] = bool(
        abs(float(kink["difference"])) <= kink_tolerance
        and float(kink["boundary_kappa"]) > 0.0
    )

    tie_count = int(
        np.sum(
            np.sort(
                scores[:, np.asarray(dgp.base_pool)],
                axis=1,
            )[:, -1]
            == np.sort(
                scores[:, np.asarray(dgp.base_pool)],
                axis=1,
            )[:, -2]
        )
    )

    checks = {
        "positive_definite_covariance": True,
        "regular_threshold_separation": bool(
            np.min(np.abs(separation)) > 0.10
        ),
        "no_observed_winner_ties": bool(tie_count == 0),
        "nonzero_contrast": bool(abs(summary.delta_pi) > 0.002),
        "candidate_derivatives": bool(
            all(item["pass"] for item in candidate_checks)
        ),
        "trigger_derivative": bool(trigger_check["pass"]),
        "maximum_density_decomposition": density_pass,
        "coincidence_kink": bool(kink["pass"]),
    }
    status = "PASS" if all(checks.values()) else "FAIL"

    return {
        "status": status,
        "role": "runtime-only mathematical and implementation preflight",
        "scientific_evidence": False,
        "settings": {
            "unconditional_size": int(unconditional_size),
            "conditional_size_per_boundary": int(conditional_size),
            "seed": int(seed),
            "relative_step": float(relative_step),
            "batches": int(batches),
            "absolute_tolerance": float(absolute_tolerance),
            "standard_error_multiplier": float(
                standard_error_multiplier
            ),
        },
        "dgp": {
            "mean": dgp.mean.tolist(),
            "covariance": dgp.covariance.tolist(),
            "base_pool": list(dgp.base_pool),
            "full_pool": list(dgp.full_pool),
            "alpha": dgp.alpha,
            "activation_rate": dgp.activation_rate,
            **validation,
        },
        "thresholds": {
            "candidate": thresholds.tolist(),
            "trigger": float(trigger),
            "base_candidate_minus_trigger": separation.tolist(),
            "minimum_absolute_separation": float(
                np.min(np.abs(separation))
            ),
        },
        "population_benchmark": {
            "e0": summary.e0,
            "rho": summary.rho,
            "mu": summary.mu,
            "nu": summary.nu,
            "pi_adaptive": summary.pi_adaptive,
            "pi_comparator": summary.pi_comparator,
            "delta_pi": summary.delta_pi,
        },
        "candidate_derivative_checks": candidate_checks,
        "trigger_derivative_check": trigger_check,
        "maximum_density_check": {
            "winner_region_decomposition": float(density_t),
            "cdf_finite_difference": float(density_fd),
            "difference": density_difference,
            "tolerance": 0.0025,
            "pass": density_pass,
        },
        "coincidence_kink_check": kink,
        "observed_winner_ties": tie_count,
        "checks": checks,
    }
