from __future__ import annotations

import math
import numpy as np
from scipy.stats import multivariate_normal, norm

FloatArray = np.ndarray


def gaussian_cdf(bounds: FloatArray, covariance: FloatArray) -> float:
    upper = np.asarray(bounds, dtype=float)
    sigma = np.asarray(covariance, dtype=float)
    d = upper.size
    if sigma.shape != (d, d):
        raise ValueError("covariance shape mismatch")
    if d == 0:
        return 1.0
    if d == 1:
        return float(norm.cdf(upper[0] / math.sqrt(float(sigma[0, 0]))))
    return float(
        multivariate_normal.cdf(
            upper,
            mean=np.zeros(d),
            cov=sigma,
            maxpts=800000,
            abseps=5e-12,
            releps=5e-12,
            rng=np.random.default_rng(314159),
        )
    )


def gaussian_cdf_derivatives(
    bounds: FloatArray,
    covariance: FloatArray,
) -> tuple[float, FloatArray, FloatArray]:
    upper = np.asarray(bounds, dtype=float)
    sigma = np.asarray(covariance, dtype=float)
    d = upper.size
    if sigma.shape != (d, d):
        raise ValueError("covariance shape mismatch")
    if d == 0:
        return 1.0, np.zeros(0), np.zeros((0, 0))

    value = gaussian_cdf(upper, sigma)
    gradient = np.zeros(d)
    hessian = np.zeros((d, d))

    for i in range(d):
        variance = float(sigma[i, i])
        sd = math.sqrt(variance)
        density = float(norm.pdf(upper[i] / sd) / sd)
        rest = [j for j in range(d) if j != i]
        if not rest:
            conditional_cdf = 1.0
            conditional_derivative = 0.0
        else:
            cross = sigma[np.ix_(rest, [i])].reshape(-1)
            slope = cross / variance
            conditional_bounds = upper[rest] - slope * upper[i]
            conditional_covariance = (
                sigma[np.ix_(rest, rest)] - np.outer(cross, cross) / variance
            )
            conditional_cdf, conditional_gradient, _ = gaussian_cdf_derivatives(
                conditional_bounds,
                conditional_covariance,
            )
            conditional_derivative = float(-slope @ conditional_gradient)
        gradient[i] = density * conditional_cdf
        density_derivative = -upper[i] / variance * density
        hessian[i, i] = (
            density_derivative * conditional_cdf
            + density * conditional_derivative
        )

    for i in range(d):
        for j in range(i + 1, d):
            pair = [i, j]
            pair_covariance = sigma[np.ix_(pair, pair)]
            pair_value = upper[pair]
            pair_density = float(
                multivariate_normal.pdf(
                    pair_value,
                    mean=np.zeros(2),
                    cov=pair_covariance,
                )
            )
            rest = [k for k in range(d) if k not in pair]
            if not rest:
                conditional_cdf = 1.0
            else:
                cross = sigma[np.ix_(rest, pair)]
                inverse_pair = np.linalg.inv(pair_covariance)
                conditional_mean = cross @ inverse_pair @ pair_value
                conditional_covariance = (
                    sigma[np.ix_(rest, rest)]
                    - cross @ inverse_pair @ cross.T
                )
                conditional_cdf = gaussian_cdf(
                    upper[rest] - conditional_mean,
                    conditional_covariance,
                )
            mixed = pair_density * conditional_cdf
            hessian[i, j] = mixed
            hessian[j, i] = mixed

    return value, gradient, hessian


def linear_gaussian_term_derivatives(
    linear_map: FloatArray,
    bounds: FloatArray,
    bound_jacobian: FloatArray,
    correlation_matrix: FloatArray,
) -> tuple[float, FloatArray, FloatArray]:
    matrix = np.asarray(linear_map, dtype=float)
    upper = np.asarray(bounds, dtype=float)
    jacobian = np.asarray(bound_jacobian, dtype=float)
    correlation = np.asarray(correlation_matrix, dtype=float)
    covariance = matrix @ correlation @ matrix.T
    value, grad_bounds, hess_bounds = gaussian_cdf_derivatives(upper, covariance)
    gradient = jacobian.T @ grad_bounds
    hessian = jacobian.T @ hess_bounds @ jacobian
    return value, gradient, (hessian + hessian.T) / 2.0


def _zero() -> tuple[float, FloatArray, FloatArray]:
    return 0.0, np.zeros(4), np.zeros((4, 4))


def _add(left, right):
    return left[0] + right[0], left[1] + right[1], left[2] + right[2]


def _subtract(left, right):
    return left[0] - right[0], left[1] - right[1], left[2] - right[2]


def _product(left, right):
    value = float(left[0] * right[0])
    gradient = right[0] * left[1] + left[0] * right[1]
    hessian = (
        right[0] * left[2]
        + left[0] * right[2]
        + np.outer(left[1], right[1])
        + np.outer(right[1], left[1])
    )
    return value, gradient, (hessian + hessian.T) / 2.0


def _base_reject_term(
    threshold_index: int,
    winner_index: int,
    correlation: FloatArray,
    theta: FloatArray,
):
    loser = 1 - winner_index
    row1 = np.zeros(3)
    row1[loser] = 1.0
    row1[winner_index] = -1.0
    row2 = np.zeros(3)
    row2[winner_index] = -1.0
    jacobian = np.zeros((2, 4))
    jacobian[1, threshold_index] = -1.0
    return linear_gaussian_term_derivatives(
        np.vstack([row1, row2]),
        np.array([0.0, -theta[threshold_index]]),
        jacobian,
        correlation,
    )


def _incremental_term(
    winner_threshold_index: int,
    winner_index: int,
    correlation: FloatArray,
    theta: FloatArray,
):
    loser = 1 - winner_index
    row1 = np.zeros(3)
    row1[loser] = 1.0
    row1[winner_index] = -1.0
    row2 = np.zeros(3)
    row2[winner_index] = 1.0
    row3 = np.zeros(3)
    row3[2] = -1.0
    jacobian = np.zeros((3, 4))
    jacobian[1, winner_threshold_index] = 1.0
    jacobian[2, 2] = -1.0
    return linear_gaussian_term_derivatives(
        np.vstack([row1, row2, row3]),
        np.array([0.0, theta[winner_threshold_index], -theta[2]]),
        jacobian,
        correlation,
    )


def _trigger_incremental_term(
    winner_index: int,
    correlation: FloatArray,
    theta: FloatArray,
):
    loser = 1 - winner_index
    row1 = np.zeros(3)
    row1[loser] = 1.0
    row1[winner_index] = -1.0
    row2 = np.zeros(3)
    row2[winner_index] = 1.0
    row3 = np.zeros(3)
    row3[2] = -1.0
    jacobian = np.zeros((3, 4))
    jacobian[1, 3] = 1.0
    jacobian[2, 2] = -1.0
    return linear_gaussian_term_derivatives(
        np.vstack([row1, row2, row3]),
        np.array([0.0, theta[3], -theta[2]]),
        jacobian,
        correlation,
    )


def analytic_policy_components(
    theta: FloatArray,
    correlation_matrix: FloatArray,
) -> dict[str, tuple]:
    thresholds = np.asarray(theta, dtype=float)
    correlation = np.asarray(correlation_matrix, dtype=float)
    base = _zero()
    incremental = _zero()
    joint = _zero()

    for winner in (0, 1):
        base = _add(
            base,
            _base_reject_term(winner, winner, correlation, thresholds),
        )
        branch = _incremental_term(winner, winner, correlation, thresholds)
        incremental = _add(incremental, branch)
        if thresholds[3] < thresholds[winner]:
            joint = _add(
                joint,
                _subtract(
                    branch,
                    _trigger_incremental_term(winner, correlation, thresholds),
                ),
            )

    activation_lower = linear_gaussian_term_derivatives(
        np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        np.array([thresholds[3], thresholds[3]]),
        np.array([[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]]),
        correlation,
    )
    activation = _subtract(
        (1.0, np.zeros(4), np.zeros((4, 4))),
        activation_lower,
    )
    adaptive = _add(base, joint)
    comparator = _add(base, _product(activation, incremental))
    delta = _subtract(adaptive, comparator)
    return {
        "base_probability": base,
        "activation_probability": activation,
        "incremental_probability": incremental,
        "joint_am_probability": joint,
        "adaptive_probability": adaptive,
        "comparator_probability": comparator,
        "delta_pi": delta,
    }


def analytic_target_derivatives(
    class_record: dict[str, object],
    theta: FloatArray,
) -> dict[str, dict[str, FloatArray | float]]:
    correlation = np.asarray(class_record["correlation_matrix"], dtype=float)
    components = analytic_policy_components(theta, correlation)
    return {
        name: {
            "value": components[name][0],
            "gradient": components[name][1],
            "smooth_hessian": components[name][2],
        }
        for name in (
            "delta_pi",
            "adaptive_probability",
            "comparator_probability",
        )
    }

# ---------------------------------------------------------------------------
# Deterministic CDF backend candidate for analytic boundary derivatives.
# ---------------------------------------------------------------------------

_genz_gaussian_cdf_legacy = gaussian_cdf

from d8a_deterministic_gaussian import (  # noqa: E402
    gaussian_cdf as gaussian_cdf,
)
