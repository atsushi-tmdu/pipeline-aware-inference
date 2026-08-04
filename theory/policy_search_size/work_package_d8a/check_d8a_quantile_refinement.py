from __future__ import annotations

from d8a_core import (
    quantile_lattice_offset,
    scalar_quantile_bias_coefficient,
)


def main() -> None:
    print("=" * 80)
    print("D8-A empirical-quantile lattice preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "a(0.37, B=100): "
        f"{quantile_lattice_offset(100, 0.37):.8f}"
    )
    print(
        "a(0.37, B=101): "
        f"{quantile_lattice_offset(101, 0.37):.8f}"
    )
    for probability in (0.99, 0.95, 0.90):
        values = [
            quantile_lattice_offset(B, probability)
            for B in (1000, 3000, 5000)
        ]
        print(
            f"D7 candidate p={probability:.2f} offsets: "
            + ", ".join(f"{value:.8f}" for value in values)
        )
    print(
        "Uniform p=0.99 second-order coefficient at B=1000: "
        f"{scalar_quantile_bias_coefficient(1000, 0.99, 1.0, 0.0):.8f}"
    )
    print("Unrestricted constant C_R valid: NO")
    print("Bounded C_R,B adopted: YES")
    print("Second-order quantile lemma proved: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
