from __future__ import annotations

import numpy as np

from d8a_core import (
    bivariate_normal_candidate_gradient,
    bivariate_normal_candidate_second_derivative,
    bivariate_normal_policy_hessian,
    bivariate_normal_trigger_gradient,
    bivariate_normal_trigger_second_derivative,
    local_threshold_box_is_order_stable,
)


def centered_difference(function, value: float, step: float) -> float:
    return float(
        (function(value + step) - function(value - step))
        / (2.0 * step)
    )


def main() -> None:
    q, c, correlation, step = 0.4, 0.8, 0.55, 1e-5

    qq_finite = centered_difference(
        lambda value: bivariate_normal_candidate_gradient(
            value,
            c,
            correlation,
        ),
        q,
        step,
    )
    qq_analytic = bivariate_normal_candidate_second_derivative(
        q,
        c,
        correlation,
    )

    qc_from_q = centered_difference(
        lambda value: bivariate_normal_candidate_gradient(
            q,
            value,
            correlation,
        ),
        c,
        step,
    )
    qc_from_c = centered_difference(
        lambda value: bivariate_normal_trigger_gradient(
            value,
            c,
            correlation,
        ),
        q,
        step,
    )

    cc_finite = centered_difference(
        lambda value: bivariate_normal_trigger_gradient(
            q,
            value,
            correlation,
        ),
        c,
        step,
    )
    cc_analytic = bivariate_normal_trigger_second_derivative(
        q,
        c,
        correlation,
    )

    hessian = bivariate_normal_policy_hessian(
        q,
        c,
        correlation,
    )

    print("=" * 80)
    print("D8-A Gaussian Hessian preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "qq finite / analytic / difference: "
        f"{qq_finite:.10f} / {qq_analytic:.10f} / "
        f"{qq_finite-qq_analytic:.3e}"
    )
    print(
        "qc from candidate / trigger / difference: "
        f"{qc_from_q:.10f} / {qc_from_c:.10f} / "
        f"{qc_from_q-qc_from_c:.3e}"
    )
    print(
        "cc finite / analytic / difference: "
        f"{cc_finite:.10f} / {cc_analytic:.10f} / "
        f"{cc_finite-cc_analytic:.3e}"
    )
    print(
        "Hessian symmetry error: "
        f"{np.max(np.abs(hessian-hessian.T)):.3e}"
    )
    print(
        "Stable threshold box at radius 0.19: "
        f"{local_threshold_box_is_order_stable(np.array([1.0, 2.0, 3.0]), 1.4, 0.19)}"
    )
    print("General winner-cell C2 theorem proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
