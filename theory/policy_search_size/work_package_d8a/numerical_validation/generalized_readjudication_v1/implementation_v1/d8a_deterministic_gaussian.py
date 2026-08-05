from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.integrate import quad
from scipy.stats import norm


FloatArray = np.ndarray


def _rounded(value: float) -> float:
    return round(float(value), 15)


@lru_cache(maxsize=8192)
def _bvn_cached(
    upper_left: float,
    upper_right: float,
    correlation: float,
) -> float:
    left = float(upper_left)
    right = float(upper_right)
    rho = float(correlation)

    if math.isinf(left):
        if left < 0.0:
            return 0.0
        return float(norm.cdf(right))
    if math.isinf(right):
        if right < 0.0:
            return 0.0
        return float(norm.cdf(left))

    if rho >= 1.0:
        return float(
            norm.cdf(min(left, right))
        )
    if rho <= -1.0:
        lower = -right
        if left <= lower:
            return 0.0
        return float(
            norm.cdf(left)
            - norm.cdf(lower)
        )
    if abs(rho) <= 1e-16:
        return float(
            norm.cdf(left)
            * norm.cdf(right)
        )

    base = float(
        norm.cdf(left)
        * norm.cdf(right)
    )

    def plackett_integrand(
        local_rho: float,
    ) -> float:
        denominator = (
            1.0 - local_rho**2
        )
        exponent = -(
            left**2
            - 2.0
            * local_rho
            * left
            * right
            + right**2
        ) / (
            2.0 * denominator
        )
        return float(
            math.exp(exponent)
            / (
                2.0
                * math.pi
                * math.sqrt(denominator)
            )
        )

    correction, _ = quad(
        plackett_integrand,
        0.0,
        rho,
        epsabs=2e-13,
        epsrel=2e-13,
        limit=180,
    )
    return float(base + correction)


def bvn_cdf(
    upper_left: float,
    upper_right: float,
    correlation: float,
) -> float:
    return _bvn_cached(
        _rounded(upper_left),
        _rounded(upper_right),
        _rounded(correlation),
    )


def _standardized_bvn_cdf(
    bounds: FloatArray,
    covariance: FloatArray,
) -> float:
    upper = np.asarray(
        bounds,
        dtype=float,
    )
    sigma = np.asarray(
        covariance,
        dtype=float,
    )
    sd_left = math.sqrt(
        float(sigma[0, 0])
    )
    sd_right = math.sqrt(
        float(sigma[1, 1])
    )
    correlation = float(
        sigma[0, 1]
        / (sd_left * sd_right)
    )
    correlation = float(
        np.clip(
            correlation,
            -1.0,
            1.0,
        )
    )
    return bvn_cdf(
        float(upper[0] / sd_left),
        float(upper[1] / sd_right),
        correlation,
    )


def gaussian_cdf(
    bounds: FloatArray,
    covariance: FloatArray,
) -> float:
    upper = np.asarray(
        bounds,
        dtype=float,
    )
    sigma = np.asarray(
        covariance,
        dtype=float,
    )
    dimension = int(upper.size)

    if sigma.shape != (
        dimension,
        dimension,
    ):
        raise ValueError(
            "covariance shape mismatch"
        )
    if dimension == 0:
        return 1.0
    if dimension == 1:
        variance = float(
            sigma[0, 0]
        )
        if variance <= 0.0:
            raise ValueError(
                "variance must be positive"
            )
        return float(
            norm.cdf(
                upper[0]
                / math.sqrt(variance)
            )
        )
    if dimension == 2:
        return _standardized_bvn_cdf(
            upper,
            sigma,
        )
    if dimension != 3:
        raise ValueError(
            "deterministic backend supports "
            "dimensions 0 through 3"
        )

    standardized_upper = np.array(
        [
            upper[index]
            / math.sqrt(
                float(
                    sigma[index, index]
                )
            )
            for index in range(3)
        ],
        dtype=float,
    )
    condition_index = int(
        np.argmin(
            np.abs(
                standardized_upper
            )
        )
    )
    rest = [
        index
        for index in range(3)
        if index != condition_index
    ]

    variance = float(
        sigma[
            condition_index,
            condition_index,
        ]
    )
    sd = math.sqrt(variance)
    covariance_rest_index = sigma[
        np.ix_(
            rest,
            [condition_index],
        )
    ].reshape(-1)
    slope = (
        covariance_rest_index
        / sd
    )
    conditional_covariance = (
        sigma[np.ix_(rest, rest)]
        - np.outer(
            covariance_rest_index,
            covariance_rest_index,
        )
        / variance
    )
    standardized_limit = float(
        upper[condition_index] / sd
    )

    def integrand(
        standardized_value: float,
    ) -> float:
        conditional_bounds = (
            upper[rest]
            - slope
            * standardized_value
        )
        conditional_probability = (
            _standardized_bvn_cdf(
                conditional_bounds,
                conditional_covariance,
            )
        )
        return float(
            norm.pdf(
                standardized_value
            )
            * conditional_probability
        )

    value, _ = quad(
        integrand,
        -math.inf,
        standardized_limit,
        epsabs=3e-12,
        epsrel=3e-12,
        limit=220,
    )
    return float(value)


def linear_gaussian_cdf(
    linear_map: FloatArray,
    bounds: FloatArray,
    correlation_matrix: FloatArray,
) -> float:
    matrix = np.asarray(
        linear_map,
        dtype=float,
    )
    upper = np.asarray(
        bounds,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    covariance = (
        matrix
        @ correlation
        @ matrix.T
    )
    covariance = (
        covariance
        + covariance.T
    ) / 2.0
    return gaussian_cdf(
        upper,
        covariance,
    )


def mvn3_cdf(
    upper: FloatArray,
    correlation_matrix: FloatArray,
) -> float:
    bounds = np.asarray(
        upper,
        dtype=float,
    )
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    if bounds.shape != (3,):
        raise ValueError(
            "upper must have shape (3,)"
        )
    if correlation.shape != (3, 3):
        raise ValueError(
            "correlation_matrix must have shape (3,3)"
        )
    return gaussian_cdf(
        bounds,
        correlation,
    )
