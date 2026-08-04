from __future__ import annotations

import numpy as np

from scipy.stats import norm


def gaussian_cell_branch_antiderivative(
    cdf_value: float,
) -> float:
    value = float(cdf_value)
    return float(
        0.5 * value**2
        - value**3 / 3.0
    )


def gaussian_cell_branch_probability(
    base_threshold: float,
    added_threshold: float,
) -> float:
    base_cdf = float(norm.cdf(base_threshold))
    added_cdf = float(norm.cdf(added_threshold))
    added_survival = 1.0 - added_cdf

    if base_threshold <= added_threshold:
        return float(
            0.5
            * base_cdf**2
            * added_survival
        )

    return float(
        0.5
        * added_cdf**2
        * added_survival
        + gaussian_cell_branch_antiderivative(
            base_cdf
        )
        - gaussian_cell_branch_antiderivative(
            added_cdf
        )
    )


def gaussian_cell_branch_base_derivative(
    base_threshold: float,
    added_threshold: float,
) -> float:
    return float(
        norm.pdf(base_threshold)
        * norm.cdf(base_threshold)
        * norm.sf(max(base_threshold, added_threshold))
    )


def gaussian_cell_branch_kink_jump(
    threshold: float,
) -> float:
    return float(
        -norm.pdf(threshold) ** 2
        * norm.cdf(threshold)
    )


def gaussian_cell_branch_kink_coefficient(
    threshold: float,
) -> float:
    return float(
        0.5
        * gaussian_cell_branch_kink_jump(threshold)
    )


def gaussian_cell_branch_local_coefficients(
    threshold: float,
) -> dict[str, float]:
    t = float(threshold)
    phi = float(norm.pdf(t))
    cdf = float(norm.cdf(t))
    sf = float(norm.sf(t))

    density_face = phi * cdf
    density_face_derivative = (
        -t * phi * cdf
        + phi**2
    )
    upper_tail_derivative = -phi
    upper_tail_second_derivative = t * phi

    base_integral = 0.5 * cdf**2

    return {
        "value": gaussian_cell_branch_probability(t, t),
        "linear_base": density_face * sf,
        "linear_added": base_integral * upper_tail_derivative,
        "smooth_uu": sf * density_face_derivative,
        "smooth_uv": (
            density_face * upper_tail_derivative
        ),
        "smooth_vv": (
            base_integral
            * upper_tail_second_derivative
        ),
        "kink_coefficient": (
            0.5
            * density_face
            * upper_tail_derivative
        ),
    }


def gaussian_cell_branch_piecewise_quadratic(
    threshold: float,
    base_increment: float,
    added_increment: float,
) -> float:
    coefficients = (
        gaussian_cell_branch_local_coefficients(
            threshold
        )
    )
    u = float(base_increment)
    v = float(added_increment)

    smooth_quadratic = 0.5 * (
        coefficients["smooth_uu"] * u**2
        + 2.0
        * coefficients["smooth_uv"]
        * u
        * v
        + coefficients["smooth_vv"] * v**2
    )
    kink_quadratic = (
        coefficients["kink_coefficient"]
        * max(u - v, 0.0) ** 2
    )

    return float(
        coefficients["value"]
        + coefficients["linear_base"] * u
        + coefficients["linear_added"] * v
        + smooth_quadratic
        + kink_quadratic
    )


def centered_gaussian_positive_part_second_moment(
    variance: float,
) -> float:
    if variance < 0.0:
        raise ValueError("variance must be nonnegative")
    return float(0.5 * variance)


def generalized_kink_expectation_coefficient(
    kink_coefficient: float,
    contrast_variance: float,
) -> float:
    return float(
        kink_coefficient
        * centered_gaussian_positive_part_second_moment(
            contrast_variance
        )
    )


def ordinary_c2_applicable_at_candidate_coincidence() -> bool:
    return False

def generalized_policy_kink_coefficients(
    activation_probability: float,
    active_am_flags: FloatArray,
    branch_kink_coefficients: FloatArray,
) -> FloatArray:
    flags = np.asarray(
        active_am_flags,
        dtype=float,
    )
    kappas = np.asarray(
        branch_kink_coefficients,
        dtype=float,
    )
    if flags.shape != kappas.shape:
        raise ValueError(
            "active flags and kink coefficients must match"
        )
    if not 0.0 <= activation_probability <= 1.0:
        raise ValueError(
            "activation_probability must lie in [0,1]"
        )
    if np.any((flags != 0.0) & (flags != 1.0)):
        raise ValueError(
            "active_am_flags must be binary"
        )

    return (
        flags - activation_probability
    ) * kappas


def generalized_policy_expectation_coefficient(
    gradient: FloatArray,
    mean_bias_coefficient: FloatArray,
    smooth_hessian: FloatArray,
    covariance: FloatArray,
    kink_directions: FloatArray,
    kink_coefficients: FloatArray,
) -> float:
    grad = np.asarray(gradient, dtype=float)
    bias = np.asarray(
        mean_bias_coefficient,
        dtype=float,
    )
    hessian = np.asarray(
        smooth_hessian,
        dtype=float,
    )
    sigma = np.asarray(covariance, dtype=float)
    directions = np.asarray(
        kink_directions,
        dtype=float,
    )
    coefficients = np.asarray(
        kink_coefficients,
        dtype=float,
    )

    dimension = grad.size
    if bias.shape != (dimension,):
        raise ValueError("bias shape mismatch")
    if (
        hessian.shape != (dimension, dimension)
        or sigma.shape != (dimension, dimension)
    ):
        raise ValueError("matrix shape mismatch")
    if directions.ndim != 2:
        raise ValueError(
            "kink_directions must be a matrix"
        )
    if directions.shape[1] != dimension:
        raise ValueError(
            "kink direction dimension mismatch"
        )
    if coefficients.shape != (
        directions.shape[0],
    ):
        raise ValueError(
            "kink coefficient count mismatch"
        )

    smooth = float(
        grad @ bias
        + 0.5 * np.trace(hessian @ sigma)
    )
    kink = 0.0
    for coefficient, direction in zip(
        coefficients,
        directions,
    ):
        contrast_variance = float(
            direction @ sigma @ direction
        )
        if contrast_variance < -1e-12:
            raise ValueError(
                "negative contrast variance"
            )
        kink += (
            float(coefficient)
            * 0.5
            * max(contrast_variance, 0.0)
        )
    return float(smooth + kink)


def generalized_smooth_composition_coefficient(
    transform_first_derivative: float,
    transform_second_derivative: float,
    probability_gradient: FloatArray,
    probability_generalized_coefficient: float,
    covariance: FloatArray,
) -> float:
    gradient = np.asarray(
        probability_gradient,
        dtype=float,
    )
    sigma = np.asarray(covariance, dtype=float)
    if sigma.shape != (
        gradient.size,
        gradient.size,
    ):
        raise ValueError(
            "composition covariance shape mismatch"
        )
    reference_variance = float(
        gradient @ sigma @ gradient
    )
    return float(
        transform_first_derivative
        * probability_generalized_coefficient
        + 0.5
        * transform_second_derivative
        * reference_variance
    )


def generalized_policy_quadratic_value(
    increment: FloatArray,
    smooth_hessian: FloatArray,
    kink_directions: FloatArray,
    kink_coefficients: FloatArray,
) -> float:
    value = np.asarray(
        increment,
        dtype=float,
    )
    hessian = np.asarray(
        smooth_hessian,
        dtype=float,
    )
    directions = np.asarray(
        kink_directions,
        dtype=float,
    )
    coefficients = np.asarray(
        kink_coefficients,
        dtype=float,
    )

    if hessian.shape != (
        value.size,
        value.size,
    ):
        raise ValueError(
            "quadratic Hessian shape mismatch"
        )
    if (
        directions.ndim != 2
        or directions.shape[1] != value.size
        or coefficients.shape != (
            directions.shape[0],
        )
    ):
        raise ValueError(
            "quadratic kink shape mismatch"
        )

    result = float(
        0.5 * value @ hessian @ value
    )
    for coefficient, direction in zip(
        coefficients,
        directions,
    ):
        result += float(
            coefficient
            * max(
                float(direction @ value),
                0.0,
            )
            ** 2
        )
    return float(result)


def gaussian_toy_policy_contrast(
    base_candidate_threshold: float,
    added_candidate_threshold: float,
    trigger_threshold: float,
) -> float:
    if not trigger_threshold < base_candidate_threshold:
        raise ValueError(
            "toy policy requires trigger below base threshold"
        )
    activation = float(norm.sf(trigger_threshold))
    branch = gaussian_cell_branch_probability(
        base_candidate_threshold,
        added_candidate_threshold,
    )
    trigger_branch = gaussian_cell_branch_probability(
        trigger_threshold,
        added_candidate_threshold,
    )
    return float(
        (1.0 - activation) * branch
        - trigger_branch
    )


def gaussian_toy_policy_local_components(
    candidate_threshold: float,
    trigger_threshold: float,
) -> dict[str, FloatArray | float]:
    t = float(candidate_threshold)
    c = float(trigger_threshold)
    if not c < t:
        raise ValueError(
            "toy policy requires trigger below candidate threshold"
        )

    branch = gaussian_cell_branch_local_coefficients(t)
    activation = float(norm.sf(c))
    activation_complement = 1.0 - activation
    complement_first = float(norm.pdf(c))
    complement_second = float(
        -c * norm.pdf(c)
    )

    cdf_c = float(norm.cdf(c))
    phi_c = float(norm.pdf(c))
    cdf_t = float(norm.cdf(t))
    phi_t = float(norm.pdf(t))
    sf_t = float(norm.sf(t))

    trigger_branch = float(
        0.5 * cdf_c**2 * sf_t
    )
    trigger_gradient = np.array(
        [
            0.0,
            -0.5 * cdf_c**2 * phi_t,
            phi_c * cdf_c * sf_t,
        ],
        dtype=float,
    )
    trigger_hessian = np.zeros(
        (3, 3),
        dtype=float,
    )
    trigger_hessian[1, 1] = (
        0.5
        * cdf_c**2
        * t
        * phi_t
    )
    trigger_hessian[2, 2] = (
        (-c * phi_c * cdf_c + phi_c**2)
        * sf_t
    )
    trigger_hessian[1, 2] = (
        -phi_c * cdf_c * phi_t
    )
    trigger_hessian[2, 1] = (
        trigger_hessian[1, 2]
    )

    branch_gradient = np.array(
        [
            branch["linear_base"],
            branch["linear_added"],
            0.0,
        ],
        dtype=float,
    )
    branch_hessian = np.zeros(
        (3, 3),
        dtype=float,
    )
    branch_hessian[0, 0] = (
        branch["smooth_uu"]
    )
    branch_hessian[0, 1] = (
        branch["smooth_uv"]
    )
    branch_hessian[1, 0] = (
        branch["smooth_uv"]
    )
    branch_hessian[1, 1] = (
        branch["smooth_vv"]
    )

    gradient = (
        activation_complement
        * branch_gradient
        - trigger_gradient
    )
    gradient[2] += (
        complement_first
        * branch["value"]
    )

    smooth_hessian = (
        activation_complement
        * branch_hessian
        - trigger_hessian
    )
    smooth_hessian[0, 2] += (
        complement_first
        * branch["linear_base"]
    )
    smooth_hessian[2, 0] = (
        smooth_hessian[0, 2]
    )
    smooth_hessian[1, 2] += (
        complement_first
        * branch["linear_added"]
    )
    smooth_hessian[2, 1] = (
        smooth_hessian[1, 2]
    )
    smooth_hessian[2, 2] += (
        complement_second
        * branch["value"]
    )

    kink_direction = np.array(
        [[1.0, -1.0, 0.0]],
        dtype=float,
    )
    kink_coefficient = np.array(
        [
            activation_complement
            * branch["kink_coefficient"]
        ],
        dtype=float,
    )

    value = float(
        activation_complement
        * branch["value"]
        - trigger_branch
    )

    return {
        "value": value,
        "gradient": gradient,
        "smooth_hessian": smooth_hessian,
        "kink_directions": kink_direction,
        "kink_coefficients": kink_coefficient,
    }


def gaussian_toy_policy_piecewise_quadratic(
    candidate_threshold: float,
    trigger_threshold: float,
    base_increment: float,
    added_increment: float,
    trigger_increment: float,
) -> float:
    components = (
        gaussian_toy_policy_local_components(
            candidate_threshold,
            trigger_threshold,
        )
    )
    increment = np.array(
        [
            base_increment,
            added_increment,
            trigger_increment,
        ],
        dtype=float,
    )
    return float(
        components["value"]
        + components["gradient"] @ increment
        + generalized_policy_quadratic_value(
            increment,
            components["smooth_hessian"],
            components["kink_directions"],
            components["kink_coefficients"],
        )
    )
