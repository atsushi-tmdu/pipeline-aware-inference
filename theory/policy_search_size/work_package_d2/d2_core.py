from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Any

import numpy as np


NORMAL = NormalDist()


def empirical_generalized_inverse(values: np.ndarray, probability: float) -> float:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or x.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    k = int(math.ceil(x.size * probability))
    return float(np.partition(x, k - 1)[k - 1])


def tess_from_rejection(pi: float, alpha: float) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    if not 0.0 <= pi < 1.0:
        raise ValueError("pi must lie in [0,1)")
    return math.log1p(-pi) / math.log1p(-alpha)


def policy_rejection(
    evaluation: np.ndarray,
    q0: float,
    q1: float,
    c: float,
) -> float:
    y = np.asarray(evaluation, dtype=float)
    if y.ndim != 2 or y.shape[1] != 3:
        raise ValueError("evaluation must have shape (n,3) ordered as U,X0,X1")
    u, x0, x1 = y[:, 0], y[:, 1], y[:, 2]
    reject = (x0 > q0) | ((x0 <= q0) & (u > c) & (x1 > q1))
    return float(np.mean(reject))


def estimate_d2(reference: np.ndarray, evaluation: np.ndarray, alpha: float, r: float) -> dict[str, float]:
    z = np.asarray(reference, dtype=float)
    if z.ndim != 2 or z.shape[1] != 3:
        raise ValueError("reference must have shape (B,3) ordered as U,X0,X1")
    p = 1.0 - alpha
    s = 1.0 - r
    c = empirical_generalized_inverse(z[:, 0], s)
    q0 = empirical_generalized_inverse(z[:, 1], p)
    q1 = empirical_generalized_inverse(z[:, 2], p)
    pi_hat = policy_rejection(evaluation, q0=q0, q1=q1, c=c)
    return {
        "q0_hat": q0,
        "q1_hat": q1,
        "c_hat": c,
        "pi_hat": pi_hat,
        "tess_hat": tess_from_rejection(pi_hat, alpha),
    }


def estimate_d1_known_trigger(
    reference: np.ndarray,
    evaluation: np.ndarray,
    alpha: float,
    r: float,
) -> dict[str, float]:
    z = np.asarray(reference, dtype=float)
    p = 1.0 - alpha
    c = NORMAL.inv_cdf(1.0 - r)
    q0 = empirical_generalized_inverse(z[:, 1], p)
    q1 = empirical_generalized_inverse(z[:, 2], p)
    pi_hat = policy_rejection(evaluation, q0=q0, q1=q1, c=c)
    return {
        "q0_hat": q0,
        "q1_hat": q1,
        "c": c,
        "pi_hat": pi_hat,
        "tess_hat": tess_from_rejection(pi_hat, alpha),
    }


def independent_normal_policy_probability(t0: float, t1: float, c: float) -> float:
    F0 = NORMAL.cdf(t0)
    tail0 = 1.0 - F0
    tail1 = 1.0 - NORMAL.cdf(t1)
    activation = 1.0 - NORMAL.cdf(c)
    return tail0 + F0 * activation * tail1


def independent_normal_derivatives(t0: float, t1: float, c: float) -> tuple[float, float, float]:
    F0 = NORMAL.cdf(t0)
    tail1 = 1.0 - NORMAL.cdf(t1)
    activation = 1.0 - NORMAL.cdf(c)
    f0 = NORMAL.pdf(t0)
    f1 = NORMAL.pdf(t1)
    fu = NORMAL.pdf(c)
    dm_dt0 = -f0 * (1.0 - activation * tail1)
    dm_dt1 = -f1 * F0 * activation
    dm_dc = -fu * F0 * tail1
    return dm_dt0, dm_dt1, dm_dc


def exact_independent_normal_benchmark(alpha: float, r: float, lambda_ratio: float = 1.0) -> dict[str, float]:
    p = 1.0 - alpha
    pi = alpha + p * r * alpha
    a0 = 1.0 - r * alpha
    b1 = p * r
    d_u = p * alpha
    sigma_e2 = pi * (1.0 - pi)
    sigma_r_d1_2 = alpha * p * (a0 * a0 + b1 * b1)
    sigma_trigger2 = r * (1.0 - r) * d_u * d_u
    sigma_r_d2_2 = sigma_r_d1_2 + sigma_trigger2
    sigma_pi2 = sigma_e2 + lambda_ratio * sigma_r_d2_2
    gprime = -1.0 / ((1.0 - pi) * math.log1p(-alpha))
    return {
        "alpha": alpha,
        "activation_rate": r,
        "lambda_ratio": lambda_ratio,
        "pi": pi,
        "tess": tess_from_rejection(pi, alpha),
        "a0": a0,
        "b1": b1,
        "d_u": d_u,
        "sigma_e2_sqrt_n": sigma_e2,
        "sigma_r_d1_2_sqrt_B": sigma_r_d1_2,
        "sigma_trigger_2_sqrt_B": sigma_trigger2,
        "sigma_r_d2_2_sqrt_B": sigma_r_d2_2,
        "sigma_pi2_sqrt_n": sigma_pi2,
        "sigma_tess2_sqrt_n": gprime * gprime * sigma_pi2,
    }


def exact_finite_reference_mean(alpha: float, r: float, B: int, estimated_trigger: bool = True) -> dict[str, float]:
    if B < 1:
        raise ValueError("B must be positive")
    p = 1.0 - alpha
    s = 1.0 - r
    k_alpha = int(math.ceil(B * p))
    tau = (B + 1 - k_alpha) / (B + 1)
    if estimated_trigger:
        k_r = int(math.ceil(B * s))
        rho = (B + 1 - k_r) / (B + 1)
    else:
        k_r = -1
        rho = r
    mean_pi = tau + (1.0 - tau) * rho * tau
    population_pi = alpha + (1.0 - alpha) * r * alpha
    return {
        "B": B,
        "k_alpha": k_alpha,
        "k_r": k_r,
        "tau_B": tau,
        "rho_B": rho,
        "mean_pi": mean_pi,
        "population_pi": population_pi,
        "bias": mean_pi - population_pi,
    }


def one_outer_d2(
    rng: np.random.Generator,
    B: int,
    n: int,
    alpha: float,
    r: float,
    bootstrap_repetitions: int,
) -> dict[str, Any]:
    reference = rng.standard_normal((B, 3))
    evaluation = rng.standard_normal((n, 3))
    observed = estimate_d2(reference, evaluation, alpha=alpha, r=r)
    known = estimate_d1_known_trigger(reference, evaluation, alpha=alpha, r=r)

    boot_pi = np.empty(bootstrap_repetitions, dtype=float)
    boot_tess = np.empty(bootstrap_repetitions, dtype=float)
    for j in range(bootstrap_repetitions):
        ref_idx = rng.integers(0, B, size=B)
        eval_idx = rng.integers(0, n, size=n)
        star = estimate_d2(
            reference[ref_idx],
            evaluation[eval_idx],
            alpha=alpha,
            r=r,
        )
        boot_pi[j] = star["pi_hat"]
        boot_tess[j] = star["tess_hat"]

    return {
        **observed,
        "known_trigger_pi_hat": known["pi_hat"],
        "known_trigger_tess_hat": known["tess_hat"],
        "trigger_estimation_pi_difference": observed["pi_hat"] - known["pi_hat"],
        "bootstrap_pi_sd": float(np.std(boot_pi, ddof=1)),
        "bootstrap_tess_sd": float(np.std(boot_tess, ddof=1)),
    }
