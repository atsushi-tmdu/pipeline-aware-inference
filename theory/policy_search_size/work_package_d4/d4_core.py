from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
from scipy.stats import multivariate_normal, norm


@dataclass(frozen=True)
class D4Thresholds:
    q0: float
    q1: float
    c: float


@dataclass(frozen=True)
class D4Estimate:
    alpha: float
    target_activation_rate: float
    q0_hat: float
    q1_hat: float
    c_hat: float
    e0_hat: float
    activation_rate_hat: float
    mu_hat: float
    nu_hat: float
    pi_adaptive_hat: float
    pi_comparator_hat: float
    delta_pi_hat: float
    tess_adaptive_hat: float
    tess_comparator_hat: float
    delta_tess_hat: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def empirical_generalized_inverse(values: np.ndarray, probability: float) -> float:
    """Empirical generalized-inverse quantile with index ceil(B * probability)."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size == 0:
        raise ValueError("values must be a non-empty one-dimensional array")
    if not (0.0 < probability < 1.0):
        raise ValueError("probability must lie strictly between 0 and 1")
    if not np.all(np.isfinite(x)):
        raise ValueError("values contain non-finite entries")
    index = int(np.ceil(x.size * probability)) - 1
    return float(np.partition(x, index)[index])


def tess_transform(pi: float, alpha: float) -> float:
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie strictly between 0 and 1")
    if not (0.0 <= pi < 1.0):
        raise ValueError("pi must lie in [0, 1)")
    return float(np.log1p(-pi) / np.log1p(-alpha))


def tess_derivative(pi: float, alpha: float) -> float:
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie strictly between 0 and 1")
    if not (0.0 <= pi < 1.0):
        raise ValueError("pi must lie in [0, 1)")
    return float(-1.0 / ((1.0 - pi) * np.log1p(-alpha)))


def estimate_thresholds(
    reference: np.ndarray,
    alpha: float,
    target_activation_rate: float,
) -> D4Thresholds:
    reference = np.asarray(reference, dtype=float)
    if reference.ndim != 2 or reference.shape[1] != 3:
        raise ValueError("reference must have shape (B, 3) with columns U, X0, X1")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie strictly between 0 and 1")
    if not (0.0 < target_activation_rate < 1.0):
        raise ValueError("target_activation_rate must lie strictly between 0 and 1")
    p = 1.0 - alpha
    s = 1.0 - target_activation_rate
    return D4Thresholds(
        q0=empirical_generalized_inverse(reference[:, 1], p),
        q1=empirical_generalized_inverse(reference[:, 2], p),
        c=empirical_generalized_inverse(reference[:, 0], s),
    )


def policy_components(evaluation: np.ndarray, thresholds: D4Thresholds) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    evaluation = np.asarray(evaluation, dtype=float)
    if evaluation.ndim != 2 or evaluation.shape[1] != 3:
        raise ValueError("evaluation must have shape (n, 3) with columns U, X0, X1")
    u = evaluation[:, 0]
    x0 = evaluation[:, 1]
    x1 = evaluation[:, 2]
    r0 = (x0 > thresholds.q0).astype(float)
    activation = (u > thresholds.c).astype(float)
    increment = ((x0 <= thresholds.q0) & (x1 > thresholds.q1)).astype(float)
    adaptive_rejection = r0 + activation * increment
    return r0, activation, increment, adaptive_rejection


def estimate_d4(
    reference: np.ndarray,
    evaluation: np.ndarray,
    alpha: float,
    target_activation_rate: float,
) -> D4Estimate:
    thresholds = estimate_thresholds(reference, alpha, target_activation_rate)
    r0, activation, increment, adaptive_rejection = policy_components(evaluation, thresholds)

    e0_hat = float(np.mean(r0))
    activation_rate_hat = float(np.mean(activation))
    mu_hat = float(np.mean(increment))
    nu_hat = float(np.mean(activation * increment))

    pi_adaptive_hat = float(np.mean(adaptive_rejection))
    pi_comparator_hat = float(e0_hat + activation_rate_hat * mu_hat)
    delta_pi_hat = float(pi_adaptive_hat - pi_comparator_hat)

    # Finite samples can produce pi = 1 only under pathological tiny samples.
    if not (0.0 <= pi_adaptive_hat < 1.0 and 0.0 <= pi_comparator_hat < 1.0):
        raise ValueError("estimated rejection probabilities must lie in [0, 1)")

    tess_adaptive_hat = tess_transform(pi_adaptive_hat, alpha)
    tess_comparator_hat = tess_transform(pi_comparator_hat, alpha)
    delta_tess_hat = float(tess_adaptive_hat - tess_comparator_hat)

    return D4Estimate(
        alpha=float(alpha),
        target_activation_rate=float(target_activation_rate),
        q0_hat=thresholds.q0,
        q1_hat=thresholds.q1,
        c_hat=thresholds.c,
        e0_hat=e0_hat,
        activation_rate_hat=activation_rate_hat,
        mu_hat=mu_hat,
        nu_hat=nu_hat,
        pi_adaptive_hat=pi_adaptive_hat,
        pi_comparator_hat=pi_comparator_hat,
        delta_pi_hat=delta_pi_hat,
        tess_adaptive_hat=tess_adaptive_hat,
        tess_comparator_hat=tess_comparator_hat,
        delta_tess_hat=delta_tess_hat,
    )


def paired_two_bank_bootstrap(
    reference: np.ndarray,
    evaluation: np.ndarray,
    alpha: float,
    target_activation_rate: float,
    repetitions: int,
    seed: int,
) -> dict[str, np.ndarray]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    reference = np.asarray(reference, dtype=float)
    evaluation = np.asarray(evaluation, dtype=float)
    rng = np.random.default_rng(seed)
    B = reference.shape[0]
    n = evaluation.shape[0]
    delta_pi = np.empty(repetitions, dtype=float)
    delta_tess = np.empty(repetitions, dtype=float)
    pi_adaptive = np.empty(repetitions, dtype=float)
    pi_comparator = np.empty(repetitions, dtype=float)

    for b in range(repetitions):
        ref_index = rng.integers(0, B, size=B)
        eval_index = rng.integers(0, n, size=n)
        estimate = estimate_d4(
            reference[ref_index],
            evaluation[eval_index],
            alpha,
            target_activation_rate,
        )
        delta_pi[b] = estimate.delta_pi_hat
        delta_tess[b] = estimate.delta_tess_hat
        pi_adaptive[b] = estimate.pi_adaptive_hat
        pi_comparator[b] = estimate.pi_comparator_hat

    return {
        "delta_pi": delta_pi,
        "delta_tess": delta_tess,
        "pi_adaptive": pi_adaptive,
        "pi_comparator": pi_comparator,
    }


def _validate_correlation(correlation: np.ndarray) -> np.ndarray:
    correlation = np.asarray(correlation, dtype=float)
    if correlation.shape != (3, 3):
        raise ValueError("correlation must have shape (3, 3), ordered U, X0, X1")
    if not np.allclose(correlation, correlation.T, atol=1e-12):
        raise ValueError("correlation must be symmetric")
    if not np.allclose(np.diag(correlation), 1.0, atol=1e-12):
        raise ValueError("correlation must have unit diagonal")
    if np.min(np.linalg.eigvalsh(correlation)) <= 0.0:
        raise ValueError("correlation must be positive definite")
    return correlation


def _mvn_cdf(x: np.ndarray, covariance: np.ndarray, seed: int) -> float:
    x = np.asarray(x, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    return float(
        multivariate_normal.cdf(
            x,
            mean=np.zeros(x.size),
            cov=covariance,
            maxpts=2_000_000,
            abseps=1e-9,
            releps=1e-9,
            rng=np.random.default_rng(seed),
        )
    )


def _conditional_parameters(
    correlation: np.ndarray,
    target_indices: list[int],
    given_index: int,
    given_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    cross = correlation[np.ix_(target_indices, [given_index])]
    mean = cross[:, 0] * given_value
    covariance = correlation[np.ix_(target_indices, target_indices)] - cross @ cross.T
    return mean, covariance


def _bivariate_both_greater(
    thresholds: np.ndarray,
    mean: np.ndarray,
    covariance: np.ndarray,
    seed: int,
) -> float:
    thresholds = np.asarray(thresholds, dtype=float)
    sd = np.sqrt(np.diag(covariance))
    p0 = norm.cdf((thresholds[0] - mean[0]) / sd[0])
    p1 = norm.cdf((thresholds[1] - mean[1]) / sd[1])
    both_lower = multivariate_normal.cdf(
        thresholds,
        mean=mean,
        cov=covariance,
        maxpts=2_000_000,
        abseps=1e-9,
        releps=1e-9,
        rng=np.random.default_rng(seed),
    )
    return float(1.0 - p0 - p1 + both_lower)


def gaussian_population_functionals(
    thresholds: D4Thresholds,
    correlation: np.ndarray,
) -> dict[str, float]:
    """Population D4 functionals at arbitrary thresholds under a trivariate normal law."""
    correlation = _validate_correlation(correlation)
    c, q0, q1 = thresholds.c, thresholds.q0, thresholds.q1

    e0 = float(1.0 - norm.cdf(q0))
    activation_rate = float(1.0 - norm.cdf(c))

    f01 = _mvn_cdf(
        np.array([q0, q1]),
        correlation[np.ix_([1, 2], [1, 2])],
        seed=1001,
    )
    mu = float(norm.cdf(q0) - f01)

    f_u0 = _mvn_cdf(
        np.array([c, q0]),
        correlation[np.ix_([0, 1], [0, 1])],
        seed=1002,
    )
    f_u01 = _mvn_cdf(
        np.array([c, q0, q1]),
        correlation,
        seed=1003,
    )
    nu = float(mu - (f_u0 - f_u01))

    pi_adaptive = float(e0 + nu)
    pi_comparator = float(e0 + activation_rate * mu)
    return {
        "e0": e0,
        "activation_rate": activation_rate,
        "mu": mu,
        "nu": nu,
        "pi_adaptive": pi_adaptive,
        "pi_comparator": pi_comparator,
        "delta_pi": float(pi_adaptive - pi_comparator),
    }


def gaussian_d4_benchmark(
    alpha: float,
    target_activation_rate: float,
    correlation: np.ndarray,
    lambda_ratio: float = 1.0,
) -> dict[str, Any]:
    """Exact/numerically integrated benchmark for the regular Gaussian D4 model."""
    correlation = _validate_correlation(correlation)
    if not (0.0 < lambda_ratio < np.inf):
        raise ValueError("lambda_ratio must be positive and finite")
    p = 1.0 - alpha
    s = 1.0 - target_activation_rate
    q = float(norm.ppf(p))
    c = float(norm.ppf(s))
    thresholds = D4Thresholds(q0=q, q1=q, c=c)
    pop = gaussian_population_functionals(thresholds, correlation)

    e0 = pop["e0"]
    rho = pop["activation_rate"]
    mu = pop["mu"]
    nu = pop["nu"]
    pi_a = pop["pi_adaptive"]
    pi_c = pop["pi_comparator"]

    # Adaptive-policy boundary coefficients.
    mean_u1, cov_u1 = _conditional_parameters(correlation, [0, 2], 1, q)
    a0 = float(1.0 - _bivariate_both_greater(np.array([c, q]), mean_u1, cov_u1, seed=2001))

    mean_0u, cov_0u = _conditional_parameters(correlation, [1, 0], 2, q)
    p_x0_lower = float(norm.cdf((q - mean_0u[0]) / np.sqrt(cov_0u[0, 0])))
    p_x0_u_lower = float(
        multivariate_normal.cdf(
            np.array([q, c]),
            mean=mean_0u,
            cov=cov_0u,
            maxpts=2_000_000,
            abseps=1e-9,
            releps=1e-9,
            rng=np.random.default_rng(2002),
        )
    )
    b1 = float(p_x0_lower - p_x0_u_lower)

    mean_01, cov_01 = _conditional_parameters(correlation, [1, 2], 0, c)
    p_x0_lower_at_u = float(norm.cdf((q - mean_01[0]) / np.sqrt(cov_01[0, 0])))
    p_both_lower_at_u = float(
        multivariate_normal.cdf(
            np.array([q, q]),
            mean=mean_01,
            cov=cov_01,
            maxpts=2_000_000,
            abseps=1e-9,
            releps=1e-9,
            rng=np.random.default_rng(2003),
        )
    )
    d_u = float(p_x0_lower_at_u - p_both_lower_at_u)

    rho_01 = correlation[1, 2]
    conditional_sd = float(np.sqrt(1.0 - rho_01**2))
    s0 = float(1.0 - norm.cdf((q - rho_01 * q) / conditional_sd))
    t1 = float(norm.cdf((q - rho_01 * q) / conditional_sd))
    comparator_a0 = float(1.0 - rho * s0)
    comparator_b1 = float(rho * t1)
    comparator_d_u = float(mu)

    g_a = tess_derivative(pi_a, alpha)
    g_c = tess_derivative(pi_c, alpha)
    kappa0 = float(g_a * a0 - g_c * comparator_a0)
    kappa1 = float(g_a * b1 - g_c * comparator_b1)
    kappa_u = float(g_a * d_u - g_c * comparator_d_u)

    f01 = _mvn_cdf(
        np.array([q, q]),
        correlation[np.ix_([1, 2], [1, 2])],
        seed=3001,
    )
    f0u = _mvn_cdf(
        np.array([q, c]),
        correlation[np.ix_([1, 0], [1, 0])],
        seed=3002,
    )
    f1u = _mvn_cdf(
        np.array([q, c]),
        correlation[np.ix_([2, 0], [2, 0])],
        seed=3003,
    )
    covariance_w = np.array(
        [
            [alpha * p, f01 - p**2, f0u - p * s],
            [f01 - p**2, alpha * p, f1u - p * s],
            [f0u - p * s, f1u - p * s, rho * s],
        ],
        dtype=float,
    )
    kappa = np.array([kappa0, kappa1, kappa_u], dtype=float)
    sigma_r2 = float(kappa @ covariance_w @ kappa)

    # Evaluation IF variance from the six possible (A, R0, D) states.
    f_u0 = _mvn_cdf(
        np.array([c, q]),
        correlation[np.ix_([0, 1], [0, 1])],
        seed=4001,
    )
    p_a1_r01 = float(1.0 - s - p + f_u0)
    state_probabilities = {
        "A1_R01_D0": p_a1_r01,
        "A0_R01_D0": e0 - p_a1_r01,
        "A1_R00_D1": nu,
        "A0_R00_D1": mu - nu,
        "A1_R00_D0": rho - p_a1_r01 - nu,
        "A0_R00_D0": 1.0 - e0 - mu - (rho - p_a1_r01 - nu),
    }

    def evaluation_if(a_value: float, r0_value: float, d_value: float) -> float:
        adaptive = r0_value + a_value * d_value
        if_a = g_a * (adaptive - pi_a)
        if_c = g_c * (
            (r0_value - e0)
            + mu * (a_value - rho)
            + rho * (d_value - mu)
        )
        return float(if_a - if_c)

    state_values = {
        "A1_R01_D0": evaluation_if(1.0, 1.0, 0.0),
        "A0_R01_D0": evaluation_if(0.0, 1.0, 0.0),
        "A1_R00_D1": evaluation_if(1.0, 0.0, 1.0),
        "A0_R00_D1": evaluation_if(0.0, 0.0, 1.0),
        "A1_R00_D0": evaluation_if(1.0, 0.0, 0.0),
        "A0_R00_D0": evaluation_if(0.0, 0.0, 0.0),
    }
    sigma_e2 = float(
        sum(state_probabilities[key] * state_values[key] ** 2 for key in state_probabilities)
    )
    if_mean = float(
        sum(state_probabilities[key] * state_values[key] for key in state_probabilities)
    )

    delta_tess = float(tess_transform(pi_a, alpha) - tess_transform(pi_c, alpha))
    gradient_pi_a = np.array(
        [
            -norm.pdf(q) * a0,
            -norm.pdf(q) * b1,
            -norm.pdf(c) * d_u,
        ]
    )
    gradient_pi_c = np.array(
        [
            -norm.pdf(q) * comparator_a0,
            -norm.pdf(q) * comparator_b1,
            -norm.pdf(c) * comparator_d_u,
        ]
    )
    gradient_delta_tess = g_a * gradient_pi_a - g_c * gradient_pi_c

    return {
        "alpha": float(alpha),
        "target_activation_rate": float(target_activation_rate),
        "lambda_ratio": float(lambda_ratio),
        "correlation": correlation.tolist(),
        "q0": q,
        "q1": q,
        "c": c,
        **pop,
        "tess_adaptive": tess_transform(pi_a, alpha),
        "tess_comparator": tess_transform(pi_c, alpha),
        "delta_tess": delta_tess,
        "a0": a0,
        "b1": b1,
        "d_u": d_u,
        "s0": s0,
        "t1": t1,
        "comparator_a0": comparator_a0,
        "comparator_b1": comparator_b1,
        "comparator_d_u": comparator_d_u,
        "g_prime_adaptive": g_a,
        "g_prime_comparator": g_c,
        "kappa0": kappa0,
        "kappa1": kappa1,
        "kappa_u": kappa_u,
        "gradient_delta_tess": gradient_delta_tess.tolist(),
        "sigma_e2_sqrt_n": sigma_e2,
        "sigma_r2_sqrt_B": sigma_r2,
        "sigma_total2_sqrt_n": float(sigma_e2 + lambda_ratio * sigma_r2),
        "evaluation_if_mean": if_mean,
        "state_probabilities": state_probabilities,
        "state_evaluation_if": state_values,
    }


def finite_difference_gradient_gaussian(
    alpha: float,
    target_activation_rate: float,
    correlation: np.ndarray,
    step: float = 1e-4,
) -> np.ndarray:
    correlation = _validate_correlation(correlation)
    q = float(norm.ppf(1.0 - alpha))
    c = float(norm.ppf(1.0 - target_activation_rate))
    base = np.array([q, q, c], dtype=float)

    def objective(vector: np.ndarray) -> float:
        thresholds = D4Thresholds(q0=float(vector[0]), q1=float(vector[1]), c=float(vector[2]))
        pop = gaussian_population_functionals(thresholds, correlation)
        return float(
            tess_transform(pop["pi_adaptive"], alpha)
            - tess_transform(pop["pi_comparator"], alpha)
        )

    gradient = np.empty(3, dtype=float)
    for j in range(3):
        plus = base.copy()
        minus = base.copy()
        plus[j] += step
        minus[j] -= step
        gradient[j] = (objective(plus) - objective(minus)) / (2.0 * step)
    return gradient
