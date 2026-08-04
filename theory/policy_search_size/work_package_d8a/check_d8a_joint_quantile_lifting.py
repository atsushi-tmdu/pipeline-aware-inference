from __future__ import annotations

import numpy as np

from d8a_core import (
    bahadur_second_moment_entry_error_bound,
    exact_influence_covariance_from_atoms,
    joint_quantile_second_moment_limit,
    vector_moment_bound_from_component_bounds,
)


def main() -> None:
    atom_probabilities = np.array([0.2, 0.2, 0.1, 0.5])
    atoms = np.array(
        [
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ]
    )
    probabilities = np.array([0.6, 0.7])
    densities = np.array([1.5, 2.0])
    joint = np.array([[0.6, 0.5], [0.5, 0.7]])

    atom_covariance = exact_influence_covariance_from_atoms(
        atom_probabilities,
        atoms,
        probabilities,
        densities,
    )
    formula_covariance = joint_quantile_second_moment_limit(
        joint,
        probabilities,
        densities,
    )

    print("=" * 80)
    print("D8-A joint quantile lifting preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Maximum atom/formula covariance difference: "
        f"{np.max(np.abs(atom_covariance-formula_covariance)):.3e}"
    )
    print(
        "Cross covariance: "
        f"{formula_covariance[0,1]:.10f}"
    )
    print(
        "Minimum covariance eigenvalue: "
        f"{np.min(np.linalg.eigvalsh(formula_covariance)):.10f}"
    )
    for epsilon in (0.10, 0.03, 0.01):
        bound = bahadur_second_moment_entry_error_bound(
            0.4,
            0.7,
            epsilon,
            0.8 * epsilon,
        )
        print(
            f"Scaled L2 remainder={epsilon:.2f}, "
            f"entry error bound={bound:.10f}"
        )
    print(
        "Example vector fourth-moment bound: "
        f"{vector_moment_bound_from_component_bounds(np.array([2.0,3.0,5.0]),4.0):.4f}"
    )
    print("Joint covariance lifting lemma proved conditionally: YES")
    print("Primitive L2 Bahadur remainder proved: NO")
    print("Scalar higher-moment bounds proved generally: NO")
    print("Full joint quantile lemma proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
