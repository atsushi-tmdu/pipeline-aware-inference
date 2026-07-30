#!/usr/bin/env python3
"""Exact and Monte Carlo TESS for adaptive branching search rules."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005, 0.001)


def parse_csv_numbers(text: str, cast=float) -> tuple:
    values = tuple(cast(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one value is required.")
    return values


def survival_min_uniform(alpha: float, k: int) -> float:
    return (1.0 - alpha) ** k


def tess_from_nonrejection(q: float, alpha: float) -> float:
    if not (0.0 < q <= 1.0):
        raise ValueError(f"nonrejection probability must be in (0,1], got {q}")
    return math.log(q) / math.log1p(-alpha)


def trigger_threshold(base_k: int, expansion_probability: float) -> float:
    """Threshold tau with P(min base p <= tau) = expansion_probability."""
    if base_k < 1:
        raise ValueError("base_k must be >= 1")
    if not (0.0 < expansion_probability < 1.0):
        raise ValueError("expansion_probability must be in (0,1)")
    return 1.0 - (1.0 - expansion_probability) ** (1.0 / base_k)


def exact_nonrejection(
    scenario: str,
    alpha: float,
    base_k: int,
    extra_k: int,
    tau: float,
    random_expansion_probability: float,
) -> float:
    s0 = survival_min_uniform(alpha, base_k)
    s1 = survival_min_uniform(alpha, extra_k)
    s_tau = survival_min_uniform(tau, base_k)

    if scenario == "fixed_base":
        return s0
    if scenario == "fixed_full":
        return s0 * s1
    if scenario == "random_expansion":
        r = random_expansion_probability
        return s0 * ((1.0 - r) + r * s1)
    if scenario == "promising_triggered":
        if alpha <= tau:
            return s_tau + (s0 - s_tau) * s1
        return s0
    if scenario == "rescue_triggered":
        if alpha <= tau:
            return (s0 - s_tau) + s_tau * s1
        return s0 * s1
    raise ValueError(f"Unknown scenario: {scenario}")


def expected_candidates(
    scenario: str,
    base_k: int,
    extra_k: int,
    tau: float,
    random_expansion_probability: float,
) -> float:
    base_trigger_probability = 1.0 - survival_min_uniform(tau, base_k)
    if scenario == "fixed_base":
        return float(base_k)
    if scenario == "fixed_full":
        return float(base_k + extra_k)
    if scenario == "random_expansion":
        return float(base_k + extra_k * random_expansion_probability)
    if scenario == "promising_triggered":
        return float(base_k + extra_k * base_trigger_probability)
    if scenario == "rescue_triggered":
        return float(base_k + extra_k * (1.0 - base_trigger_probability))
    raise ValueError(f"Unknown scenario: {scenario}")


def build_exact_grid(
    alphas: Iterable[float],
    base_k: int,
    extra_k: int,
    expansion_probability: float,
) -> pd.DataFrame:
    tau = trigger_threshold(base_k, expansion_probability)
    scenarios = (
        "fixed_base",
        "fixed_full",
        "random_expansion",
        "promising_triggered",
        "rescue_triggered",
    )
    labels = {
        "fixed_base": "Fixed base only",
        "fixed_full": "Fixed full search",
        "random_expansion": "Random expansion",
        "promising_triggered": "Expand when promising",
        "rescue_triggered": "Expand for rescue",
    }

    rows = []
    for scenario in scenarios:
        exp_k = expected_candidates(
            scenario,
            base_k,
            extra_k,
            tau,
            expansion_probability,
        )
        for alpha in alphas:
            q = exact_nonrejection(
                scenario,
                alpha,
                base_k,
                extra_k,
                tau,
                expansion_probability,
            )
            rows.append(
                {
                    "scenario": scenario,
                    "scenario_label": labels[scenario],
                    "local_alpha": float(alpha),
                    "base_candidate_count": base_k,
                    "extra_candidate_count": extra_k,
                    "maximum_candidate_count": base_k + extra_k,
                    "trigger_threshold": tau,
                    "expansion_probability": expansion_probability,
                    "expected_evaluated_candidates": exp_k,
                    "exact_nonrejection_probability": q,
                    "exact_rejection_probability": 1.0 - q,
                    "exact_tess": tess_from_nonrejection(q, alpha),
                    "tess_minus_expected_candidates": (
                        tess_from_nonrejection(q, alpha) - exp_k
                    ),
                }
            )
    return pd.DataFrame(rows)


def monte_carlo_counts(
    alphas: tuple[float, ...],
    repetitions: int,
    base_k: int,
    extra_k: int,
    tau: float,
    expansion_probability: float,
    seed: int,
    chunk_size: int,
) -> dict[str, np.ndarray]:
    scenarios = (
        "fixed_base",
        "fixed_full",
        "random_expansion",
        "promising_triggered",
        "rescue_triggered",
    )
    counts = {scenario: np.zeros(len(alphas), dtype=np.int64) for scenario in scenarios}
    rng = np.random.default_rng(seed)

    done = 0
    while done < repetitions:
        n = min(chunk_size, repetitions - done)
        base_min = rng.random((n, base_k)).min(axis=1)
        extra_min = rng.random((n, extra_k)).min(axis=1)
        random_expand = rng.random(n) < expansion_probability
        promising_expand = base_min <= tau
        rescue_expand = base_min > tau

        final = {
            "fixed_base": base_min,
            "fixed_full": np.minimum(base_min, extra_min),
            "random_expansion": np.where(
                random_expand, np.minimum(base_min, extra_min), base_min
            ),
            "promising_triggered": np.where(
                promising_expand, np.minimum(base_min, extra_min), base_min
            ),
            "rescue_triggered": np.where(
                rescue_expand, np.minimum(base_min, extra_min), base_min
            ),
        }

        for scenario, values in final.items():
            for idx, alpha in enumerate(alphas):
                counts[scenario][idx] += int(np.count_nonzero(values < alpha))
        done += n
    return counts


def add_monte_carlo(
    exact: pd.DataFrame,
    alphas: tuple[float, ...],
    repetitions: int,
    base_k: int,
    extra_k: int,
    expansion_probability: float,
    seed: int,
    chunk_size: int,
) -> pd.DataFrame:
    tau = trigger_threshold(base_k, expansion_probability)
    counts = monte_carlo_counts(
        alphas,
        repetitions,
        base_k,
        extra_k,
        tau,
        expansion_probability,
        seed,
        chunk_size,
    )

    rows = []
    for scenario, scenario_counts in counts.items():
        for alpha, reject_count in zip(alphas, scenario_counts):
            p = reject_count / repetitions
            q = 1.0 - p
            rows.append(
                {
                    "scenario": scenario,
                    "local_alpha": alpha,
                    "monte_carlo_repetitions": repetitions,
                    "monte_carlo_rejections": int(reject_count),
                    "monte_carlo_rejection_probability": p,
                    "monte_carlo_tess": tess_from_nonrejection(q, alpha),
                }
            )
    mc = pd.DataFrame(rows)
    merged = exact.merge(
        mc,
        on=["scenario", "local_alpha"],
        how="left",
        validate="one_to_one",
    )
    merged["monte_carlo_minus_exact_tess"] = (
        merged["monte_carlo_tess"] - merged["exact_tess"]
    )
    merged["absolute_tess_error"] = merged["monte_carlo_minus_exact_tess"].abs()
    return merged


def plot_curves(data: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for _, subset in data.groupby("scenario", sort=False):
        ordered = subset.sort_values("local_alpha", ascending=False)
        ax.plot(
            ordered["local_alpha"],
            ordered["exact_tess"],
            marker="o",
            label=ordered["scenario_label"].iloc[0],
        )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Exact TESS")
    ax.set_title("Adaptive activation rules change effective search size")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "adaptive_branching_tess_curves.png", dpi=220)
    fig.savefig(output_dir / "adaptive_branching_tess_curves.svg")
    plt.close(fig)

    adaptive = data[
        data["scenario"].isin(
            ["random_expansion", "promising_triggered", "rescue_triggered"]
        )
    ]
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for _, subset in adaptive.groupby("scenario", sort=False):
        ordered = subset.sort_values("local_alpha", ascending=False)
        ax.plot(
            ordered["local_alpha"],
            ordered["exact_tess"],
            marker="o",
            label=ordered["scenario_label"].iloc[0],
        )
    expected_k = float(adaptive["expected_evaluated_candidates"].iloc[0])
    ax.axhline(
        expected_k,
        linestyle="--",
        linewidth=1,
        label=f"Same expected evaluated candidates = {expected_k:g}",
    )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Exact TESS")
    ax.set_title(
        "Same maximum K and expected K, different TESS\n"
        "Only the data-dependent activation rule changes"
    )
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "adaptive_rules_same_expected_K.png", dpi=220)
    fig.savefig(output_dir / "adaptive_rules_same_expected_K.svg")
    plt.close(fig)


def write_summary(data: pd.DataFrame, output_path: Path) -> None:
    lines = [
        "# Adaptive branching TESS summary",
        "",
        "The three adaptive rules have the same maximum candidate count and the same expected evaluated candidate count.",
        "They differ only in which data states activate the extra candidates.",
        "",
    ]
    selected = data[data["local_alpha"].isin([0.2, 0.1, 0.05, 0.01, 0.001])]
    pivot = selected.pivot(
        index="scenario_label",
        columns="local_alpha",
        values="exact_tess",
    )
    lines.extend(["```text", pivot.round(4).to_string(), "```", ""])

    metadata = (
        data[
            [
                "scenario_label",
                "maximum_candidate_count",
                "expected_evaluated_candidates",
                "trigger_threshold",
            ]
        ]
        .drop_duplicates()
        .sort_values("scenario_label")
    )
    lines.extend(["```text", metadata.to_string(index=False), "```", ""])

    alpha_point = 0.1
    point = data[np.isclose(data["local_alpha"], alpha_point)]
    lines.append(f"At alpha={alpha_point}:")
    lines.append("```text")
    lines.append(
        point[
            [
                "scenario_label",
                "expected_evaluated_candidates",
                "exact_tess",
            ]
        ].sort_values("exact_tess").to_string(index=False)
    )
    lines.append("```")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--alphas", default=",".join(str(x) for x in DEFAULT_ALPHAS)
    )
    parser.add_argument("--base-k", type=int, default=5)
    parser.add_argument("--extra-k", type=int, default=15)
    parser.add_argument("--expansion-probability", type=float, default=0.5)
    parser.add_argument("--repetitions", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument("--chunk-size", type=int, default=100_000)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("simulations/ess/outputs/adaptive_branching"),
    )
    args = parser.parse_args()

    alphas = parse_csv_numbers(args.alphas, float)
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = args.repo_root.resolve() / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    exact = build_exact_grid(
        alphas,
        args.base_k,
        args.extra_k,
        args.expansion_probability,
    )
    result = add_monte_carlo(
        exact,
        alphas,
        args.repetitions,
        args.base_k,
        args.extra_k,
        args.expansion_probability,
        args.seed,
        args.chunk_size,
    )
    result.to_csv(output_dir / "adaptive_branching_tess.csv", index=False)
    plot_curves(result, output_dir)
    write_summary(result, output_dir / "ADAPTIVE_BRANCHING_SUMMARY.md")

    tau = trigger_threshold(args.base_k, args.expansion_probability)
    print("Adaptive branching TESS analysis complete")
    print(f"Output directory: {output_dir}")
    print(f"Trigger threshold: {tau:.8f}")
    print(
        "Maximum absolute Monte Carlo-minus-exact TESS error: "
        f"{result['absolute_tess_error'].max():.6f}"
    )
    print("\nAdaptive rules at alpha=0.10:")
    print(
        result[
            result["scenario"].isin(
                ["random_expansion", "promising_triggered", "rescue_triggered"]
            )
            & np.isclose(result["local_alpha"], 0.10)
        ][
            [
                "scenario_label",
                "expected_evaluated_candidates",
                "exact_tess",
                "monte_carlo_tess",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
