"""Core implementation for Work Package D5.

D5 compares the D1-D4 empirical-quantile candidate boundary with the exact
finite-bank plus-one Monte Carlo p-value boundary on identical reference and
evaluation banks.

This module does not modify or import D4 estimator code. Parent-code imports
are confined to validation tests so that D5 has an independently auditable
implementation of the bridge.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Literal

import numpy as np


BoundaryMode = Literal["quantile", "plus_one"]


@dataclass(frozen=True)
class BoundaryInfo:
    B: int
    alpha: float
    count_ceiling: int
    quantile_index: int
    plus_one_index: int | None
    plus_one_attainable: bool
    index_gap: int | None
    tau_quantile: float
    tau_plus_one: float
    tail_probability_gap: float

    def to_dict(self) -> dict[str, int | float | bool | None]:
        return asdict(self)


@dataclass(frozen=True)
class ModeEstimate:
    mode: BoundaryMode
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

    def to_dict(self) -> dict[str, str | float]:
        return asdict(self)


@dataclass(frozen=True)
class BridgeEstimate:
    alpha: float
    target_activation_rate: float
    boundary: BoundaryInfo
    quantile: ModeEstimate
    plus_one: ModeEstimate
    q0_spacing: float
    q1_spacing: float
    delta_pi_bridge: float
    delta_tess_bridge: float
    abs_delta_pi_bridge: float
    abs_delta_tess_bridge: float
    delta_pi_strict_sign_reversal: bool
    delta_tess_strict_sign_reversal: bool
    delta_pi_zero_status_change: bool
    delta_tess_zero_status_change: bool

    def to_dict(self) -> dict[str, int | float | bool | None | str]:
        row: dict[str, int | float | bool | None | str] = {
            "alpha": self.alpha,
            "target_activation_rate": self.target_activation_rate,
            **self.boundary.to_dict(),
            "q0_spacing": self.q0_spacing,
            "q1_spacing": self.q1_spacing,
            "delta_pi_bridge": self.delta_pi_bridge,
            "delta_tess_bridge": self.delta_tess_bridge,
            "abs_delta_pi_bridge": self.abs_delta_pi_bridge,
            "abs_delta_tess_bridge": self.abs_delta_tess_bridge,
            "delta_pi_strict_sign_reversal": (
                self.delta_pi_strict_sign_reversal
            ),
            "delta_tess_strict_sign_reversal": (
                self.delta_tess_strict_sign_reversal
            ),
            "delta_pi_zero_status_change": (
                self.delta_pi_zero_status_change
            ),
            "delta_tess_zero_status_change": (
                self.delta_tess_zero_status_change
            ),
        }
        row.update(
            {
                f"quantile_{key}": value
                for key, value in self.quantile.to_dict().items()
            }
        )
        row.update(
            {
                f"plus_one_{key}": value
                for key, value in self.plus_one.to_dict().items()
            }
        )
        return row


def _validate_B_alpha(B: int, alpha: float) -> tuple[int, float]:
    if isinstance(B, bool) or int(B) != B or int(B) < 1:
        raise ValueError("B must be a positive integer")
    B = int(B)
    alpha = float(alpha)
    if not math.isfinite(alpha) or not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie strictly between 0 and 1")
    return B, alpha


def quantile_index(B: int, alpha: float) -> int:
    """One-based D1-D4 generalized-inverse index ceil(B * (1-alpha))."""
    B, alpha = _validate_B_alpha(B, alpha)
    index = int(math.ceil(B * (1.0 - alpha)))
    return min(B, max(1, index))


def plus_one_count_ceiling(B: int, alpha: float) -> int:
    """Return C_B(alpha) = ceil((B+1) * alpha)."""
    B, alpha = _validate_B_alpha(B, alpha)
    return int(math.ceil((B + 1) * alpha))


def plus_one_index(B: int, alpha: float) -> int | None:
    """Return the one-based exact plus-one order-statistic index.

    Returns None when the strict event p_plus < alpha is unattainable.
    """
    B, alpha = _validate_B_alpha(B, alpha)
    count_ceiling = plus_one_count_ceiling(B, alpha)
    if count_ceiling <= 1:
        return None
    index = B + 2 - count_ceiling
    if not 1 <= index <= B:
        raise RuntimeError("internal plus-one index calculation failed")
    return index


def boundary_info(B: int, alpha: float) -> BoundaryInfo:
    B, alpha = _validate_B_alpha(B, alpha)
    count_ceiling = plus_one_count_ceiling(B, alpha)
    q_index = quantile_index(B, alpha)
    p_index = plus_one_index(B, alpha)

    tau_quantile = (B + 1 - q_index) / (B + 1)
    tau_plus_one = (count_ceiling - 1) / (B + 1)
    attainable = p_index is not None
    index_gap = None if p_index is None else p_index - q_index

    if attainable and index_gap not in (0, 1):
        raise RuntimeError("adjacent-boundary identity failed")

    tail_gap = tau_quantile - tau_plus_one
    expected_gap = (
        tau_quantile
        if not attainable
        else float(index_gap) / (B + 1)
    )
    if not math.isclose(tail_gap, expected_gap, abs_tol=1e-15):
        raise RuntimeError("finite-B tail-probability identity failed")

    return BoundaryInfo(
        B=B,
        alpha=alpha,
        count_ceiling=count_ceiling,
        quantile_index=q_index,
        plus_one_index=p_index,
        plus_one_attainable=attainable,
        index_gap=index_gap,
        tau_quantile=float(tau_quantile),
        tau_plus_one=float(tau_plus_one),
        tail_probability_gap=float(tail_gap),
    )


def order_statistic(values: np.ndarray, one_based_index: int) -> float:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError("values must be finite")
    if (
        isinstance(one_based_index, bool)
        or int(one_based_index) != one_based_index
    ):
        raise ValueError("one_based_index must be an integer")
    one_based_index = int(one_based_index)
    if not 1 <= one_based_index <= array.size:
        raise ValueError("one_based_index is outside the sample")
    zero_based = one_based_index - 1
    return float(np.partition(array, zero_based)[zero_based])


def empirical_generalized_inverse(
    values: np.ndarray,
    probability: float,
) -> float:
    array = np.asarray(values, dtype=float)
    probability = float(probability)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie strictly between 0 and 1")
    index = int(math.ceil(array.size * probability))
    return order_statistic(array, index)


def candidate_threshold(
    values: np.ndarray,
    alpha: float,
    mode: BoundaryMode,
) -> float:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError("values must be a nonempty one-dimensional array")
    if mode == "quantile":
        return order_statistic(array, quantile_index(array.size, alpha))
    if mode == "plus_one":
        index = plus_one_index(array.size, alpha)
        if index is None:
            return math.inf
        return order_statistic(array, index)
    raise ValueError("mode must be 'quantile' or 'plus_one'")


def plus_one_pvalue(reference_scores: np.ndarray, x: float) -> float:
    scores = np.asarray(reference_scores, dtype=float)
    if scores.ndim != 1 or scores.size == 0:
        raise ValueError(
            "reference_scores must be a nonempty one-dimensional array"
        )
    if not np.all(np.isfinite(scores)) or not math.isfinite(float(x)):
        raise ValueError("scores and x must be finite")
    exceedances = int(np.count_nonzero(scores >= float(x)))
    return float((1 + exceedances) / (scores.size + 1))


def plus_one_rejects(
    reference_scores: np.ndarray,
    x: float,
    alpha: float,
) -> bool:
    return bool(plus_one_pvalue(reference_scores, x) < float(alpha))


def tess_transform(pi: float, alpha: float) -> float:
    pi = float(pi)
    alpha = float(alpha)
    if not 0.0 <= pi < 1.0:
        raise ValueError("pi must lie in [0, 1)")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    return float(math.log1p(-pi) / math.log1p(-alpha))


def _strict_sign_reversal(left: float, right: float) -> bool:
    return bool(left * right < 0.0)


def _zero_status_change(left: float, right: float) -> bool:
    return bool((left == 0.0) != (right == 0.0))


def _validate_banks(
    reference: np.ndarray,
    evaluation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    reference = np.asarray(reference, dtype=float)
    evaluation = np.asarray(evaluation, dtype=float)
    if reference.ndim != 2 or reference.shape[1] != 3:
        raise ValueError(
            "reference must have shape (B, 3) with columns U, X0, X1"
        )
    if evaluation.ndim != 2 or evaluation.shape[1] != 3:
        raise ValueError(
            "evaluation must have shape (n, 3) with columns U, X0, X1"
        )
    if reference.shape[0] < 1 or evaluation.shape[0] < 1:
        raise ValueError("reference and evaluation banks must be nonempty")
    if not np.all(np.isfinite(reference)):
        raise ValueError("reference bank must be finite")
    if not np.all(np.isfinite(evaluation)):
        raise ValueError("evaluation bank must be finite")
    return reference, evaluation


def estimate_mode(
    reference: np.ndarray,
    evaluation: np.ndarray,
    alpha: float,
    target_activation_rate: float,
    mode: BoundaryMode,
    *,
    common_activation_threshold: float | None = None,
) -> ModeEstimate:
    reference, evaluation = _validate_banks(reference, evaluation)
    alpha = float(alpha)
    target_activation_rate = float(target_activation_rate)

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1")
    if not 0.0 < target_activation_rate < 1.0:
        raise ValueError(
            "target_activation_rate must lie strictly between 0 and 1"
        )

    q0 = candidate_threshold(reference[:, 1], alpha, mode)
    q1 = candidate_threshold(reference[:, 2], alpha, mode)

    if common_activation_threshold is None:
        c = empirical_generalized_inverse(
            reference[:, 0],
            1.0 - target_activation_rate,
        )
    else:
        c = float(common_activation_threshold)
        if not math.isfinite(c):
            raise ValueError("common_activation_threshold must be finite")

    u = evaluation[:, 0]
    x0 = evaluation[:, 1]
    x1 = evaluation[:, 2]

    r0 = (x0 > q0).astype(float)
    activation = (u > c).astype(float)
    increment = ((x0 <= q0) & (x1 > q1)).astype(float)
    adaptive_rejection = r0 + activation * increment

    e0_hat = float(np.mean(r0))
    activation_rate_hat = float(np.mean(activation))
    mu_hat = float(np.mean(increment))
    nu_hat = float(np.mean(activation * increment))
    pi_adaptive_hat = float(np.mean(adaptive_rejection))
    pi_comparator_hat = float(
        e0_hat + activation_rate_hat * mu_hat
    )
    delta_pi_hat = float(pi_adaptive_hat - pi_comparator_hat)

    if not (
        0.0 <= pi_adaptive_hat < 1.0
        and 0.0 <= pi_comparator_hat < 1.0
    ):
        raise ValueError(
            "estimated rejection probabilities must lie in [0, 1)"
        )

    tess_adaptive_hat = tess_transform(pi_adaptive_hat, alpha)
    tess_comparator_hat = tess_transform(pi_comparator_hat, alpha)
    delta_tess_hat = float(
        tess_adaptive_hat - tess_comparator_hat
    )

    return ModeEstimate(
        mode=mode,
        q0_hat=float(q0),
        q1_hat=float(q1),
        c_hat=float(c),
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


def estimate_bridge(
    reference: np.ndarray,
    evaluation: np.ndarray,
    alpha: float,
    target_activation_rate: float,
) -> BridgeEstimate:
    reference, evaluation = _validate_banks(reference, evaluation)
    info = boundary_info(reference.shape[0], alpha)

    common_c = empirical_generalized_inverse(
        reference[:, 0],
        1.0 - float(target_activation_rate),
    )

    quantile = estimate_mode(
        reference,
        evaluation,
        alpha,
        target_activation_rate,
        "quantile",
        common_activation_threshold=common_c,
    )
    plus_one = estimate_mode(
        reference,
        evaluation,
        alpha,
        target_activation_rate,
        "plus_one",
        common_activation_threshold=common_c,
    )

    if quantile.c_hat != plus_one.c_hat:
        raise RuntimeError("activation threshold differs across modes")
    if quantile.activation_rate_hat != plus_one.activation_rate_hat:
        raise RuntimeError("activation realization differs across modes")

    q0_spacing = float(plus_one.q0_hat - quantile.q0_hat)
    q1_spacing = float(plus_one.q1_hat - quantile.q1_hat)
    delta_pi_bridge = float(
        plus_one.delta_pi_hat - quantile.delta_pi_hat
    )
    delta_tess_bridge = float(
        plus_one.delta_tess_hat - quantile.delta_tess_hat
    )

    return BridgeEstimate(
        alpha=float(alpha),
        target_activation_rate=float(target_activation_rate),
        boundary=info,
        quantile=quantile,
        plus_one=plus_one,
        q0_spacing=q0_spacing,
        q1_spacing=q1_spacing,
        delta_pi_bridge=delta_pi_bridge,
        delta_tess_bridge=delta_tess_bridge,
        abs_delta_pi_bridge=abs(delta_pi_bridge),
        abs_delta_tess_bridge=abs(delta_tess_bridge),
        delta_pi_strict_sign_reversal=_strict_sign_reversal(
            quantile.delta_pi_hat,
            plus_one.delta_pi_hat,
        ),
        delta_tess_strict_sign_reversal=_strict_sign_reversal(
            quantile.delta_tess_hat,
            plus_one.delta_tess_hat,
        ),
        delta_pi_zero_status_change=_zero_status_change(
            quantile.delta_pi_hat,
            plus_one.delta_pi_hat,
        ),
        delta_tess_zero_status_change=_zero_status_change(
            quantile.delta_tess_hat,
            plus_one.delta_tess_hat,
        ),
    )
