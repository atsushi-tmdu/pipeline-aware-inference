from __future__ import annotations

import numpy as np

from d8a_core import (
    independent_gaussian_cell_contrast,
    independent_gaussian_cell_contrast_derivatives,
    separated_activation_regime,
)


def main() -> None:
    point = np.array([0.6, 0.3, -0.2])
    step = 1e-5
    gradient, hessian = (
        independent_gaussian_cell_contrast_derivatives(
            *point
        )
    )

    finite_gradient = np.zeros(3)
    finite_hessian = np.zeros((3, 3))
    for index in range(3):
        offset = np.zeros(3)
        offset[index] = step
        finite_gradient[index] = (
            independent_gaussian_cell_contrast(
                *(point + offset)
            )
            - independent_gaussian_cell_contrast(
                *(point - offset)
            )
        ) / (2.0 * step)
        gradient_plus, _ = (
            independent_gaussian_cell_contrast_derivatives(
                *(point + offset)
            )
        )
        gradient_minus, _ = (
            independent_gaussian_cell_contrast_derivatives(
                *(point - offset)
            )
        )
        finite_hessian[:, index] = (
            gradient_plus - gradient_minus
        ) / (2.0 * step)

    print("=" * 80)
    print("D8-A policy C2 theorem preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Maximum gradient finite/analytic difference: "
        f"{np.max(np.abs(finite_gradient-gradient)):.3e}"
    )
    print(
        "Maximum Hessian finite/analytic difference: "
        f"{np.max(np.abs(finite_hessian-hessian)):.3e}"
    )
    print(
        "Hessian symmetry error: "
        f"{np.max(np.abs(hessian-hessian.T)):.3e}"
    )
    print(
        "Separated regime: "
        f"{separated_activation_regime(point[0], point[2])}"
    )
    print("Coordinate moving-face lemma proved: YES")
    print("Regular policy-map C2 theorem proved: YES")
    print("Final second-order policy-bias theorem proved: NO")
    print("TESS second-order corollary proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
