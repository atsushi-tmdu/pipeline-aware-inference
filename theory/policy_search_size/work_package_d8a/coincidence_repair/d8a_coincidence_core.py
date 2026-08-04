from __future__ import annotations

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
