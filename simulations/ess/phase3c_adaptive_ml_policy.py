#!/usr/bin/env python3
"""Reconstruct adaptive ML search policies from frozen Phase 3C model-level banks."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


POLICIES = (
    "fixed_base",
    "fixed_full",
    "random_expansion",
    "promising_triggered",
    "rescue_triggered",
)

POLICY_LABELS = {
    "fixed_base": "Fixed base (K=7)",
    "fixed_full": "Fixed full (K=20)",
    "random_expansion": "Random expansion",
    "promising_triggered": "Expand when promising",
    "rescue_triggered": "Expand for rescue",
}

DEFAULT_ALPHAS = (0.2, 0.1, 0.05, 0.025, 0.01, 0.005)


def parse_csv_numbers(text: str, cast=float) -> tuple:
    values = tuple(cast(x.strip()) for x in text.split(",") if x.strip())
    if not values:
        raise ValueError("At least one value is required.")
    return values


def tess_from_rejection_probability(pi: float, alpha: float) -> float:
    if not (0.0 <= pi < 1.0):
        raise ValueError(f"pi must be in [0,1), received {pi}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0,1), received {alpha}")
    return math.log1p(-pi) / math.log1p(-alpha)


def deterministic_uniform(key: str, seed: int) -> float:
    payload = f"{seed}|{key}".encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    integer = int.from_bytes(digest, "big", signed=False)
    return (integer + 0.5) / (2**64)


def empirical_upper_p(observed: float, sorted_reference: np.ndarray) -> float:
    if not np.isfinite(observed):
        return 1.0
    reference = np.asarray(sorted_reference, dtype=float)
    reference = reference[np.isfinite(reference)]
    if reference.size == 0:
        raise ValueError("Reference distribution is empty.")
    reference.sort()
    first_ge = int(np.searchsorted(reference, observed, side="left"))
    count_ge = reference.size - first_ge
    return float((1 + count_ge) / (reference.size + 1))


def filter_design(
    frame: pd.DataFrame,
    *,
    target_auc: float | None,
    event_count: int,
) -> pd.DataFrame:
    result = frame.copy()

    if target_auc is not None and "target_auc" in result.columns:
        result = result[np.isclose(result["target_auc"].astype(float), target_auc)]

    if "feature_selection" in result.columns:
        result = result[result["feature_selection"].astype(str) == "none"]

    if "selection_event_count" in result.columns:
        result = result[
            result["selection_event_count"].astype(int) == int(event_count)
        ]

    return result.copy()


def load_candidate_order(run_dir: Path) -> tuple[list[str], list[str]]:
    manifest_path = run_dir / "candidate_library_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Candidate manifest not found: {manifest_path}")

    manifest = pd.read_csv(manifest_path)
    required = {"candidate_order", "candidate_name", "included_in_k7"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"Manifest missing columns: {sorted(missing)}")

    manifest = manifest.sort_values("candidate_order")
    full_models = manifest["candidate_name"].astype(str).tolist()
    base_models = (
        manifest[manifest["included_in_k7"].astype(bool)]
        ["candidate_name"]
        .astype(str)
        .tolist()
    )

    if len(full_models) != 20:
        raise ValueError(f"Expected 20 models, found {len(full_models)}")
    if len(base_models) != 7:
        raise ValueError(f"Expected 7 base models, found {len(base_models)}")

    return base_models, full_models


def pivot_selection_scores(
    frame: pd.DataFrame,
    models: list[str],
) -> tuple[pd.DataFrame, pd.Series | None]:
    required = {"replication", "model", "selection_roc_auc"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Model metrics missing columns: {sorted(missing)}")

    subset = frame[frame["model"].astype(str).isin(models)].copy()
    subset["model"] = subset["model"].astype(str)

    duplicated = subset.duplicated(["replication", "model"]).any()
    if duplicated:
        raise ValueError("Duplicate replication/model rows remain after filtering.")

    matrix = subset.pivot(
        index="replication",
        columns="model",
        values="selection_roc_auc",
    )
    matrix = matrix.reindex(columns=models).sort_index()

    seed_series = None
    if "seed" in subset.columns:
        seed_series = (
            subset[["replication", "seed"]]
            .drop_duplicates("replication")
            .set_index("replication")["seed"]
            .reindex(matrix.index)
        )

    return matrix, seed_series


def candidate_winners(
    score_matrix: pd.DataFrame,
    models: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    scores = score_matrix[models].to_numpy(dtype=float)
    safe_scores = np.where(np.isfinite(scores), scores, -np.inf)
    winner_indices = np.argmax(safe_scores, axis=1)
    winner_models = np.asarray(models, dtype=object)[winner_indices]
    winner_scores = safe_scores[np.arange(safe_scores.shape[0]), winner_indices]
    winner_scores = np.where(np.isfinite(winner_scores), winner_scores, np.nan)
    return winner_models, winner_scores


def calibrate_promising_trigger(
    reference_base_max: np.ndarray,
    target_probability: float,
) -> tuple[float, float]:
    values = np.asarray(reference_base_max, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("No finite base maxima in the reference bank.")
    if not (0.0 < target_probability < 1.0):
        raise ValueError("target_probability must be in (0,1).")

    descending = np.sort(values)[::-1]
    target_count = target_probability * values.size
    rank = min(max(int(math.ceil(target_count)) - 1, 0), values.size - 1)
    threshold = float(descending[rank])

    greater_count = int(np.count_nonzero(values > threshold))
    equal_count = int(np.count_nonzero(values == threshold))
    tie_probability = (target_count - greater_count) / equal_count
    tie_probability = float(min(max(tie_probability, 0.0), 1.0))
    return threshold, tie_probability


def apply_promising_trigger(
    values: np.ndarray,
    replication_ids: Iterable,
    threshold: float,
    tie_probability: float,
    seed: int,
) -> np.ndarray:
    scores = np.asarray(values, dtype=float)
    trigger = scores > threshold
    ties = np.isclose(scores, threshold, rtol=0.0, atol=1e-15)
    if tie_probability <= 0:
        return trigger
    ids = list(replication_ids)
    for idx in np.flatnonzero(ties):
        u = deterministic_uniform(f"tie|{ids[idx]}", seed)
        trigger[idx] = u < tie_probability
    return trigger


def random_trigger(replication_ids: Iterable, probability: float, seed: int) -> np.ndarray:
    return np.asarray(
        [
            deterministic_uniform(f"random|{replication}", seed) < probability
            for replication in replication_ids
        ],
        dtype=bool,
    )


def build_reference_lookup(
    reference_frame: pd.DataFrame,
    models: list[str],
) -> dict[str, np.ndarray]:
    required = {"model", "selection_roc_auc"}
    missing = required.difference(reference_frame.columns)
    if missing:
        raise ValueError(f"Reference metrics missing columns: {sorted(missing)}")

    lookup: dict[str, np.ndarray] = {}
    for model in models:
        values = reference_frame.loc[
            reference_frame["model"].astype(str) == model,
            "selection_roc_auc",
        ].to_numpy(dtype=float)
        values = values[np.isfinite(values)]
        if values.size == 0:
            raise ValueError(f"No reference scores for model {model}")
        lookup[model] = np.sort(values)
    return lookup


def pvalues_for_winners(
    winner_models: np.ndarray,
    winner_scores: np.ndarray,
    reference_lookup: dict[str, np.ndarray],
) -> np.ndarray:
    return np.asarray(
        [
            empirical_upper_p(score, reference_lookup[str(model)])
            for model, score in zip(winner_models, winner_scores)
        ],
        dtype=float,
    )


def policy_winners(
    base_models: np.ndarray,
    base_scores: np.ndarray,
    full_models: np.ndarray,
    full_scores: np.ndarray,
    expand: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    models = np.where(expand, full_models, base_models)
    scores = np.where(expand, full_scores, base_scores)
    return models, scores


def construct_policy_bank(
    reference_scores: pd.DataFrame,
    evaluation_scores: pd.DataFrame,
    reference_seeds: pd.Series | None,
    evaluation_seeds: pd.Series | None,
    base_models: list[str],
    full_models: list[str],
    reference_lookup: dict[str, np.ndarray],
    target_expansion_probability: float,
    random_seed: int,
) -> tuple[pd.DataFrame, dict[str, float]]:
    reference_base_winner_model, reference_base_max = candidate_winners(
        reference_scores, base_models
    )
    del reference_base_winner_model

    threshold, tie_probability = calibrate_promising_trigger(
        reference_base_max,
        target_expansion_probability,
    )

    eval_base_models, eval_base_scores = candidate_winners(
        evaluation_scores, base_models
    )
    eval_full_models, eval_full_scores = candidate_winners(
        evaluation_scores, full_models
    )

    replication_ids = evaluation_scores.index.to_numpy()

    promising_expand = apply_promising_trigger(
        eval_base_scores,
        replication_ids,
        threshold,
        tie_probability,
        random_seed + 101,
    )
    rescue_expand = ~promising_expand
    random_expand = random_trigger(
        replication_ids,
        target_expansion_probability,
        random_seed + 211,
    )

    expansion_map = {
        "fixed_base": np.zeros(len(replication_ids), dtype=bool),
        "fixed_full": np.ones(len(replication_ids), dtype=bool),
        "random_expansion": random_expand,
        "promising_triggered": promising_expand,
        "rescue_triggered": rescue_expand,
    }

    rows = []
    base_k = len(base_models)
    full_k = len(full_models)
    extra_k = full_k - base_k

    for policy in POLICIES:
        expand = expansion_map[policy]
        winner_models, winner_scores = policy_winners(
            eval_base_models,
            eval_base_scores,
            eval_full_models,
            eval_full_scores,
            expand,
        )
        pvalues = pvalues_for_winners(
            winner_models,
            winner_scores,
            reference_lookup,
        )

        for idx, replication in enumerate(replication_ids):
            row = {
                "replication": int(replication),
                "policy": policy,
                "policy_label": POLICY_LABELS[policy],
                "expanded": bool(expand[idx]),
                "evaluated_candidate_count": int(
                    full_k if expand[idx] else base_k
                ),
                "base_stage_max_selection_roc_auc": float(
                    eval_base_scores[idx]
                ),
                "winner_model": str(winner_models[idx]),
                "winner_selection_roc_auc": float(winner_scores[idx]),
                "naive_empirical_p_value": float(pvalues[idx]),
            }
            if evaluation_seeds is not None:
                seed_value = evaluation_seeds.loc[replication]
                if pd.notna(seed_value):
                    row["seed"] = int(seed_value)
            rows.append(row)

    metadata = {
        "trigger_threshold": threshold,
        "trigger_tie_probability": tie_probability,
        "target_expansion_probability": target_expansion_probability,
        "reference_base_repetitions": int(len(reference_scores)),
        "evaluation_repetitions": int(len(evaluation_scores)),
        "base_candidate_count": base_k,
        "extra_candidate_count": extra_k,
        "maximum_candidate_count": full_k,
    }
    return pd.DataFrame(rows), metadata


def summarize_curves(
    bank: pd.DataFrame,
    alphas: tuple[float, ...],
) -> pd.DataFrame:
    rows = []
    for policy, group in bank.groupby("policy", sort=False):
        pvalues = group["naive_empirical_p_value"].to_numpy(dtype=float)
        expansion_rate = float(group["expanded"].mean())
        mean_k = float(group["evaluated_candidate_count"].mean())
        for alpha in alphas:
            rejects = int(np.count_nonzero(pvalues < alpha))
            pi = rejects / pvalues.size
            rows.append(
                {
                    "policy": policy,
                    "policy_label": POLICY_LABELS[policy],
                    "local_alpha": alpha,
                    "evaluation_repetitions": int(pvalues.size),
                    "naive_rejections": rejects,
                    "naive_rejection_probability": pi,
                    "tess": tess_from_rejection_probability(pi, alpha),
                    "expansion_rate": expansion_rate,
                    "mean_evaluated_candidate_count": mean_k,
                }
            )
    return pd.DataFrame(rows)


def bootstrap_policy_curves(
    bank: pd.DataFrame,
    alphas: tuple[float, ...],
    repetitions: int,
    seed: int,
    chunk_size: int = 500,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pivot = bank.pivot(
        index="replication",
        columns="policy",
        values="naive_empirical_p_value",
    ).reindex(columns=POLICIES)

    pvalues = pivot.to_numpy(dtype=float)
    n = pvalues.shape[0]
    policy_count = len(POLICIES)
    alpha_count = len(alphas)

    reject = np.zeros((n, policy_count, alpha_count), dtype=np.float64)
    for a_idx, alpha in enumerate(alphas):
        reject[:, :, a_idx] = pvalues < alpha

    point_pi = reject.mean(axis=0)
    point_tess = np.zeros_like(point_pi)
    for p_idx in range(policy_count):
        for a_idx, alpha in enumerate(alphas):
            point_tess[p_idx, a_idx] = tess_from_rejection_probability(
                float(point_pi[p_idx, a_idx]),
                alpha,
            )

    boot = np.empty((repetitions, policy_count, alpha_count), dtype=float)
    rng = np.random.default_rng(seed)

    done = 0
    while done < repetitions:
        b = min(chunk_size, repetitions - done)
        indices = rng.integers(0, n, size=(b, n))
        sampled_pi = reject[indices].mean(axis=1)
        for local_b in range(b):
            for p_idx in range(policy_count):
                for a_idx, alpha in enumerate(alphas):
                    boot[done + local_b, p_idx, a_idx] = (
                        tess_from_rejection_probability(
                            float(sampled_pi[local_b, p_idx, a_idx]),
                            alpha,
                        )
                    )
        done += b

    curve_rows = []
    for p_idx, policy in enumerate(POLICIES):
        for a_idx, alpha in enumerate(alphas):
            values = boot[:, p_idx, a_idx]
            curve_rows.append(
                {
                    "policy": policy,
                    "policy_label": POLICY_LABELS[policy],
                    "local_alpha": alpha,
                    "tess": point_tess[p_idx, a_idx],
                    "bootstrap_mean": float(values.mean()),
                    "bootstrap_se": float(values.std(ddof=1)),
                    "pointwise_low_95": float(np.quantile(values, 0.025)),
                    "pointwise_high_95": float(np.quantile(values, 0.975)),
                    "bootstrap_repetitions": repetitions,
                }
            )

    contrasts = (
        ("rescue_minus_promising", "rescue_triggered", "promising_triggered"),
        ("random_minus_promising", "random_expansion", "promising_triggered"),
        ("rescue_minus_random", "rescue_triggered", "random_expansion"),
    )
    policy_index = {policy: idx for idx, policy in enumerate(POLICIES)}
    contrast_rows = []

    for name, left, right in contrasts:
        left_idx = policy_index[left]
        right_idx = policy_index[right]
        for a_idx, alpha in enumerate(alphas):
            values = boot[:, left_idx, a_idx] - boot[:, right_idx, a_idx]
            estimate = (
                point_tess[left_idx, a_idx] - point_tess[right_idx, a_idx]
            )
            contrast_rows.append(
                {
                    "contrast": name,
                    "details": (
                        f"{POLICY_LABELS[left]} minus {POLICY_LABELS[right]}"
                    ),
                    "local_alpha": alpha,
                    "estimate": estimate,
                    "bootstrap_mean": float(values.mean()),
                    "bootstrap_se": float(values.std(ddof=1)),
                    "ci_low_95": float(np.quantile(values, 0.025)),
                    "ci_high_95": float(np.quantile(values, 0.975)),
                    "bootstrap_probability_gt_zero": float(
                        np.mean(values > 0)
                    ),
                    "bootstrap_repetitions": repetitions,
                }
            )

    return pd.DataFrame(curve_rows), pd.DataFrame(contrast_rows)


def validate_fixed_pvalues(
    run_dir: Path,
    bank: pd.DataFrame,
    event_count: int,
) -> pd.DataFrame:
    path = run_dir / "independent_inference_results.csv"
    if not path.exists():
        return pd.DataFrame()

    existing = pd.read_csv(path)
    existing = filter_design(
        existing,
        target_auc=0.50,
        event_count=event_count,
    )
    if "metric" in existing.columns:
        existing = existing[existing["metric"].astype(str) == "roc_auc"]
    existing = existing[
        existing["method"].astype(str) == "naive_empirical"
    ].copy()

    rows = []
    for policy, pool_size in (("fixed_base", 7), ("fixed_full", 20)):
        old = existing[
            existing["pool_size"].astype(int) == pool_size
        ][["replication", "p_value"]].copy()
        new = bank[bank["policy"] == policy][
            ["replication", "naive_empirical_p_value"]
        ].copy()
        merged = old.merge(new, on="replication", how="inner")
        if merged.empty:
            continue
        difference = (
            merged["naive_empirical_p_value"] - merged["p_value"]
        ).abs()
        rows.append(
            {
                "policy": policy,
                "pool_size": pool_size,
                "rows_compared": len(merged),
                "maximum_absolute_p_value_difference": float(
                    difference.max()
                ),
                "mean_absolute_p_value_difference": float(
                    difference.mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def plot_policy_curves(
    curve: pd.DataFrame,
    output_dir: Path,
    library: str,
) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for policy, group in curve.groupby("policy", sort=False):
        ordered = group.sort_values("local_alpha", ascending=False)
        ax.plot(
            ordered["local_alpha"],
            ordered["tess"],
            marker="o",
            label=POLICY_LABELS[policy],
        )
        ax.fill_between(
            ordered["local_alpha"],
            ordered["pointwise_low_95"],
            ordered["pointwise_high_95"],
            alpha=0.12,
        )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("TESS")
    ax.set_title(f"Adaptive ML search policies: {library}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "adaptive_ml_policy_tess_curves.png", dpi=220)
    fig.savefig(output_dir / "adaptive_ml_policy_tess_curves.svg")
    plt.close(fig)


def plot_contrasts(
    contrasts: pd.DataFrame,
    output_dir: Path,
    library: str,
) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    for contrast, group in contrasts.groupby("contrast", sort=False):
        ordered = group.sort_values("local_alpha", ascending=False)
        ax.plot(
            ordered["local_alpha"],
            ordered["estimate"],
            marker="o",
            label=contrast.replace("_", " "),
        )
        ax.fill_between(
            ordered["local_alpha"],
            ordered["ci_low_95"],
            ordered["ci_high_95"],
            alpha=0.12,
        )
    ax.axhline(0.0, linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Paired TESS difference")
    ax.set_title(f"Adaptive policy contrasts: {library}")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "adaptive_ml_policy_contrasts.png", dpi=220)
    fig.savefig(output_dir / "adaptive_ml_policy_contrasts.svg")
    plt.close(fig)


def analyze_library(
    run_dir: Path,
    library: str,
    output_root: Path,
    alphas: tuple[float, ...],
    event_count: int,
    target_expansion_probability: float,
    bootstrap_repetitions: int,
    random_seed: int,
) -> dict[str, pd.DataFrame]:
    base_models, full_models = load_candidate_order(run_dir)

    reference = pd.read_csv(run_dir / "null_reference_model_metrics.csv")
    evaluation = pd.read_csv(run_dir / "evaluation_model_metrics.csv")

    reference = filter_design(
        reference,
        target_auc=0.50,
        event_count=event_count,
    )
    evaluation = filter_design(
        evaluation,
        target_auc=0.50,
        event_count=event_count,
    )

    reference_scores, reference_seeds = pivot_selection_scores(
        reference,
        full_models,
    )
    evaluation_scores, evaluation_seeds = pivot_selection_scores(
        evaluation,
        full_models,
    )

    reference_lookup = build_reference_lookup(reference, full_models)

    bank, metadata = construct_policy_bank(
        reference_scores,
        evaluation_scores,
        reference_seeds,
        evaluation_seeds,
        base_models,
        full_models,
        reference_lookup,
        target_expansion_probability,
        random_seed,
    )
    bank.insert(0, "library", library)

    point = summarize_curves(bank, alphas)
    point.insert(0, "library", library)

    boot_curve, contrasts = bootstrap_policy_curves(
        bank,
        alphas,
        bootstrap_repetitions,
        random_seed + 1001,
    )
    boot_curve.insert(0, "library", library)
    contrasts.insert(0, "library", library)

    validation = validate_fixed_pvalues(run_dir, bank, event_count)
    if not validation.empty:
        validation.insert(0, "library", library)

    output_dir = output_root / library
    output_dir.mkdir(parents=True, exist_ok=True)

    bank.to_csv(output_dir / "adaptive_ml_policy_replication_bank.csv", index=False)
    point.to_csv(output_dir / "adaptive_ml_policy_tess_point_estimates.csv", index=False)
    boot_curve.to_csv(output_dir / "adaptive_ml_policy_tess_bootstrap_curves.csv", index=False)
    contrasts.to_csv(output_dir / "adaptive_ml_policy_tess_contrasts.csv", index=False)
    validation.to_csv(output_dir / "fixed_policy_reconstruction_validation.csv", index=False)

    pd.DataFrame([{"library": library, **metadata}]).to_csv(
        output_dir / "adaptive_ml_policy_metadata.csv",
        index=False,
    )

    plot_policy_curves(boot_curve, output_dir, library)
    plot_contrasts(contrasts, output_dir, library)

    return {
        "bank": bank,
        "point": point,
        "curve": boot_curve,
        "contrasts": contrasts,
        "validation": validation,
        "metadata": pd.DataFrame([{"library": library, **metadata}]),
    }


def write_combined_summary(
    results: dict[str, dict[str, pd.DataFrame]],
    output_root: Path,
) -> None:
    combined_point = pd.concat(
        [value["point"] for value in results.values()],
        ignore_index=True,
    )
    combined_contrasts = pd.concat(
        [value["contrasts"] for value in results.values()],
        ignore_index=True,
    )
    combined_metadata = pd.concat(
        [value["metadata"] for value in results.values()],
        ignore_index=True,
    )
    combined_validation = pd.concat(
        [
            value["validation"]
            for value in results.values()
            if not value["validation"].empty
        ],
        ignore_index=True,
    )

    combined_point.to_csv(
        output_root / "phase3c_adaptive_ml_policy_tess_all_libraries.csv",
        index=False,
    )
    combined_contrasts.to_csv(
        output_root / "phase3c_adaptive_ml_policy_contrasts_all_libraries.csv",
        index=False,
    )
    combined_metadata.to_csv(
        output_root / "phase3c_adaptive_ml_policy_metadata_all_libraries.csv",
        index=False,
    )
    combined_validation.to_csv(
        output_root / "phase3c_adaptive_ml_policy_validation_all_libraries.csv",
        index=False,
    )

    alpha05 = combined_point[
        np.isclose(combined_point["local_alpha"], 0.05)
    ].copy()

    lines = [
        "# Phase 3C adaptive ML policy summary",
        "",
        "All results are conditional on the frozen null-reference bank.",
        "",
        "## Expansion metadata",
        "",
        "```text",
        combined_metadata.to_string(index=False),
        "```",
        "",
        "## TESS at alpha=0.05",
        "",
        "```text",
        alpha05[
            [
                "library",
                "policy_label",
                "tess",
                "expansion_rate",
                "mean_evaluated_candidate_count",
            ]
        ].sort_values(["library", "tess"]).to_string(index=False),
        "```",
        "",
        "## Fixed-policy reconstruction validation",
        "",
        "```text",
        combined_validation.to_string(index=False),
        "```",
    ]
    (output_root / "PHASE3C_ADAPTIVE_ML_POLICY_SUMMARY.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--high-dependency-run-dir", type=Path, required=True)
    parser.add_argument("--mixed-realistic-run-dir", type=Path, required=True)
    parser.add_argument(
        "--alphas",
        default=",".join(str(alpha) for alpha in DEFAULT_ALPHAS),
    )
    parser.add_argument("--event-count", type=int, default=100)
    parser.add_argument("--target-expansion-probability", type=float, default=0.5)
    parser.add_argument("--bootstrap-repetitions", type=int, default=20_000)
    parser.add_argument("--random-seed", type=int, default=20260730)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("simulations/ess/outputs/phase3c_adaptive_ml_policy"),
    )
    args = parser.parse_args()

    alphas = parse_csv_numbers(args.alphas, float)

    output_root = args.output_dir
    if not output_root.is_absolute():
        output_root = args.repo_root.resolve() / output_root
    output_root.mkdir(parents=True, exist_ok=True)

    run_dirs = {
        "high_dependency_linear_20": args.high_dependency_run_dir.expanduser().resolve(),
        "mixed_realistic_20": args.mixed_realistic_run_dir.expanduser().resolve(),
    }

    results = {}
    for library, run_dir in run_dirs.items():
        print(f"Analyzing {library}: {run_dir}")
        results[library] = analyze_library(
            run_dir,
            library,
            output_root,
            alphas,
            args.event_count,
            args.target_expansion_probability,
            args.bootstrap_repetitions,
            args.random_seed,
        )

    write_combined_summary(results, output_root)

    print("\nPhase 3C adaptive ML policy reanalysis complete")
    print(f"Output directory: {output_root}")

    for library, result in results.items():
        metadata = result["metadata"].iloc[0]
        alpha05 = result["point"][
            np.isclose(result["point"]["local_alpha"], 0.05)
        ]
        print(f"\n=== {library} ===")
        print(
            "Trigger threshold: "
            f"{metadata['trigger_threshold']:.8f}; "
            "tie probability: "
            f"{metadata['trigger_tie_probability']:.4f}"
        )
        print(
            alpha05[
                [
                    "policy_label",
                    "tess",
                    "expansion_rate",
                    "mean_evaluated_candidate_count",
                ]
            ].sort_values("tess").to_string(index=False)
        )
        if not result["validation"].empty:
            print("\nFixed-policy validation:")
            print(result["validation"].to_string(index=False))


if __name__ == "__main__":
    main()
