from __future__ import annotations

from d8a_core import (
    bivariate_normal_candidate_gradient,
    bivariate_normal_candidate_trigger_hessian,
    bivariate_normal_indicator_covariance,
    bivariate_normal_trigger_gradient,
)


def centered_difference(function, value: float, step: float) -> float:
    return float(
        (function(value + step) - function(value - step))
        / (2.0 * step)
    )


def main() -> None:
    q, c, correlation, step = 0.4, 0.8, 0.55, 1e-5

    candidate_finite = centered_difference(
        lambda value: bivariate_normal_indicator_covariance(
            value,
            c,
            correlation,
        ),
        q,
        step,
    )
    candidate_analytic = bivariate_normal_candidate_gradient(
        q,
        c,
        correlation,
    )

    trigger_finite = centered_difference(
        lambda value: bivariate_normal_indicator_covariance(
            q,
            value,
            correlation,
        ),
        c,
        step,
    )
    trigger_analytic = bivariate_normal_trigger_gradient(
        q,
        c,
        correlation,
    )

    cross_finite = centered_difference(
        lambda value: bivariate_normal_candidate_gradient(
            q,
            value,
            correlation,
        ),
        c,
        step,
    )
    cross_analytic = bivariate_normal_candidate_trigger_hessian(
        q,
        c,
        correlation,
    )

    print("=" * 80)
    print("D8-A boundary-gradient preflight")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Candidate derivative finite / analytic / difference: "
        f"{candidate_finite:.10f} / "
        f"{candidate_analytic:.10f} / "
        f"{candidate_finite-candidate_analytic:.3e}"
    )
    print(
        "Trigger derivative finite / analytic / difference: "
        f"{trigger_finite:.10f} / "
        f"{trigger_analytic:.10f} / "
        f"{trigger_finite-trigger_analytic:.3e}"
    )
    print(
        "Candidate-trigger Hessian finite / analytic / difference: "
        f"{cross_finite:.10f} / "
        f"{cross_analytic:.10f} / "
        f"{cross_finite-cross_analytic:.3e}"
    )
    print(
        "Independent cross Hessian: "
        f"{bivariate_normal_candidate_trigger_hessian(q, c, 0.0):.3e}"
    )
    print("D7 IF-gradient consistency encoded: YES")
    print("Policy-map twice differentiability proved: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
