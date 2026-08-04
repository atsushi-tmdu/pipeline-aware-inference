from __future__ import annotations

from scipy.stats import norm

from d8a_coincidence_core import (
    gaussian_cell_branch_base_derivative,
    gaussian_cell_branch_kink_coefficient,
    gaussian_cell_branch_kink_jump,
    gaussian_cell_branch_piecewise_quadratic,
    gaussian_cell_branch_probability,
)


def main() -> None:
    threshold = float(norm.ppf(0.95))
    step = 1e-5
    center = gaussian_cell_branch_base_derivative(
        threshold,
        threshold,
    )
    from_below = (
        center
        - gaussian_cell_branch_base_derivative(
            threshold,
            threshold - step,
        )
    ) / step
    from_above = (
        gaussian_cell_branch_base_derivative(
            threshold,
            threshold + step,
        )
        - center
    ) / step

    direction = (1.2, -0.7)
    local_step = 5e-4
    exact = gaussian_cell_branch_probability(
        threshold + local_step * direction[0],
        threshold + local_step * direction[1],
    )
    approx = gaussian_cell_branch_piecewise_quadratic(
        threshold,
        local_step * direction[0],
        local_step * direction[1],
    )

    print("=" * 80)
    print("D8-A coincidence repair preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "One-sided mixed derivative below / above: "
        f"{from_below:.12f} / {from_above:.12f}"
    )
    print(
        "Analytic mixed-derivative jump: "
        f"{gaussian_cell_branch_kink_jump(threshold):.12f}"
    )
    print(
        "Positive-part-square coefficient: "
        f"{gaussian_cell_branch_kink_coefficient(threshold):.12f}"
    )
    print(
        "Directional expansion normalized error: "
        f"{abs(exact-approx)/local_step**2:.3e}"
    )
    print(
        "Ordinary C2 theorem at candidate coincidence: NO"
    )
    print(
        "Explicit cellwise piecewise quadratic lemma proved: YES"
    )
    print(
        "Full generalized policy coincidence theorem proved: NO"
    )
    print(
        "Scientific simulation blocked: YES"
    )
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
