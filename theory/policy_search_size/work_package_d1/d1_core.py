from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np


@dataclass(frozen=True)
class IndependentNormalBenchmark:
    alpha: float
    activation_rate: float
    lambda_ratio: float
    rejection_probability: float
    tess: float
    boundary_base: float
    boundary_optional: float
    evaluation_variance: float
    reference_variance: float
    total_variance_sqrt_n: float
    tess_variance_sqrt_n: float


def empirical_quantile_inverted_cdf(values: np.ndarray, p: float) -> float:
    """Empirical generalized-inverse quantile: inf{x: F_n(x) >= p}."""
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0,1)")
    k = int(math.ceil(arr.size * p)) - 1
    k = min(max(k, 0), arr.size - 1)
    return float(np.partition(arr, k)[k])


def tess_from_rejection(rejection_probability: float, alpha: float) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 <= rejection_probability < 1.0:
        raise ValueError("rejection_probability must lie in [0,1)")
    return math.log1p(-rejection_probability) / math.log1p(-alpha)


def tess_derivative(rejection_probability: float, alpha: float) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 <= rejection_probability < 1.0:
        raise ValueError("rejection_probability must lie in [0,1)")
    return -1.0 / ((1.0 - rejection_probability) * math.log1p(-alpha))


def estimate_policy(
    reference: np.ndarray,
    evaluation: np.ndarray,
    *,
    alpha: float,
    activation_rate: float,
) -> tuple[float, float, float, float]:
    """Estimate rejection probability and TESS in the D1 known-trigger model.

    Columns are ordered as (U, X0, X1). The known trigger is the exact
    standard-normal quantile corresponding to the declared activation rate.
    """
    reference = np.asarray(reference, dtype=float)
    evaluation = np.asarray(evaluation, dtype=float)
    if reference.ndim != 2 or reference.shape[1] != 3:
        raise ValueError("reference must have shape (B,3)")
    if evaluation.ndim != 2 or evaluation.shape[1] != 3:
        raise ValueError("evaluation must have shape (n,3)")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 < activation_rate < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")

    p = 1.0 - alpha
    q0 = empirical_quantile_inverted_cdf(reference[:, 1], p)
    q1 = empirical_quantile_inverted_cdf(reference[:, 2], p)
    c = NormalDist().inv_cdf(1.0 - activation_rate)

    u = evaluation[:, 0]
    x0 = evaluation[:, 1]
    x1 = evaluation[:, 2]
    reject = (x0 > q0) | ((x0 <= q0) & (u > c) & (x1 > q1))
    pi_hat = float(np.mean(reject))
    s_hat = tess_from_rejection(pi_hat, alpha)
    return pi_hat, s_hat, q0, q1


def independent_normal_benchmark(
    *, alpha: float, activation_rate: float, lambda_ratio: float
) -> IndependentNormalBenchmark:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 < activation_rate < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    if lambda_ratio <= 0.0:
        raise ValueError("lambda_ratio must be positive")

    r = activation_rate
    pi = alpha + (1.0 - alpha) * r * alpha
    a0 = 1.0 - r * alpha
    b1 = r * (1.0 - alpha)
    sigma_e2 = pi * (1.0 - pi)
    sigma_r2 = alpha * (1.0 - alpha) * (a0 * a0 + b1 * b1)
    sigma2 = sigma_e2 + lambda_ratio * sigma_r2
    s = tess_from_rejection(pi, alpha)
    gp = tess_derivative(pi, alpha)
    return IndependentNormalBenchmark(
        alpha=alpha,
        activation_rate=r,
        lambda_ratio=lambda_ratio,
        rejection_probability=pi,
        tess=s,
        boundary_base=a0,
        boundary_optional=b1,
        evaluation_variance=sigma_e2,
        reference_variance=sigma_r2,
        total_variance_sqrt_n=sigma2,
        tess_variance_sqrt_n=gp * gp * sigma2,
    )


def independent_normal_rejection_at_thresholds(
    q0: float, q1: float, *, activation_rate: float
) -> float:
    """Exact rejection probability under independent standard-normal coordinates."""
    phi = NormalDist().cdf
    r = activation_rate
    # no rejection = P(X0 <= q0) * [P(U <= c) + P(U > c, X1 <= q1)]
    no_reject = phi(q0) * ((1.0 - r) + r * phi(q1))
    return 1.0 - no_reject


def independent_normal_boundary_derivatives(
    q0: float, q1: float, *, activation_rate: float
) -> tuple[float, float]:
    nd = NormalDist()
    r = activation_rate
    f0 = nd.pdf(q0)
    f1 = nd.pdf(q1)
    a0 = 1.0 - r * (1.0 - nd.cdf(q1))
    b1 = nd.cdf(q0) * r
    return -f0 * a0, -f1 * b1
