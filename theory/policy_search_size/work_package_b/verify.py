from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def tess(alpha: np.ndarray, rejection: np.ndarray) -> np.ndarray:
    alpha = np.asarray(alpha, dtype=float)
    rejection = np.asarray(rejection, dtype=float)
    if np.any((alpha <= 0) | (alpha >= 1)):
        raise ValueError("alpha must lie in (0,1)")
    if np.any((rejection < 0) | (rejection >= 1)):
        raise ValueError("rejection probabilities must lie in [0,1)")
    return np.log1p(-rejection) / np.log1p(-alpha)


def coherent_example() -> pd.DataFrame:
    alpha = np.geomspace(0.005, 0.20, 120)
    c = 0.8 * alpha * (1.0 - alpha)
    pi_promising = alpha + 0.25 * c
    pi_random = alpha
    pi_rescue = alpha - 0.25 * c
    df = pd.DataFrame(
        {
            "alpha": alpha,
            "pi_promising": pi_promising,
            "pi_random": pi_random,
            "pi_rescue": pi_rescue,
            "tess_promising": tess(alpha, pi_promising),
            "tess_random": tess(alpha, pi_random),
            "tess_rescue": tess(alpha, pi_rescue),
        }
    )
    assert np.all(df["pi_promising"] > df["pi_random"])
    assert np.all(df["pi_random"] > df["pi_rescue"])
    return df


def h_single(x: np.ndarray, tau: float) -> np.ndarray:
    return x * (1.0 - x) * (tau - x)


def h_single_prime(x: np.ndarray, tau: float) -> np.ndarray:
    return tau - 2.0 * (tau + 1.0) * x + 3.0 * x * x


def crossing_exact_grid(
    tau: float = 0.05,
    epsilon: float = 0.90,
    r: float = 0.50,
    d: float = 0.50,
) -> pd.DataFrame:
    alpha = np.geomspace(0.0025, 0.25, 180)
    h = h_single(alpha, tau)
    pi_plus = alpha + 2.0 * d * epsilon * h
    pi_minus = alpha - 2.0 * d * epsilon * h

    x = np.linspace(0.0, 1.0, 200001)
    max_abs_deriv = float(np.max(np.abs(h_single_prime(x, tau))))
    if epsilon * max_abs_deriv >= 1.0:
        raise ValueError("epsilon is too large for monotone CDFs")
    if d <= 0 or d > min(r, 1.0 - r):
        raise ValueError("d must lie in (0,min(r,1-r)]")

    # The crossing is exact at tau, even if tau is not a point in the plotting grid.
    assert abs(float(h_single(np.array([tau]), tau)[0])) < 1e-15
    assert float(h_single(np.array([tau / 2]), tau)[0]) > 0
    assert float(h_single(np.array([(tau + 1.0) / 2]), tau)[0]) < 0

    return pd.DataFrame(
        {
            "alpha": alpha,
            "h_tau": h,
            "pi_policy_plus": pi_plus,
            "pi_policy_minus": pi_minus,
            "pi_fixed_branch": alpha,
            "tess_policy_plus": tess(alpha, pi_plus),
            "tess_policy_minus": tess(alpha, pi_minus),
            "tess_fixed_branch": np.ones_like(alpha),
            "exact_rejection_difference_plus_minus": 4.0 * d * epsilon * h,
        }
    )


def invert_cdf(u: np.ndarray, xgrid: np.ndarray, cdf: np.ndarray) -> np.ndarray:
    return np.interp(u, cdf, xgrid)


def crossing_monte_carlo(
    rng: np.random.Generator,
    tau: float = 0.05,
    epsilon: float = 0.90,
    r: float = 0.50,
    d: float = 0.50,
    n: int = 600_000,
) -> pd.DataFrame:
    xgrid = np.linspace(0.0, 1.0, 500001)
    hgrid = h_single(xgrid, tau)
    F = xgrid + epsilon * hgrid
    G = xgrid - epsilon * hgrid
    if np.any(np.diff(F) < -1e-12) or np.any(np.diff(G) < -1e-12):
        raise RuntimeError("constructed CDF is not monotone")

    state_plus = rng.integers(0, 2, size=n).astype(bool)
    u0 = rng.random(n)
    u1 = rng.random(n)
    p0 = np.empty(n)
    p1 = np.empty(n)

    p0[state_plus] = invert_cdf(u0[state_plus], xgrid, G)
    p1[state_plus] = invert_cdf(u1[state_plus], xgrid, F)
    p0[~state_plus] = invert_cdf(u0[~state_plus], xgrid, F)
    p1[~state_plus] = invert_cdf(u1[~state_plus], xgrid, G)

    vplus = rng.random(n)
    vminus = rng.random(n)
    prob_plus = np.where(state_plus, r + d, r - d)
    prob_minus = np.where(state_plus, r - d, r + d)
    aplus = vplus <= prob_plus
    aminus = vminus <= prob_minus
    pplus = np.where(aplus, p1, p0)
    pminus = np.where(aminus, p1, p0)

    rows = []
    for a in [0.005, 0.010, 0.025, 0.050, 0.075, 0.100, 0.200]:
        h = float(h_single(np.array([a]), tau)[0])
        exact_plus = a + 2 * d * epsilon * h
        exact_minus = a - 2 * d * epsilon * h
        mc_plus = float(np.mean(pplus < a))
        mc_minus = float(np.mean(pminus < a))
        rows.append(
            {
                "alpha": a,
                "exact_pi_plus": exact_plus,
                "mc_pi_plus": mc_plus,
                "abs_error_plus": abs(mc_plus - exact_plus),
                "exact_pi_minus": exact_minus,
                "mc_pi_minus": mc_minus,
                "abs_error_minus": abs(mc_minus - exact_minus),
                "exact_difference": exact_plus - exact_minus,
                "mc_difference": mc_plus - mc_minus,
                "activation_rate_plus_mc": float(aplus.mean()),
                "activation_rate_minus_mc": float(aminus.mean()),
                "P0_rejection_mc": float(np.mean(p0 < a)),
                "P1_rejection_mc": float(np.mean(p1 < a)),
            }
        )
    return pd.DataFrame(rows)


def h_multi(x: np.ndarray, roots: tuple[float, ...]) -> np.ndarray:
    y = x * (1.0 - x)
    for root in roots:
        y = y * (x - root)
    return y


def multi_crossing_grid(
    roots: tuple[float, ...] = (0.025, 0.10),
    epsilon: float = 0.80,
    r: float = 0.50,
    d: float = 0.50,
) -> pd.DataFrame:
    alpha = np.geomspace(0.0025, 0.25, 220)
    h = h_multi(alpha, roots)
    x = np.linspace(0.0, 1.0, 500001)
    hx = h_multi(x, roots)
    deriv = np.gradient(hx, x)
    if epsilon * float(np.max(np.abs(deriv))) >= 1:
        raise ValueError("epsilon too large for multi-crossing CDF construction")
    pi_plus = alpha + 2 * d * epsilon * h
    pi_minus = alpha - 2 * d * epsilon * h

    for root in roots:
        assert abs(float(h_multi(np.array([root]), roots)[0])) < 1e-15

    return pd.DataFrame(
        {
            "alpha": alpha,
            "h": h,
            "pi_plus": pi_plus,
            "pi_minus": pi_minus,
            "tess_plus": tess(alpha, pi_plus),
            "tess_minus": tess(alpha, pi_minus),
            "difference": pi_plus - pi_minus,
        }
    )


def make_plots(
    coherent: pd.DataFrame,
    crossing: pd.DataFrame,
    multi: pd.DataFrame,
    outdir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.8))
    ax.plot(coherent["alpha"], coherent["tess_promising"], marker="o", markevery=15, label="Top-score activation")
    ax.plot(coherent["alpha"], coherent["tess_random"], marker="o", markevery=15, label="Random activation")
    ax.plot(coherent["alpha"], coherent["tess_rescue"], marker="o", markevery=15, label="Bottom-score activation")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local threshold alpha (smaller = deeper tail)")
    ax.set_ylabel("TESS")
    ax.set_title("Threshold-coherent common-index ordering")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
    ax.grid(True, alpha=0.25)
    fig.subplots_adjust(bottom=0.24, left=0.12, right=0.97, top=0.90)
    fig.savefig(outdir / "WORK_PACKAGE_B_COHERENT_POLICY_TESS_CURVES.png", dpi=300)
    fig.savefig(outdir / "WORK_PACKAGE_B_COHERENT_POLICY_TESS_CURVES.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    ax.plot(crossing["alpha"], crossing["tess_policy_plus"], marker="o", markevery=20, label="High-alignment policy")
    ax.plot(crossing["alpha"], crossing["tess_policy_minus"], marker="o", markevery=20, label="Low-alignment policy")
    ax.plot(crossing["alpha"], crossing["tess_fixed_branch"], linestyle="--", label="Each fixed branch")
    ax.axvline(0.05, linestyle=":", linewidth=1.2, label="Crossing threshold")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local threshold alpha (smaller = deeper tail)")
    ax.set_ylabel("TESS")
    ax.set_title("Same-budget policy curves can reverse ordering with alpha")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outdir / "WORK_PACKAGE_B_SINGLE_CROSSING_TESS_CURVES.png", dpi=300)
    fig.savefig(outdir / "WORK_PACKAGE_B_SINGLE_CROSSING_TESS_CURVES.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    ax.plot(multi["alpha"], multi["difference"], linewidth=2, label="High minus low alignment")
    ax.axhline(0.0, linestyle="--", linewidth=1)
    ax.axvline(0.025, linestyle=":", linewidth=1, label="Prescribed crossings")
    ax.axvline(0.10, linestyle=":", linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local threshold alpha (smaller = deeper tail)")
    ax.set_ylabel("Rejection-probability difference")
    ax.set_title("Arbitrary finite crossing patterns are attainable")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outdir / "WORK_PACKAGE_B_ARBITRARY_CROSSING_PREMIUM.png", dpi=300)
    fig.savefig(outdir / "WORK_PACKAGE_B_ARBITRARY_CROSSING_PREMIUM.pdf")
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
    parser = argparse.ArgumentParser(description="Reproduce Work Package B numerical checks.")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--mc-states", type=int, default=600_000)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--tolerance", type=float, default=0.0020)
    args = parser.parse_args()

    if args.mc_states < 10_000:
        raise ValueError("--mc-states must be at least 10000")

    outdir = args.outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    coherent = coherent_example()
    crossing = crossing_exact_grid()
    mc = crossing_monte_carlo(rng=rng, n=args.mc_states)
    multi = multi_crossing_grid()

    coherent.to_csv(outdir / "WORK_PACKAGE_B_COHERENT_ORDERING.csv", index=False)
    crossing.to_csv(outdir / "WORK_PACKAGE_B_SINGLE_CROSSING_EXACT.csv", index=False)
    mc.to_csv(outdir / "WORK_PACKAGE_B_SINGLE_CROSSING_MONTE_CARLO_CHECK.csv", index=False)
    multi.to_csv(outdir / "WORK_PACKAGE_B_ARBITRARY_CROSSING_EXACT.csv", index=False)
    make_plots(coherent, crossing, multi, outdir)

    max_mc_error = float(max(mc["abs_error_plus"].max(), mc["abs_error_minus"].max()))
    passed = bool(max_mc_error <= args.tolerance)

    # Exact and numerical sanity checks.
    row_cross = mc.loc[np.isclose(mc["alpha"], 0.05)].iloc[0]
    assert abs(float(row_cross["exact_difference"])) < 1e-14
    assert coherent["tess_promising"].gt(coherent["tess_random"]).all()
    assert coherent["tess_random"].gt(coherent["tess_rescue"]).all()

    summary = {
        "work_package": "B",
        "status": "PASS" if passed else "FAIL",
        "maximum_absolute_rejection_probability_error": max_mc_error,
        "tolerance": args.tolerance,
        "seed": args.seed,
        "monte_carlo_states": args.mc_states,
        "single_crossing_threshold": 0.05,
        "arbitrary_crossing_thresholds": [0.025, 0.10],
    }
    (outdir / "VALIDATION_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (outdir / "ENVIRONMENT.json").write_text(
        json.dumps(environment_record(args.seed, args.mc_states), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Work Package B numerical verification complete")
    print(f"Maximum Monte Carlo absolute rejection-probability error: {max_mc_error:.6f}")
    print(f"Tolerance: {args.tolerance:.6f}")
    print(f"Status: {summary['status']}")
    print(f"Outputs written to: {outdir}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
