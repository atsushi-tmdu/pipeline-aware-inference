from __future__ import annotations

import math
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def empirical_covariance_estimator(a: FloatArray, m: FloatArray) -> float:
    a = np.asarray(a, dtype=float)
    m = np.asarray(m, dtype=float)
    if a.ndim != 1 or m.ndim != 1 or a.shape != m.shape or len(a) == 0:
        raise ValueError("a and m must be nonempty equal-length vectors")
    return float(np.mean(a * m) - np.mean(a) * np.mean(m))


def exact_conditional_expectation(delta: float, n: int) -> float:
    if n < 1:
        raise ValueError("n must be positive")
    return float((1.0 - 1.0 / n) * delta)


def exact_evaluation_bias(delta: float, n: int) -> float:
    return exact_conditional_expectation(delta, n) - delta


def second_order_reference_coefficient(
    gradient: FloatArray,
    threshold_bias: FloatArray,
    hessian: FloatArray,
    threshold_covariance: FloatArray,
) -> float:
    g = np.asarray(gradient, dtype=float)
    b = np.asarray(threshold_bias, dtype=float)
    h = np.asarray(hessian, dtype=float)
    s = np.asarray(threshold_covariance, dtype=float)
    d = g.size
    if b.shape != (d,) or h.shape != (d, d) or s.shape != (d, d):
        raise ValueError("shape mismatch")
    if not np.allclose(h, h.T) or not np.allclose(s, s.T):
        raise ValueError("hessian and covariance must be symmetric")
    return float(g @ b + 0.5 * np.trace(h @ s))


def combined_bias_approximation(
    delta: float,
    reference_coefficient: float,
    B: int,
    n: int,
    retain_interaction: bool = True,
) -> float:
    if B < 1 or n < 1:
        raise ValueError("sample sizes must be positive")
    value = reference_coefficient / B - delta / n
    if retain_interaction:
        value -= reference_coefficient / (B * n)
    return float(value)


def exact_mean_from_truncated_reference_expansion(
    delta: float,
    reference_coefficient: float,
    B: int,
    n: int,
) -> float:
    return exact_conditional_expectation(
        delta + reference_coefficient / B,
        n,
    )


def candidate_trigger_cross_curvature(
    h_qc: FloatArray,
    sigma_qc: FloatArray,
) -> float:
    h_qc = np.asarray(h_qc, dtype=float)
    sigma_qc = np.asarray(sigma_qc, dtype=float)
    if h_qc.shape != sigma_qc.shape:
        raise ValueError("cross-block shape mismatch")
    return float(np.sum(h_qc * sigma_qc))


def tess_value(x: float, alpha: float) -> float:
    if not 0.0 <= x < 1.0 or not 0.0 < alpha < 1.0:
        raise ValueError("invalid probability or alpha")
    return float(math.log1p(-x) / math.log1p(-alpha))


def tess_first_derivative(x: float, alpha: float) -> float:
    return float(-1.0 / ((1.0 - x) * math.log1p(-alpha)))


def tess_second_derivative(x: float, alpha: float) -> float:
    return float(-1.0 / ((1.0 - x) ** 2 * math.log1p(-alpha)))


def transformed_second_order_bias(
    first_derivative: float,
    second_derivative: float,
    mean_bias_coefficient: float,
    variance_coefficient: float,
) -> float:
    return float(
        first_derivative * mean_bias_coefficient
        + 0.5 * second_derivative * variance_coefficient
    )


def quantile_order_index(reference_size: int, probability: float) -> int:
    if reference_size < 1:
        raise ValueError("reference_size must be positive")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    return int(math.ceil(reference_size * probability))


def quantile_lattice_offset(
    reference_size: int,
    probability: float,
) -> float:
    k = quantile_order_index(reference_size, probability)
    return float(k - (reference_size + 1) * probability)


def uniform_order_statistic_bias(
    reference_size: int,
    probability: float,
) -> float:
    k = quantile_order_index(reference_size, probability)
    return float(k / (reference_size + 1) - probability)


def scalar_quantile_bias_coefficient(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    if density_at_quantile <= 0.0:
        raise ValueError("density_at_quantile must be positive")
    lattice = quantile_lattice_offset(
        reference_size,
        probability,
    )
    return float(
        lattice / density_at_quantile
        - probability
        * (1.0 - probability)
        * density_derivative_at_quantile
        / (2.0 * density_at_quantile**3)
    )


def joint_quantile_first_order_covariance(
    joint_lower_probability: float,
    probability_left: float,
    probability_right: float,
    density_left: float,
    density_right: float,
) -> float:
    for value in (
        joint_lower_probability,
        probability_left,
        probability_right,
    ):
        if not 0.0 <= value <= 1.0:
            raise ValueError("probabilities must lie in [0,1]")
    if density_left <= 0.0 or density_right <= 0.0:
        raise ValueError("densities must be positive")
    return float(
        (
            joint_lower_probability
            - probability_left * probability_right
        )
        / (density_left * density_right)
    )


def second_order_reference_coefficient_b_dependent(
    gradient: FloatArray,
    threshold_bias_coefficient_b: FloatArray,
    hessian: FloatArray,
    threshold_covariance: FloatArray,
) -> float:
    return second_order_reference_coefficient(
        gradient,
        threshold_bias_coefficient_b,
        hessian,
        threshold_covariance,
    )


def assemble_joint_quantile_covariance(
    probabilities: FloatArray,
    densities: FloatArray,
    joint_lower_probabilities: FloatArray,
) -> FloatArray:
    probabilities = np.asarray(probabilities, dtype=float)
    densities = np.asarray(densities, dtype=float)
    joint = np.asarray(joint_lower_probabilities, dtype=float)

    dimension = probabilities.size
    if densities.shape != (dimension,):
        raise ValueError("densities shape mismatch")
    if joint.shape != (dimension, dimension):
        raise ValueError("joint_lower_probabilities shape mismatch")
    if np.any(probabilities <= 0.0) or np.any(probabilities >= 1.0):
        raise ValueError("probabilities must lie in (0,1)")
    if np.any(densities <= 0.0):
        raise ValueError("densities must be positive")
    if not np.allclose(joint, joint.T):
        raise ValueError("joint lower-probability matrix must be symmetric")
    if not np.allclose(np.diag(joint), probabilities):
        raise ValueError("joint diagonal must equal marginal probabilities")

    numerator = joint - np.outer(probabilities, probabilities)
    denominator = np.outer(densities, densities)
    covariance = numerator / denominator
    return (covariance + covariance.T) / 2.0


def hessian_covariance_block_contraction(
    hessian_qq: FloatArray,
    hessian_qc: FloatArray,
    hessian_cc: float,
    covariance_qq: FloatArray,
    covariance_qc: FloatArray,
    covariance_cc: float,
) -> dict[str, float]:
    h_qq = np.asarray(hessian_qq, dtype=float)
    h_qc = np.asarray(hessian_qc, dtype=float)
    s_qq = np.asarray(covariance_qq, dtype=float)
    s_qc = np.asarray(covariance_qc, dtype=float)

    if h_qq.ndim != 2 or h_qq.shape[0] != h_qq.shape[1]:
        raise ValueError("hessian_qq must be square")
    dimension = h_qq.shape[0]
    if s_qq.shape != (dimension, dimension):
        raise ValueError("covariance_qq shape mismatch")
    if h_qc.shape not in {(dimension,), (dimension, 1)}:
        raise ValueError("hessian_qc shape mismatch")
    if s_qc.shape not in {(dimension,), (dimension, 1)}:
        raise ValueError("covariance_qc shape mismatch")
    if not np.allclose(h_qq, h_qq.T):
        raise ValueError("hessian_qq must be symmetric")
    if not np.allclose(s_qq, s_qq.T):
        raise ValueError("covariance_qq must be symmetric")
    if covariance_cc < 0.0:
        raise ValueError("covariance_cc must be nonnegative")

    candidate = float(0.5 * np.trace(h_qq @ s_qq))
    cross = float(
        np.asarray(h_qc).reshape(-1)
        @ np.asarray(s_qc).reshape(-1)
    )
    trigger = float(0.5 * hessian_cc * covariance_cc)
    return {
        "candidate_candidate": candidate,
        "candidate_trigger": cross,
        "trigger_trigger": trigger,
        "total": candidate + cross + trigger,
    }


def expectation_level_reference_coefficient(
    gradient: FloatArray,
    mean_bias_coefficient_b: FloatArray,
    hessian: FloatArray,
    first_order_covariance: FloatArray,
) -> float:
    return second_order_reference_coefficient_b_dependent(
        gradient,
        mean_bias_coefficient_b,
        hessian,
        first_order_covariance,
    )


def threshold_ordering_stability_radius(
    candidate_thresholds: FloatArray,
    trigger_threshold: float,
) -> float:
    candidates = np.asarray(candidate_thresholds, dtype=float)
    if candidates.ndim != 1 or candidates.size == 0:
        raise ValueError("candidate_thresholds must be a nonempty vector")
    return float(0.5 * np.min(np.abs(candidates - trigger_threshold)))
def covariance_candidate_boundary_coefficient(
    activation_probability: float,
    conditional_activation_jump: float,
    conditional_jump: float,
) -> float:
    return float(
        conditional_activation_jump
        - activation_probability * conditional_jump
    )


def covariance_trigger_boundary_coefficient(
    incremental_probability: float,
    conditional_incremental_at_trigger: float,
) -> float:
    return float(
        incremental_probability
        - conditional_incremental_at_trigger
    )


def boundary_gradient_from_if_coefficient(
    boundary_density: float,
    reference_if_coefficient: float,
) -> float:
    if boundary_density <= 0.0:
        raise ValueError("boundary_density must be positive")
    return float(boundary_density * reference_if_coefficient)


def reference_if_coefficient_from_gradient(
    boundary_gradient: float,
    boundary_density: float,
) -> float:
    if boundary_density <= 0.0:
        raise ValueError("boundary_density must be positive")
    return float(boundary_gradient / boundary_density)


def bivariate_normal_indicator_covariance(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.integrate import quad
    from scipy.stats import norm

    if not -1.0 < correlation < 1.0:
        raise ValueError("correlation must lie in (-1,1)")

    conditional_sd = (1.0 - correlation**2) ** 0.5

    def integrand(candidate_value: float) -> float:
        conditional_mean = correlation * candidate_value
        conditional_upper = norm.sf(
            (
                trigger_threshold
                - conditional_mean
            )
            / conditional_sd
        )
        return float(
            norm.pdf(candidate_value)
            * conditional_upper
        )

    joint_upper, _ = quad(
        integrand,
        candidate_threshold,
        float("inf"),
        epsabs=1e-12,
        epsrel=1e-12,
        limit=200,
    )
    candidate_upper = float(norm.sf(candidate_threshold))
    trigger_upper = float(norm.sf(trigger_threshold))
    return float(
        joint_upper - candidate_upper * trigger_upper
    )


def bivariate_normal_candidate_beta(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    conditional_mean = correlation * candidate_threshold
    conditional_sd = (1.0 - correlation**2) ** 0.5
    conditional_activation = float(
        norm.sf(
            (trigger_threshold - conditional_mean)
            / conditional_sd
        )
    )
    activation_probability = float(norm.sf(trigger_threshold))
    # Raising the candidate threshold turns M=I(X>q) off, so D=-1.
    return float(
        activation_probability - conditional_activation
    )


def bivariate_normal_trigger_beta(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    conditional_mean = correlation * trigger_threshold
    conditional_sd = (1.0 - correlation**2) ** 0.5
    conditional_incremental = float(
        norm.sf(
            (candidate_threshold - conditional_mean)
            / conditional_sd
        )
    )
    incremental_probability = float(norm.sf(candidate_threshold))
    return float(
        incremental_probability - conditional_incremental
    )


def bivariate_normal_candidate_gradient(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    beta = bivariate_normal_candidate_beta(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    return boundary_gradient_from_if_coefficient(
        float(norm.pdf(candidate_threshold)),
        beta,
    )


def bivariate_normal_trigger_gradient(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    beta = bivariate_normal_trigger_beta(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    return boundary_gradient_from_if_coefficient(
        float(norm.pdf(trigger_threshold)),
        beta,
    )


def bivariate_normal_candidate_trigger_hessian(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    conditional_mean = correlation * candidate_threshold
    conditional_sd = (1.0 - correlation**2) ** 0.5
    conditional_density = float(
        norm.pdf(
            (trigger_threshold - conditional_mean)
            / conditional_sd
        )
        / conditional_sd
    )
    marginal_density = float(norm.pdf(trigger_threshold))
    return float(
        norm.pdf(candidate_threshold)
        * (conditional_density - marginal_density)
    )
def bivariate_normal_candidate_second_derivative(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    if not -1.0 < correlation < 1.0:
        raise ValueError("correlation must lie in (-1,1)")

    conditional_sd = (1.0 - correlation**2) ** 0.5
    z = (
        trigger_threshold
        - correlation * candidate_threshold
    ) / conditional_sd
    candidate_density = float(norm.pdf(candidate_threshold))
    candidate_beta = bivariate_normal_candidate_beta(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    conditional_density = float(norm.pdf(z) / conditional_sd)

    return float(
        -candidate_threshold
        * candidate_density
        * candidate_beta
        - candidate_density
        * correlation
        * conditional_density
    )


def bivariate_normal_trigger_second_derivative(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> float:
    from scipy.stats import norm

    if not -1.0 < correlation < 1.0:
        raise ValueError("correlation must lie in (-1,1)")

    conditional_sd = (1.0 - correlation**2) ** 0.5
    z = (
        candidate_threshold
        - correlation * trigger_threshold
    ) / conditional_sd
    trigger_density = float(norm.pdf(trigger_threshold))
    trigger_beta = bivariate_normal_trigger_beta(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    conditional_density = float(norm.pdf(z) / conditional_sd)

    return float(
        -trigger_threshold
        * trigger_density
        * trigger_beta
        - trigger_density
        * correlation
        * conditional_density
    )


def bivariate_normal_policy_hessian(
    candidate_threshold: float,
    trigger_threshold: float,
    correlation: float,
) -> FloatArray:
    qq = bivariate_normal_candidate_second_derivative(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    qc = bivariate_normal_candidate_trigger_hessian(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    cc = bivariate_normal_trigger_second_derivative(
        candidate_threshold,
        trigger_threshold,
        correlation,
    )
    return np.array(
        [[qq, qc], [qc, cc]],
        dtype=float,
    )


def local_threshold_box_is_order_stable(
    candidate_thresholds: FloatArray,
    trigger_threshold: float,
    radius: float,
) -> bool:
    candidates = np.asarray(candidate_thresholds, dtype=float)
    if candidates.ndim != 1 or candidates.size == 0:
        raise ValueError("candidate_thresholds must be a nonempty vector")
    if radius < 0.0:
        raise ValueError("radius must be nonnegative")

    original_signs = np.sign(candidates - trigger_threshold)
    if np.any(original_signs == 0.0):
        return radius == 0.0

    worst_case_margin = (
        np.abs(candidates - trigger_threshold)
        - 2.0 * radius
    )
    return bool(np.all(worst_case_margin > 0.0))


def finite_winner_cell_count(
    base_pool_size: int,
    full_pool_size: int,
) -> int:
    if base_pool_size < 1 or full_pool_size < 1:
        raise ValueError("pool sizes must be positive")
    if base_pool_size > full_pool_size:
        raise ValueError("base pool cannot exceed full pool")
    return int(base_pool_size * full_pool_size)
