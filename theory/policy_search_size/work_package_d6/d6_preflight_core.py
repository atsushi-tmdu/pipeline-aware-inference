from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import norm

from d6_core import (
    candidate_threshold_jump_field,
    contrast_summary,
    policy_state,
)


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class GaussianDGP:
    mean: FloatArray
    covariance: FloatArray
    base_pool: tuple[int, ...]
    full_pool: tuple[int, ...]
    alpha: float
    activation_rate: float

    @property
    def candidate_count(self) -> int:
        return len(self.full_pool)


def default_gaussian_dgp() -> GaussianDGP:
    mean = np.array([0.0, 0.0, 0.08, 0.15], dtype=float)
    standard_deviation = np.array([1.0, 1.0, 0.9, 1.1], dtype=float)
    correlation = np.array(
        [
            [1.00, 0.55, -0.20, 0.65],
            [0.55, 1.00, 0.35, 0.25],
            [-0.20, 0.35, 1.00, -0.15],
            [0.65, 0.25, -0.15, 1.00],
        ],
        dtype=float,
    )
    covariance = (
        np.diag(standard_deviation)
        @ correlation
        @ np.diag(standard_deviation)
    )
    return GaussianDGP(
        mean=mean,
        covariance=covariance,
        base_pool=(0, 1),
        full_pool=(0, 1, 2),
        alpha=0.05,
        activation_rate=0.50,
    )


def validate_dgp(dgp: GaussianDGP) -> dict[str, float]:
    dimension = dgp.candidate_count + 1
    if dgp.mean.shape != (dimension,):
        raise ValueError("DGP mean has the wrong dimension")
    if dgp.covariance.shape != (dimension, dimension):
        raise ValueError("DGP covariance has the wrong dimension")
    if not np.allclose(dgp.covariance, dgp.covariance.T):
        raise ValueError("DGP covariance must be symmetric")
    eigenvalues = np.linalg.eigvalsh(dgp.covariance)
    if float(np.min(eigenvalues)) <= 0.0:
        raise ValueError("DGP covariance must be positive definite")
    if not 0.0 < dgp.alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 < dgp.activation_rate < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    if not set(dgp.base_pool).issubset(dgp.full_pool):
        raise ValueError("base_pool must be nested in full_pool")
    return {
        "minimum_covariance_eigenvalue": float(np.min(eigenvalues)),
        "maximum_covariance_eigenvalue": float(np.max(eigenvalues)),
    }


def marginal_standard_deviations(dgp: GaussianDGP) -> FloatArray:
    return np.sqrt(np.diag(dgp.covariance))


def population_thresholds(dgp: GaussianDGP) -> tuple[FloatArray, float]:
    standard_deviation = marginal_standard_deviations(dgp)
    candidate_probability = 1.0 - dgp.alpha
    activation_probability = 1.0 - dgp.activation_rate

    candidate_thresholds = (
        dgp.mean[1:]
        + standard_deviation[1:] * norm.ppf(candidate_probability)
    )
    activation_threshold = float(
        dgp.mean[0]
        + standard_deviation[0] * norm.ppf(activation_probability)
    )
    return candidate_thresholds.astype(float), activation_threshold


def marginal_density(
    dgp: GaussianDGP,
    variable_index: int,
    value: float,
) -> float:
    standard_deviation = marginal_standard_deviations(dgp)[variable_index]
    standardized = (value - dgp.mean[variable_index]) / standard_deviation
    return float(norm.pdf(standardized) / standard_deviation)


def draw_gaussian(
    dgp: GaussianDGP,
    size: int,
    rng: np.random.Generator,
) -> FloatArray:
    if size <= 0:
        raise ValueError("size must be positive")
    return rng.multivariate_normal(
        dgp.mean,
        dgp.covariance,
        size=size,
        method="cholesky",
    )


def conditional_gaussian_parameters(
    dgp: GaussianDGP,
    fixed_index: int,
    fixed_value: float,
) -> tuple[tuple[int, ...], FloatArray, FloatArray]:
    dimension = dgp.mean.size
    if fixed_index < 0 or fixed_index >= dimension:
        raise ValueError("fixed_index is out of range")
    remaining = tuple(index for index in range(dimension) if index != fixed_index)
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


def draw_conditional_gaussian(
    dgp: GaussianDGP,
    fixed_index: int,
    fixed_value: float,
    size: int,
    rng: np.random.Generator,
) -> FloatArray:
    if size <= 0:
        raise ValueError("size must be positive")
    remaining, conditional_mean, conditional_covariance = (
        conditional_gaussian_parameters(dgp, fixed_index, fixed_value)
    )
    draws = rng.multivariate_normal(
        conditional_mean,
        conditional_covariance,
        size=size,
        method="cholesky",
    )
    output = np.empty((size, dgp.mean.size), dtype=float)
    output[:, fixed_index] = fixed_value
    output[:, np.asarray(remaining)] = draws
    return output


def state_from_complete_vectors(
    complete_vectors: ArrayLike,
    dgp: GaussianDGP,
    candidate_thresholds: ArrayLike,
    activation_threshold: float,
):
    vectors = np.asarray(complete_vectors, dtype=float)
    if vectors.ndim != 2 or vectors.shape[1] != dgp.mean.size:
        raise ValueError("complete_vectors has the wrong shape")
    return policy_state(
        vectors[:, 1:],
        vectors[:, 0],
        candidate_thresholds,
        dgp.base_pool,
        dgp.full_pool,
        activation_threshold,
    )


def contrast_from_complete_vectors(
    complete_vectors: ArrayLike,
    dgp: GaussianDGP,
    candidate_thresholds: ArrayLike,
    activation_threshold: float,
) -> float:
    state = state_from_complete_vectors(
        complete_vectors,
        dgp,
        candidate_thresholds,
        activation_threshold,
    )
    return contrast_summary(state).delta_pi


def _batch_slices(size: int, batches: int) -> list[slice]:
    if batches <= 1 or batches > size:
        raise ValueError("batches must lie between 2 and size")
    edges = np.linspace(0, size, batches + 1, dtype=int)
    return [
        slice(int(edges[index]), int(edges[index + 1]))
        for index in range(batches)
    ]


def _standard_error_from_batch_values(values: ArrayLike) -> float:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size < 2:
        raise ValueError("at least two batch values are required")
    return float(np.std(array, ddof=1) / np.sqrt(array.size))


def finite_difference_candidate_derivative(
    complete_vectors: FloatArray,
    dgp: GaussianDGP,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
    candidate: int,
    relative_step: float,
    batches: int,
) -> tuple[float, float, float]:
    standard_deviation = marginal_standard_deviations(dgp)[candidate + 1]
    step = float(relative_step * standard_deviation)
    plus = candidate_thresholds.copy()
    minus = candidate_thresholds.copy()
    plus[candidate] += step
    minus[candidate] -= step

    estimate = (
        contrast_from_complete_vectors(
            complete_vectors,
            dgp,
            plus,
            activation_threshold,
        )
        - contrast_from_complete_vectors(
            complete_vectors,
            dgp,
            minus,
            activation_threshold,
        )
    ) / (2.0 * step)

    batch_values = []
    for batch in _batch_slices(complete_vectors.shape[0], batches):
        values = complete_vectors[batch]
        batch_values.append(
            (
                contrast_from_complete_vectors(
                    values,
                    dgp,
                    plus,
                    activation_threshold,
                )
                - contrast_from_complete_vectors(
                    values,
                    dgp,
                    minus,
                    activation_threshold,
                )
            )
            / (2.0 * step)
        )
    return float(estimate), _standard_error_from_batch_values(batch_values), step


def finite_difference_activation_derivative(
    complete_vectors: FloatArray,
    dgp: GaussianDGP,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
    relative_step: float,
    batches: int,
) -> tuple[float, float, float]:
    standard_deviation = marginal_standard_deviations(dgp)[0]
    step = float(relative_step * standard_deviation)
    estimate = (
        contrast_from_complete_vectors(
            complete_vectors,
            dgp,
            candidate_thresholds,
            activation_threshold + step,
        )
        - contrast_from_complete_vectors(
            complete_vectors,
            dgp,
            candidate_thresholds,
            activation_threshold - step,
        )
    ) / (2.0 * step)

    batch_values = []
    for batch in _batch_slices(complete_vectors.shape[0], batches):
        values = complete_vectors[batch]
        batch_values.append(
            (
                contrast_from_complete_vectors(
                    values,
                    dgp,
                    candidate_thresholds,
                    activation_threshold + step,
                )
                - contrast_from_complete_vectors(
                    values,
                    dgp,
                    candidate_thresholds,
                    activation_threshold - step,
                )
            )
            / (2.0 * step)
        )
    return float(estimate), _standard_error_from_batch_values(batch_values), step


def conditional_candidate_derivative(
    dgp: GaussianDGP,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
    candidate: int,
    size: int,
    seed: int,
    rho: float,
    batches: int,
) -> tuple[float, float, float, float]:
    rng = np.random.default_rng(seed)
    conditional = draw_conditional_gaussian(
        dgp,
        candidate + 1,
        float(candidate_thresholds[candidate]),
        size,
        rng,
    )
    state = state_from_complete_vectors(
        conditional,
        dgp,
        candidate_thresholds,
        activation_threshold,
    )
    jump = candidate_threshold_jump_field(
        state,
        candidate,
        dgp.base_pool,
        dgp.full_pool,
    ).astype(float)
    values = (state.activation.astype(float) - rho) * jump
    beta = float(np.mean(values))
    density = marginal_density(
        dgp,
        candidate + 1,
        float(candidate_thresholds[candidate]),
    )
    derivative = float(density * beta)

    batch_values = [
        density * float(np.mean(values[batch]))
        for batch in _batch_slices(size, batches)
    ]
    standard_error = _standard_error_from_batch_values(batch_values)
    nonzero_jump_rate = float(np.mean(jump != 0.0))
    return derivative, standard_error, beta, nonzero_jump_rate


def conditional_activation_derivative(
    dgp: GaussianDGP,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
    size: int,
    seed: int,
    mu: float,
    batches: int,
) -> tuple[float, float, float, float]:
    rng = np.random.default_rng(seed)
    conditional = draw_conditional_gaussian(
        dgp,
        0,
        activation_threshold,
        size,
        rng,
    )
    state = state_from_complete_vectors(
        conditional,
        dgp,
        candidate_thresholds,
        activation_threshold,
    )
    m = state.incremental.astype(float)
    conditional_mean = float(np.mean(m))
    beta = float(mu - conditional_mean)
    density = marginal_density(dgp, 0, activation_threshold)
    derivative = float(density * beta)

    batch_values = [
        density * (mu - float(np.mean(m[batch])))
        for batch in _batch_slices(size, batches)
    ]
    standard_error = _standard_error_from_batch_values(batch_values)
    return derivative, standard_error, beta, conditional_mean


def derivative_check(
    finite_difference: float,
    finite_difference_se: float,
    conditional: float,
    conditional_se: float,
    absolute_tolerance: float,
    standard_error_multiplier: float,
) -> dict[str, Any]:
    difference = float(finite_difference - conditional)
    combined_se = float(
        np.sqrt(finite_difference_se**2 + conditional_se**2)
    )
    tolerance = float(
        max(
            absolute_tolerance,
            standard_error_multiplier * combined_se,
        )
    )
    return {
        "finite_difference": float(finite_difference),
        "finite_difference_se": float(finite_difference_se),
        "conditional_boundary": float(conditional),
        "conditional_boundary_se": float(conditional_se),
        "difference": difference,
        "combined_se": combined_se,
        "tolerance": tolerance,
        "pass": bool(abs(difference) <= tolerance),
    }


def run_derivative_preflight(
    *,
    unconditional_size: int,
    conditional_size: int,
    seed: int,
    relative_step: float,
    batches: int,
    absolute_tolerance: float,
    standard_error_multiplier: float,
) -> dict[str, Any]:
    dgp = default_gaussian_dgp()
    dgp_validation = validate_dgp(dgp)
    candidate_thresholds, activation_threshold = population_thresholds(dgp)

    unconditional_rng = np.random.default_rng(seed)
    unconditional = draw_gaussian(
        dgp,
        unconditional_size,
        unconditional_rng,
    )
    population_state = state_from_complete_vectors(
        unconditional,
        dgp,
        candidate_thresholds,
        activation_threshold,
    )
    summary = contrast_summary(population_state)
    rho = summary.rho
    mu = summary.mu

    candidate_checks = []
    for candidate in dgp.full_pool:
        finite, finite_se, step = finite_difference_candidate_derivative(
            unconditional,
            dgp,
            candidate_thresholds,
            activation_threshold,
            candidate,
            relative_step,
            batches,
        )
        conditional, conditional_se, beta, jump_rate = (
            conditional_candidate_derivative(
                dgp,
                candidate_thresholds,
                activation_threshold,
                candidate,
                conditional_size,
                seed + 100 + candidate,
                rho,
                batches,
            )
        )
        check = derivative_check(
            finite,
            finite_se,
            conditional,
            conditional_se,
            absolute_tolerance,
            standard_error_multiplier,
        )
        check.update(
            {
                "candidate": int(candidate),
                "step": float(step),
                "beta": float(beta),
                "nonzero_jump_rate_at_boundary": float(jump_rate),
            }
        )
        candidate_checks.append(check)

    finite_c, finite_c_se, step_c = finite_difference_activation_derivative(
        unconditional,
        dgp,
        candidate_thresholds,
        activation_threshold,
        relative_step,
        batches,
    )
    conditional_c, conditional_c_se, beta_c, conditional_m = (
        conditional_activation_derivative(
            dgp,
            candidate_thresholds,
            activation_threshold,
            conditional_size,
            seed + 200,
            mu,
            batches,
        )
    )
    activation_check = derivative_check(
        finite_c,
        finite_c_se,
        conditional_c,
        conditional_c_se,
        absolute_tolerance,
        standard_error_multiplier,
    )
    activation_check.update(
        {
            "step": float(step_c),
            "beta": float(beta_c),
            "conditional_incremental_probability": float(conditional_m),
        }
    )

    winner_ties = int(
        np.sum(
            np.sort(unconditional[:, 1:3], axis=1)[:, -1]
            == np.sort(unconditional[:, 1:3], axis=1)[:, -2]
        )
        + np.sum(
            np.sort(unconditional[:, 1:4], axis=1)[:, -1]
            == np.sort(unconditional[:, 1:4], axis=1)[:, -2]
        )
    )

    checks = {
        "positive_definite_covariance": bool(
            dgp_validation["minimum_covariance_eigenvalue"] > 0.0
        ),
        "no_observed_winner_ties": bool(winner_ties == 0),
        "nonzero_contrast_benchmark": bool(abs(summary.delta_pi) >= 0.005),
        "candidate_derivatives": bool(
            all(item["pass"] for item in candidate_checks)
        ),
        "activation_derivative": bool(activation_check["pass"]),
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
            "standard_error_multiplier": float(standard_error_multiplier),
        },
        "dgp": {
            "mean": dgp.mean.tolist(),
            "covariance": dgp.covariance.tolist(),
            "base_pool": list(dgp.base_pool),
            "full_pool": list(dgp.full_pool),
            "alpha": dgp.alpha,
            "activation_rate": dgp.activation_rate,
            **dgp_validation,
        },
        "population_thresholds": {
            "candidate": candidate_thresholds.tolist(),
            "activation": float(activation_threshold),
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
        "observed_winner_ties": winner_ties,
        "candidate_derivative_checks": candidate_checks,
        "activation_derivative_check": activation_check,
        "checks": checks,
    }
