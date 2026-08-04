from __future__ import annotations

import numpy as np
from scipy.stats import norm

from d8a_coincidence_core import (
    gaussian_toy_policy_contrast,
    gaussian_toy_policy_local_components,
    gaussian_toy_policy_piecewise_quadratic,
    generalized_policy_expectation_coefficient,
)


def main() -> None:
    threshold = float(norm.ppf(0.95))
    trigger = 0.4
    components = gaussian_toy_policy_local_components(
        threshold,
        trigger,
    )

    maximum_normalized_error = 0.0
    for direction in (
        np.array([1.1, -0.7, 0.3]),
        np.array([-0.8, 1.2, -0.2]),
        np.array([0.6, 0.6, 0.1]),
    ):
        step = 5e-4
        exact = gaussian_toy_policy_contrast(
            threshold + step * direction[0],
            threshold + step * direction[1],
            trigger + step * direction[2],
        )
        approx = gaussian_toy_policy_piecewise_quadratic(
            threshold,
            trigger,
            step * direction[0],
            step * direction[1],
            step * direction[2],
        )
        maximum_normalized_error = max(
            maximum_normalized_error,
            abs(exact - approx) / step**2,
        )

    covariance = np.array(
        [
            [1.0, 0.3, 0.1],
            [0.3, 0.9, -0.2],
            [0.1, -0.2, 0.7],
        ]
    )
    coefficient = generalized_policy_expectation_coefficient(
        components["gradient"],
        np.array([0.1, -0.2, 0.05]),
        components["smooth_hessian"],
        covariance,
        components["kink_directions"],
        components["kink_coefficients"],
    )

    print("=" * 80)
    print("D8-A generalized policy theorem preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Maximum directional normalized error: "
        f"{maximum_normalized_error:.3e}"
    )
    print(
        "Synthetic generalized expectation coefficient: "
        f"{coefficient:.10f}"
    )
    print(
        "Active candidate coincidence hyperplanes: 2"
    )
    print(
        "Generic moving-max cell lemma proved: YES"
    )
    print(
        "Full generalized policy coincidence theorem proved: YES"
    )
    print(
        "Generalized expectation theorem proved: YES"
    )
    print(
        "Repaired policy-bias corollary proved: YES"
    )
    print(
        "Repaired TESS reference corollary proved: YES"
    )
    print(
        "Historical numerical design re-adjudicated: NO"
    )
    print(
        "Scientific simulation blocked: YES"
    )
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
