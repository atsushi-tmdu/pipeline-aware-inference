#!/usr/bin/env python3
"""Budget-standardized adaptive-policy effects and fixed-policy reconstruction audit."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005)


def parse_alphas(text: str) -> tuple[float, ...]:
    values = tuple(float(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one alpha is required.")
    return values


def tess(pi: float, alpha: float) -> float:
    if not (0.0 <= pi < 1.0):
        raise ValueError(f"pi must be in [0,1), got {pi}")
    return math.log1p(-pi) / math.log1p(-alpha)


def load_policy_bank(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    bank = pd.read_csv(path)
    required = {
        "replication",
        "policy",
        "expanded",
        "winner_model",
        "winner_selection_roc_auc",
        "naive_empirical_p_value",
    }
    missing = required.difference(bank.columns)
    if missing:
        raise ValueError(f"Policy bank missing columns: {sorted(missing)}")

    pvalues = bank.pivot(
        index="replication",
        columns="policy",
        values="naive_empirical_p_value",
    )
    promising = (
        bank[bank["policy"] == "promising_triggered"]
        .drop_duplicates("replication")
        .set_index("replication")
        .reindex(pvalues.index)
    )
    state = pd.DataFrame(
        {
            "activation": promising["expanded"].astype(bool),
        },
        index=pvalues.index,
    )
    return bank, pd.concat([pvalues, state], axis=1)


def point_effects(
    joined: pd.DataFrame,
    alphas: tuple[float, ...],
    library: str,
) -> pd.DataFrame:
    p_base = joined["fixed_base"].to_numpy(float)
    p_full = joined["fixed_full"].to_numpy(float)
    p_prom = joined["promising_triggered"].to_numpy(float)
    p_rescue = joined["rescue_triggered"].to_numpy(float)
    activation = joined["activation"].to_numpy(bool).astype(float)
    r = float(activation.mean())

    rows = []
    for alpha in alphas:
        r0 = (p_base < alpha).astype(float)
        r1 = (p_full < alpha).astype(float)
        d = r1 - r0

        pi_base = float(r0.mean())
        pi_full = float(r1.mean())
        pi_prom = float(np.mean(p_prom < alpha))
        pi_rescue = float(np.mean(p_rescue < alpha))
        e_d = float(d.mean())
        cov = float(np.mean(activation * d) - r * e_d)

        pi_random_prom_budget = pi_base + r * e_d
        pi_random_rescue_budget = pi_base + (1.0 - r) * e_d

        gain = d == 1
        loss = d == -1
        gain_total = int(gain.sum())
        loss_total = int(loss.sum())

        rows.append(
            {
                "library": library,
                "local_alpha": alpha,
                "n": len(d),
                "promising_activation_rate": r,
                "rescue_activation_rate": 1.0 - r,
                "pi_base": pi_base,
                "pi_full": pi_full,
                "pi_promising": pi_prom,
                "pi_rescue": pi_rescue,
                "pi_random_matched_promising_budget": pi_random_prom_budget,
                "pi_random_matched_rescue_budget": pi_random_rescue_budget,
                "cov_activation_increment": cov,
                "pi_promising_minus_matched_random": (
                    pi_prom - pi_random_prom_budget
                ),
                "pi_rescue_minus_matched_random": (
                    pi_rescue - pi_random_rescue_budget
                ),
                "tess_promising": tess(pi_prom, alpha),
                "tess_rescue": tess(pi_rescue, alpha),
                "tess_random_matched_promising_budget": tess(
                    pi_random_prom_budget, alpha
                ),
                "tess_random_matched_rescue_budget": tess(
                    pi_random_rescue_budget, alpha
                ),
                "tess_promising_minus_matched_random": (
                    tess(pi_prom, alpha)
                    - tess(pi_random_prom_budget, alpha)
                ),
                "tess_rescue_minus_matched_random": (
                    tess(pi_rescue, alpha)
                    - tess(pi_random_rescue_budget, alpha)
                ),
                "incremental_gain_count": gain_total,
                "incremental_loss_count": loss_total,
                "gain_count_activated_promising": int(
                    np.sum(gain & (activation == 1))
                ),
                "gain_count_allocated_rescue": int(
                    np.sum(gain & (activation == 0))
                ),
                "loss_count_activated_promising": int(
                    np.sum(loss & (activation == 1))
                ),
                "loss_count_allocated_rescue": int(
                    np.sum(loss & (activation == 0))
                ),
                "promising_gain_capture_fraction": (
                    float(np.sum(gain & (activation == 1)) / gain_total)
                    if gain_total > 0
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_effects(
    joined: pd.DataFrame,
    alphas: tuple[float, ...],
    library: str,
    repetitions: int,
    seed: int,
    chunk_size: int = 1000,
) -> pd.DataFrame:
    p_base = joined["fixed_base"].to_numpy(float)
    p_full = joined["fixed_full"].to_numpy(float)
    p_prom = joined["promising_triggered"].to_numpy(float)
    p_rescue = joined["rescue_triggered"].to_numpy(float)
    activation = joined["activation"].to_numpy(bool).astype(float)
    n = len(activation)

    values = np.empty((repetitions, len(alphas), 4), dtype=float)
    rng = np.random.default_rng(seed)
    done = 0

    while done < repetitions:
        b = min(chunk_size, repetitions - done)
        idx = rng.integers(0, n, size=(b, n))

        a = activation[idx]
        mean_a = a.mean(axis=1)

        for alpha_idx, alpha in enumerate(alphas):
            r0 = (p_base < alpha).astype(float)[idx]
            r1 = (p_full < alpha).astype(float)[idx]
            d = r1 - r0
            prom = (p_prom < alpha).astype(float)[idx]
            rescue = (p_rescue < alpha).astype(float)[idx]

            pi_base = r0.mean(axis=1)
            e_d = d.mean(axis=1)
            pi_prom = prom.mean(axis=1)
            pi_rescue = rescue.mean(axis=1)

            pi_rand_prom = pi_base + mean_a * e_d
            pi_rand_rescue = pi_base + (1.0 - mean_a) * e_d

            for local in range(b):
                values[done + local, alpha_idx, 0] = (
                    pi_prom[local] - pi_rand_prom[local]
                )
                values[done + local, alpha_idx, 1] = (
                    pi_rescue[local] - pi_rand_rescue[local]
                )
                values[done + local, alpha_idx, 2] = (
                    tess(float(pi_prom[local]), alpha)
                    - tess(float(pi_rand_prom[local]), alpha)
                )
                values[done + local, alpha_idx, 3] = (
                    tess(float(pi_rescue[local]), alpha)
                    - tess(float(pi_rand_rescue[local]), alpha)
                )
        done += b

    metric_names = (
        "pi_promising_minus_matched_random",
        "pi_rescue_minus_matched_random",
        "tess_promising_minus_matched_random",
        "tess_rescue_minus_matched_random",
    )
    rows = []
    for alpha_idx, alpha in enumerate(alphas):
        for metric_idx, metric in enumerate(metric_names):
            sample = values[:, alpha_idx, metric_idx]
            rows.append(
                {
                    "library": library,
                    "local_alpha": alpha,
                    "metric": metric,
                    "bootstrap_mean": float(sample.mean()),
                    "bootstrap_se": float(sample.std(ddof=1)),
                    "ci_low_95": float(np.quantile(sample, 0.025)),
                    "ci_high_95": float(np.quantile(sample, 0.975)),
                    "bootstrap_probability_gt_zero": float(
                        np.mean(sample > 0)
                    ),
                    "bootstrap_probability_lt_zero": float(
                        np.mean(sample < 0)
                    ),
                    "bootstrap_repetitions": repetitions,
                }
            )
    return pd.DataFrame(rows)


def filter_existing(
    frame: pd.DataFrame,
    pool_size: int,
    event_count: int,
) -> pd.DataFrame:
    result = frame.copy()
    if "target_auc" in result.columns:
        result = result[np.isclose(result["target_auc"].astype(float), 0.5)]
    if "feature_selection" in result.columns:
        result = result[result["feature_selection"].astype(str) == "none"]
    if "selection_event_count" in result.columns:
        result = result[
            result["selection_event_count"].astype(int) == event_count
        ]
    if "metric" in result.columns:
        result = result[result["metric"].astype(str) == "roc_auc"]
    result = result[
        (result["method"].astype(str) == "naive_empirical")
        & (result["pool_size"].astype(int) == pool_size)
    ]
    return result.copy()


def reconstruction_audit(
    bank: pd.DataFrame,
    existing_path: Path,
    alphas: tuple[float, ...],
    library: str,
    event_count: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    existing = pd.read_csv(existing_path)
    summary_rows = []
    mismatch_rows = []

    for policy, pool_size in (("fixed_base", 7), ("fixed_full", 20)):
        old = filter_existing(existing, pool_size, event_count)
        old = old[
            [
                "replication",
                "best_model",
                "best_selection_metric",
                "p_value",
            ]
        ].copy()

        new = bank[bank["policy"] == policy][
            [
                "replication",
                "winner_model",
                "winner_selection_roc_auc",
                "naive_empirical_p_value",
            ]
        ].copy()

        merged = old.merge(new, on="replication", how="inner")
        merged["model_match"] = (
            merged["best_model"].astype(str)
            == merged["winner_model"].astype(str)
        )
        merged["score_abs_diff"] = (
            merged["best_selection_metric"]
            - merged["winner_selection_roc_auc"]
        ).abs()
        merged["p_abs_diff"] = (
            merged["p_value"] - merged["naive_empirical_p_value"]
        ).abs()

        decision_mismatch_total = 0
        decision_columns = []
        for alpha in alphas:
            column = f"decision_mismatch_alpha_{alpha:g}"
            merged[column] = (
                (merged["p_value"] < alpha)
                != (merged["naive_empirical_p_value"] < alpha)
            )
            decision_mismatch_total += int(merged[column].sum())
            decision_columns.append(column)

        summary_rows.append(
            {
                "library": library,
                "policy": policy,
                "pool_size": pool_size,
                "rows_compared": len(merged),
                "model_mismatch_count": int((~merged["model_match"]).sum()),
                "score_difference_count_gt_1e12": int(
                    np.sum(merged["score_abs_diff"] > 1e-12)
                ),
                "p_difference_count_gt_1e12": int(
                    np.sum(merged["p_abs_diff"] > 1e-12)
                ),
                "p_difference_count_gt_1e4": int(
                    np.sum(merged["p_abs_diff"] > 1e-4)
                ),
                "maximum_absolute_p_value_difference": float(
                    merged["p_abs_diff"].max()
                ),
                "mean_absolute_p_value_difference": float(
                    merged["p_abs_diff"].mean()
                ),
                "decision_mismatch_count_across_all_alphas": (
                    decision_mismatch_total
                ),
            }
        )

        mismatches = merged[
            (~merged["model_match"])
            | (merged["p_abs_diff"] > 1e-12)
            | (merged["score_abs_diff"] > 1e-12)
            | merged[decision_columns].any(axis=1)
        ].copy()
        if not mismatches.empty:
            mismatches.insert(0, "library", library)
            mismatches.insert(1, "policy", policy)
            mismatch_rows.append(mismatches)

    summary = pd.DataFrame(summary_rows)
    details = (
        pd.concat(mismatch_rows, ignore_index=True)
        if mismatch_rows
        else pd.DataFrame()
    )
    return summary, details


def plot_standardized_effects(
    point: pd.DataFrame,
    boot: pd.DataFrame,
    output_dir: Path,
    library: str,
) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 5.5))

    for metric, label in (
        (
            "tess_promising_minus_matched_random",
            "Promising minus matched random",
        ),
        (
            "tess_rescue_minus_matched_random",
            "Rescue minus matched random",
        ),
    ):
        subset = boot[boot["metric"] == metric].copy()
        estimates = point[
            ["local_alpha", metric]
        ].rename(columns={metric: "estimate"})
        merged = estimates.merge(subset, on="local_alpha")
        merged = merged.sort_values("local_alpha", ascending=False)

        ax.plot(
            merged["local_alpha"],
            merged["estimate"],
            marker="o",
            label=label,
        )
        ax.fill_between(
            merged["local_alpha"],
            merged["ci_low_95"],
            merged["ci_high_95"],
            alpha=0.18,
        )

    ax.axhline(0.0, linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Budget-standardized TESS effect")
    ax.set_title(f"Adaptive allocation effect at matched search budget: {library}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        output_dir / "budget_standardized_policy_effects.png",
        dpi=220,
    )
    fig.savefig(
        output_dir / "budget_standardized_policy_effects.svg"
    )
    plt.close(fig)


def analyze_library(
    bank_path: Path,
    existing_path: Path,
    library: str,
    output_root: Path,
    alphas: tuple[float, ...],
    event_count: int,
    bootstrap_repetitions: int,
    seed: int,
) -> dict[str, pd.DataFrame]:
    bank, joined = load_policy_bank(bank_path)
    point = point_effects(joined, alphas, library)
    boot = bootstrap_effects(
        joined,
        alphas,
        library,
        bootstrap_repetitions,
        seed,
    )
    audit, audit_details = reconstruction_audit(
        bank,
        existing_path,
        alphas,
        library,
        event_count,
    )

    output_dir = output_root / library
    output_dir.mkdir(parents=True, exist_ok=True)

    point.to_csv(
        output_dir / "budget_standardized_policy_effects.csv",
        index=False,
    )
    boot.to_csv(
        output_dir / "budget_standardized_policy_effects_bootstrap.csv",
        index=False,
    )
    audit.to_csv(
        output_dir / "fixed_policy_reconstruction_audit.csv",
        index=False,
    )
    audit_details.to_csv(
        output_dir / "fixed_policy_reconstruction_mismatch_details.csv",
        index=False,
    )
    plot_standardized_effects(point, boot, output_dir, library)

    return {
        "point": point,
        "boot": boot,
        "audit": audit,
        "audit_details": audit_details,
    }


def write_summary(
    results: dict[str, dict[str, pd.DataFrame]],
    output_root: Path,
    alpha: float,
) -> None:
    point = pd.concat(
        [result["point"] for result in results.values()],
        ignore_index=True,
    )
    boot = pd.concat(
        [result["boot"] for result in results.values()],
        ignore_index=True,
    )
    audit = pd.concat(
        [result["audit"] for result in results.values()],
        ignore_index=True,
    )

    point.to_csv(
        output_root / "budget_standardized_policy_effects_all_libraries.csv",
        index=False,
    )
    boot.to_csv(
        output_root / "budget_standardized_policy_effects_bootstrap_all_libraries.csv",
        index=False,
    )
    audit.to_csv(
        output_root / "fixed_policy_reconstruction_audit_all_libraries.csv",
        index=False,
    )

    selected = point[np.isclose(point["local_alpha"], alpha)]
    selected_boot = boot[
        np.isclose(boot["local_alpha"], alpha)
        & boot["metric"].isin(
            [
                "tess_promising_minus_matched_random",
                "tess_rescue_minus_matched_random",
            ]
        )
    ]

    lines = [
        "# Budget-standardized policy effect summary",
        "",
        f"## Point estimates at alpha={alpha}",
        "",
        "```text",
        selected.to_string(index=False),
        "```",
        "",
        "## Bootstrap TESS effects",
        "",
        "```text",
        selected_boot.to_string(index=False),
        "```",
        "",
        "## Fixed-policy reconstruction audit",
        "",
        "```text",
        audit.to_string(index=False),
        "```",
    ]
    (output_root / "BUDGET_STANDARDIZED_POLICY_AUDIT_SUMMARY.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--policy-root",
        type=Path,
        default=Path(
            "simulations/ess/outputs/phase3c_adaptive_ml_policy"
        ),
    )
    parser.add_argument(
        "--high-dependency-run-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--mixed-realistic-run-dir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--alphas",
        default=",".join(str(x) for x in DEFAULT_ALPHAS),
    )
    parser.add_argument("--event-count", type=int, default=100)
    parser.add_argument("--bootstrap-repetitions", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "simulations/ess/outputs/budget_standardized_policy_audit"
        ),
    )
    args = parser.parse_args()

    alphas = parse_alphas(args.alphas)

    policy_root = args.policy_root
    if not policy_root.is_absolute():
        policy_root = args.repo_root.resolve() / policy_root

    output_root = args.output_dir
    if not output_root.is_absolute():
        output_root = args.repo_root.resolve() / output_root
    output_root.mkdir(parents=True, exist_ok=True)

    run_dirs = {
        "high_dependency_linear_20": (
            args.high_dependency_run_dir.expanduser().resolve()
        ),
        "mixed_realistic_20": (
            args.mixed_realistic_run_dir.expanduser().resolve()
        ),
    }

    results = {}
    for index, (library, run_dir) in enumerate(run_dirs.items()):
        bank_path = (
            policy_root
            / library
            / "adaptive_ml_policy_replication_bank.csv"
        )
        existing_path = run_dir / "independent_inference_results.csv"

        if not bank_path.exists():
            raise FileNotFoundError(f"Policy bank not found: {bank_path}")
        if not existing_path.exists():
            raise FileNotFoundError(
                f"Original inference results not found: {existing_path}"
            )

        results[library] = analyze_library(
            bank_path,
            existing_path,
            library,
            output_root,
            alphas,
            args.event_count,
            args.bootstrap_repetitions,
            args.seed + index * 1000,
        )

    write_summary(results, output_root, alpha=0.05)

    print("Budget-standardized policy analysis and reconstruction audit complete")
    print(f"Output directory: {output_root}")

    for library, result in results.items():
        selected = result["point"][
            np.isclose(result["point"]["local_alpha"], 0.05)
        ]
        selected_boot = result["boot"][
            np.isclose(result["boot"]["local_alpha"], 0.05)
            & result["boot"]["metric"].isin(
                [
                    "tess_promising_minus_matched_random",
                    "tess_rescue_minus_matched_random",
                ]
            )
        ]
        print(f"\n=== {library}, alpha=0.05 ===")
        print(
            selected[
                [
                    "promising_activation_rate",
                    "rescue_activation_rate",
                    "tess_promising",
                    "tess_random_matched_promising_budget",
                    "tess_promising_minus_matched_random",
                    "tess_rescue",
                    "tess_random_matched_rescue_budget",
                    "tess_rescue_minus_matched_random",
                    "incremental_gain_count",
                    "promising_gain_capture_fraction",
                ]
            ].to_string(index=False)
        )
        print("\nBootstrap standardized TESS effects:")
        print(selected_boot.to_string(index=False))
        print("\nReconstruction audit:")
        print(result["audit"].to_string(index=False))


if __name__ == "__main__":
    main()
