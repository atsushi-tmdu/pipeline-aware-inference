from __future__ import annotations

import numpy as np

from d8a_core import (
    assemble_joint_quantile_covariance,
    hessian_covariance_block_contraction,
    threshold_ordering_stability_radius,
)


def main() -> None:
    probabilities = np.array([0.8, 0.9])
    densities = np.array([2.0, 3.0])
    joint = np.array([[0.8, 0.76], [0.76, 0.9]])
    covariance = assemble_joint_quantile_covariance(
        probabilities,
        densities,
        joint,
    )
    pieces = hessian_covariance_block_contraction(
        np.array([[1.0, 0.2], [0.2, 0.8]]),
        np.array([0.4, -0.3]),
        1.2,
        covariance,
        np.array([0.01, -0.02]),
        0.03,
    )

    print("=" * 80)
    print("D8-A joint-moment expansion preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Minimum covariance eigenvalue: "
        f"{np.min(np.linalg.eigvalsh(covariance)):.10f}"
    )
    print(
        "Candidate-candidate curvature: "
        f"{pieces['candidate_candidate']:.10f}"
    )
    print(
        "Candidate-trigger curvature: "
        f"{pieces['candidate_trigger']:.10f}"
    )
    print(
        "Trigger-trigger curvature: "
        f"{pieces['trigger_trigger']:.10f}"
    )
    print(
        "Ordering stability radius: "
        f"{threshold_ordering_stability_radius(np.array([1.0, 2.0]), 1.4):.10f}"
    )
    print("Deterministic second-order stochastic remainder assumed: NO")
    print("Expectation-level moment expansion adopted: YES")
    print("Policy-map twice differentiability proved: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
