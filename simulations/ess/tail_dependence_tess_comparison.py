#!/usr/bin/env python3
"""Compare TESS under asymptotic independence and dependence.

Families:
- Equicorrelated Gaussian copula: asymptotically independent for rho < 1.
- Equicorrelated t copula: asymptotically dependent for finite degrees of freedom.
- Gumbel-Hougaard extreme-value copula: threshold-constant extremal coefficient.

The equicorrelated t-copula diagonal is evaluated deterministically using
Gauss-Hermite × generalized Gauss-Laguerre quadrature.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import gammaln, log_ndtr, roots_genlaguerre, roots_hermitenorm
from scipy.stats import t as student_t

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations.ess.gaussian_copula_tess_exact import (
    gaussian_equicorrelated_nonrejection_probability,
)


DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005, 0.002, 0.001)
DEFAULT_K = (7, 20)
DEFAULT_T_DF = (3, 5, 10)


def parse_csv_numbers(text: str, cast=float) -> tuple:
    values = tuple(cast(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one value is required.")
    return values


def tess_from_nonrejection(nonrejection: float, alpha: float) -> float:
    if not (0.0 < nonrejection <= 1.0):
        raise ValueError("nonrejection must be in (0, 1].")
    return math.log(nonrejection) / math.log1p(-alpha)


def _quadrature_nodes(df: float, n_hermite: int, n_laguerre: int):
    h_nodes, h_weights = roots_hermitenorm(n_hermite)
    h_weights = h_weights / math.sqrt(2.0 * math.pi)

    shape = df / 2.0
    l_nodes, l_weights = roots_genlaguerre(n_laguerre, shape - 1.0)
    l_weights = np.exp(np.log(l_weights) - gammaln(shape))
    return h_nodes, h_weights, l_nodes, l_weights


def equicorrelated_multivariate_t_equal_cdf(
    threshold: float,
    dimension: int,
    rho: float,
    df: float,
    *,
    n_hermite: int = 120,
    n_laguerre: int = 120,
) -> float:
    """CDF at a common threshold for an equicorrelated multivariate t."""
    if dimension < 1:
        raise ValueError("dimension must be >= 1")
    if not (0.0 <= rho < 1.0):
        raise ValueError("rho must be in [0, 1) for this quadrature.")
    if df <= 0:
        raise ValueError("df must be positive.")
    if dimension == 1:
        return float(student_t.cdf(threshold, df=df))

    h_nodes, h_weights, l_nodes, l_weights = _quadrature_nodes(
        df, n_hermite, n_laguerre
    )
    common = h_nodes[:, None]
    chi_square = 2.0 * l_nodes[None, :]

    standardized = (
        threshold * np.sqrt(chi_square / df) - math.sqrt(rho) * common
    ) / math.sqrt(1.0 - rho)

    conditional_probability = np.exp(dimension * log_ndtr(standardized))
    probability = np.sum(
        h_weights[:, None] * l_weights[None, :] * conditional_probability
    )
    return min(max(float(probability), 0.0), 1.0)


def t_copula_nonrejection_probability(
    alpha: float,
    k: int,
    rho: float,
    df: float,
    *,
    n_hermite: int = 120,
    n_laguerre: int = 120,
) -> float:
    """P(P_1 >= alpha, ..., P_K >= alpha) for an equicorrelated t copula."""
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0,1)")
    if k < 1:
        raise ValueError("k must be >= 1")
    if rho == 1.0 or k == 1:
        return 1.0 - alpha
    threshold = float(student_t.ppf(1.0 - alpha, df=df))
    return equicorrelated_multivariate_t_equal_cdf(
        threshold,
        k,
        rho,
        df,
        n_hermite=n_hermite,
        n_laguerre=n_laguerre,
    )


def t_copula_tess(alpha: float, k: int, rho: float, df: float) -> float:
    return tess_from_nonrejection(
        t_copula_nonrejection_probability(alpha, k, rho, df),
        alpha,
    )


def extremal_t_limit(k: int, rho: float, df: float) -> float:
    """Extremal coefficient of the extremal-t domain-of-attraction limit.

    For an equicorrelated t copula with df=nu and correlation rho:
      theta_K = K * T_{nu+1,K-1}(a,...,a; conditional correlation rho/(1+rho))
    where a = sqrt((nu+1)(1-rho)/(1+rho)).
    """
    if k == 1 or rho == 1.0:
        return 1.0
    if not (0.0 <= rho < 1.0):
        raise ValueError("rho must be in [0,1].")
    a = math.sqrt((df + 1.0) * (1.0 - rho) / (1.0 + rho))
    conditional_rho = rho / (1.0 + rho)
    probability = equicorrelated_multivariate_t_equal_cdf(
        a,
        k - 1,
        conditional_rho,
        df + 1.0,
    )
    return float(k * probability)


def gumbel_hougaard_tess(k: int, theta: float) -> float:
    """TESS for a Gumbel-Hougaard copula with parameter theta >= 1."""
    if theta < 1.0:
        raise ValueError("theta must be >= 1.")
    return float(k ** (1.0 / theta))


def build_grid(
    alphas: Iterable[float],
    candidate_counts: Iterable[int],
    rho: float,
    t_dfs: Iterable[float],
    gumbel_theta: float,
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []

    for k in candidate_counts:
        for alpha in alphas:
            gaussian_q, _ = gaussian_equicorrelated_nonrejection_probability(
                alpha, k, rho
            )
            rows.append(
                {
                    "family": "Gaussian copula",
                    "parameters": f"rho={rho:g}",
                    "nominal_candidate_count": k,
                    "local_alpha": alpha,
                    "tess": tess_from_nonrejection(gaussian_q, alpha),
                    "asymptotic_tess_limit": float(k),
                    "tail_class": "asymptotic independence",
                }
            )

            for df in t_dfs:
                limit = extremal_t_limit(k, rho, df)
                rows.append(
                    {
                        "family": "t copula",
                        "parameters": f"rho={rho:g}, df={df:g}",
                        "nominal_candidate_count": k,
                        "local_alpha": alpha,
                        "tess": t_copula_tess(alpha, k, rho, df),
                        "asymptotic_tess_limit": limit,
                        "tail_class": "asymptotic dependence",
                    }
                )

            gumbel_value = gumbel_hougaard_tess(k, gumbel_theta)
            rows.append(
                {
                    "family": "Gumbel-Hougaard",
                    "parameters": f"theta={gumbel_theta:g}",
                    "nominal_candidate_count": k,
                    "local_alpha": alpha,
                    "tess": gumbel_value,
                    "asymptotic_tess_limit": gumbel_value,
                    "tail_class": "max-stable / threshold-constant",
                }
            )
    return pd.DataFrame(rows)


def plot_comparison(data: pd.DataFrame, output_dir: Path) -> None:
    for k, group in data.groupby("nominal_candidate_count", sort=True):
        fig, ax = plt.subplots(figsize=(9, 5.8))
        for (family, params), subset in group.groupby(
            ["family", "parameters"], sort=False
        ):
            ordered = subset.sort_values("local_alpha", ascending=False)
            label = f"{family}: {params}"
            ax.plot(
                ordered["local_alpha"],
                ordered["tess"],
                marker="o",
                label=label,
            )

            if family == "t copula":
                limit = float(ordered["asymptotic_tess_limit"].iloc[0])
                ax.axhline(limit, linestyle=":", linewidth=0.8)

        ax.axhline(float(k), linestyle="--", linewidth=1, label=f"Independence K={k}")
        ax.axhline(1.0, linestyle=":", linewidth=1, label="Complete dependence")
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_xlabel("Local alpha (smaller = deeper tail)")
        ax.set_ylabel("TESS")
        ax.set_title(
            f"Tail geometry of effective search size, K={k}\n"
            "Gaussian vs t-copula vs max-stable copula"
        )
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=8, ncol=2)
        fig.tight_layout()
        fig.savefig(output_dir / f"tess_tail_class_comparison_K{k}.png", dpi=220)
        fig.savefig(output_dir / f"tess_tail_class_comparison_K{k}.svg")
        plt.close(fig)


def write_summary(data: pd.DataFrame, output_path: Path) -> None:
    lines = [
        "# TESS tail-class comparison",
        "",
        "Gaussian copula is asymptotically independent for rho<1, so TESS tends toward K.",
        "Finite-df t copulas are asymptotically dependent, so TESS tends toward an extremal-t coefficient below K.",
        "Gumbel-Hougaard is max-stable, so TESS is constant across alpha.",
        "",
    ]
    selected = data[data["local_alpha"].isin([0.2, 0.05, 0.01, 0.001])]
    for k in sorted(selected["nominal_candidate_count"].unique()):
        lines.extend([f"## K={k}", ""])
        table = selected[selected["nominal_candidate_count"] == k].copy()
        table["model"] = table["family"] + " (" + table["parameters"] + ")"
        pivot = table.pivot(index="model", columns="local_alpha", values="tess")
        lines.append("```text")
        lines.append(pivot.round(4).to_string())
        lines.append("```")
        lines.append("")
        limits = (
            table[["model", "asymptotic_tess_limit"]]
            .drop_duplicates()
            .sort_values("model")
        )
        lines.append("Asymptotic/constant limits:")
        lines.append("```text")
        lines.append(limits.to_string(index=False))
        lines.append("```")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--alphas", default=",".join(str(x) for x in DEFAULT_ALPHAS)
    )
    parser.add_argument(
        "--candidate-counts", default=",".join(str(x) for x in DEFAULT_K)
    )
    parser.add_argument("--rho", type=float, default=0.5)
    parser.add_argument(
        "--t-dfs", default=",".join(str(x) for x in DEFAULT_T_DF)
    )
    parser.add_argument("--gumbel-theta", type=float, default=2.0)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("simulations/ess/outputs/tail_dependence_comparison"),
    )
    args = parser.parse_args()

    alphas = parse_csv_numbers(args.alphas, float)
    candidate_counts = parse_csv_numbers(args.candidate_counts, int)
    t_dfs = parse_csv_numbers(args.t_dfs, float)

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = args.repo_root.resolve() / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    data = build_grid(
        alphas,
        candidate_counts,
        args.rho,
        t_dfs,
        args.gumbel_theta,
    )
    data.to_csv(output_dir / "tess_tail_class_comparison.csv", index=False)
    plot_comparison(data, output_dir)
    write_summary(data, output_dir / "TAIL_CLASS_COMPARISON_SUMMARY.md")

    print("Tail-dependence comparison complete")
    print(f"Output directory: {output_dir}")
    print(f"Rows: {len(data)}")
    for k in candidate_counts:
        subset = data[
            (data["nominal_candidate_count"] == k)
            & (data["local_alpha"] == min(alphas))
        ]
        print(f"\nK={k}, deepest alpha={min(alphas):g}")
        print(
            subset[
                ["family", "parameters", "tess", "asymptotic_tess_limit"]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()
