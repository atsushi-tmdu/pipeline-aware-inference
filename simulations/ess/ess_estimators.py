#!/usr/bin/env python3
"""Core estimators for pipeline-level effective search size (ESS).

The primary estimand is the Šidák-equivalent tail ESS at local level alpha:

    ESS(alpha) = log(1 - pi(alpha)) / log(1 - alpha),

where pi(alpha) is the global-null probability that the complete search
pipeline's selected result would be declared significant at local level alpha
if it were incorrectly treated as prespecified.

This is an operational, pipeline-level multiplicity measure. It is not the
usual propensity-score effective sample size and is distinct from an
eigenvalue participation-ratio dimension.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from statistics import NormalDist


@dataclass(frozen=True)
class ESSEstimate:
    """Point estimate and confidence interval for tail ESS."""

    local_alpha: float
    rejection_probability: float
    ess: float
    rejection_probability_low: float
    rejection_probability_high: float
    ess_low: float
    ess_high: float
    rejections: int
    repetitions: int


def _validate_probability(value: float, name: str) -> None:
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1; got {value!r}.")


def sidak_equivalent_ess(
    rejection_probability: float,
    local_alpha: float,
) -> float:
    """Return the independent-search count with the same null rejection rate.

    Parameters
    ----------
    rejection_probability:
        Global-null probability of a post-search naive rejection.
    local_alpha:
        Candidate-wise significance level used by the naive decision rule.

    Returns
    -------
    float
        Šidák-equivalent effective search size.
    """
    _validate_probability(rejection_probability, "rejection_probability")
    _validate_probability(local_alpha, "local_alpha")
    return log(1.0 - rejection_probability) / log(1.0 - local_alpha)


def ess_adjusted_p_value(naive_p_value: float, ess: float) -> float:
    """Apply a Šidák-form adjustment using a fixed ESS.

    This is only an approximation unless calibration has been established
    independently. Exact pipeline max-statistic calibration remains the
    reference method.
    """
    if not 0.0 <= naive_p_value <= 1.0:
        raise ValueError("naive_p_value must lie in [0, 1].")
    if ess <= 0.0:
        raise ValueError("ess must be positive.")
    return 1.0 - (1.0 - naive_p_value) ** ess


def local_alpha_for_global_alpha(global_alpha: float, ess: float) -> float:
    """Return the local threshold corresponding to a target global alpha."""
    _validate_probability(global_alpha, "global_alpha")
    if ess <= 0.0:
        raise ValueError("ess must be positive.")
    return 1.0 - (1.0 - global_alpha) ** (1.0 / ess)


def wilson_interval(
    rejections: int,
    repetitions: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if repetitions <= 0:
        raise ValueError("repetitions must be positive.")
    if not 0 <= rejections <= repetitions:
        raise ValueError("rejections must lie between 0 and repetitions.")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie strictly between 0 and 1.")

    p_hat = rejections / repetitions
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    z2 = z * z
    denominator = 1.0 + z2 / repetitions
    center = (p_hat + z2 / (2.0 * repetitions)) / denominator
    half_width = (
        z
        * ((p_hat * (1.0 - p_hat) / repetitions + z2 / (4.0 * repetitions**2)) ** 0.5)
        / denominator
    )
    return max(0.0, center - half_width), min(1.0, center + half_width)


def estimate_tail_ess(
    rejections: int,
    repetitions: int,
    local_alpha: float,
    confidence: float = 0.95,
) -> ESSEstimate:
    """Estimate tail ESS and transform a Wilson interval."""
    _validate_probability(local_alpha, "local_alpha")
    if rejections in (0, repetitions):
        raise ValueError(
            "Finite ESS requires a rejection count strictly between 0 and repetitions. "
            "Increase the null-bank size or use a prespecified continuity correction."
        )

    p_hat = rejections / repetitions
    p_low, p_high = wilson_interval(rejections, repetitions, confidence)
    tiny = 1e-15
    p_low = min(max(p_low, tiny), 1.0 - tiny)
    p_high = min(max(p_high, tiny), 1.0 - tiny)

    return ESSEstimate(
        local_alpha=local_alpha,
        rejection_probability=p_hat,
        ess=sidak_equivalent_ess(p_hat, local_alpha),
        rejection_probability_low=p_low,
        rejection_probability_high=p_high,
        ess_low=sidak_equivalent_ess(p_low, local_alpha),
        ess_high=sidak_equivalent_ess(p_high, local_alpha),
        rejections=rejections,
        repetitions=repetitions,
    )
