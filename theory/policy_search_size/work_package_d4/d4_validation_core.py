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


def _integrate(
    func: Callable[[float], float],
    a: float,
    b: float,
    *,
    epsabs: float,
    epsrel: float,
    limit: int,
) -> float:
    value, error = quad(func, a, b, epsabs=epsabs, epsrel=epsrel, limit=limit)
    if not math.isfinite(value) or not math.isfinite(error):
        raise RuntimeError("Nonfinite numerical integral")
    return float(value)


def _marginal_cdf(dgp: LatentFactorDGP, j: int, t: float, opts: dict[str, Any]) -> float:
    mu = dgp.mu0 if j == 0 else dgp.mu1
    sigma = dgp.sigma0 if j == 0 else dgp.sigma1
    return _integrate(
        lambda u: _cond_cdf(t, u, mu, sigma) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    )


def _marginal_pdf(dgp: LatentFactorDGP, j: int, t: float, opts: dict[str, Any]) -> float:
    mu = dgp.mu0 if j == 0 else dgp.mu1
    sigma = dgp.sigma0 if j == 0 else dgp.sigma1
    return _integrate(
        lambda u: _cond_pdf(t, u, mu, sigma) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    )


def _marginal_quantile(
    dgp: LatentFactorDGP,
    j: int,
    probability: float,
    opts: dict[str, Any],
) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    objective = lambda t: _marginal_cdf(dgp, j, t, opts) - probability
    lower, upper = -8.0, 8.0
    if objective(lower) >= 0 or objective(upper) <= 0:
        raise RuntimeError("Quantile root is not bracketed")
    return float(brentq(objective, lower, upper, xtol=1e-12, rtol=1e-12, maxiter=200))


def _tess(pi: float, alpha: float) -> float:
    return float(math.log1p(-pi) / math.log1p(-alpha))


def _gprime(pi: float, alpha: float) -> float:
    return float(-1.0 / ((1.0 - pi) * math.log1p(-alpha)))


def _population_at_thresholds(
    dgp: LatentFactorDGP,
    alpha: float,
    q0: float,
    q1: float,
    c: float,
    opts: dict[str, Any],
) -> dict[str, float]:
    rho = float(1.0 - ndtr(c))
    cdf0 = lambda u: _cond_cdf(q0, u, dgp.mu0, dgp.sigma0)
    cdf1 = lambda u: _cond_cdf(q1, u, dgp.mu1, dgp.sigma1)
    tail0 = lambda u: 1.0 - cdf0(u)
    tail1 = lambda u: 1.0 - cdf1(u)
    e0 = _integrate(lambda u: tail0(u) * _phi(u), -math.inf, math.inf, **opts)
    mu = _integrate(lambda u: cdf0(u) * tail1(u) * _phi(u), -math.inf, math.inf, **opts)
    nu = _integrate(lambda u: cdf0(u) * tail1(u) * _phi(u), c, math.inf, **opts)
    pi_a = e0 + nu
    pi_c = e0 + rho * mu
    delta_pi = pi_a - pi_c
    delta_tess = _tess(pi_a, alpha) - _tess(pi_c, alpha)
    return {
        "e0": e0,
        "activation_rate": rho,
        "mu": mu,
        "nu": nu,
        "pi_adaptive": pi_a,
        "pi_comparator": pi_c,
        "delta_pi": delta_pi,
        "tess_adaptive": _tess(pi_a, alpha),
        "tess_comparator": _tess(pi_c, alpha),
        "delta_tess": delta_tess,
    }


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
    opts = {"epsabs": epsabs, "epsrel": epsrel, "limit": limit}
    c = NORMAL.inv_cdf(s)
    q0 = _marginal_quantile(dgp, 0, p, opts)
    q1 = _marginal_quantile(dgp, 1, p, opts)

    pop = _population_at_thresholds(dgp, alpha, q0, q1, c, opts)
    e0 = pop["e0"]
    rho = pop["activation_rate"]
    mu = pop["mu"]
    nu = pop["nu"]
    pi_a = pop["pi_adaptive"]
    pi_c = pop["pi_comparator"]

    cdf0 = lambda u: _cond_cdf(q0, u, dgp.mu0, dgp.sigma0)
    cdf1 = lambda u: _cond_cdf(q1, u, dgp.mu1, dgp.sigma1)
    tail0 = lambda u: 1.0 - cdf0(u)
    tail1 = lambda u: 1.0 - cdf1(u)

    f0 = _marginal_pdf(dgp, 0, q0, opts)
    f1 = _marginal_pdf(dgp, 1, q1, opts)

    adaptive_optional_given_base_boundary = _integrate(
        lambda u: tail1(u) * _cond_pdf(q0, u, dgp.mu0, dgp.sigma0) * _phi(u),
        c,
        math.inf,
        **opts,
    ) / f0
    a0 = 1.0 - adaptive_optional_given_base_boundary
    b1 = _integrate(
        lambda u: cdf0(u) * _cond_pdf(q1, u, dgp.mu1, dgp.sigma1) * _phi(u),
        c,
        math.inf,
        **opts,
    ) / f1
    d_u = cdf0(c) * tail1(c)

    s0 = _integrate(
        lambda u: tail1(u) * _cond_pdf(q0, u, dgp.mu0, dgp.sigma0) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    ) / f0
    t1 = _integrate(
        lambda u: cdf0(u) * _cond_pdf(q1, u, dgp.mu1, dgp.sigma1) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    ) / f1
    comparator_a0 = 1.0 - rho * s0
    comparator_b1 = rho * t1
    comparator_d_u = mu

    g_a = _gprime(pi_a, alpha)
    g_c = _gprime(pi_c, alpha)
    kappa_tess = np.array(
        [
            g_a * a0 - g_c * comparator_a0,
            g_a * b1 - g_c * comparator_b1,
            g_a * d_u - g_c * comparator_d_u,
        ],
        dtype=float,
    )
    kappa_pi = np.array(
        [
            a0 - comparator_a0,
            b1 - comparator_b1,
            d_u - comparator_d_u,
        ],
        dtype=float,
    )

    F01 = _integrate(lambda u: cdf0(u) * cdf1(u) * _phi(u), -math.inf, math.inf, **opts)
    F0U = _integrate(lambda u: cdf0(u) * _phi(u), -math.inf, c, **opts)
    F1U = _integrate(lambda u: cdf1(u) * _phi(u), -math.inf, c, **opts)
    covariance_w = np.array(
        [
            [alpha * p, F01 - p * p, F0U - p * s],
            [F01 - p * p, alpha * p, F1U - p * s],
            [F0U - p * s, F1U - p * s, rho * s],
        ],
        dtype=float,
    )
    sigma_r_pi = float(kappa_pi @ covariance_w @ kappa_pi)
    sigma_r_tess = float(kappa_tess @ covariance_w @ kappa_tess)

    delta_pi = pop["delta_pi"]

    def evaluation_if_values(u: float, r0: float, d_value: float) -> tuple[float, float]:
        a_value = 1.0 if u > c else 0.0
        adaptive_if = g_a * (r0 + a_value * d_value - pi_a)
        comparator_if = g_c * (
            (r0 - e0)
            + mu * (a_value - rho)
            + rho * (d_value - mu)
        )
        tess_if = adaptive_if - comparator_if
        pi_if = (a_value - rho) * (d_value - mu) - delta_pi
        return float(pi_if), float(tess_if)

    def conditional_second_moment(u: float, index: int) -> float:
        p_r0 = tail0(u)
        p_d = cdf0(u) * tail1(u)
        p_none = cdf0(u) * cdf1(u)
        if_r0 = evaluation_if_values(u, 1.0, 0.0)[index]
        if_d = evaluation_if_values(u, 0.0, 1.0)[index]
        if_none = evaluation_if_values(u, 0.0, 0.0)[index]
        return p_r0 * if_r0 * if_r0 + p_d * if_d * if_d + p_none * if_none * if_none

    sigma_e_pi = _integrate(
        lambda u: conditional_second_moment(u, 0) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    )
    sigma_e_tess = _integrate(
        lambda u: conditional_second_moment(u, 1) * _phi(u),
        -math.inf,
        math.inf,
        **opts,
    )

    sigma_total_pi = sigma_e_pi + lambda_ratio * sigma_r_pi
    sigma_total_tess = sigma_e_tess + lambda_ratio * sigma_r_tess
    if min(sigma_e_pi, sigma_e_tess, sigma_total_pi, sigma_total_tess) <= 0.0:
        raise RuntimeError("Nonpositive D4 asymptotic variance")

    return {
        "dgp": name,
        "dgp_parameters": dgp.parameters,
        "alpha": float(alpha),
        "target_activation_rate": float(activation_rate),
        "lambda_ratio": float(lambda_ratio),
        "q0": q0,
        "q1": q1,
        "c": c,
        **pop,
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
        "kappa_pi": kappa_pi.tolist(),
        "kappa_tess": kappa_tess.tolist(),
        "F01": F01,
        "F0U": F0U,
        "F1U": F1U,
        "sigma_e_delta_pi_2_sqrt_n": sigma_e_pi,
        "sigma_r_delta_pi_2_sqrt_B": sigma_r_pi,
        "sigma_total_delta_pi_2_sqrt_n": sigma_total_pi,
        "sigma_e_delta_tess_2_sqrt_n": sigma_e_tess,
        "sigma_r_delta_tess_2_sqrt_B": sigma_r_tess,
        "sigma_total_delta_tess_2_sqrt_n": sigma_total_tess,
        "reference_variance_fraction_delta_pi": lambda_ratio * sigma_r_pi / sigma_total_pi,
        "reference_variance_fraction_delta_tess": lambda_ratio * sigma_r_tess / sigma_total_tess,
    }


def benchmark_gradient_finite_difference(
    name: str,
    alpha: float,
    activation_rate: float,
    step: float = 1e-4,
) -> dict[str, Any]:
    dgp = get_dgp(name)
    base = benchmark_dgp(name, alpha, activation_rate, 1.0)
    opts = {"epsabs": 1e-10, "epsrel": 1e-10, "limit": 300}
    vector = np.array([base["q0"], base["q1"], base["c"]], dtype=float)

    def objective(v: np.ndarray, key: str) -> float:
        pop = _population_at_thresholds(dgp, alpha, float(v[0]), float(v[1]), float(v[2]), opts)
        return float(pop[key])

    gradients: dict[str, Any] = {}
    for key, analytic_key in [("delta_pi", "kappa_pi"), ("delta_tess", "kappa_tess")]:
        numeric = np.empty(3, dtype=float)
        for j in range(3):
            plus = vector.copy()
            minus = vector.copy()
            plus[j] += step
            minus[j] -= step
            numeric[j] = (objective(plus, key) - objective(minus, key)) / (2.0 * step)

        f0 = _marginal_pdf(dgp, 0, vector[0], opts)
        f1 = _marginal_pdf(dgp, 1, vector[1], opts)
        fu = _phi(vector[2])
        kappa = np.asarray(base[analytic_key], dtype=float)
        analytic_gradient = -np.array([f0, f1, fu], dtype=float) * kappa
        gradients[key] = {
            "numeric": numeric.tolist(),
            "analytic": analytic_gradient.tolist(),
            "maximum_absolute_error": float(np.max(np.abs(numeric - analytic_gradient))),
        }
    return gradients
