from __future__ import annotations

import functools
import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Any, Callable

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr

from d2_core import exact_finite_reference_mean, tess_from_rejection


NORMAL = NormalDist()
SQRT_2PI = math.sqrt(2.0 * math.pi)


def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / SQRT_2PI


@dataclass(frozen=True)
class LatentFactorDGP:
    name: str
    mu0: Callable[[float], float]
    sigma0: float
    mu1: Callable[[float], float]
    sigma1: float
    parameters: dict[str, float]


def get_dgp(name: str) -> LatentFactorDGP:
    if name == "independent_normal":
        return LatentFactorDGP(
            name=name,
            mu0=lambda u: 0.0,
            sigma0=1.0,
            mu1=lambda u: 0.0,
            sigma1=1.0,
            parameters={},
        )
    if name == "gaussian_factor":
        rho0 = 0.60
        rho1 = 0.75
        return LatentFactorDGP(
            name=name,
            mu0=lambda u: rho0 * u,
            sigma0=math.sqrt(1.0 - rho0 * rho0),
            mu1=lambda u: rho1 * u,
            sigma1=math.sqrt(1.0 - rho1 * rho1),
            parameters={"rho0": rho0, "rho1": rho1},
        )
    if name == "nonlinear_smooth":
        rho0 = 0.55
        amplitude = 2.00
        sigma1 = 0.45
        center = 1.0 / math.sqrt(2.0)
        return LatentFactorDGP(
            name=name,
            mu0=lambda u: rho0 * u,
            sigma0=math.sqrt(1.0 - rho0 * rho0),
            mu1=lambda u: amplitude * (math.exp(-0.5 * u * u) - center),
            sigma1=sigma1,
            parameters={
                "rho0": rho0,
                "peak_amplitude": amplitude,
                "sigma1": sigma1,
            },
        )
    raise ValueError(f"Unknown DGP: {name}")


def sample_dgp(rng: np.random.Generator, name: str, size: int) -> np.ndarray:
    if size < 1:
        raise ValueError("size must be positive")
    u = rng.standard_normal(size)
    e0 = rng.standard_normal(size)
    e1 = rng.standard_normal(size)
    if name == "independent_normal":
        x0 = e0
        x1 = e1
    elif name == "gaussian_factor":
        rho0 = 0.60
        rho1 = 0.75
        x0 = rho0 * u + math.sqrt(1.0 - rho0 * rho0) * e0
        x1 = rho1 * u + math.sqrt(1.0 - rho1 * rho1) * e1
    elif name == "nonlinear_smooth":
        rho0 = 0.55
        x0 = rho0 * u + math.sqrt(1.0 - rho0 * rho0) * e0
        x1 = 2.00 * (np.exp(-0.5 * u * u) - 1.0 / math.sqrt(2.0)) + 0.45 * e1
    else:
        raise ValueError(f"Unknown DGP: {name}")
    return np.column_stack([u, x0, x1])


def _cond_cdf(t: float, u: float, mu: Callable[[float], float], sigma: float) -> float:
    return float(ndtr((t - mu(u)) / sigma))


def _cond_pdf(t: float, u: float, mu: Callable[[float], float], sigma: float) -> float:
    z = (t - mu(u)) / sigma
    return _phi(z) / sigma


def _integrate(func: Callable[[float], float], a: float, b: float, *, epsabs: float, epsrel: float, limit: int) -> float:
    value, error = quad(func, a, b, epsabs=epsabs, epsrel=epsrel, limit=limit)
    if not math.isfinite(value) or not math.isfinite(error):
        raise RuntimeError("Nonfinite numerical integral")
    return float(value)


def _marginal_cdf(dgp: LatentFactorDGP, j: int, t: float, quad_opts: dict[str, Any]) -> float:
    mu = dgp.mu0 if j == 0 else dgp.mu1
    sigma = dgp.sigma0 if j == 0 else dgp.sigma1
    return _integrate(
        lambda u: _cond_cdf(t, u, mu, sigma) * _phi(u),
        -math.inf,
        math.inf,
        **quad_opts,
    )


def _marginal_pdf(dgp: LatentFactorDGP, j: int, t: float, quad_opts: dict[str, Any]) -> float:
    mu = dgp.mu0 if j == 0 else dgp.mu1
    sigma = dgp.sigma0 if j == 0 else dgp.sigma1
    return _integrate(
        lambda u: _cond_pdf(t, u, mu, sigma) * _phi(u),
        -math.inf,
        math.inf,
        **quad_opts,
    )


def _marginal_quantile(dgp: LatentFactorDGP, j: int, probability: float, quad_opts: dict[str, Any]) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    objective = lambda t: _marginal_cdf(dgp, j, t, quad_opts) - probability
    lower, upper = -8.0, 8.0
    if objective(lower) >= 0 or objective(upper) <= 0:
        raise RuntimeError("Quantile root is not bracketed")
    return float(brentq(objective, lower, upper, xtol=1e-12, rtol=1e-12, maxiter=200))


@functools.lru_cache(maxsize=None)
def benchmark_dgp(
    name: str,
    alpha: float,
    activation_rate: float,
    lambda_ratio: float,
    epsabs: float = 1e-10,
    epsrel: float = 1e-10,
    limit: int = 300,
) -> dict[str, Any]:
    dgp = get_dgp(name)
    p = 1.0 - alpha
    s = 1.0 - activation_rate
    quad_opts = {"epsabs": epsabs, "epsrel": epsrel, "limit": limit}
    c = NORMAL.inv_cdf(s)
    q0 = _marginal_quantile(dgp, 0, p, quad_opts)
    q1 = _marginal_quantile(dgp, 1, p, quad_opts)

    cdf0 = lambda u: _cond_cdf(q0, u, dgp.mu0, dgp.sigma0)
    cdf1 = lambda u: _cond_cdf(q1, u, dgp.mu1, dgp.sigma1)
    tail0 = lambda u: 1.0 - cdf0(u)
    tail1 = lambda u: 1.0 - cdf1(u)

    pi = (
        _integrate(lambda u: tail0(u) * _phi(u), -math.inf, math.inf, **quad_opts)
        + _integrate(lambda u: cdf0(u) * tail1(u) * _phi(u), c, math.inf, **quad_opts)
    )

    f0 = _marginal_pdf(dgp, 0, q0, quad_opts)
    f1 = _marginal_pdf(dgp, 1, q1, quad_opts)

    optional_given_base_boundary = _integrate(
        lambda u: tail1(u) * _cond_pdf(q0, u, dgp.mu0, dgp.sigma0) * _phi(u),
        c,
        math.inf,
        **quad_opts,
    ) / f0
    a0 = 1.0 - optional_given_base_boundary

    b1 = _integrate(
        lambda u: cdf0(u) * _cond_pdf(q1, u, dgp.mu1, dgp.sigma1) * _phi(u),
        c,
        math.inf,
        **quad_opts,
    ) / f1

    d_u = cdf0(c) * tail1(c)
    F01 = _integrate(lambda u: cdf0(u) * cdf1(u) * _phi(u), -math.inf, math.inf, **quad_opts)
    F0U = _integrate(lambda u: cdf0(u) * _phi(u), -math.inf, c, **quad_opts)
    F1U = _integrate(lambda u: cdf1(u) * _phi(u), -math.inf, c, **quad_opts)

    sigma_e2 = pi * (1.0 - pi)
    sigma_r_d1_2 = (
        alpha * p * (a0 * a0 + b1 * b1)
        + 2.0 * a0 * b1 * (F01 - p * p)
    )
    sigma_trigger_2 = activation_rate * (1.0 - activation_rate) * d_u * d_u
    sigma_r_d2_2 = (
        sigma_r_d1_2
        + sigma_trigger_2
        + 2.0 * a0 * d_u * (F0U - p * s)
        + 2.0 * b1 * d_u * (F1U - p * s)
    )
    if sigma_r_d2_2 <= 0 or sigma_e2 <= 0:
        raise RuntimeError("Nonpositive asymptotic variance component")

    sigma_pi_d2_2 = sigma_e2 + lambda_ratio * sigma_r_d2_2
    sigma_pi_d1_2 = sigma_e2 + lambda_ratio * sigma_r_d1_2
    sigma_trigger_delta_2 = lambda_ratio * sigma_trigger_2
    gprime = -1.0 / ((1.0 - pi) * math.log1p(-alpha))

    result: dict[str, Any] = {
        "dgp": name,
        "dgp_parameters": dgp.parameters,
        "alpha": alpha,
        "activation_rate": activation_rate,
        "lambda_ratio": lambda_ratio,
        "q0": q0,
        "q1": q1,
        "c": c,
        "pi": pi,
        "tess": tess_from_rejection(pi, alpha),
        "a0": a0,
        "b1": b1,
        "d_u": d_u,
        "F01": F01,
        "F0U": F0U,
        "F1U": F1U,
        "sigma_e2_sqrt_n": sigma_e2,
        "sigma_r_d1_2_sqrt_B": sigma_r_d1_2,
        "sigma_trigger_2_sqrt_B": sigma_trigger_2,
        "sigma_r_d2_2_sqrt_B": sigma_r_d2_2,
        "sigma_pi_d1_2_sqrt_n": sigma_pi_d1_2,
        "sigma_pi_d2_2_sqrt_n": sigma_pi_d2_2,
        "sigma_trigger_delta_2_sqrt_n": sigma_trigger_delta_2,
        "sigma_tess_d1_2_sqrt_n": gprime * gprime * sigma_pi_d1_2,
        "sigma_tess_d2_2_sqrt_n": gprime * gprime * sigma_pi_d2_2,
        "sigma_trigger_delta_tess_2_sqrt_n": gprime * gprime * sigma_trigger_delta_2,
        "reference_variance_fraction_d2": lambda_ratio * sigma_r_d2_2 / sigma_pi_d2_2,
        "trigger_only_fraction_of_reference_variance": sigma_trigger_2 / sigma_r_d2_2,
    }
    return result


def finite_reference_independent(alpha: float, activation_rate: float, B: int) -> dict[str, Any]:
    return {
        "estimated_trigger": exact_finite_reference_mean(alpha, activation_rate, B, estimated_trigger=True),
        "known_trigger": exact_finite_reference_mean(alpha, activation_rate, B, estimated_trigger=False),
    }


def benchmark_derivatives_finite_difference(
    name: str,
    alpha: float,
    activation_rate: float,
    step: float = 1e-4,
) -> dict[str, float]:
    dgp = get_dgp(name)
    base = benchmark_dgp(name, alpha, activation_rate, 1.0)
    q0, q1, c = base["q0"], base["q1"], base["c"]
    quad_opts = {"epsabs": 1e-10, "epsrel": 1e-10, "limit": 300}

    def probability(t0: float, t1: float, tc: float) -> float:
        cdf0 = lambda u: _cond_cdf(t0, u, dgp.mu0, dgp.sigma0)
        cdf1 = lambda u: _cond_cdf(t1, u, dgp.mu1, dgp.sigma1)
        tail0 = lambda u: 1.0 - cdf0(u)
        tail1 = lambda u: 1.0 - cdf1(u)
        return (
            _integrate(lambda u: tail0(u) * _phi(u), -math.inf, math.inf, **quad_opts)
            + _integrate(lambda u: cdf0(u) * tail1(u) * _phi(u), tc, math.inf, **quad_opts)
        )

    dm0 = (probability(q0 + step, q1, c) - probability(q0 - step, q1, c)) / (2.0 * step)
    dm1 = (probability(q0, q1 + step, c) - probability(q0, q1 - step, c)) / (2.0 * step)
    dmc = (probability(q0, q1, c + step) - probability(q0, q1, c - step)) / (2.0 * step)

    f0 = _marginal_pdf(dgp, 0, q0, quad_opts)
    f1 = _marginal_pdf(dgp, 1, q1, quad_opts)
    fu = _phi(c)
    return {
        "numeric_dm_dq0": dm0,
        "analytic_dm_dq0": -f0 * base["a0"],
        "numeric_dm_dq1": dm1,
        "analytic_dm_dq1": -f1 * base["b1"],
        "numeric_dm_dc": dmc,
        "analytic_dm_dc": -fu * base["d_u"],
    }
