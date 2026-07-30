#!/usr/bin/env python3
"""Mechanism decomposition for adaptive Phase 3C search policies."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005)


def parse_csv_numbers(text: str) -> tuple[float, ...]:
    values = tuple(float(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one alpha is required.")
    return values


def tess(pi: float, alpha: float) -> float:
    return math.log1p(-pi) / math.log1p(-alpha)


def load_policy_pivot(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    bank = pd.read_csv(path)
    required = {
        "replication",
        "policy",
        "expanded",
        "base_stage_max_selection_roc_auc",
        "naive_empirical_p_value",
    }
    missing = required.difference(bank.columns)
    if missing:
        raise ValueError(f"Bank missing columns: {sorted(missing)}")

    pivot = bank.pivot(
        index="replication",
        columns="policy",
        values="naive_empirical_p_value",
    )

    promising = bank[bank["policy"] == "promising_triggered"].copy()
    promising = promising.set_index("replication").reindex(pivot.index)

    state = pd.DataFrame(
        {
            "promising_activation": promising["expanded"].astype(bool),
            "base_stage_score": promising[
                "base_stage_max_selection_roc_auc"
            ].astype(float),
        },
        index=pivot.index,
    )
    return pivot, state


def mechanism_table(
    pivot: pd.DataFrame,
    state: pd.DataFrame,
    alphas: tuple[float, ...],
    library: str,
) -> pd.DataFrame:
    rows = []
    p_base = pivot["fixed_base"].to_numpy(float)
    p_full = pivot["fixed_full"].to_numpy(float)
    p_prom = pivot["promising_triggered"].to_numpy(float)
    p_rescue = pivot["rescue_triggered"].to_numpy(float)
    p_random = pivot["random_expansion"].to_numpy(float)
    activation = state["promising_activation"].to_numpy(bool).astype(float)

    r = float(activation.mean())

    for alpha in alphas:
        r0 = (p_base < alpha).astype(float)
        r1 = (p_full < alpha).astype(float)
        d = r1 - r0

        observed = {
            "base": float(np.mean(p_base < alpha)),
            "full": float(np.mean(p_full < alpha)),
            "promising": float(np.mean(p_prom < alpha)),
            "rescue": float(np.mean(p_rescue < alpha)),
            "random": float(np.mean(p_random < alpha)),
        }

        e_d = float(d.mean())
        e_ad = float(np.mean(activation * d))
        covariance = float(e_ad - r * e_d)
        e_d_a1 = float(d[activation == 1].mean())
        e_d_a0 = float(d[activation == 0].mean())

        predicted_promising = observed["base"] + e_ad
        predicted_rescue = observed["base"] + e_d - e_ad
        predicted_random_population = observed["base"] + r * e_d

        gain = d == 1
        loss = d == -1

        rows.append(
            {
                "library": library,
                "local_alpha": alpha,
                "n": len(d),
                "promising_activation_rate": r,
                "pi_base": observed["base"],
                "pi_full": observed["full"],
                "pi_promising_observed": observed["promising"],
                "pi_random_observed": observed["random"],
                "pi_rescue_observed": observed["rescue"],
                "mean_incremental_effect_E_D": e_d,
                "mean_activated_increment_E_AD": e_ad,
                "cov_activation_increment": covariance,
                "mean_D_given_promising": e_d_a1,
                "mean_D_given_rescue": e_d_a0,
                "gain_count_total": int(gain.sum()),
                "loss_count_total": int(loss.sum()),
                "gain_count_promising": int(np.sum(gain & (activation == 1))),
                "gain_count_rescue": int(np.sum(gain & (activation == 0))),
                "loss_count_promising": int(np.sum(loss & (activation == 1))),
                "loss_count_rescue": int(np.sum(loss & (activation == 0))),
                "pi_promising_from_identity": predicted_promising,
                "pi_rescue_from_identity": predicted_rescue,
                "pi_random_population_benchmark": predicted_random_population,
                "promising_identity_error": (
                    observed["promising"] - predicted_promising
                ),
                "rescue_identity_error": (
                    observed["rescue"] - predicted_rescue
                ),
                "tess_base": tess(observed["base"], alpha),
                "tess_full": tess(observed["full"], alpha),
                "tess_promising": tess(observed["promising"], alpha),
                "tess_random": tess(observed["random"], alpha),
                "tess_rescue": tess(observed["rescue"], alpha),
            }
        )
    return pd.DataFrame(rows)


def score_bin_table(
    pivot: pd.DataFrame,
    state: pd.DataFrame,
    alpha: float,
    library: str,
    bins: int = 10,
) -> pd.DataFrame:
    p_base = pivot["fixed_base"].to_numpy(float)
    p_full = pivot["fixed_full"].to_numpy(float)
    r0 = (p_base < alpha).astype(int)
    r1 = (p_full < alpha).astype(int)
    d = r1 - r0

    frame = pd.DataFrame(
        {
            "base_stage_score": state["base_stage_score"].to_numpy(float),
            "promising_activation": state[
                "promising_activation"
            ].to_numpy(bool),
            "base_reject": r0,
            "full_reject": r1,
            "incremental_effect": d,
        }
    )

    frame["score_bin"] = pd.qcut(
        frame["base_stage_score"],
        q=bins,
        duplicates="drop",
    )

    summary = (
        frame.groupby("score_bin", observed=True)
        .agg(
            n=("incremental_effect", "size"),
            score_min=("base_stage_score", "min"),
            score_max=("base_stage_score", "max"),
            score_mean=("base_stage_score", "mean"),
            promising_rate=("promising_activation", "mean"),
            base_rejection_rate=("base_reject", "mean"),
            full_rejection_rate=("full_reject", "mean"),
            incremental_gain_rate=(
                "incremental_effect",
                lambda x: float(np.mean(np.asarray(x) == 1)),
            ),
            incremental_loss_rate=(
                "incremental_effect",
                lambda x: float(np.mean(np.asarray(x) == -1)),
            ),
            mean_incremental_effect=("incremental_effect", "mean"),
        )
        .reset_index()
    )
    summary.insert(0, "library", library)
    summary.insert(1, "local_alpha", alpha)
    summary["score_bin"] = summary["score_bin"].astype(str)
    return summary


def bootstrap_covariance(
    pivot: pd.DataFrame,
    state: pd.DataFrame,
    alphas: tuple[float, ...],
    library: str,
    repetitions: int,
    seed: int,
    chunk_size: int = 1000,
) -> pd.DataFrame:
    p_base = pivot["fixed_base"].to_numpy(float)
    p_full = pivot["fixed_full"].to_numpy(float)
    activation = state["promising_activation"].to_numpy(bool).astype(float)
    n = len(activation)

    d_matrix = np.column_stack(
        [
            (p_full < alpha).astype(float)
            - (p_base < alpha).astype(float)
            for alpha in alphas
        ]
    )

    point_r = activation.mean()
    point_cov = (
        (activation[:, None] * d_matrix).mean(axis=0)
        - point_r * d_matrix.mean(axis=0)
    )

    boot = np.empty((repetitions, len(alphas)), dtype=float)
    rng = np.random.default_rng(seed)
    done = 0

    while done < repetitions:
        b = min(chunk_size, repetitions - done)
        indices = rng.integers(0, n, size=(b, n))
        a = activation[indices]
        d = d_matrix[indices, :]
        mean_a = a.mean(axis=1)
        mean_d = d.mean(axis=1)
        mean_ad = (a[:, :, None] * d).mean(axis=1)
        boot[done : done + b, :] = mean_ad - mean_a[:, None] * mean_d
        done += b

    rows = []
    for idx, alpha in enumerate(alphas):
        values = boot[:, idx]
        rows.append(
            {
                "library": library,
                "local_alpha": alpha,
                "cov_activation_increment": float(point_cov[idx]),
                "bootstrap_mean": float(values.mean()),
                "bootstrap_se": float(values.std(ddof=1)),
                "ci_low_95": float(np.quantile(values, 0.025)),
                "ci_high_95": float(np.quantile(values, 0.975)),
                "bootstrap_probability_gt_zero": float(np.mean(values > 0)),
                "bootstrap_probability_lt_zero": float(np.mean(values < 0)),
                "bootstrap_repetitions": repetitions,
            }
        )
    return pd.DataFrame(rows)


def plot_covariance(
    covariance: pd.DataFrame,
    output_dir: Path,
    library: str,
) -> None:
    ordered = covariance.sort_values("local_alpha", ascending=False)
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    ax.plot(
        ordered["local_alpha"],
        ordered["cov_activation_increment"],
        marker="o",
    )
    ax.fill_between(
        ordered["local_alpha"],
        ordered["ci_low_95"],
        ordered["ci_high_95"],
        alpha=0.18,
    )
    ax.axhline(0.0, linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Cov(activation, incremental rejection effect)")
    ax.set_title(f"Why adaptive-policy ordering changes: {library}")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "activation_increment_covariance.png", dpi=220)
    fig.savefig(output_dir / "activation_increment_covariance.svg")
    plt.close(fig)


def plot_score_bins(
    bins: pd.DataFrame,
    output_dir: Path,
    library: str,
) -> None:
    ordered = bins.sort_values("score_mean")
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    ax.plot(
        ordered["score_mean"],
        ordered["incremental_gain_rate"],
        marker="o",
        label="Base nonreject → full reject",
    )
    ax.plot(
        ordered["score_mean"],
        ordered["incremental_loss_rate"],
        marker="o",
        label="Base reject → full nonreject",
    )
    ax.plot(
        ordered["score_mean"],
        ordered["mean_incremental_effect"],
        marker="o",
        label="Net incremental effect",
    )
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel("Mean base-stage maximum ROC AUC within decile")
    ax.set_ylabel("Conditional probability / mean effect")
    ax.set_title(f"Incremental rejection opportunity by base-stage score: {library}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "incremental_effect_by_base_score.png", dpi=220)
    fig.savefig(output_dir / "incremental_effect_by_base_score.svg")
    plt.close(fig)


def analyze_library(
    bank_path: Path,
    library: str,
    output_root: Path,
    alphas: tuple[float, ...],
    mechanism_alpha: float,
    bootstrap_repetitions: int,
    seed: int,
) -> dict[str, pd.DataFrame]:
    pivot, state = load_policy_pivot(bank_path)
    mechanism = mechanism_table(pivot, state, alphas, library)
    bins = score_bin_table(
        pivot,
        state,
        mechanism_alpha,
        library,
    )
    covariance = bootstrap_covariance(
        pivot,
        state,
        alphas,
        library,
        bootstrap_repetitions,
        seed,
    )

    output_dir = output_root / library
    output_dir.mkdir(parents=True, exist_ok=True)

    mechanism.to_csv(output_dir / "adaptive_policy_mechanism_decomposition.csv", index=False)
    bins.to_csv(output_dir / "incremental_effect_by_base_score.csv", index=False)
    covariance.to_csv(output_dir / "activation_increment_covariance_bootstrap.csv", index=False)

    plot_covariance(covariance, output_dir, library)
    plot_score_bins(bins, output_dir, library)

    return {
        "mechanism": mechanism,
        "bins": bins,
        "covariance": covariance,
    }


def write_summary(
    results: dict[str, dict[str, pd.DataFrame]],
    output_root: Path,
    alpha: float,
) -> None:
    mechanisms = pd.concat(
        [result["mechanism"] for result in results.values()],
        ignore_index=True,
    )
    covariances = pd.concat(
        [result["covariance"] for result in results.values()],
        ignore_index=True,
    )

    mechanisms.to_csv(
        output_root / "phase3c_policy_mechanism_all_libraries.csv",
        index=False,
    )
    covariances.to_csv(
        output_root / "phase3c_activation_increment_covariance_all_libraries.csv",
        index=False,
    )

    selected = mechanisms[np.isclose(mechanisms["local_alpha"], alpha)].copy()
    selected_cov = covariances[
        np.isclose(covariances["local_alpha"], alpha)
    ].copy()

    columns = [
        "library",
        "local_alpha",
        "pi_base",
        "pi_full",
        "pi_promising_observed",
        "pi_random_observed",
        "pi_rescue_observed",
        "mean_incremental_effect_E_D",
        "cov_activation_increment",
        "mean_D_given_promising",
        "mean_D_given_rescue",
        "gain_count_promising",
        "gain_count_rescue",
        "loss_count_promising",
        "loss_count_rescue",
    ]

    lines = [
        "# Adaptive policy mechanism summary",
        "",
        f"## Decomposition at alpha={alpha}",
        "",
        "```text",
        selected[columns].to_string(index=False),
        "```",
        "",
        "## Bootstrap covariance intervals",
        "",
        "```text",
        selected_cov.to_string(index=False),
        "```",
        "",
        "Positive covariance means the promising trigger preferentially activates",
        "the extra search in replications where full search has a more positive",
        "incremental rejection effect than base search.",
    ]
    (output_root / "ADAPTIVE_POLICY_MECHANISM_SUMMARY.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path(
            "simulations/ess/outputs/phase3c_adaptive_ml_policy"
        ),
    )
    parser.add_argument(
        "--alphas",
        default=",".join(str(alpha) for alpha in DEFAULT_ALPHAS),
    )
    parser.add_argument("--mechanism-alpha", type=float, default=0.05)
    parser.add_argument("--bootstrap-repetitions", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "simulations/ess/outputs/phase3c_adaptive_policy_mechanism"
        ),
    )
    args = parser.parse_args()

    alphas = parse_csv_numbers(args.alphas)

    input_root = args.input_root
    if not input_root.is_absolute():
        input_root = args.repo_root.resolve() / input_root

    output_root = args.output_dir
    if not output_root.is_absolute():
        output_root = args.repo_root.resolve() / output_root
    output_root.mkdir(parents=True, exist_ok=True)

    libraries = (
        "high_dependency_linear_20",
        "mixed_realistic_20",
    )

    results = {}
    for idx, library in enumerate(libraries):
        bank_path = (
            input_root
            / library
            / "adaptive_ml_policy_replication_bank.csv"
        )
        if not bank_path.exists():
            raise FileNotFoundError(
                f"Adaptive policy bank not found: {bank_path}"
            )
        results[library] = analyze_library(
            bank_path,
            library,
            output_root,
            alphas,
            args.mechanism_alpha,
            args.bootstrap_repetitions,
            args.seed + idx * 1000,
        )

    write_summary(results, output_root, args.mechanism_alpha)

    print("Adaptive policy mechanism decomposition complete")
    print(f"Output directory: {output_root}")

    for library, result in results.items():
        selected = result["mechanism"][
            np.isclose(
                result["mechanism"]["local_alpha"],
                args.mechanism_alpha,
            )
        ]
        covariance = result["covariance"][
            np.isclose(
                result["covariance"]["local_alpha"],
                args.mechanism_alpha,
            )
        ]
        print(f"\n=== {library}, alpha={args.mechanism_alpha} ===")
        print(
            selected[
                [
                    "pi_base",
                    "pi_full",
                    "pi_promising_observed",
                    "pi_random_observed",
                    "pi_rescue_observed",
                    "mean_incremental_effect_E_D",
                    "cov_activation_increment",
                    "mean_D_given_promising",
                    "mean_D_given_rescue",
                    "gain_count_promising",
                    "gain_count_rescue",
                    "loss_count_promising",
                    "loss_count_rescue",
                    "promising_identity_error",
                    "rescue_identity_error",
                ]
            ].to_string(index=False)
        )
        print("\nCovariance bootstrap:")
        print(covariance.to_string(index=False))


if __name__ == "__main__":
    main()
