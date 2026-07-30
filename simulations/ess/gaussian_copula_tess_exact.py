#!/usr/bin/env python3
"""Exact TESS curves for an equicorrelated Gaussian copula.

For p_j = 1 - Phi(Z_j), where Z is an equicorrelated standard Gaussian
vector with pairwise correlation rho >= 0,

    TESS(alpha) = log P(max_j Z_j <= z_alpha) / log(1-alpha).

For 0 < rho < 1, the joint non-rejection probability is evaluated through
the one-factor representation and one-dimensional numerical quadrature.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.special import log_ndtr
from scipy.stats import norm


DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005, 0.001, 1e-4, 1e-5, 1e-6)
DEFAULT_RHOS = (0.0, 0.25, 0.50, 0.75, 0.90, 0.99, 1.0)
DEFAULT_K = (7, 20)


def parse_csv_numbers(text: str, cast=float) -> tuple:
    values = tuple(cast(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one value is required.")
    return values


def validate_inputs(alpha: float, k: int, rho: float) -> None:
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0, 1); received {alpha}")
    if k < 1:
        raise ValueError(f"k must be >= 1; received {k}")
    if not (0.0 <= rho <= 1.0):
        raise ValueError(
            "This exact one-factor implementation supports rho in [0, 1]. "
            f"Received {rho}."
        )


def gaussian_equicorrelated_nonrejection_probability(
    alpha: float,
    k: int,
    rho: float,
    *,
    epsabs: float = 2e-13,
    epsrel: float = 2e-12,
) -> tuple[float, float]:
    """Return P(P_1 >= alpha, ..., P_K >= alpha) and quadrature error."""
    validate_inputs(alpha, k, rho)

    if k == 1 or rho == 1.0:
        return 1.0 - alpha, 0.0
    if rho == 0.0:
        return (1.0 - alpha) ** k, 0.0

    z_alpha = float(norm.ppf(1.0 - alpha))
    sqrt_rho = math.sqrt(rho)
    residual_sd = math.sqrt(1.0 - rho)
    normalizer = math.sqrt(2.0 * math.pi)

    def integrand(v: float) -> float:
        conditional_z = (z_alpha - sqrt_rho * v) / residual_sd
        log_conditional_cdf = float(log_ndtr(conditional_z))
        return (
            math.exp(-0.5 * v * v)
            / normalizer
            * math.exp(k * log_conditional_cdf)
        )

    probability, error = quad(
        integrand,
        -np.inf,
        np.inf,
        epsabs=epsabs,
        epsrel=epsrel,
        limit=500,
    )
    probability = min(max(float(probability), 0.0), 1.0)
    return probability, float(error)


def gaussian_equicorrelated_tess(alpha: float, k: int, rho: float) -> float:
    """Calculate exact finite-threshold TESS."""
    validate_inputs(alpha, k, rho)
    if k == 1 or rho == 1.0:
        return 1.0
    if rho == 0.0:
        return float(k)
    q, _ = gaussian_equicorrelated_nonrejection_probability(alpha, k, rho)
    if q <= 0.0:
        return math.inf
    return math.log(q) / math.log1p(-alpha)


def build_exact_grid(
    alphas: Iterable[float],
    candidate_counts: Iterable[int],
    rhos: Iterable[float],
) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for k in candidate_counts:
        for rho in rhos:
            for alpha in alphas:
                q, quadrature_error = gaussian_equicorrelated_nonrejection_probability(
                    alpha, k, rho
                )
                rejection_probability = 1.0 - q
                tess = math.log(q) / math.log1p(-alpha)
                rows.append(
                    {
                        "nominal_candidate_count": int(k),
                        "rho": float(rho),
                        "local_alpha": float(alpha),
                        "exact_nonrejection_probability": q,
                        "exact_rejection_probability": rejection_probability,
                        "exact_tess": tess,
                        "quadrature_absolute_error": quadrature_error,
                        "distance_from_independence_K": float(k - tess),
                    }
                )
    return pd.DataFrame(rows)


def compare_with_monte_carlo(
    exact: pd.DataFrame,
    monte_carlo_path: Path,
) -> pd.DataFrame:
    mc = pd.read_csv(monte_carlo_path)
    required = {
        "scenario",
        "nominal_candidate_count",
        "rho",
        "local_alpha",
        "tess",
        "rejection_probability",
    }
    missing = required.difference(mc.columns)
    if missing:
        raise ValueError(f"Monte Carlo file is missing columns: {sorted(missing)}")

    gaussian = mc.loc[
        mc["scenario"] == "gaussian_copula",
        [
            "nominal_candidate_count",
            "rho",
            "local_alpha",
            "tess",
            "rejection_probability",
        ],
    ].copy()

    merged = gaussian.merge(
        exact,
        on=["nominal_candidate_count", "rho", "local_alpha"],
        how="inner",
        validate="one_to_one",
    )
    merged["tess_monte_carlo_minus_exact"] = merged["tess"] - merged["exact_tess"]
    merged["absolute_tess_difference"] = merged[
        "tess_monte_carlo_minus_exact"
    ].abs()
    merged["rejection_probability_monte_carlo_minus_exact"] = (
        merged["rejection_probability"] - merged["exact_rejection_probability"]
    )
    return merged


def plot_exact_curves(exact: pd.DataFrame, output_path: Path) -> None:
    for k, group in exact.groupby("nominal_candidate_count", sort=True):
        fig, ax = plt.subplots(figsize=(8.5, 5.5))
        for rho, subset in group.groupby("rho", sort=True):
            ordered = subset.sort_values("local_alpha", ascending=False)
            ax.plot(
                ordered["local_alpha"],
                ordered["exact_tess"],
                marker="o",
                label=f"rho={rho:g}",
            )
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_xlabel("Local alpha (smaller = deeper tail)")
        ax.set_ylabel("Exact TESS")
        ax.set_title(f"Equicorrelated Gaussian copula: exact TESS, K={k}")
        ax.axhline(float(k), linestyle="--", linewidth=1, label=f"Independence limit K={k}")
        ax.axhline(1.0, linestyle=":", linewidth=1, label="Complete dependence")
        ax.grid(True, alpha=0.25)
        ax.legend(ncol=2)
        fig.tight_layout()
        fig.savefig(output_path.with_name(f"{output_path.stem}_K{k}.png"), dpi=220)
        fig.savefig(output_path.with_name(f"{output_path.stem}_K{k}.svg"))
        plt.close(fig)


def plot_convergence(exact: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    k = int(exact["nominal_candidate_count"].max())
    subset_k = exact[exact["nominal_candidate_count"] == k]
    for rho, subset in subset_k.groupby("rho", sort=True):
        if rho in (0.0, 1.0):
            continue
        ordered = subset.sort_values("local_alpha", ascending=False)
        ax.plot(
            ordered["local_alpha"],
            ordered["exact_tess"],
            marker="o",
            label=f"rho={rho:g}",
        )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Exact TESS")
    ax.set_title(f"Slow convergence toward K under Gaussian asymptotic independence (K={k})")
    ax.axhline(float(k), linestyle="--", linewidth=1, label=f"Limit K={k}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path.with_suffix(".png"), dpi=220)
    fig.savefig(output_path.with_suffix(".svg"))
    plt.close(fig)


def write_summary(exact: pd.DataFrame, comparison: pd.DataFrame | None, path: Path) -> None:
    lines = [
        "# Exact Gaussian-copula TESS summary",
        "",
        "TESS is evaluated through a one-dimensional common-factor integral.",
        "For rho=0, TESS=K exactly. For rho=1, TESS=1 exactly.",
        "For every fixed rho<1, Gaussian asymptotic independence implies TESS(alpha) -> K as alpha -> 0.",
        "",
    ]
    selected = exact[
        exact["local_alpha"].isin([0.2, 0.05, 0.005, 1e-4, 1e-6])
    ].copy()
    for k in sorted(selected["nominal_candidate_count"].unique()):
        lines.extend([f"## K={k}", ""])
        pivot = (
            selected[selected["nominal_candidate_count"] == k]
            .pivot(index="rho", columns="local_alpha", values="exact_tess")
            .sort_index()
        )
        lines.append("```text")
        lines.append(pivot.round(4).to_string())
        lines.append("```")
        lines.append("")

    if comparison is not None and not comparison.empty:
        worst = comparison.loc[comparison["absolute_tess_difference"].idxmax()]
        lines.extend(
            [
                "## Monte Carlo comparison",
                "",
                f"Rows compared: {len(comparison)}",
                (
                    "Maximum absolute Monte Carlo-minus-exact TESS difference: "
                    f"{worst['absolute_tess_difference']:.6f}"
                ),
                (
                    "Worst condition: "
                    f"K={int(worst['nominal_candidate_count'])}, "
                    f"rho={worst['rho']}, alpha={worst['local_alpha']}"
                ),
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exact finite-threshold TESS for equicorrelated Gaussian copulas."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--alphas",
        default=",".join(str(x) for x in DEFAULT_ALPHAS),
    )
    parser.add_argument(
        "--candidate-counts",
        default=",".join(str(x) for x in DEFAULT_K),
    )
    parser.add_argument(
        "--rhos",
        default=",".join(str(x) for x in DEFAULT_RHOS),
    )
    parser.add_argument(
        "--monte-carlo-boundary-csv",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("simulations/ess/outputs/gaussian_copula_exact"),
    )
    args = parser.parse_args()

    alphas = parse_csv_numbers(args.alphas, float)
    candidate_counts = parse_csv_numbers(args.candidate_counts, int)
    rhos = parse_csv_numbers(args.rhos, float)

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = args.repo_root.resolve() / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    exact = build_exact_grid(alphas, candidate_counts, rhos)
    exact_path = output_dir / "gaussian_copula_tess_exact.csv"
    exact.to_csv(exact_path, index=False)

    comparison = None
    if args.monte_carlo_boundary_csv is not None:
        mc_path = args.monte_carlo_boundary_csv
        if not mc_path.is_absolute():
            mc_path = args.repo_root.resolve() / mc_path
        if mc_path.exists():
            comparison = compare_with_monte_carlo(exact, mc_path)
            comparison.to_csv(
                output_dir / "gaussian_copula_exact_vs_monte_carlo.csv",
                index=False,
            )
        else:
            print(f"Warning: Monte Carlo boundary CSV not found: {mc_path}")

    plot_exact_curves(exact, output_dir / "gaussian_copula_tess_exact_curves")
    plot_convergence(exact, output_dir / "gaussian_copula_tess_convergence")
    write_summary(
        exact,
        comparison,
        output_dir / "GAUSSIAN_COPULA_EXACT_SUMMARY.md",
    )

    print("Exact Gaussian-copula TESS calculation complete")
    print(f"Output directory: {output_dir}")
    print(f"Rows: {len(exact)}")
    if comparison is not None and not comparison.empty:
        print(
            "Maximum absolute Monte Carlo-minus-exact TESS difference: "
            f"{comparison['absolute_tess_difference'].max():.6f}"
        )


if __name__ == "__main__":
    main()
