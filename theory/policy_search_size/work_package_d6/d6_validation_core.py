from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import norm

from d6_core import (
    D6PolicyState,
    candidate_threshold_jump_field,
    contrast_summary,
    tess_derivative,
    tess_transform,
    validate_nested_pools,
    winner_indices,
)


FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class ValidationDGP:
    name: str
    mean: FloatArray
    covariance: FloatArray
    base_pool: tuple[int, ...]
    full_pool: tuple[int, ...]

    @property
    def candidate_count(self) -> int:
        return len(self.full_pool)

    @property
    def dimension(self) -> int:
        return self.candidate_count + 1


@dataclass(frozen=True)
class ThresholdBundle:
    candidate: FloatArray
    activation: float
    candidate_indices_one_based: tuple[int, ...]
    candidate_plus_indices_one_based: tuple[int, ...]
    activation_index_one_based: int


@dataclass(frozen=True)
class PolicyEstimate:
    state: D6PolicyState
    e0: float
    rho: float
    mu: float
    nu: float
    pi_adaptive: float
    pi_comparator: float
    delta_pi: float
    delta_s: float


def _as_float_array(values: ArrayLike, label: str) -> FloatArray:
    array = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{label} must be finite")
    return array


def _candidate_means_and_sds(candidate_count: int) -> tuple[FloatArray, FloatArray]:
    if candidate_count <= 0:
        raise ValueError("candidate_count must be positive")
    j = np.arange(1, candidate_count + 1, dtype=float)
    means = (
        0.06 * np.sin(2.0 * np.pi * j / 20.0)
        + 0.02 * (((j.astype(int) - 1) % 3) - 1)
    )
    sds = 0.85 + 0.05 * ((j.astype(int) - 1) % 5)
    return means.astype(float), sds.astype(float)


def _latent_factor_dgp(name: str, specification: dict[str, Any]) -> ValidationDGP:
    candidate_count = 20
    base_pool = tuple(range(7))
    full_pool = tuple(range(candidate_count))
    means, sds = _candidate_means_and_sds(candidate_count)

    if name == "gain_coupled_k20":
        factor_names = ["H", "G", "B0", "O0", "O1", "O2"]
        base = specification["base_loadings"]
        optional = specification["optional_loadings"]
        base_block_count = int(base["block_count"])
        optional_block_count = int(optional["block_count"])
        if base_block_count != 1 or optional_block_count != 3:
            raise ValueError("unexpected gain-coupled block counts")
    elif name == "loss_coupled_k20":
        factor_names = ["H", "G", "B0", "B1", "O0", "O1", "O2", "O3"]
        base = specification["base_loadings"]
        optional = specification["optional_loadings"]
        base_block_count = int(base["block_count"])
        optional_block_count = int(optional["block_count"])
        if base_block_count != 2 or optional_block_count != 4:
            raise ValueError("unexpected loss-coupled block counts")
    else:
        raise ValueError(f"unsupported latent-factor DGP: {name}")

    factor_index = {factor: index for index, factor in enumerate(factor_names)}
    loadings = np.zeros((candidate_count + 1, len(factor_names)), dtype=float)

    activation_loading = float(specification["activation_loading"])
    loadings[0, factor_index["H"]] = activation_loading

    for candidate in range(candidate_count):
        row = candidate + 1
        if candidate < 7:
            loadings[row, factor_index["H"]] = float(base["activation_factor"])
            loadings[row, factor_index["G"]] = float(base["global_factor"])
            block = candidate % base_block_count
            loadings[row, factor_index[f"B{block}"]] = float(base["block_factor"])
        else:
            loadings[row, factor_index["H"]] = float(optional["activation_factor"])
            loadings[row, factor_index["G"]] = float(optional["global_factor"])
            block = (candidate - 7) % optional_block_count
            loadings[row, factor_index[f"O{block}"]] = float(
                optional["block_factor"]
            )

    residual_variance = 1.0 - np.sum(loadings**2, axis=1)
    if np.any(residual_variance <= 0.0):
        raise ValueError(f"{name}: nonpositive residual variance")

    standardized_covariance = (
        loadings @ loadings.T + np.diag(residual_variance)
    )
    scales = np.concatenate(([1.0], sds))
    covariance = (
        np.diag(scales)
        @ standardized_covariance
        @ np.diag(scales)
    )
    mean = np.concatenate(([0.0], means))
    return ValidationDGP(
        name=name,
        mean=mean,
        covariance=covariance,
        base_pool=base_pool,
        full_pool=full_pool,
    )


def build_dgps(config: dict[str, Any]) -> list[ValidationDGP]:
    output: list[ValidationDGP] = []
    for specification in config["dgps"]:
        name = str(specification["name"])
        if name == "transparent_k3":
            standard_deviation = _as_float_array(
                specification["standard_deviation"],
                "transparent standard deviations",
            )
            correlation = _as_float_array(
                specification["correlation"],
                "transparent correlation",
            )
            covariance = (
                np.diag(standard_deviation)
                @ correlation
                @ np.diag(standard_deviation)
            )
            dgp = ValidationDGP(
                name=name,
                mean=_as_float_array(specification["mean"], "transparent mean"),
                covariance=covariance,
                base_pool=(0, 1),
                full_pool=(0, 1, 2),
            )
        else:
            dgp = _latent_factor_dgp(name, specification)
        validate_dgp(dgp)
        output.append(dgp)
    return output


def validate_dgp(dgp: ValidationDGP) -> dict[str, float]:
    if dgp.mean.shape != (dgp.dimension,):
        raise ValueError(f"{dgp.name}: mean dimension mismatch")
    if dgp.covariance.shape != (dgp.dimension, dgp.dimension):
        raise ValueError(f"{dgp.name}: covariance dimension mismatch")
    if not np.allclose(dgp.covariance, dgp.covariance.T, atol=1e-12):
        raise ValueError(f"{dgp.name}: covariance is not symmetric")
    validate_nested_pools(
        dgp.base_pool,
        dgp.full_pool,
        dgp.candidate_count,
    )
    eigenvalues = np.linalg.eigvalsh(dgp.covariance)
    minimum = float(np.min(eigenvalues))
    if minimum <= 0.0:
        raise ValueError(f"{dgp.name}: covariance is not positive definite")
    return {
        "minimum_covariance_eigenvalue": minimum,
        "maximum_covariance_eigenvalue": float(np.max(eigenvalues)),
    }


def population_thresholds(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
) -> tuple[FloatArray, float]:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 < activation_rate < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    standard_deviation = np.sqrt(np.diag(dgp.covariance))
    candidate = (
        dgp.mean[1:]
        + standard_deviation[1:] * norm.ppf(1.0 - alpha)
    )
    activation = float(
        dgp.mean[0]
        + standard_deviation[0] * norm.ppf(1.0 - activation_rate)
    )
    return candidate.astype(float), activation


def empirical_quantile_index(size: int, probability: float) -> int:
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    return int(min(size, max(1, np.ceil(size * probability))))


def plus_one_threshold_index(size: int, alpha: float) -> int:
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    critical_count = int(np.ceil((size + 1) * alpha))
    if critical_count <= 1:
        raise ValueError("strict plus-one rejection is unattainable")
    index = size + 2 - critical_count
    if index < 1 or index > size:
        raise RuntimeError("plus-one threshold index is out of range")
    return int(index)


def _order_statistic(values: FloatArray, index_one_based: int) -> float:
    if values.ndim != 1 or values.size == 0:
        raise ValueError("values must be a nonempty vector")
    if index_one_based < 1 or index_one_based > values.size:
        raise ValueError("order-statistic index is out of range")
    return float(np.partition(values, index_one_based - 1)[index_one_based - 1])


def empirical_threshold_bundle(
    reference: ArrayLike,
    alpha: float,
    activation_rate: float,
) -> tuple[ThresholdBundle, FloatArray]:
    matrix = _as_float_array(reference, "reference")
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        raise ValueError("reference must be a complete-vector matrix")
    size = matrix.shape[0]
    candidate_probability = 1.0 - alpha
    activation_probability = 1.0 - activation_rate

    q_index = empirical_quantile_index(size, candidate_probability)
    plus_index = plus_one_threshold_index(size, alpha)
    activation_index = empirical_quantile_index(size, activation_probability)

    q = np.array(
        [
            _order_statistic(matrix[:, candidate + 1], q_index)
            for candidate in range(matrix.shape[1] - 1)
        ],
        dtype=float,
    )
    q_plus = np.array(
        [
            _order_statistic(matrix[:, candidate + 1], plus_index)
            for candidate in range(matrix.shape[1] - 1)
        ],
        dtype=float,
    )
    activation = _order_statistic(matrix[:, 0], activation_index)
    bundle = ThresholdBundle(
        candidate=q,
        activation=activation,
        candidate_indices_one_based=tuple(
            q_index for _ in range(matrix.shape[1] - 1)
        ),
        candidate_plus_indices_one_based=tuple(
            plus_index for _ in range(matrix.shape[1] - 1)
        ),
        activation_index_one_based=activation_index,
    )
    return bundle, q_plus


def draw_complete_vectors(
    dgp: ValidationDGP,
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


def _policy_state_from_thresholds(
    complete_vectors: FloatArray,
    dgp: ValidationDGP,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
) -> D6PolicyState:
    scores = complete_vectors[:, 1:]
    base_winner = winner_indices(scores, dgp.base_pool)
    full_winner = winner_indices(scores, dgp.full_pool)
    rows = np.arange(scores.shape[0])
    base_reject = (
        scores[rows, base_winner]
        > candidate_thresholds[base_winner]
    )
    full_reject = (
        scores[rows, full_winner]
        > candidate_thresholds[full_winner]
    )
    activation = complete_vectors[:, 0] > activation_threshold
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


def policy_estimate(
    complete_vectors: ArrayLike,
    dgp: ValidationDGP,
    candidate_thresholds: ArrayLike,
    activation_threshold: float,
    alpha: float,
) -> PolicyEstimate:
    matrix = _as_float_array(complete_vectors, "complete_vectors")
    candidate = _as_float_array(
        candidate_thresholds,
        "candidate_thresholds",
    )
    if matrix.shape != (matrix.shape[0], dgp.dimension):
        raise ValueError("complete_vectors dimension mismatch")
    if candidate.shape != (dgp.candidate_count,):
        raise ValueError("candidate threshold dimension mismatch")
    state = _policy_state_from_thresholds(
        matrix,
        dgp,
        candidate,
        float(activation_threshold),
    )
    summary = contrast_summary(state)
    delta_s = float(
        tess_transform(summary.pi_adaptive, alpha)
        - tess_transform(summary.pi_comparator, alpha)
    )
    return PolicyEstimate(
        state=state,
        e0=summary.e0,
        rho=summary.rho,
        mu=summary.mu,
        nu=summary.nu,
        pi_adaptive=summary.pi_adaptive,
        pi_comparator=summary.pi_comparator,
        delta_pi=summary.delta_pi,
        delta_s=delta_s,
    )


def conditional_gaussian_parameters(
    dgp: ValidationDGP,
    fixed_index: int,
    fixed_value: float,
) -> tuple[IntArray, FloatArray, FloatArray]:
    if fixed_index < 0 or fixed_index >= dgp.dimension:
        raise ValueError("fixed_index is out of range")
    remaining = np.array(
        [index for index in range(dgp.dimension) if index != fixed_index],
        dtype=np.int64,
    )
    variance = float(dgp.covariance[fixed_index, fixed_index])
    cross = dgp.covariance[remaining, fixed_index]
    conditional_mean = (
        dgp.mean[remaining]
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


def draw_conditional_vectors(
    dgp: ValidationDGP,
    fixed_index: int,
    fixed_value: float,
    size: int,
    rng: np.random.Generator,
) -> FloatArray:
    remaining, mean, covariance = conditional_gaussian_parameters(
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
    output = np.empty((size, dgp.dimension), dtype=float)
    output[:, fixed_index] = fixed_value
    output[:, remaining] = draws
    return output


def _marginal_density(
    dgp: ValidationDGP,
    variable_index: int,
    value: float,
) -> float:
    sd = float(np.sqrt(dgp.covariance[variable_index, variable_index]))
    standardized = (value - dgp.mean[variable_index]) / sd
    return float(norm.pdf(standardized) / sd)


def _batch_sizes(total: int, batches: int) -> list[int]:
    if total <= 0 or batches <= 0:
        raise ValueError("total and batches must be positive")
    batches = min(total, batches)
    quotient, remainder = divmod(total, batches)
    return [
        quotient + (1 if index < remainder else 0)
        for index in range(batches)
    ]


def _seed_rng(*components: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(list(components)))


def _batch_se(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=float)
    if array.size < 2:
        return 0.0
    return float(np.std(array, ddof=1) / np.sqrt(array.size))


def _summarize_state_batches(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    total_draws: int,
    batches: int,
    seed_components: tuple[int, ...],
) -> dict[str, Any]:
    q, c = population_thresholds(dgp, alpha, activation_rate)
    totals = {
        "count": 0,
        "r0": 0.0,
        "a": 0.0,
        "m": 0.0,
        "am": 0.0,
        "adaptive": 0.0,
    }
    base_winner_counts = np.zeros(dgp.candidate_count, dtype=np.int64)
    full_winner_counts = np.zeros(dgp.candidate_count, dtype=np.int64)
    batch_records: list[dict[str, float]] = []

    rng = _seed_rng(*seed_components)
    for size in _batch_sizes(total_draws, batches):
        vectors = draw_complete_vectors(dgp, size, rng)
        estimate = policy_estimate(vectors, dgp, q, c, alpha)
        state = estimate.state
        totals["count"] += size
        totals["r0"] += float(np.sum(state.base_reject))
        totals["a"] += float(np.sum(state.activation))
        totals["m"] += float(np.sum(state.incremental))
        totals["am"] += float(
            np.sum(state.activation & state.incremental)
        )
        totals["adaptive"] += float(np.sum(state.adaptive_reject))
        base_winner_counts += np.bincount(
            state.base_winner,
            minlength=dgp.candidate_count,
        )
        full_winner_counts += np.bincount(
            state.full_winner,
            minlength=dgp.candidate_count,
        )
        batch_records.append(
            {
                "e0": estimate.e0,
                "rho": estimate.rho,
                "mu": estimate.mu,
                "nu": estimate.nu,
                "pi_adaptive": estimate.pi_adaptive,
                "pi_comparator": estimate.pi_comparator,
                "delta_pi": estimate.delta_pi,
                "delta_s": estimate.delta_s,
            }
        )

    count = float(totals["count"])
    e0 = totals["r0"] / count
    rho = totals["a"] / count
    mu = totals["m"] / count
    nu = totals["am"] / count
    pi_adaptive = totals["adaptive"] / count
    pi_comparator = e0 + rho * mu
    delta_pi = pi_adaptive - pi_comparator
    delta_s = (
        tess_transform(pi_adaptive, alpha)
        - tess_transform(pi_comparator, alpha)
    )
    return {
        "candidate_thresholds": q,
        "activation_threshold": c,
        "e0": float(e0),
        "rho": float(rho),
        "mu": float(mu),
        "nu": float(nu),
        "pi_adaptive": float(pi_adaptive),
        "pi_comparator": float(pi_comparator),
        "delta_pi": float(delta_pi),
        "delta_s": float(delta_s),
        "base_winner_frequencies": (
            base_winner_counts / count
        ).astype(float),
        "full_winner_frequencies": (
            full_winner_counts / count
        ).astype(float),
        "batch_se": {
            key: _batch_se(record[key] for record in batch_records)
            for key in batch_records[0]
        },
    }


def _estimate_boundary_coefficients(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    summary: dict[str, Any],
    conditional_draws: int,
    batches: int,
    seed_root: int,
    dgp_index: int,
    alpha_index: int,
) -> dict[str, Any]:
    q = np.asarray(summary["candidate_thresholds"], dtype=float)
    c = float(summary["activation_threshold"])
    rho = float(summary["rho"])
    mu = float(summary["mu"])

    beta_delta = np.zeros(dgp.candidate_count, dtype=float)
    beta_adaptive = np.zeros(dgp.candidate_count, dtype=float)
    beta_comparator = np.zeros(dgp.candidate_count, dtype=float)
    candidate_se = np.zeros((dgp.candidate_count, 3), dtype=float)
    jump_rates = np.zeros(dgp.candidate_count, dtype=float)

    for candidate in range(dgp.candidate_count):
        values_delta: list[float] = []
        values_adaptive: list[float] = []
        values_comparator: list[float] = []
        jumps_nonzero = 0
        total = 0
        rng = _seed_rng(
            seed_root,
            dgp_index,
            alpha_index,
            20,
            candidate,
        )
        for size in _batch_sizes(conditional_draws, batches):
            vectors = draw_conditional_vectors(
                dgp,
                candidate + 1,
                float(q[candidate]),
                size,
                rng,
            )
            state = _policy_state_from_thresholds(
                vectors,
                dgp,
                q,
                c,
            )
            jump = candidate_threshold_jump_field(
                state,
                candidate,
                dgp.base_pool,
                dgp.full_pool,
            ).astype(float)
            b0 = (
                (candidate in dgp.base_pool)
                & (state.base_winner == candidate)
            ).astype(float)
            activation = state.activation.astype(float)
            values_delta.append(
                float(np.mean((activation - rho) * jump))
            )
            values_adaptive.append(
                float(np.mean(-b0 + activation * jump))
            )
            values_comparator.append(
                float(np.mean(-b0 + rho * jump))
            )
            jumps_nonzero += int(np.sum(jump != 0.0))
            total += size

        beta_delta[candidate] = float(np.mean(values_delta))
        beta_adaptive[candidate] = float(np.mean(values_adaptive))
        beta_comparator[candidate] = float(np.mean(values_comparator))
        candidate_se[candidate, 0] = _batch_se(values_delta)
        candidate_se[candidate, 1] = _batch_se(values_adaptive)
        candidate_se[candidate, 2] = _batch_se(values_comparator)
        jump_rates[candidate] = jumps_nonzero / total

    conditional_m_values: list[float] = []
    rng = _seed_rng(seed_root, dgp_index, alpha_index, 30)
    for size in _batch_sizes(conditional_draws, batches):
        vectors = draw_conditional_vectors(
            dgp,
            0,
            c,
            size,
            rng,
        )
        state = _policy_state_from_thresholds(vectors, dgp, q, c)
        conditional_m_values.append(float(np.mean(state.incremental)))

    conditional_m = float(np.mean(conditional_m_values))
    beta_c_delta = float(mu - conditional_m)
    beta_c_adaptive = float(-conditional_m)
    beta_c_comparator = float(-mu)
    beta_c_se = _batch_se(conditional_m_values)

    return {
        "beta_delta": beta_delta,
        "beta_adaptive": beta_adaptive,
        "beta_comparator": beta_comparator,
        "beta_c_delta": beta_c_delta,
        "beta_c_adaptive": beta_c_adaptive,
        "beta_c_comparator": beta_c_comparator,
        "candidate_beta_batch_se": candidate_se,
        "activation_conditional_m_batch_se": beta_c_se,
        "conditional_incremental_probability": conditional_m,
        "candidate_nonzero_jump_rates": jump_rates,
    }


def _influence_variance_benchmark(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    summary: dict[str, Any],
    coefficients: dict[str, Any],
    total_draws: int,
    batches: int,
    seed_components: tuple[int, ...],
) -> dict[str, Any]:
    q = np.asarray(summary["candidate_thresholds"], dtype=float)
    c = float(summary["activation_threshold"])
    p = 1.0 - alpha
    s = 1.0 - activation_rate

    e0 = float(summary["e0"])
    rho = float(summary["rho"])
    mu = float(summary["mu"])
    pi_a = float(summary["pi_adaptive"])
    pi_c = float(summary["pi_comparator"])
    delta = float(summary["delta_pi"])

    beta_delta = np.asarray(coefficients["beta_delta"], dtype=float)
    beta_a = np.asarray(coefficients["beta_adaptive"], dtype=float)
    beta_cand_c = np.asarray(
        coefficients["beta_comparator"],
        dtype=float,
    )
    beta_u_delta = float(coefficients["beta_c_delta"])
    beta_u_a = float(coefficients["beta_c_adaptive"])
    beta_u_c = float(coefficients["beta_c_comparator"])

    sums = {
        "eval_delta_2": 0.0,
        "ref_delta_2": 0.0,
        "eval_s_2": 0.0,
        "ref_s_2": 0.0,
        "eval_a_2": 0.0,
        "eval_c_2": 0.0,
        "ref_a_2": 0.0,
        "ref_c_2": 0.0,
        "count": 0,
    }
    batch_values: dict[str, list[float]] = {
        key: [] for key in sums if key != "count"
    }

    derivative_a = tess_derivative(pi_a, alpha)
    derivative_c = tess_derivative(pi_c, alpha)

    rng = _seed_rng(*seed_components)
    for size in _batch_sizes(total_draws, batches):
        vectors = draw_complete_vectors(dgp, size, rng)
        state = _policy_state_from_thresholds(vectors, dgp, q, c)
        r0 = state.base_reject.astype(float)
        activation = state.activation.astype(float)
        incremental = state.incremental.astype(float)
        am = activation * incremental

        phi_eval_delta = (
            (activation - rho) * (incremental - mu) - delta
        )
        phi_eval_a = r0 + am - pi_a
        phi_eval_c = (
            (r0 - e0)
            + mu * (activation - rho)
            + rho * (incremental - mu)
        )
        phi_eval_s = (
            derivative_a * phi_eval_a
            - derivative_c * phi_eval_c
        )

        candidate_indicators = (
            p - (vectors[:, 1:] <= q).astype(float)
        )
        activation_indicator = (
            s - (vectors[:, 0] <= c).astype(float)
        )
        phi_ref_delta = (
            candidate_indicators @ beta_delta
            + beta_u_delta * activation_indicator
        )
        phi_ref_a = (
            candidate_indicators @ beta_a
            + beta_u_a * activation_indicator
        )
        phi_ref_c = (
            candidate_indicators @ beta_cand_c
            + beta_u_c * activation_indicator
        )
        phi_ref_s = (
            derivative_a * phi_ref_a
            - derivative_c * phi_ref_c
        )

        arrays = {
            "eval_delta_2": phi_eval_delta**2,
            "ref_delta_2": phi_ref_delta**2,
            "eval_s_2": phi_eval_s**2,
            "ref_s_2": phi_ref_s**2,
            "eval_a_2": phi_eval_a**2,
            "eval_c_2": phi_eval_c**2,
            "ref_a_2": phi_ref_a**2,
            "ref_c_2": phi_ref_c**2,
        }
        for key, array in arrays.items():
            value = float(np.mean(array))
            sums[key] += float(np.sum(array))
            batch_values[key].append(value)
        sums["count"] += size

    count = float(sums["count"])
    return {
        "var_phi_eval_delta": sums["eval_delta_2"] / count,
        "var_phi_ref_delta": sums["ref_delta_2"] / count,
        "var_phi_eval_s": sums["eval_s_2"] / count,
        "var_phi_ref_s": sums["ref_s_2"] / count,
        "var_phi_eval_adaptive": sums["eval_a_2"] / count,
        "var_phi_eval_comparator": sums["eval_c_2"] / count,
        "var_phi_ref_adaptive": sums["ref_a_2"] / count,
        "var_phi_ref_comparator": sums["ref_c_2"] / count,
        "batch_se": {
            key: _batch_se(values)
            for key, values in batch_values.items()
        },
    }


def compute_population_benchmark(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    benchmark_config: dict[str, Any],
    seed_root: int,
    dgp_index: int,
    alpha_index: int,
) -> dict[str, Any]:
    unconditional_draws = int(
        benchmark_config["unconditional_draws_per_dgp"]
    )
    conditional_draws = int(
        benchmark_config["conditional_draws_per_boundary"]
    )
    batches = int(benchmark_config["batches"])

    summary = _summarize_state_batches(
        dgp,
        alpha,
        activation_rate,
        unconditional_draws,
        batches,
        (seed_root, dgp_index, alpha_index, 10),
    )
    coefficients = _estimate_boundary_coefficients(
        dgp,
        alpha,
        activation_rate,
        summary,
        conditional_draws,
        batches,
        seed_root,
        dgp_index,
        alpha_index,
    )
    influence = _influence_variance_benchmark(
        dgp,
        alpha,
        activation_rate,
        summary,
        coefficients,
        unconditional_draws,
        batches,
        (seed_root, dgp_index, alpha_index, 40),
    )
    validation = validate_dgp(dgp)
    return {
        "dgp": dgp.name,
        "alpha": float(alpha),
        "activation_rate": float(activation_rate),
        "candidate_count": dgp.candidate_count,
        "base_count": len(dgp.base_pool),
        "candidate_thresholds": np.asarray(
            summary["candidate_thresholds"],
            dtype=float,
        ).tolist(),
        "activation_threshold": float(summary["activation_threshold"]),
        "population": {
            key: float(summary[key])
            for key in [
                "e0",
                "rho",
                "mu",
                "nu",
                "pi_adaptive",
                "pi_comparator",
                "delta_pi",
                "delta_s",
            ]
        },
        "population_batch_se": {
            key: float(value)
            for key, value in summary["batch_se"].items()
        },
        "base_winner_frequencies": np.asarray(
            summary["base_winner_frequencies"],
            dtype=float,
        ).tolist(),
        "full_winner_frequencies": np.asarray(
            summary["full_winner_frequencies"],
            dtype=float,
        ).tolist(),
        "coefficients": {
            "beta_delta": np.asarray(
                coefficients["beta_delta"],
                dtype=float,
            ).tolist(),
            "beta_adaptive": np.asarray(
                coefficients["beta_adaptive"],
                dtype=float,
            ).tolist(),
            "beta_comparator": np.asarray(
                coefficients["beta_comparator"],
                dtype=float,
            ).tolist(),
            "beta_c_delta": float(coefficients["beta_c_delta"]),
            "beta_c_adaptive": float(
                coefficients["beta_c_adaptive"]
            ),
            "beta_c_comparator": float(
                coefficients["beta_c_comparator"]
            ),
            "conditional_incremental_probability": float(
                coefficients["conditional_incremental_probability"]
            ),
            "candidate_nonzero_jump_rates": np.asarray(
                coefficients["candidate_nonzero_jump_rates"],
                dtype=float,
            ).tolist(),
            "candidate_beta_batch_se": np.asarray(
                coefficients["candidate_beta_batch_se"],
                dtype=float,
            ).tolist(),
            "activation_conditional_m_batch_se": float(
                coefficients["activation_conditional_m_batch_se"]
            ),
        },
        "influence": {
            key: float(value)
            for key, value in influence.items()
            if key != "batch_se"
        },
        "influence_batch_se": {
            key: float(value)
            for key, value in influence["batch_se"].items()
        },
        "dgp_validation": validation,
        "benchmark_draws": {
            "unconditional": unconditional_draws,
            "conditional_per_boundary": conditional_draws,
            "batches": batches,
        },
    }


def _sample_variance(values: FloatArray) -> float:
    if values.size < 2:
        return 0.0
    return float(np.var(values, ddof=1))


def _estimated_influence_variances(
    reference: FloatArray,
    evaluation: FloatArray,
    estimate: PolicyEstimate,
    candidate_thresholds: FloatArray,
    activation_threshold: float,
    alpha: float,
    activation_rate: float,
    benchmark: dict[str, Any],
) -> dict[str, float]:
    coefficients = benchmark["coefficients"]
    beta_delta = np.asarray(coefficients["beta_delta"], dtype=float)
    beta_a = np.asarray(coefficients["beta_adaptive"], dtype=float)
    beta_c = np.asarray(coefficients["beta_comparator"], dtype=float)
    beta_u_delta = float(coefficients["beta_c_delta"])
    beta_u_a = float(coefficients["beta_c_adaptive"])
    beta_u_c = float(coefficients["beta_c_comparator"])

    p = 1.0 - alpha
    s = 1.0 - activation_rate
    candidate_indicators = (
        p - (reference[:, 1:] <= candidate_thresholds).astype(float)
    )
    activation_indicator = (
        s - (reference[:, 0] <= activation_threshold).astype(float)
    )
    phi_ref_delta = (
        candidate_indicators @ beta_delta
        + beta_u_delta * activation_indicator
    )
    phi_ref_a = (
        candidate_indicators @ beta_a
        + beta_u_a * activation_indicator
    )
    phi_ref_c = (
        candidate_indicators @ beta_c
        + beta_u_c * activation_indicator
    )

    state = estimate.state
    r0 = state.base_reject.astype(float)
    activation = state.activation.astype(float)
    incremental = state.incremental.astype(float)
    am = activation * incremental
    phi_eval_delta = (
        (activation - estimate.rho)
        * (incremental - estimate.mu)
        - estimate.delta_pi
    )
    phi_eval_a = r0 + am - estimate.pi_adaptive
    phi_eval_c = (
        (r0 - estimate.e0)
        + estimate.mu * (activation - estimate.rho)
        + estimate.rho * (incremental - estimate.mu)
    )

    derivative_a = tess_derivative(estimate.pi_adaptive, alpha)
    derivative_c = tess_derivative(estimate.pi_comparator, alpha)
    phi_eval_s = (
        derivative_a * phi_eval_a - derivative_c * phi_eval_c
    )
    phi_ref_s = (
        derivative_a * phi_ref_a - derivative_c * phi_ref_c
    )

    reference_size = reference.shape[0]
    evaluation_size = evaluation.shape[0]
    var_eval_delta = _sample_variance(phi_eval_delta)
    var_ref_delta = _sample_variance(phi_ref_delta)
    var_eval_s = _sample_variance(phi_eval_s)
    var_ref_s = _sample_variance(phi_ref_s)
    return {
        "var_eval_delta_per_observation": var_eval_delta,
        "var_ref_delta_per_observation": var_ref_delta,
        "var_total_delta": (
            var_eval_delta / evaluation_size
            + var_ref_delta / reference_size
        ),
        "var_eval_only_delta": var_eval_delta / evaluation_size,
        "var_eval_s_per_observation": var_eval_s,
        "var_ref_s_per_observation": var_ref_s,
        "var_total_s": (
            var_eval_s / evaluation_size
            + var_ref_s / reference_size
        ),
        "var_eval_only_s": var_eval_s / evaluation_size,
    }


def _bridge_support_check(
    evaluation_scores: FloatArray,
    regular_thresholds: FloatArray,
    plus_thresholds: FloatArray,
    regular_state: D6PolicyState,
    plus_state: D6PolicyState,
) -> dict[str, Any]:
    low = np.minimum(regular_thresholds, plus_thresholds)
    high = np.maximum(regular_thresholds, plus_thresholds)
    interval_union = np.any(
        (evaluation_scores > low) & (evaluation_scores <= high),
        axis=1,
    )
    disagreement = (
        (regular_state.base_reject != plus_state.base_reject)
        | (regular_state.full_reject != plus_state.full_reject)
        | (regular_state.incremental != plus_state.incremental)
        | (regular_state.adaptive_reject != plus_state.adaptive_reject)
    )
    violations = int(np.sum(disagreement & (~interval_union)))
    return {
        "interval_union_probability": float(np.mean(interval_union)),
        "pathwise_disagreement_probability": float(np.mean(disagreement)),
        "support_violation_count": violations,
    }


def run_outer_replication(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    reference_size: int,
    evaluation_size: int,
    seed_components: tuple[int, ...],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    seed_sequence = np.random.SeedSequence(list(seed_components))
    reference_seed, evaluation_seed = seed_sequence.spawn(2)
    reference_rng = np.random.default_rng(reference_seed)
    evaluation_rng = np.random.default_rng(evaluation_seed)
    reference = draw_complete_vectors(dgp, reference_size, reference_rng)
    evaluation = draw_complete_vectors(dgp, evaluation_size, evaluation_rng)

    bundle, plus_thresholds = empirical_threshold_bundle(
        reference,
        alpha,
        activation_rate,
    )
    regular = policy_estimate(
        evaluation,
        dgp,
        bundle.candidate,
        bundle.activation,
        alpha,
    )
    plus = policy_estimate(
        evaluation,
        dgp,
        plus_thresholds,
        bundle.activation,
        alpha,
    )
    influence = _estimated_influence_variances(
        reference,
        evaluation,
        regular,
        bundle.candidate,
        bundle.activation,
        alpha,
        activation_rate,
        benchmark,
    )
    support = _bridge_support_check(
        evaluation[:, 1:],
        bundle.candidate,
        plus_thresholds,
        regular.state,
        plus.state,
    )

    true_delta = float(benchmark["population"]["delta_pi"])
    true_s = float(benchmark["population"]["delta_s"])
    se_delta = float(np.sqrt(max(0.0, influence["var_total_delta"])))
    se_s = float(np.sqrt(max(0.0, influence["var_total_s"])))
    se_eval_delta = float(
        np.sqrt(max(0.0, influence["var_eval_only_delta"]))
    )
    se_eval_s = float(
        np.sqrt(max(0.0, influence["var_eval_only_s"]))
    )
    z = float(norm.ppf(0.975))

    covariance_error = abs(
        regular.delta_pi
        - (
            regular.nu - regular.rho * regular.mu
        )
    )
    return {
        "delta_pi_regular": regular.delta_pi,
        "delta_s_regular": regular.delta_s,
        "delta_pi_plus": plus.delta_pi,
        "delta_s_plus": plus.delta_s,
        "bridge_delta_pi": plus.delta_pi - regular.delta_pi,
        "bridge_delta_s": plus.delta_s - regular.delta_s,
        "pi_adaptive": regular.pi_adaptive,
        "pi_comparator": regular.pi_comparator,
        "e0": regular.e0,
        "rho": regular.rho,
        "mu": regular.mu,
        "nu": regular.nu,
        "var_total_delta_hat": influence["var_total_delta"],
        "var_eval_only_delta_hat": influence["var_eval_only_delta"],
        "var_total_s_hat": influence["var_total_s"],
        "var_eval_only_s_hat": influence["var_eval_only_s"],
        "se_total_delta_hat": se_delta,
        "se_eval_only_delta_hat": se_eval_delta,
        "se_total_s_hat": se_s,
        "se_eval_only_s_hat": se_eval_s,
        "cover_normal_delta": int(
            regular.delta_pi - z * se_delta
            <= true_delta
            <= regular.delta_pi + z * se_delta
        ),
        "cover_eval_only_delta": int(
            regular.delta_pi - z * se_eval_delta
            <= true_delta
            <= regular.delta_pi + z * se_eval_delta
        ),
        "cover_normal_s": int(
            regular.delta_s - z * se_s
            <= true_s
            <= regular.delta_s + z * se_s
        ),
        "cover_eval_only_s": int(
            regular.delta_s - z * se_eval_s
            <= true_s
            <= regular.delta_s + z * se_eval_s
        ),
        "regular_quantile_index": bundle.candidate_indices_one_based[0],
        "plus_one_index": bundle.candidate_plus_indices_one_based[0],
        "activation_quantile_index": bundle.activation_index_one_based,
        "maximum_candidate_threshold_gap": float(
            np.max(np.abs(plus_thresholds - bundle.candidate))
        ),
        "covariance_identity_error": float(covariance_error),
        **support,
    }


def _bootstrap_one(
    reference: FloatArray,
    evaluation: FloatArray,
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    reference_indices = rng.integers(
        0,
        reference.shape[0],
        size=reference.shape[0],
    )
    evaluation_indices = rng.integers(
        0,
        evaluation.shape[0],
        size=evaluation.shape[0],
    )
    reference_star = reference[reference_indices]
    evaluation_star = evaluation[evaluation_indices]
    bundle, _ = empirical_threshold_bundle(
        reference_star,
        alpha,
        activation_rate,
    )
    estimate = policy_estimate(
        evaluation_star,
        dgp,
        bundle.candidate,
        bundle.activation,
        alpha,
    )
    return estimate.delta_pi, estimate.delta_s


def run_bootstrap_outer_dataset(
    dgp: ValidationDGP,
    alpha: float,
    activation_rate: float,
    reference_size: int,
    evaluation_size: int,
    resamples: int,
    outer_seed_components: tuple[int, ...],
    resample_seed_components: tuple[int, ...],
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    outer_sequence = np.random.SeedSequence(list(outer_seed_components))
    reference_seed, evaluation_seed = outer_sequence.spawn(2)
    reference = draw_complete_vectors(
        dgp,
        reference_size,
        np.random.default_rng(reference_seed),
    )
    evaluation = draw_complete_vectors(
        dgp,
        evaluation_size,
        np.random.default_rng(evaluation_seed),
    )
    bundle, _ = empirical_threshold_bundle(
        reference,
        alpha,
        activation_rate,
    )
    estimate = policy_estimate(
        evaluation,
        dgp,
        bundle.candidate,
        bundle.activation,
        alpha,
    )

    rng = _seed_rng(*resample_seed_components)
    delta_values = np.empty(resamples, dtype=float)
    s_values = np.empty(resamples, dtype=float)
    failures = 0
    for index in range(resamples):
        try:
            delta_values[index], s_values[index] = _bootstrap_one(
                reference,
                evaluation,
                dgp,
                alpha,
                activation_rate,
                rng,
            )
        except Exception:
            failures += 1
            delta_values[index] = np.nan
            s_values[index] = np.nan

    finite = np.isfinite(delta_values) & np.isfinite(s_values)
    delta_values = delta_values[finite]
    s_values = s_values[finite]
    if delta_values.size < max(5, resamples // 2):
        raise RuntimeError("too few finite bootstrap replicates")

    true_delta = float(benchmark["population"]["delta_pi"])
    true_s = float(benchmark["population"]["delta_s"])
    z = float(norm.ppf(0.975))

    def intervals(
        estimate_value: float,
        values: FloatArray,
        truth: float,
    ) -> dict[str, float | int]:
        sd = float(np.std(values, ddof=1))
        lower_normal = estimate_value - z * sd
        upper_normal = estimate_value + z * sd
        lower_percentile, upper_percentile = np.quantile(
            values,
            [0.025, 0.975],
            method="linear",
        )
        lower_basic = 2.0 * estimate_value - upper_percentile
        upper_basic = 2.0 * estimate_value - lower_percentile
        return {
            "bootstrap_sd": sd,
            "cover_bootstrap_normal": int(
                lower_normal <= truth <= upper_normal
            ),
            "cover_percentile": int(
                lower_percentile <= truth <= upper_percentile
            ),
            "cover_basic": int(lower_basic <= truth <= upper_basic),
        }

    delta_interval = intervals(
        estimate.delta_pi,
        delta_values,
        true_delta,
    )
    s_interval = intervals(
        estimate.delta_s,
        s_values,
        true_s,
    )
    return {
        "delta_pi": estimate.delta_pi,
        "delta_s": estimate.delta_s,
        "bootstrap_replicates_requested": resamples,
        "bootstrap_replicates_finite": int(delta_values.size),
        "bootstrap_failures": failures,
        **{f"delta_{key}": value for key, value in delta_interval.items()},
        **{f"s_{key}": value for key, value in s_interval.items()},
    }
