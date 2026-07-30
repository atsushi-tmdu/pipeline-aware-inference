#!/usr/bin/env python3
"""Estimate Phase 3C pipeline tail-ESS curves from stored null p-values.

This script reuses ``independent_inference_results.csv`` from the two frozen
Phase 3C full runs. No model fitting or simulation rerun is required.

Primary analysis
----------------
* target_auc == 0.50
* metric == roc_auc
* feature_selection == none
* method == naive_empirical
* pool_size in {7, 20}
* strict rejection rule p < alpha, matching the Phase 3 engine

The default alpha grid is 0.20, 0.10, 0.05, 0.025, 0.01, and 0.005.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from ess_estimators import estimate_tail_ess_curve

DEFAULT_ALPHAS = (0.20, 0.10, 0.05, 0.025, 0.01, 0.005)
PRIMARY_METHOD = "naive_empirical"
SENSITIVITY_METHOD = "naive_mannwhitney"


def parse_alpha_grid(value: str) -> tuple[float, ...]:
    alphas = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    if not alphas:
        raise argparse.ArgumentTypeError("alpha grid must not be empty")
    if len(set(alphas)) != len(alphas):
        raise argparse.ArgumentTypeError("alpha grid must not contain duplicates")
    if any(not 0.0 < alpha < 1.0 for alpha in alphas):
        raise argparse.ArgumentTypeError("every alpha must lie strictly between 0 and 1")
    return alphas


def read_participation_ratio(path: Path) -> dict[tuple[str, int], float]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        return {
            (row["library"], int(row["pool_size"])): float(row["effective_candidate_count"])
            for row in rows
        }


def validate_input(df: pd.DataFrame, path: Path) -> None:
    required = {
        "replication",
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "pool_size",
        "metric",
        "method",
        "p_value",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    if df.empty:
        raise ValueError(f"{path} is empty")


def filtered_null_pvalues(df: pd.DataFrame, method: str, pool_size: int) -> pd.Series:
    subset = df[
        np.isclose(df["target_auc"].astype(float), 0.50)
        & (df["feature_selection"] == "none")
        & (df["metric"] == "roc_auc")
        & (df["method"] == method)
        & (df["pool_size"].astype(int) == pool_size)
    ].copy()

    if subset.empty:
        raise ValueError(f"No rows found for method={method!r}, K={pool_size}")
    if subset["replication"].duplicated().any():
        duplicates = subset.loc[subset["replication"].duplicated(), "replication"].head().tolist()
        raise ValueError(
            f"Expected one p-value per replication for method={method!r}, K={pool_size}; "
            f"duplicate replication IDs include {duplicates}"
        )

    p_values = pd.to_numeric(subset["p_value"], errors="raise")
    if p_values.isna().any() or ((p_values < 0.0) | (p_values > 1.0)).any():
        raise ValueError(f"Invalid p-values for method={method!r}, K={pool_size}")
    return p_values.sort_index()


def make_rows(
    library: str,
    input_path: Path,
    df: pd.DataFrame,
    methods: Iterable[str],
    pool_sizes: Iterable[int],
    alphas: tuple[float, ...],
    participation_ratio: dict[tuple[str, int], float],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for method in methods:
        for pool_size in pool_sizes:
            p_values = filtered_null_pvalues(df, method=method, pool_size=pool_size)
            estimates = estimate_tail_ess_curve(
                p_values=tuple(float(value) for value in p_values),
                local_alphas=alphas,
            )
            pr = participation_ratio.get((library, int(pool_size)), float("nan"))
            for estimate in estimates:
                rows.append(
                    {
                        "library": library,
                        "input_file": str(input_path),
                        "method": method,
                        "analysis_role": "primary" if method == PRIMARY_METHOD else "sensitivity",
                        "nominal_candidate_count": int(pool_size),
                        "local_alpha": estimate.local_alpha,
                        "null_evaluation_repetitions": estimate.repetitions,
                        "naive_rejections": estimate.rejections,
                        "naive_rejection_probability": estimate.rejection_probability,
                        "naive_rejection_probability_low_95": estimate.rejection_probability_low,
                        "naive_rejection_probability_high_95": estimate.rejection_probability_high,
                        "tail_ess": estimate.ess,
                        "tail_ess_low_95": estimate.ess_low,
                        "tail_ess_high_95": estimate.ess_high,
                        "participation_ratio_count": pr,
                        "tail_minus_participation_ratio": estimate.ess - pr,
                        "tail_to_participation_ratio": estimate.ess / pr,
                        "strict_rejection_rule": "p < alpha",
                    }
                )
    return rows


def plot_primary_curve(results: pd.DataFrame, output_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipped figures")
        return

    primary = results[results["method"] == PRIMARY_METHOD].copy()
    if primary.empty:
        return

    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    for (library, pool_size), group in primary.groupby(
        ["library", "nominal_candidate_count"], sort=True
    ):
        group = group.sort_values("local_alpha")
        alpha = group["local_alpha"].to_numpy(float)
        ess = group["tail_ess"].to_numpy(float)
        low = group["tail_ess_low_95"].to_numpy(float)
        high = group["tail_ess_high_95"].to_numpy(float)
        label = f"{library}, K={int(pool_size)}"
        line = ax.plot(alpha, ess, marker="o", label=label)[0]
        ax.fill_between(alpha, low, high, alpha=0.16, color=line.get_color())

    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local significance level (alpha)")
    ax.set_ylabel("Sidak-equivalent tail ESS")
    ax.set_title("Phase 3C tail effective search size curves")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "phase3c_tail_ess_curve_primary.png", dpi=300)
    fig.savefig(output_dir / "phase3c_tail_ess_curve_primary.svg")
    plt.close(fig)


def plot_method_sensitivity(results: pd.DataFrame, output_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    if SENSITIVITY_METHOD not in set(results["method"]):
        return

    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    for (library, pool_size, method), group in results.groupby(
        ["library", "nominal_candidate_count", "method"], sort=True
    ):
        group = group.sort_values("local_alpha")
        linestyle = "-" if method == PRIMARY_METHOD else "--"
        label = f"{library}, K={int(pool_size)}, {method}"
        ax.plot(
            group["local_alpha"],
            group["tail_ess"],
            marker="o",
            linestyle=linestyle,
            label=label,
        )

    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local significance level (alpha)")
    ax.set_ylabel("Sidak-equivalent tail ESS")
    ax.set_title("Phase 3C ESS sensitivity to naive p-value definition")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "phase3c_tail_ess_curve_method_sensitivity.png", dpi=300)
    fig.savefig(output_dir / "phase3c_tail_ess_curve_method_sensitivity.svg")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--high-dependency", type=Path, required=True)
    parser.add_argument("--mixed-realistic", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--alphas",
        type=parse_alpha_grid,
        default=DEFAULT_ALPHAS,
        help="Comma-separated local-alpha grid.",
    )
    parser.add_argument(
        "--include-mannwhitney-sensitivity",
        action="store_true",
        help="Also estimate curves from naive_mannwhitney p-values.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Defaults to simulations/ess/outputs/phase3c_curve under repo-root.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else repo_root / "simulations" / "ess" / "outputs" / "phase3c_curve"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    dependence_path = (
        repo_root
        / "simulations"
        / "phase3c"
        / "frozen_results"
        / "candidate_dependence_summary.csv"
    )
    participation_ratio = read_participation_ratio(dependence_path)

    inputs = {
        "high_dependency_linear_20": args.high_dependency.expanduser().resolve(),
        "mixed_realistic_20": args.mixed_realistic.expanduser().resolve(),
    }
    methods = [PRIMARY_METHOD]
    if args.include_mannwhitney_sensitivity:
        methods.append(SENSITIVITY_METHOD)

    rows: list[dict[str, object]] = []
    for library, path in inputs.items():
        if not path.is_file():
            raise FileNotFoundError(path)
        df = pd.read_csv(path)
        validate_input(df, path)
        rows.extend(
            make_rows(
                library=library,
                input_path=path,
                df=df,
                methods=methods,
                pool_sizes=(7, 20),
                alphas=tuple(args.alphas),
                participation_ratio=participation_ratio,
            )
        )

    results = pd.DataFrame(rows).sort_values(
        ["method", "library", "nominal_candidate_count", "local_alpha"],
        ascending=[True, True, True, False],
    )
    output_csv = output_dir / "phase3c_tail_ess_curve.csv"
    results.to_csv(output_csv, index=False)

    primary = results[results["method"] == PRIMARY_METHOD].copy()
    wide = primary.pivot_table(
        index=["library", "nominal_candidate_count"],
        columns="local_alpha",
        values="tail_ess",
        aggfunc="first",
    ).reset_index()
    wide.columns = [
        str(column) if not isinstance(column, float) else f"ess_alpha_{column:g}"
        for column in wide.columns
    ]
    wide.to_csv(output_dir / "phase3c_tail_ess_curve_wide.csv", index=False)

    plot_primary_curve(results, output_dir)
    plot_method_sensitivity(results, output_dir)

    print(f"Wrote {output_csv}")
    print(f"Wrote outputs to {output_dir}")
    print()
    print(primary[
        [
            "library",
            "nominal_candidate_count",
            "local_alpha",
            "naive_rejection_probability",
            "tail_ess",
            "tail_ess_low_95",
            "tail_ess_high_95",
            "participation_ratio_count",
        ]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
