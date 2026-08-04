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

def beta_order_statistic_mean(
    reference_size: int,
    order_index: int,
) -> float:
    if reference_size < 1:
        raise ValueError("reference_size must be positive")
    if not 1 <= order_index <= reference_size:
        raise ValueError("order_index must lie in 1,...,B")
    return float(order_index / (reference_size + 1))


def beta_order_statistic_variance(
    reference_size: int,
    order_index: int,
) -> float:
    if reference_size < 1:
        raise ValueError("reference_size must be positive")
    if not 1 <= order_index <= reference_size:
        raise ValueError("order_index must lie in 1,...,B")
    numerator = order_index * (
        reference_size + 1 - order_index
    )
    denominator = (
        (reference_size + 1) ** 2
        * (reference_size + 2)
    )
    return float(numerator / denominator)


def beta_order_statistic_second_central_about_probability(
    reference_size: int,
    probability: float,
) -> float:
    order_index = quantile_order_index(
        reference_size,
        probability,
    )
    mean_shift = (
        beta_order_statistic_mean(
            reference_size,
            order_index,
        )
        - probability
    )
    return float(
        beta_order_statistic_variance(
            reference_size,
            order_index,
        )
        + mean_shift**2
    )


def scalar_quantile_mean_bias_leading_term(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    coefficient = scalar_quantile_bias_coefficient(
        reference_size,
        probability,
        density_at_quantile,
        density_derivative_at_quantile,
    )
    return float(coefficient / reference_size)


def inverse_cdf_first_derivative(
    density_at_quantile: float,
) -> float:
    if density_at_quantile <= 0.0:
        raise ValueError("density_at_quantile must be positive")
    return float(1.0 / density_at_quantile)


def inverse_cdf_second_derivative(
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    if density_at_quantile <= 0.0:
        raise ValueError("density_at_quantile must be positive")
    return float(
        -density_derivative_at_quantile
        / density_at_quantile**3
    )


def scalar_quantile_taylor_bias_from_exact_beta_moments(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    order_index = quantile_order_index(
        reference_size,
        probability,
    )
    mean_shift = (
        beta_order_statistic_mean(
            reference_size,
            order_index,
        )
        - probability
    )
    second_moment = (
        beta_order_statistic_second_central_about_probability(
            reference_size,
            probability,
        )
    )
    return float(
        inverse_cdf_first_derivative(
            density_at_quantile
        )
        * mean_shift
        + 0.5
        * inverse_cdf_second_derivative(
            density_at_quantile,
            density_derivative_at_quantile,
        )
        * second_moment
    )

def quantile_influence_vector(
    lower_indicators: FloatArray,
    probabilities: FloatArray,
    densities: FloatArray,
) -> FloatArray:
    indicators = np.asarray(lower_indicators, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    densities = np.asarray(densities, dtype=float)

    if indicators.shape != probabilities.shape:
        raise ValueError("indicator/probability shape mismatch")
    if densities.shape != probabilities.shape:
        raise ValueError("density/probability shape mismatch")
    if np.any((indicators != 0.0) & (indicators != 1.0)):
        raise ValueError("lower_indicators must be binary")
    if np.any(probabilities <= 0.0) or np.any(probabilities >= 1.0):
        raise ValueError("probabilities must lie in (0,1)")
    if np.any(densities <= 0.0):
        raise ValueError("densities must be positive")

    return (probabilities - indicators) / densities


def exact_influence_covariance_from_atoms(
    atom_probabilities: FloatArray,
    lower_indicator_atoms: FloatArray,
    probabilities: FloatArray,
    densities: FloatArray,
) -> FloatArray:
    weights = np.asarray(atom_probabilities, dtype=float)
    atoms = np.asarray(lower_indicator_atoms, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    densities = np.asarray(densities, dtype=float)

    if weights.ndim != 1:
        raise ValueError("atom_probabilities must be a vector")
    if atoms.ndim != 2 or atoms.shape[0] != weights.size:
        raise ValueError("indicator atom shape mismatch")
    if atoms.shape[1] != probabilities.size:
        raise ValueError("atom dimension mismatch")
    if not np.isclose(np.sum(weights), 1.0):
        raise ValueError("atom probabilities must sum to one")
    if np.any(weights < 0.0):
        raise ValueError("atom probabilities must be nonnegative")

    influences = np.vstack(
        [
            quantile_influence_vector(
                atom,
                probabilities,
                densities,
            )
            for atom in atoms
        ]
    )
    mean = weights @ influences
    centered = influences - mean
    covariance = centered.T @ (
        centered * weights[:, None]
    )
    return (covariance + covariance.T) / 2.0


def bahadur_second_moment_entry_error_bound(
    leading_variance_left: float,
    leading_variance_right: float,
    scaled_l2_remainder_left: float,
    scaled_l2_remainder_right: float,
) -> float:
    values = (
        leading_variance_left,
        leading_variance_right,
        scaled_l2_remainder_left,
        scaled_l2_remainder_right,
    )
    if any(value < 0.0 for value in values):
        raise ValueError("variance and remainder quantities must be nonnegative")

    return float(
        leading_variance_left**0.5
        * scaled_l2_remainder_right
        + leading_variance_right**0.5
        * scaled_l2_remainder_left
        + scaled_l2_remainder_left
        * scaled_l2_remainder_right
    )


def vector_moment_bound_from_component_bounds(
    component_scaled_moment_bounds: FloatArray,
    moment_order: float,
) -> float:
    bounds = np.asarray(
        component_scaled_moment_bounds,
        dtype=float,
    )
    if bounds.ndim != 1 or bounds.size == 0:
        raise ValueError("component bounds must be a nonempty vector")
    if np.any(bounds < 0.0):
        raise ValueError("component bounds must be nonnegative")
    if moment_order < 2.0:
        raise ValueError("moment_order must be at least two")

    dimension_factor = bounds.size ** (
        moment_order / 2.0 - 1.0
    )
    return float(dimension_factor * np.sum(bounds))


def joint_quantile_second_moment_limit(
    joint_lower_probabilities: FloatArray,
    probabilities: FloatArray,
    densities: FloatArray,
) -> FloatArray:
    return assemble_joint_quantile_covariance(
        probabilities,
        densities,
        joint_lower_probabilities,
    )

def quantile_local_tail_bound(
    reference_size: int,
    deviation: float,
    density_lower_bound: float,
) -> float:
    if reference_size < 1:
        raise ValueError("reference_size must be positive")
    if deviation < 0.0:
        raise ValueError("deviation must be nonnegative")
    if density_lower_bound <= 0.0:
        raise ValueError("density_lower_bound must be positive")

    effective_gap = max(
        density_lower_bound * deviation
        - 1.0 / reference_size,
        0.0,
    )
    return float(
        min(
            1.0,
            2.0
            * math.exp(
                -2.0
                * reference_size
                * effective_gap**2
            ),
        )
    )


def uniform_integrability_tail_bound(
    scaled_moment_bound: float,
    cutoff: float,
    moment_order: float,
) -> float:
    if scaled_moment_bound < 0.0:
        raise ValueError("scaled_moment_bound must be nonnegative")
    if cutoff <= 0.0:
        raise ValueError("cutoff must be positive")
    if moment_order <= 2.0:
        raise ValueError("moment_order must exceed two")

    return float(
        scaled_moment_bound
        / cutoff ** (moment_order - 2.0)
    )


def joint_scaled_l2_remainder_bound(
    component_scaled_l2_remainders: FloatArray,
) -> float:
    values = np.asarray(
        component_scaled_l2_remainders,
        dtype=float,
    )
    if values.ndim != 1 or values.size == 0:
        raise ValueError(
            "component remainders must be a nonempty vector"
        )
    if np.any(values < 0.0):
        raise ValueError(
            "component remainders must be nonnegative"
        )
    return float(np.sum(values))


def empirical_quantile_leading_term(
    empirical_cdf_at_quantile: float,
    probability: float,
    density_at_quantile: float,
) -> float:
    if not 0.0 <= empirical_cdf_at_quantile <= 1.0:
        raise ValueError(
            "empirical_cdf_at_quantile must lie in [0,1]"
        )
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must lie in (0,1)")
    if density_at_quantile <= 0.0:
        raise ValueError(
            "density_at_quantile must be positive"
        )
    return float(
        (
            probability
            - empirical_cdf_at_quantile
        )
        / density_at_quantile
    )


def scaled_lattice_negligibility(
    reference_size: int,
    probability: float,
) -> float:
    order_index = quantile_order_index(
        reference_size,
        probability,
    )
    return float(
        reference_size**0.5
        * abs(
            order_index / reference_size
            - probability
        )
    )


def fixed_dimension_bahadur_l2_closure(
    component_scaled_l2_remainders: FloatArray,
) -> dict[str, float | bool]:
    total = joint_scaled_l2_remainder_bound(
        component_scaled_l2_remainders
    )
    return {
        "joint_scaled_l2_bound": total,
        "joint_l2_remainder_vanishes": bool(
            np.isclose(total, 0.0)
        ),
    }

def moving_face_first_derivative_sign(
    upper_tail: bool,
) -> float:
    return -1.0 if upper_tail else 1.0


def moving_face_mixed_derivative_sign(
    upper_tail_left: bool,
    upper_tail_right: bool,
) -> float:
    return float(
        moving_face_first_derivative_sign(
            upper_tail_left
        )
        * moving_face_first_derivative_sign(
            upper_tail_right
        )
    )


def policy_contrast_gradient(
    gradient_joint: FloatArray,
    probability_activation: float,
    gradient_activation: FloatArray,
    probability_incremental: float,
    gradient_incremental: FloatArray,
) -> FloatArray:
    grad_joint = np.asarray(
        gradient_joint,
        dtype=float,
    )
    grad_activation = np.asarray(
        gradient_activation,
        dtype=float,
    )
    grad_incremental = np.asarray(
        gradient_incremental,
        dtype=float,
    )
    if not (
        grad_joint.shape
        == grad_activation.shape
        == grad_incremental.shape
    ):
        raise ValueError("gradient shape mismatch")

    return (
        grad_joint
        - probability_incremental
        * grad_activation
        - probability_activation
        * grad_incremental
    )


def policy_contrast_hessian(
    hessian_joint: FloatArray,
    probability_activation: float,
    gradient_activation: FloatArray,
    hessian_activation: FloatArray,
    probability_incremental: float,
    gradient_incremental: FloatArray,
    hessian_incremental: FloatArray,
) -> FloatArray:
    h_joint = np.asarray(
        hessian_joint,
        dtype=float,
    )
    grad_activation = np.asarray(
        gradient_activation,
        dtype=float,
    )
    h_activation = np.asarray(
        hessian_activation,
        dtype=float,
    )
    grad_incremental = np.asarray(
        gradient_incremental,
        dtype=float,
    )
    h_incremental = np.asarray(
        hessian_incremental,
        dtype=float,
    )

    dimension = grad_activation.size
    expected = (dimension, dimension)
    if (
        grad_incremental.shape != (dimension,)
        or h_joint.shape != expected
        or h_activation.shape != expected
        or h_incremental.shape != expected
    ):
        raise ValueError("policy derivative shape mismatch")

    result = (
        h_joint
        - probability_incremental
        * h_activation
        - probability_activation
        * h_incremental
        - np.outer(
            grad_activation,
            grad_incremental,
        )
        - np.outer(
            grad_incremental,
            grad_activation,
        )
    )
    return (result + result.T) / 2.0


def winner_cell_incremental_is_possible(
    base_winner: int,
    full_winner: int,
) -> bool:
    return bool(base_winner != full_winner)


def separated_activation_regime(
    base_candidate_threshold: float,
    trigger_threshold: float,
) -> str:
    if trigger_threshold < base_candidate_threshold:
        return "trigger_below_candidate"
    if trigger_threshold > base_candidate_threshold:
        return "trigger_above_candidate"
    return "coincidence_nonregular"


def independent_gaussian_cell_components(
    base_candidate_threshold: float,
    full_candidate_threshold: float,
    trigger_threshold: float,
) -> dict[str, FloatArray | float]:
    from scipy.stats import norm

    q0 = float(base_candidate_threshold)
    q1 = float(full_candidate_threshold)
    c = float(trigger_threshold)
    if not c < q0:
        raise ValueError(
            "this separated cell formula requires c < q0"
        )

    phi_q0 = float(norm.pdf(q0))
    phi_q1 = float(norm.pdf(q1))
    phi_c = float(norm.pdf(c))
    cdf_q0 = float(norm.cdf(q0))
    cdf_c = float(norm.cdf(c))
    sf_q1 = float(norm.sf(q1))
    sf_c = float(norm.sf(c))

    p_activation = sf_c
    grad_activation = np.array(
        [0.0, 0.0, -phi_c],
        dtype=float,
    )
    h_activation = np.zeros((3, 3), dtype=float)
    h_activation[2, 2] = c * phi_c

    p_incremental = cdf_q0 * sf_q1
    grad_incremental = np.array(
        [
            phi_q0 * sf_q1,
            -cdf_q0 * phi_q1,
            0.0,
        ],
        dtype=float,
    )
    h_incremental = np.zeros((3, 3), dtype=float)
    h_incremental[0, 0] = -q0 * phi_q0 * sf_q1
    h_incremental[1, 1] = (
        cdf_q0 * q1 * phi_q1
    )
    h_incremental[0, 1] = -phi_q0 * phi_q1
    h_incremental[1, 0] = h_incremental[0, 1]

    interval_mass = cdf_q0 - cdf_c
    p_joint = interval_mass * sf_q1
    grad_joint = np.array(
        [
            phi_q0 * sf_q1,
            -interval_mass * phi_q1,
            -phi_c * sf_q1,
        ],
        dtype=float,
    )
    h_joint = np.zeros((3, 3), dtype=float)
    h_joint[0, 0] = -q0 * phi_q0 * sf_q1
    h_joint[1, 1] = (
        interval_mass * q1 * phi_q1
    )
    h_joint[2, 2] = c * phi_c * sf_q1
    h_joint[0, 1] = -phi_q0 * phi_q1
    h_joint[1, 0] = h_joint[0, 1]
    h_joint[1, 2] = phi_c * phi_q1
    h_joint[2, 1] = h_joint[1, 2]

    return {
        "probability_activation": p_activation,
        "gradient_activation": grad_activation,
        "hessian_activation": h_activation,
        "probability_incremental": p_incremental,
        "gradient_incremental": grad_incremental,
        "hessian_incremental": h_incremental,
        "probability_joint": p_joint,
        "gradient_joint": grad_joint,
        "hessian_joint": h_joint,
    }


def independent_gaussian_cell_contrast(
    base_candidate_threshold: float,
    full_candidate_threshold: float,
    trigger_threshold: float,
) -> float:
    components = independent_gaussian_cell_components(
        base_candidate_threshold,
        full_candidate_threshold,
        trigger_threshold,
    )
    return float(
        components["probability_joint"]
        - components["probability_activation"]
        * components["probability_incremental"]
    )


def independent_gaussian_cell_contrast_derivatives(
    base_candidate_threshold: float,
    full_candidate_threshold: float,
    trigger_threshold: float,
) -> tuple[FloatArray, FloatArray]:
    components = independent_gaussian_cell_components(
        base_candidate_threshold,
        full_candidate_threshold,
        trigger_threshold,
    )
    gradient = policy_contrast_gradient(
        components["gradient_joint"],
        components["probability_activation"],
        components["gradient_activation"],
        components["probability_incremental"],
        components["gradient_incremental"],
    )
    hessian = policy_contrast_hessian(
        components["hessian_joint"],
        components["probability_activation"],
        components["gradient_activation"],
        components["hessian_activation"],
        components["probability_incremental"],
        components["gradient_incremental"],
        components["hessian_incremental"],
    )
    return gradient, hessian

def second_order_expectation_coefficient(
    gradient: FloatArray,
    mean_bias_coefficient: FloatArray,
    hessian: FloatArray,
    covariance: FloatArray,
) -> float:
    return expectation_level_reference_coefficient(
        gradient,
        mean_bias_coefficient,
        hessian,
        covariance,
    )


def final_policy_bias_approximation(
    population_delta: float,
    reference_bias_coefficient: float,
    reference_size: int,
    evaluation_size: int,
    *,
    retain_interaction: bool = True,
) -> float:
    return combined_bias_approximation(
        population_delta,
        reference_bias_coefficient,
        reference_size,
        evaluation_size,
        retain_interaction=retain_interaction,
    )


def adaptive_rejection_estimator(
    adaptive_reject: FloatArray,
) -> float:
    values = np.asarray(adaptive_reject, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise ValueError(
            "adaptive_reject must be a nonempty vector"
        )
    return float(np.mean(values))


def comparator_rejection_estimator(
    base_reject: FloatArray,
    activation: FloatArray,
    incremental: FloatArray,
) -> float:
    r0 = np.asarray(base_reject, dtype=float)
    a = np.asarray(activation, dtype=float)
    m = np.asarray(incremental, dtype=float)
    if (
        r0.ndim != 1
        or a.ndim != 1
        or m.ndim != 1
        or not (r0.shape == a.shape == m.shape)
        or r0.size == 0
    ):
        raise ValueError(
            "evaluation fields must be nonempty equal-length vectors"
        )
    return float(
        np.mean(r0)
        + np.mean(a) * np.mean(m)
    )


def comparator_conditional_mean(
    comparator_probability: float,
    policy_delta: float,
    evaluation_size: int,
) -> float:
    if evaluation_size < 1:
        raise ValueError(
            "evaluation_size must be positive"
        )
    return float(
        comparator_probability
        + policy_delta / evaluation_size
    )


def adaptive_evaluation_influence(
    adaptive_reject: FloatArray,
    adaptive_probability: float,
) -> FloatArray:
    h = np.asarray(adaptive_reject, dtype=float)
    if h.ndim != 1:
        raise ValueError(
            "adaptive_reject must be a vector"
        )
    return h - adaptive_probability


def comparator_evaluation_influence(
    base_reject: FloatArray,
    activation: FloatArray,
    incremental: FloatArray,
    base_probability: float,
    activation_probability: float,
    incremental_probability: float,
) -> FloatArray:
    r0 = np.asarray(base_reject, dtype=float)
    a = np.asarray(activation, dtype=float)
    m = np.asarray(incremental, dtype=float)
    if (
        r0.ndim != 1
        or a.ndim != 1
        or m.ndim != 1
        or not (r0.shape == a.shape == m.shape)
    ):
        raise ValueError(
            "evaluation fields must be equal-length vectors"
        )
    return (
        (r0 - base_probability)
        + incremental_probability
        * (a - activation_probability)
        + activation_probability
        * (m - incremental_probability)
    )


def tess_reference_bias_coefficient(
    alpha: float,
    adaptive_probability: float,
    comparator_probability: float,
    adaptive_reference_mean_bias: float,
    comparator_reference_mean_bias: float,
    adaptive_reference_variance: float,
    comparator_reference_variance: float,
) -> float:
    return float(
        tess_first_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_reference_mean_bias
        + 0.5
        * tess_second_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_reference_variance
        - tess_first_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_reference_mean_bias
        - 0.5
        * tess_second_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_reference_variance
    )


def tess_evaluation_bias_coefficient(
    alpha: float,
    adaptive_probability: float,
    comparator_probability: float,
    policy_delta: float,
    adaptive_evaluation_variance: float,
    comparator_evaluation_variance: float,
) -> float:
    return float(
        0.5
        * tess_second_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_evaluation_variance
        - tess_first_derivative(
            comparator_probability,
            alpha,
        )
        * policy_delta
        - 0.5
        * tess_second_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_evaluation_variance
    )


def tess_second_order_bias_approximation(
    reference_coefficient: float,
    evaluation_coefficient: float,
    reference_size: int,
    evaluation_size: int,
) -> float:
    if reference_size < 1 or evaluation_size < 1:
        raise ValueError(
            "sample sizes must be positive"
        )
    return float(
        reference_coefficient / reference_size
        + evaluation_coefficient / evaluation_size
    )


def bernoulli_variance(probability: float) -> float:
    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must lie in [0,1]"
        )
    return float(
        probability * (1.0 - probability)
    )
