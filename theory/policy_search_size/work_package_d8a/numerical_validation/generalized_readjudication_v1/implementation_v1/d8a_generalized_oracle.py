from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

from d8a_policy_engine import (
    base_max_density,
    base_max_density_derivative,
    base_max_quantile,
    bvn_cdf,
    mvn3_cdf,
    policy_population_probabilities,
)


FloatArray = np.ndarray

_REPAIR_DIR = (
    Path(__file__).resolve().parents[3]
    / "coincidence_repair"
)
if str(_REPAIR_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(_REPAIR_DIR),
    )

from d8a_coincidence_core import (  # noqa: E402
    generalized_policy_expectation_coefficient,
)


def theta_from_class(
    class_record: dict[str, object],
) -> FloatArray:
    probability = float(
        class_record["candidate_probability"]
    )
    trigger_probability = float(
        class_record["trigger_probability"]
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    candidate = float(
        norm.ppf(probability)
    )
    trigger = base_max_quantile(
        trigger_probability,
        float(correlation[0, 1]),
    )
    return np.array(
        [
            candidate,
            candidate,
            candidate,
            trigger,
        ],
        dtype=float,
    )


def scalar_quantile_bias_coefficient(
    sample_size: int,
    probability: float,
    density: float,
    density_derivative: float,
) -> float:
    order_index = int(
        math.ceil(
            sample_size
            * probability
        )
    )
    lattice = (
        order_index
        - (sample_size + 1)
        * probability
    )
    return float(
        lattice / density
        - probability
        * (1.0 - probability)
        * density_derivative
        / (2.0 * density**3)
    )


def quantile_moment_oracle(
    class_record: dict[str, object],
    reference_size: int,
) -> dict[str, FloatArray]:
    probability = float(
        class_record["candidate_probability"]
    )
    trigger_probability = float(
        class_record["trigger_probability"]
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    theta = theta_from_class(
        class_record
    )
    candidate = float(theta[0])
    trigger = float(theta[3])

    candidate_density = float(
        norm.pdf(candidate)
    )
    candidate_density_derivative = float(
        -candidate
        * candidate_density
    )
    trigger_density = base_max_density(
        trigger,
        float(correlation[0, 1]),
    )
    trigger_density_derivative = (
        base_max_density_derivative(
            trigger,
            float(correlation[0, 1]),
        )
    )

    candidate_bias = scalar_quantile_bias_coefficient(
        reference_size,
        probability,
        candidate_density,
        candidate_density_derivative,
    )
    trigger_bias = scalar_quantile_bias_coefficient(
        reference_size,
        trigger_probability,
        trigger_density,
        trigger_density_derivative,
    )
    bias = np.array(
        [
            candidate_bias,
            candidate_bias,
            candidate_bias,
            trigger_bias,
        ],
        dtype=float,
    )

    densities = np.array(
        [
            candidate_density,
            candidate_density,
            candidate_density,
            trigger_density,
        ],
        dtype=float,
    )
    probabilities = np.array(
        [
            probability,
            probability,
            probability,
            trigger_probability,
        ],
        dtype=float,
    )
    joint = np.zeros(
        (4, 4),
        dtype=float,
    )
    np.fill_diagonal(
        joint,
        probabilities,
    )

    for left in range(3):
        for right in range(
            left + 1,
            3,
        ):
            value = bvn_cdf(
                candidate,
                candidate,
                float(
                    correlation[
                        left,
                        right,
                    ]
                ),
            )
            joint[left, right] = value
            joint[right, left] = value

    joint[0, 3] = bvn_cdf(
        min(candidate, trigger),
        trigger,
        float(correlation[0, 1]),
    )
    joint[3, 0] = joint[0, 3]

    joint[1, 3] = bvn_cdf(
        trigger,
        min(candidate, trigger),
        float(correlation[0, 1]),
    )
    joint[3, 1] = joint[1, 3]

    joint[2, 3] = mvn3_cdf(
        np.array(
            [
                trigger,
                trigger,
                candidate,
            ],
            dtype=float,
        ),
        correlation,
    )
    joint[3, 2] = joint[2, 3]

    covariance = (
        joint
        - np.outer(
            probabilities,
            probabilities,
        )
    ) / np.outer(
        densities,
        densities,
    )
    covariance = (
        covariance
        + covariance.T
    ) / 2.0

    return {
        "theta": theta,
        "bias_coefficient": bias,
        "covariance": covariance,
        "joint_lower_probabilities": joint,
        "densities": densities,
    }


def branch_kappa(
    candidate_threshold: float,
    winner_index: int,
    correlation_matrix: FloatArray,
) -> float:
    q = float(candidate_threshold)
    correlation = np.asarray(
        correlation_matrix,
        dtype=float,
    )
    loser_index = 1 - winner_index

    r_a2 = float(
        correlation[winner_index, 2]
    )
    mean_added = r_a2 * q
    sd_added = math.sqrt(
        1.0 - r_a2**2
    )
    added_density = float(
        norm.pdf(
            (
                q - mean_added
            )
            / sd_added
        )
        / sd_added
    )

    conditioned = [winner_index, 2]
    r_vector = correlation[
        loser_index,
        conditioned,
    ]
    conditioned_covariance = correlation[
        np.ix_(
            conditioned,
            conditioned,
        )
    ]
    inverse = np.linalg.inv(
        conditioned_covariance
    )
    conditioned_values = np.array(
        [q, q],
        dtype=float,
    )
    loser_mean = float(
        r_vector
        @ inverse
        @ conditioned_values
    )
    loser_variance = float(
        1.0
        - r_vector
        @ inverse
        @ r_vector
    )
    loser_probability = float(
        norm.cdf(
            (
                q - loser_mean
            )
            / math.sqrt(
                loser_variance
            )
        )
    )

    h_s = float(
        -norm.pdf(q)
        * added_density
        * loser_probability
    )
    return float(
        0.5 * h_s
    )


def target_kink_coefficients(
    target_name: str,
    class_record: dict[str, object],
) -> FloatArray:
    theta = theta_from_class(
        class_record
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    probabilities = (
        policy_population_probabilities(
            theta,
            correlation,
        )
    )
    activation = float(
        probabilities[
            "activation_probability"
        ]
    )
    flags = np.array(
        [
            float(theta[3] < theta[0]),
            float(theta[3] < theta[1]),
        ],
        dtype=float,
    )
    kappas = np.array(
        [
            branch_kappa(
                theta[0],
                0,
                correlation,
            ),
            branch_kappa(
                theta[1],
                1,
                correlation,
            ),
        ],
        dtype=float,
    )

    if target_name == "delta_pi":
        return (
            flags - activation
        ) * kappas
    if target_name == "adaptive_probability":
        return flags * kappas
    if target_name == "comparator_probability":
        return activation * kappas
    raise ValueError(
        f"unknown target: {target_name}"
    )


def _target_value(
    thresholds: FloatArray,
    correlation: FloatArray,
    target_name: str,
) -> float:
    probabilities = (
        policy_population_probabilities(
            thresholds,
            correlation,
        )
    )
    return float(
        probabilities[target_name]
    )


def _corrected_target_value(
    thresholds: FloatArray,
    population_theta: FloatArray,
    correlation: FloatArray,
    target_name: str,
    kink_coefficients: FloatArray,
) -> float:
    increment = (
        np.asarray(
            thresholds,
            dtype=float,
        )
        - population_theta
    )
    correction = (
        kink_coefficients[0]
        * max(
            float(
                increment[0]
                - increment[2]
            ),
            0.0,
        )
        ** 2
        + kink_coefficients[1]
        * max(
            float(
                increment[1]
                - increment[2]
            ),
            0.0,
        )
        ** 2
    )
    return float(
        _target_value(
            thresholds,
            correlation,
            target_name,
        )
        - correction
    )


def _central_derivatives(
    function,
    point: FloatArray,
    step: float,
) -> tuple[FloatArray, FloatArray]:
    theta = np.asarray(
        point,
        dtype=float,
    )
    dimension = theta.size
    base = float(
        function(theta)
    )
    gradient = np.zeros(
        dimension,
        dtype=float,
    )
    hessian = np.zeros(
        (dimension, dimension),
        dtype=float,
    )

    for index in range(dimension):
        offset = np.zeros(
            dimension,
            dtype=float,
        )
        offset[index] = step
        plus = float(
            function(theta + offset)
        )
        minus = float(
            function(theta - offset)
        )
        gradient[index] = (
            plus - minus
        ) / (2.0 * step)
        hessian[index, index] = (
            plus
            - 2.0 * base
            + minus
        ) / step**2

    for left in range(dimension):
        for right in range(
            left + 1,
            dimension,
        ):
            left_offset = np.zeros(
                dimension,
                dtype=float,
            )
            right_offset = np.zeros(
                dimension,
                dtype=float,
            )
            left_offset[left] = step
            right_offset[right] = step
            mixed = (
                function(
                    theta
                    + left_offset
                    + right_offset
                )
                - function(
                    theta
                    + left_offset
                    - right_offset
                )
                - function(
                    theta
                    - left_offset
                    + right_offset
                )
                + function(
                    theta
                    - left_offset
                    - right_offset
                )
            ) / (4.0 * step**2)
            hessian[left, right] = mixed
            hessian[right, left] = mixed

    return gradient, hessian


def smooth_derivatives(
    target_name: str,
    class_record: dict[str, object],
    *,
    step: float = 1.5e-3,
) -> tuple[FloatArray, FloatArray]:
    theta = theta_from_class(
        class_record
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    kink = target_kink_coefficients(
        target_name,
        class_record,
    )

    function = lambda value: _corrected_target_value(
        value,
        theta,
        correlation,
        target_name,
        kink,
    )

    gradient_large, hessian_large = (
        _central_derivatives(
            function,
            theta,
            step,
        )
    )
    gradient_small, hessian_small = (
        _central_derivatives(
            function,
            theta,
            step / 2.0,
        )
    )
    gradient = (
        4.0 * gradient_small
        - gradient_large
    ) / 3.0
    hessian = (
        4.0 * hessian_small
        - hessian_large
    ) / 3.0
    hessian = (
        hessian
        + hessian.T
    ) / 2.0
    return gradient, hessian


def generalized_reference_target_oracle(
    target_name: str,
    class_record: dict[str, object],
    reference_size: int,
) -> dict[str, object]:
    moments = quantile_moment_oracle(
        class_record,
        reference_size,
    )
    gradient, hessian = smooth_derivatives(
        target_name,
        class_record,
    )
    kink = target_kink_coefficients(
        target_name,
        class_record,
    )
    directions = np.array(
        [
            [1.0, 0.0, -1.0, 0.0],
            [0.0, 1.0, -1.0, 0.0],
        ],
        dtype=float,
    )
    coefficient = (
        generalized_policy_expectation_coefficient(
            gradient,
            moments["bias_coefficient"],
            hessian,
            moments["covariance"],
            directions,
            kink,
        )
    )
    return {
        "gradient": gradient,
        "smooth_hessian": hessian,
        "kink_directions": directions,
        "kink_coefficients": kink,
        "generalized_coefficient": coefficient,
        "moments": moments,
    }


def tess_first_derivative(
    probability: float,
    alpha: float,
) -> float:
    return float(
        -1.0
        / (
            (1.0 - probability)
            * math.log(
                1.0 - alpha
            )
        )
    )


def tess_second_derivative(
    probability: float,
    alpha: float,
) -> float:
    return float(
        -1.0
        / (
            (1.0 - probability) ** 2
            * math.log(
                1.0 - alpha
            )
        )
    )


def evaluation_variances(
    class_record: dict[str, object],
) -> dict[str, float]:
    theta = theta_from_class(
        class_record
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    probabilities = (
        policy_population_probabilities(
            theta,
            correlation,
        )
    )
    e0 = float(
        probabilities["base_probability"]
    )
    activation = float(
        probabilities[
            "activation_probability"
        ]
    )
    incremental = float(
        probabilities[
            "incremental_probability"
        ]
    )
    joint_am = float(
        probabilities[
            "joint_am_probability"
        ]
    )
    adaptive = float(
        probabilities[
            "adaptive_probability"
        ]
    )

    q = float(theta[0])
    trigger = float(theta[3])
    joint_r0_a = float(
        1.0
        - bvn_cdf(
            max(q, trigger),
            max(q, trigger),
            float(correlation[0, 1]),
        )
    )

    covariance = np.array(
        [
            [
                e0 * (1.0 - e0),
                joint_r0_a - e0 * activation,
                -e0 * incremental,
            ],
            [
                joint_r0_a - e0 * activation,
                activation * (1.0 - activation),
                joint_am - activation * incremental,
            ],
            [
                -e0 * incremental,
                joint_am - activation * incremental,
                incremental * (1.0 - incremental),
            ],
        ],
        dtype=float,
    )
    coefficients = np.array(
        [
            1.0,
            incremental,
            activation,
        ],
        dtype=float,
    )
    comparator_variance = float(
        coefficients
        @ covariance
        @ coefficients
    )
    return {
        "adaptive_variance": float(
            adaptive
            * (1.0 - adaptive)
        ),
        "comparator_variance": comparator_variance,
    }


def full_oracle_summary(
    class_record: dict[str, object],
    reference_size: int,
    alpha: float,
) -> dict[str, object]:
    theta = theta_from_class(
        class_record
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    probabilities = (
        policy_population_probabilities(
            theta,
            correlation,
        )
    )

    delta_oracle = (
        generalized_reference_target_oracle(
            "delta_pi",
            class_record,
            reference_size,
        )
    )
    adaptive_oracle = (
        generalized_reference_target_oracle(
            "adaptive_probability",
            class_record,
            reference_size,
        )
    )
    comparator_oracle = (
        generalized_reference_target_oracle(
            "comparator_probability",
            class_record,
            reference_size,
        )
    )

    covariance = delta_oracle[
        "moments"
    ]["covariance"]
    adaptive_gradient = adaptive_oracle[
        "gradient"
    ]
    comparator_gradient = comparator_oracle[
        "gradient"
    ]
    adaptive_probability = float(
        probabilities[
            "adaptive_probability"
        ]
    )
    comparator_probability = float(
        probabilities[
            "comparator_probability"
        ]
    )

    tess_reference = float(
        tess_first_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_oracle[
            "generalized_coefficient"
        ]
        + 0.5
        * tess_second_derivative(
            adaptive_probability,
            alpha,
        )
        * (
            adaptive_gradient
            @ covariance
            @ adaptive_gradient
        )
        - tess_first_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_oracle[
            "generalized_coefficient"
        ]
        - 0.5
        * tess_second_derivative(
            comparator_probability,
            alpha,
        )
        * (
            comparator_gradient
            @ covariance
            @ comparator_gradient
        )
    )

    evaluation = evaluation_variances(
        class_record
    )
    tess_evaluation = float(
        0.5
        * tess_second_derivative(
            adaptive_probability,
            alpha,
        )
        * evaluation[
            "adaptive_variance"
        ]
        - tess_first_derivative(
            comparator_probability,
            alpha,
        )
        * probabilities["delta_pi"]
        - 0.5
        * tess_second_derivative(
            comparator_probability,
            alpha,
        )
        * evaluation[
            "comparator_variance"
        ]
    )

    return {
        "theta": theta,
        "probabilities": probabilities,
        "delta_reference": delta_oracle,
        "adaptive_reference": adaptive_oracle,
        "comparator_reference": comparator_oracle,
        "tess_reference_coefficient": tess_reference,
        "tess_evaluation_coefficient": tess_evaluation,
        "evaluation_variances": evaluation,
    }

# ---------------------------------------------------------------------------
# Vectorized derivative and all-target generalized-oracle audit helpers.
# ---------------------------------------------------------------------------

_TARGET_NAMES = (
    "delta_pi",
    "adaptive_probability",
    "comparator_probability",
)


def _target_vector(
    thresholds: FloatArray,
    correlation: FloatArray,
) -> FloatArray:
    probabilities = (
        policy_population_probabilities(
            thresholds,
            correlation,
        )
    )
    return np.array(
        [
            probabilities[name]
            for name in _TARGET_NAMES
        ],
        dtype=float,
    )


def _target_kink_matrix(
    class_record: dict[str, object],
) -> FloatArray:
    return np.vstack(
        [
            target_kink_coefficients(
                name,
                class_record,
            )
            for name in _TARGET_NAMES
        ]
    )


def _corrected_target_vector(
    thresholds: FloatArray,
    population_theta: FloatArray,
    correlation: FloatArray,
    kink_matrix: FloatArray,
) -> FloatArray:
    increment = (
        np.asarray(thresholds, dtype=float)
        - population_theta
    )
    positive_parts = np.array(
        [
            max(
                float(
                    increment[0]
                    - increment[2]
                ),
                0.0,
            )
            ** 2,
            max(
                float(
                    increment[1]
                    - increment[2]
                ),
                0.0,
            )
            ** 2,
        ],
        dtype=float,
    )
    return (
        _target_vector(
            thresholds,
            correlation,
        )
        - kink_matrix
        @ positive_parts
    )


def _central_vector_derivatives(
    function,
    point: FloatArray,
    step: float,
) -> tuple[FloatArray, FloatArray]:
    theta = np.asarray(point, dtype=float)
    dimension = theta.size
    cache: dict[tuple[float, ...], FloatArray] = {}

    def evaluate(value: FloatArray) -> FloatArray:
        key = tuple(
            np.round(
                np.asarray(value, dtype=float),
                14,
            )
        )
        if key not in cache:
            cache[key] = np.asarray(
                function(
                    np.asarray(value, dtype=float)
                ),
                dtype=float,
            )
        return cache[key]

    base = evaluate(theta)
    target_count = base.size
    gradients = np.zeros(
        (target_count, dimension),
        dtype=float,
    )
    hessians = np.zeros(
        (
            target_count,
            dimension,
            dimension,
        ),
        dtype=float,
    )

    for index in range(dimension):
        offset = np.zeros(
            dimension,
            dtype=float,
        )
        offset[index] = step
        plus = evaluate(theta + offset)
        minus = evaluate(theta - offset)
        gradients[:, index] = (
            plus - minus
        ) / (2.0 * step)
        hessians[:, index, index] = (
            plus
            - 2.0 * base
            + minus
        ) / step**2

    for left in range(dimension):
        for right in range(
            left + 1,
            dimension,
        ):
            left_offset = np.zeros(
                dimension,
                dtype=float,
            )
            right_offset = np.zeros(
                dimension,
                dtype=float,
            )
            left_offset[left] = step
            right_offset[right] = step
            mixed = (
                evaluate(
                    theta
                    + left_offset
                    + right_offset
                )
                - evaluate(
                    theta
                    + left_offset
                    - right_offset
                )
                - evaluate(
                    theta
                    - left_offset
                    + right_offset
                )
                + evaluate(
                    theta
                    - left_offset
                    - right_offset
                )
            ) / (4.0 * step**2)
            hessians[:, left, right] = mixed
            hessians[:, right, left] = mixed

    return gradients, hessians


def all_target_smooth_derivatives(
    class_record: dict[str, object],
    *,
    step: float = 0.01,
) -> tuple[FloatArray, FloatArray]:
    theta = theta_from_class(class_record)
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    kink_matrix = _target_kink_matrix(
        class_record
    )
    function = lambda value: (
        _corrected_target_vector(
            value,
            theta,
            correlation,
            kink_matrix,
        )
    )

    gradient_large, hessian_large = (
        _central_vector_derivatives(
            function,
            theta,
            step,
        )
    )
    gradient_small, hessian_small = (
        _central_vector_derivatives(
            function,
            theta,
            step / 2.0,
        )
    )
    gradients = (
        4.0 * gradient_small
        - gradient_large
    ) / 3.0
    hessians = (
        4.0 * hessian_small
        - hessian_large
    ) / 3.0
    hessians = (
        hessians
        + np.swapaxes(
            hessians,
            1,
            2,
        )
    ) / 2.0
    return gradients, hessians


def all_target_reference_oracle(
    class_record: dict[str, object],
    reference_size: int,
    *,
    step: float = 0.01,
) -> dict[str, object]:
    moments = quantile_moment_oracle(
        class_record,
        reference_size,
    )
    gradients, hessians = (
        all_target_smooth_derivatives(
            class_record,
            step=step,
        )
    )
    kink_matrix = _target_kink_matrix(
        class_record
    )
    directions = np.array(
        [
            [1.0, 0.0, -1.0, 0.0],
            [0.0, 1.0, -1.0, 0.0],
        ],
        dtype=float,
    )

    target_results: dict[str, object] = {}
    for index, name in enumerate(_TARGET_NAMES):
        coefficient = (
            generalized_policy_expectation_coefficient(
                gradients[index],
                moments["bias_coefficient"],
                hessians[index],
                moments["covariance"],
                directions,
                kink_matrix[index],
            )
        )
        smooth_only = float(
            gradients[index]
            @ moments["bias_coefficient"]
            + 0.5
            * np.trace(
                hessians[index]
                @ moments["covariance"]
            )
        )
        kink_correction = float(
            coefficient - smooth_only
        )
        declared_kink = float(
            sum(
                kink_matrix[index, branch]
                * 0.5
                * (
                    directions[branch]
                    @ moments["covariance"]
                    @ directions[branch]
                )
                for branch in range(2)
            )
        )
        target_results[name] = {
            "gradient": gradients[index],
            "smooth_hessian": hessians[index],
            "kink_coefficients": (
                kink_matrix[index]
            ),
            "generalized_coefficient": coefficient,
            "smooth_only_coefficient": smooth_only,
            "kink_correction": kink_correction,
            "declared_kink_correction": (
                declared_kink
            ),
        }

    return {
        "moments": moments,
        "directions": directions,
        "targets": target_results,
    }


def generalized_directional_approximation(
    target_name: str,
    class_record: dict[str, object],
    direction: FloatArray,
    radius: float,
    oracle: dict[str, object],
) -> tuple[float, float]:
    theta = theta_from_class(
        class_record
    )
    correlation = np.asarray(
        class_record["correlation_matrix"],
        dtype=float,
    )
    increment = (
        radius
        * np.asarray(
            direction,
            dtype=float,
        )
    )
    target = oracle["targets"][
        target_name
    ]
    exact = _target_value(
        theta + increment,
        correlation,
        target_name,
    )
    baseline = _target_value(
        theta,
        correlation,
        target_name,
    )
    quadratic = float(
        0.5
        * increment
        @ target["smooth_hessian"]
        @ increment
    )
    kink = float(
        sum(
            target["kink_coefficients"][branch]
            * max(
                float(
                    oracle["directions"][branch]
                    @ increment
                ),
                0.0,
            )
            ** 2
            for branch in range(2)
        )
    )
    approximation = float(
        baseline
        + target["gradient"]
        @ increment
        + quadratic
        + kink
    )
    return float(exact), approximation

# Analytic boundary oracle. This supersedes finite-difference smooth
# derivatives while retaining the locked positive-part-square corrections.
_numerical_smooth_derivatives_legacy = smooth_derivatives
_numerical_all_target_smooth_derivatives_legacy = all_target_smooth_derivatives


def all_target_smooth_derivatives(
    class_record: dict[str, object],
    *,
    step: float = 0.01,
) -> tuple[FloatArray, FloatArray]:
    del step
    from d8a_analytic_policy_derivatives import analytic_target_derivatives

    derivatives = analytic_target_derivatives(
        class_record,
        theta_from_class(class_record),
    )
    order = (
        "delta_pi",
        "adaptive_probability",
        "comparator_probability",
    )
    gradients = np.vstack([derivatives[name]["gradient"] for name in order])
    hessians = np.stack(
        [derivatives[name]["smooth_hessian"] for name in order],
        axis=0,
    )
    return gradients, hessians


def smooth_derivatives(
    target_name: str,
    class_record: dict[str, object],
    *,
    step: float = 0.01,
) -> tuple[FloatArray, FloatArray]:
    del step
    gradients, hessians = all_target_smooth_derivatives(class_record)
    index = {
        "delta_pi": 0,
        "adaptive_probability": 1,
        "comparator_probability": 2,
    }[target_name]
    return gradients[index], hessians[index]
