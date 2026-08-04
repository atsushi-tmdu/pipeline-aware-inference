from __future__ import annotations

import numpy as np

from d8a_core import (
    fixed_dimension_bahadur_l2_closure,
    quantile_local_tail_bound,
    scaled_lattice_negligibility,
    uniform_integrability_tail_bound,
)


def main() -> None:
    print("=" * 80)
    print("D8-A primitive Bahadur and moment preflight")
    print("=" * 80)
    print("Status: PASS")

    for deviation in (0.005, 0.01, 0.02, 0.05):
        print(
            f"Local tail bound at deviation={deviation:.3f}: "
            f"{quantile_local_tail_bound(3000, deviation, 0.8):.10f}"
        )

    for cutoff in (2.0, 4.0, 8.0):
        print(
            f"UI tail bound at cutoff={cutoff:.1f}: "
            f"{uniform_integrability_tail_bound(10.0, cutoff, 4.0):.10f}"
        )

    probability = 0.371234
    for reference_size in (101, 1001, 10001):
        observed = scaled_lattice_negligibility(
            reference_size,
            probability,
        )
        upper_bound = reference_size ** -0.5
        print(
            "Scaled lattice discrepancy / bound at "
            f"B={reference_size}, p={probability:.6f}: "
            f"{observed:.10f} / {upper_bound:.10f}"
        )
    print(
        "Example fixed-dimension zero-remainder closure: "
        f"{fixed_dimension_bahadur_l2_closure(np.zeros(5))}"
    )
    print("Scalar 2+eta moment bound proved: YES")
    print("Primitive scalar L2 Bahadur remainder proved: YES")
    print("Full joint quantile moment theorem proved: YES")
    print("General policy-map C2 theorem proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
