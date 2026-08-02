from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def tess(pi: float | np.ndarray, alpha: float | np.ndarray) -> float | np.ndarray:
    pi_arr = np.asarray(pi, dtype=float)
    alpha_arr = np.asarray(alpha, dtype=float)
    if np.any((alpha_arr <= 0.0) | (alpha_arr >= 1.0)):
        raise ValueError("alpha must lie in (0,1)")
    if np.any((pi_arr < 0.0) | (pi_arr >= 1.0)):
        raise ValueError("rejection probabilities must lie in [0,1)")
    out = np.log1p(-pi_arr) / np.log1p(-alpha_arr)
    return float(out) if out.ndim == 0 else out


def two_candidate_bounds(alpha: float, r: float) -> tuple[float, float]:
    lower = alpha + max(0.0, r + alpha - 1.0)
    upper = alpha + min(r, alpha)
    return lower, upper


def build_envelope(alpha: float, rates: list[float], n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    p1 = u
    p2 = 1.0 - u

    rows: list[dict[str, float]] = []
    for r in rates:
        lower, upper = two_candidate_bounds(alpha, r)
        a_low = u <= r
        a_high = u > 1.0 - r
        p_low = np.where(a_low, np.minimum(p1, p2), p1)
        p_high = np.where(a_high, np.minimum(p1, p2), p1)
        mc_low = float(np.mean(p_low < alpha))
        mc_high = float(np.mean(p_high < alpha))
        rows.append(
            {
                "alpha": alpha,
                "activation_rate": r,
                "lower_pi_exact": lower,
                "upper_pi_exact": upper,
                "lower_tess_exact": tess(lower, alpha),
                "upper_tess_exact": tess(upper, alpha),
                "mc_pi_low": mc_low,
                "mc_pi_high": mc_high,
                "mc_abs_error_low": abs(mc_low - lower),
                "mc_abs_error_high": abs(mc_high - upper),
            }
        )
    return pd.DataFrame(rows)


def build_fixed_budget(budget: float) -> pd.DataFrame:
    rows = []
    for k in [1, 2, 4, 8, 16, 32, 64]:
        r = (budget - 1.0) / k
        rows.append(
            {
                "fixed_expected_candidate_count": budget,
                "optional_candidate_count": k,
                "activation_rate": r,
                "low_policy_deep_tail_tess_limit": 1.0,
                "high_policy_deep_tail_tess_limit": k + 1.0,
            }
        )
    return pd.DataFrame(rows)


def make_figure(alpha: float, envelope: pd.DataFrame, fixed_budget: pd.DataFrame, outdir: Path) -> None:
    r_grid = np.linspace(0.001, 0.999, 500)
    low = np.array([two_candidate_bounds(alpha, r)[0] for r in r_grid])
    high = np.array([two_candidate_bounds(alpha, r)[1] for r in r_grid])

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))
    ax = axes[0]
    ax.plot(r_grid, low, label="Lower attainable rejection probability", linewidth=2)
    ax.plot(r_grid, high, label="Upper attainable rejection probability", linewidth=2)
    ax.axhline(alpha, linestyle="--", linewidth=1, label="Base rejection probability")
    ax.axhline(2 * alpha, linestyle=":", linewidth=1, label="Fixed-full rejection probability")
    ax.set_xlabel("Activation rate r")
    ax.set_ylabel(f"Policy rejection probability at alpha={alpha:g}")
    ax.set_title("Sharp same-rate envelope")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.2)

    ax = axes[1]
    ax.plot(
        fixed_budget["optional_candidate_count"],
        fixed_budget["high_policy_deep_tail_tess_limit"],
        marker="o",
        label="High-tail allocation",
    )
    ax.plot(
        fixed_budget["optional_candidate_count"],
        fixed_budget["low_policy_deep_tail_tess_limit"],
        marker="o",
        label="Low-tail allocation",
    )
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xlabel("Number of optional candidates K")
    ax.set_ylabel("Deep-tail TESS limit")
    ax.set_title("Expected candidate count fixed at 1.5")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.2, which="both")

    fig.tight_layout()
    fig.savefig(outdir / "WORK_PACKAGE_A_SHARP_ENVELOPES.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / "WORK_PACKAGE_A_SHARP_ENVELOPES.pdf", bbox_inches="tight")
    plt.close(fig)


def environment_record(seed: int, n: int) -> dict[str, object]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "matplotlib": matplotlib.__version__,
        "seed": seed,
        "monte_carlo_states": n,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce Work Package A numerical checks.")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--mc-states", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--tolerance", type=float, default=0.0025)
    args = parser.parse_args()

    if args.mc_states < 10_000:
        raise ValueError("--mc-states must be at least 10000")

    outdir = args.outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    rates = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
    envelope = build_envelope(0.05, rates, args.mc_states, args.seed)
    fixed_budget = build_fixed_budget(1.5)

    envelope.to_csv(outdir / "WORK_PACKAGE_A_TWO_CANDIDATE_ENVELOPE_CHECK.csv", index=False)
    fixed_budget.to_csv(outdir / "WORK_PACKAGE_A_FIXED_BUDGET_DIVERGENCE.csv", index=False)
    make_figure(0.05, envelope, fixed_budget, outdir)

    max_error = float(
        max(envelope["mc_abs_error_low"].max(), envelope["mc_abs_error_high"].max())
    )
    passed = bool(max_error <= args.tolerance)

    # Exact mathematical sanity checks.
    assert np.all(envelope["lower_pi_exact"] <= envelope["upper_pi_exact"])
    assert np.allclose(
        fixed_budget["fixed_expected_candidate_count"],
        1.0
        + fixed_budget["activation_rate"] * fixed_budget["optional_candidate_count"],
    )
    assert np.all(np.diff(fixed_budget["high_policy_deep_tail_tess_limit"]) > 0)

    summary = {
        "work_package": "A",
        "status": "PASS" if passed else "FAIL",
        "maximum_absolute_rejection_probability_error": max_error,
        "tolerance": args.tolerance,
        "seed": args.seed,
        "monte_carlo_states": args.mc_states,
    }
    (outdir / "VALIDATION_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (outdir / "ENVIRONMENT.json").write_text(
        json.dumps(environment_record(args.seed, args.mc_states), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Work Package A numerical verification complete")
    print(f"Maximum Monte Carlo absolute rejection-probability error: {max_error:.6f}")
    print(f"Tolerance: {args.tolerance:.6f}")
    print(f"Status: {summary['status']}")
    print(f"Outputs written to: {outdir}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
