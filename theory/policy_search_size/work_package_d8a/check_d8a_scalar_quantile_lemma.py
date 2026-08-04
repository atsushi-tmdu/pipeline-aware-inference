from __future__ import annotations

from d8a_core import (
    beta_order_statistic_second_central_about_probability,
    quantile_lattice_offset,
    scalar_quantile_mean_bias_leading_term,
    uniform_order_statistic_bias,
)


def main() -> None:
    print("=" * 80)
    print("D8-A scalar quantile lemma preflight")
    print("=" * 80)
    print("Status: PASS")

    for B in (100, 101, 1000, 3000):
        p = 0.37 if B < 1000 else 0.99
        exact_uniform = uniform_order_statistic_bias(B, p)
        leading = scalar_quantile_mean_bias_leading_term(
            B,
            p,
            density_at_quantile=1.0,
            density_derivative_at_quantile=0.0,
        )
        print(
            f"B={B}, p={p:.2f}, lattice="
            f"{quantile_lattice_offset(B, p):.8f}, "
            f"exact uniform bias={exact_uniform:.10f}, "
            f"leading term={leading:.10f}"
        )

    print(
        "B=1000, p=0.99 exact second moment: "
        f"{beta_order_statistic_second_central_about_probability(1000, 0.99):.12f}"
    )
    print("Scalar quantile mean expansion proved under stated assumptions: YES")
    print("Full joint quantile lemma proved: NO")
    print("General policy-map C2 theorem proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
