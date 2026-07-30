#!/usr/bin/env python3
"""Numerical verification and manuscript tables for the adaptive-branching proposition."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from simulations.ess.adaptive_branching_tess import (
    build_exact_grid,
    trigger_threshold,
)


def verify_order(data: pd.DataFrame, tolerance: float = 1e-12) -> pd.DataFrame:
    adaptive = data[
        data["scenario"].isin(
            ["promising_triggered", "random_expansion", "rescue_triggered"]
        )
    ].copy()

    pivot = adaptive.pivot(
        index="local_alpha",
        columns="scenario",
        values="exact_tess",
    ).reset_index()

    pivot["promising_lt_random"] = (
        pivot["promising_triggered"] + tolerance
        < pivot["random_expansion"]
    )
    pivot["random_lt_rescue"] = (
        pivot["random_expansion"] + tolerance
        < pivot["rescue_triggered"]
    )
    pivot["strict_order_verified"] = (
        pivot["promising_lt_random"] & pivot["random_lt_rescue"]
    )

    pivot["rescue_minus_promising"] = (
        pivot["rescue_triggered"] - pivot["promising_triggered"]
    )
    pivot["random_minus_promising"] = (
        pivot["random_expansion"] - pivot["promising_triggered"]
    )
    pivot["rescue_minus_random"] = (
        pivot["rescue_triggered"] - pivot["random_expansion"]
    )
    return pivot


def verify_equal_nonrejection_gaps(
    data: pd.DataFrame,
) -> pd.DataFrame:
    adaptive = data[
        data["scenario"].isin(
            ["promising_triggered", "random_expansion", "rescue_triggered"]
        )
    ].copy()

    pivot = adaptive.pivot(
        index="local_alpha",
        columns="scenario",
        values="exact_nonrejection_probability",
    ).reset_index()

    pivot["promising_minus_random_Q"] = (
        pivot["promising_triggered"] - pivot["random_expansion"]
    )
    pivot["random_minus_rescue_Q"] = (
        pivot["random_expansion"] - pivot["rescue_triggered"]
    )
    pivot["gap_difference"] = (
        pivot["promising_minus_random_Q"]
        - pivot["random_minus_rescue_Q"]
    )
    return pivot


def make_manuscript_table(data: pd.DataFrame) -> pd.DataFrame:
    selected_alphas = (0.2, 0.1, 0.05, 0.01, 0.001)
    table = data[
        data["local_alpha"].isin(selected_alphas)
    ].copy()

    result = table.pivot(
        index=[
            "scenario_label",
            "expected_evaluated_candidates",
            "maximum_candidate_count",
        ],
        columns="local_alpha",
        values="exact_tess",
    ).reset_index()

    result.columns = [
        (
            f"TESS_alpha_{column:g}"
            if isinstance(column, float)
            else str(column)
        )
        for column in result.columns
    ]
    return result


def plot_policy_gap(order: pd.DataFrame, output_dir: Path) -> None:
    ordered = order.sort_values("local_alpha", ascending=False)

    fig, ax = plt.subplots(figsize=(8.6, 5.5))
    ax.plot(
        ordered["local_alpha"],
        ordered["rescue_minus_promising"],
        marker="o",
        label="Rescue minus promising",
    )
    ax.plot(
        ordered["local_alpha"],
        ordered["random_minus_promising"],
        marker="o",
        label="Random minus promising",
    )
    ax.plot(
        ordered["local_alpha"],
        ordered["rescue_minus_random"],
        marker="o",
        label="Rescue minus random",
    )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("TESS difference")
    ax.set_title("Activation-policy effect on inferential search size")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "adaptive_policy_tess_differences.png", dpi=220)
    fig.savefig(output_dir / "adaptive_policy_tess_differences.svg")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--base-k", type=int, default=5)
    parser.add_argument("--extra-k", type=int, default=15)
    parser.add_argument("--expansion-probability", type=float, default=0.5)
    parser.add_argument(
        "--alphas",
        default="0.5,0.3,0.2,0.15,0.13,0.12944944,0.12,0.1,0.05,0.025,0.01,0.005,0.001,0.0001,0.000001",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "simulations/ess/outputs/adaptive_branching_proposition"
        ),
    )
    args = parser.parse_args()

    alphas = tuple(
        float(value.strip())
        for value in args.alphas.split(",")
        if value.strip()
    )

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = args.repo_root.resolve() / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    data = build_exact_grid(
        alphas,
        args.base_k,
        args.extra_k,
        args.expansion_probability,
    )

    order = verify_order(data)
    gaps = verify_equal_nonrejection_gaps(data)
    manuscript = make_manuscript_table(data)

    data.to_csv(
        output_dir / "adaptive_branching_proposition_exact_grid.csv",
        index=False,
    )
    order.to_csv(
        output_dir / "adaptive_branching_proposition_order_check.csv",
        index=False,
    )
    gaps.to_csv(
        output_dir / "adaptive_branching_equal_Q_gap_check.csv",
        index=False,
    )
    manuscript.to_csv(
        output_dir / "adaptive_branching_manuscript_table.csv",
        index=False,
    )
    plot_policy_gap(order, output_dir)

    tau = trigger_threshold(args.base_k, args.expansion_probability)
    max_gap_error = float(np.max(np.abs(gaps["gap_difference"])))

    if not bool(order["strict_order_verified"].all()):
        failed = order[~order["strict_order_verified"]]
        raise RuntimeError(
            "Strict TESS ordering failed:\n"
            + failed.to_string(index=False)
        )

    print("Adaptive-branching proposition verification complete")
    print(f"Output directory: {output_dir}")
    print(f"Trigger threshold: {tau:.10f}")
    print(f"Alpha values checked: {len(order)}")
    print("Strict ordering verified at every checked alpha: YES")
    print(
        "Maximum absolute difference between the two exact "
        f"non-rejection gaps: {max_gap_error:.3e}"
    )
    print("\nSelected manuscript table:")
    print(manuscript.to_string(index=False))


if __name__ == "__main__":
    main()
