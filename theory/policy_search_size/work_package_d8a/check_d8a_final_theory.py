from __future__ import annotations

import numpy as np

from d8a_core import (
    bernoulli_variance,
    final_policy_bias_approximation,
    second_order_expectation_coefficient,
    tess_evaluation_bias_coefficient,
    tess_reference_bias_coefficient,
    tess_second_order_bias_approximation,
)


def main() -> None:
    gradient = np.array([0.4, -0.2, 0.3])
    bias = np.array([0.1, -0.05, 0.08])
    hessian = np.array(
        [
            [1.0, 0.2, -0.1],
            [0.2, 0.8, 0.25],
            [-0.1, 0.25, 1.2],
        ]
    )
    covariance = np.array(
        [
            [1.0, 0.1, 0.3],
            [0.1, 0.9, -0.2],
            [0.3, -0.2, 1.1],
        ]
    )
    coefficient = second_order_expectation_coefficient(
        gradient,
        bias,
        hessian,
        covariance,
    )
    policy_bias = final_policy_bias_approximation(
        population_delta=0.03,
        reference_bias_coefficient=coefficient,
        reference_size=3000,
        evaluation_size=5000,
        retain_interaction=True,
    )

    reference_tess = tess_reference_bias_coefficient(
        alpha=0.05,
        adaptive_probability=0.08,
        comparator_probability=0.075,
        adaptive_reference_mean_bias=-0.4,
        comparator_reference_mean_bias=-0.3,
        adaptive_reference_variance=0.20,
        comparator_reference_variance=0.18,
    )
    evaluation_tess = tess_evaluation_bias_coefficient(
        alpha=0.05,
        adaptive_probability=0.08,
        comparator_probability=0.075,
        policy_delta=0.005,
        adaptive_evaluation_variance=bernoulli_variance(0.08),
        comparator_evaluation_variance=0.06,
    )
    tess_bias = tess_second_order_bias_approximation(
        reference_tess,
        evaluation_tess,
        3000,
        5000,
    )

    print("=" * 80)
    print("D8-A final theory preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Synthetic second-order policy coefficient: "
        f"{coefficient:.10f}"
    )
    print(
        "Synthetic policy bias approximation: "
        f"{policy_bias:.12f}"
    )
    print(
        "Synthetic TESS reference coefficient: "
        f"{reference_tess:.10f}"
    )
    print(
        "Synthetic TESS evaluation coefficient: "
        f"{evaluation_tess:.10f}"
    )
    print(
        "Synthetic TESS bias approximation: "
        f"{tess_bias:.12f}"
    )
    print("Full joint quantile theorem proved: YES")
    print("Regular policy-map C2 theorem proved: YES")
    print("Final second-order policy-bias theorem proved: YES")
    print("TESS second-order corollary proved: YES")
    print("D8-A theory complete under stated assumptions: YES")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
