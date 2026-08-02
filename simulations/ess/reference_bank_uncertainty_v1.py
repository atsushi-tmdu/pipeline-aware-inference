#!/usr/bin/env python3
"""Two-bank bootstrap sensitivity for the locked primary TESS contrast.

This analysis resamples complete reference-bank replication IDs and complete
independent evaluation-bank replication IDs. For every bootstrap draw it
recalibrates the promising trigger and all candidate-specific empirical null
p-value mappings, then recomputes the locked mixed-realistic primary contrast.

No model is refitted and no new synthetic dataset is generated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

STUDY_ID = "TESS_REFERENCE_BANK_UNCERTAINTY_V1"
LIBRARY = "mixed_realistic_20"
REQUIRED_INPUT_FILES = (
    "candidate_library_manifest.csv",
    "null_reference_model_metrics.csv",
    "evaluation_model_metrics.csv",
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def portable_path(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


def deterministic_uniform(key: str, seed: int) -> float:
    payload = f"{seed}|{key}".encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    integer = int.from_bytes(digest, "big", signed=False)
    return (integer + 0.5) / (2**64)


def tess(pi: float, alpha: float) -> float:
    if not (0.0 <= pi < 1.0):
        raise ValueError(f"pi must lie in [0,1), received {pi}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must lie in (0,1), received {alpha}")
    return math.log1p(-pi) / math.log1p(-alpha)


def filter_locked_design(
    frame: pd.DataFrame,
    *,
    target_auc: float,
    selection_event_count: int,
    feature_selection: str,
) -> pd.DataFrame:
    result = frame.copy()
    if "target_auc" in result.columns:
        result = result[
            np.isclose(result["target_auc"].astype(float), target_auc)
        ]
    if "feature_selection" in result.columns:
        result = result[
            result["feature_selection"].astype(str) == feature_selection
        ]
    if "selection_event_count" in result.columns:
        result = result[
            result["selection_event_count"].astype(int)
            == int(selection_event_count)
        ]
    return result.copy()


def load_candidate_order(run_dir: Path) -> tuple[list[str], list[str]]:
    manifest = pd.read_csv(run_dir / "candidate_library_manifest.csv")
    required = {"candidate_order", "candidate_name", "included_in_k7"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"Candidate manifest missing: {sorted(missing)}")
    manifest = manifest.sort_values("candidate_order")
    full = manifest["candidate_name"].astype(str).tolist()
    included = manifest["included_in_k7"]
    if included.dtype == bool:
        included_mask = included.to_numpy(bool)
    else:
        normalized = included.astype(str).str.strip().str.lower()
        allowed = {"true", "false", "1", "0", "yes", "no"}
        unexpected = sorted(set(normalized) - allowed)
        if unexpected:
            raise ValueError(
                f"Unexpected included_in_k7 values: {unexpected}"
            )
        included_mask = normalized.isin({"true", "1", "yes"}).to_numpy(bool)
    base = (
        manifest.loc[included_mask, "candidate_name"]
        .astype(str)
        .tolist()
    )
    if len(full) != 20 or len(base) != 7:
        raise ValueError(
            f"Expected 20 full and 7 base candidates, found {len(full)} and {len(base)}"
        )
    if len(set(full)) != len(full):
        raise ValueError("Candidate names are not unique.")
    return base, full


def pivot_score_matrix(
    frame: pd.DataFrame,
    models: list[str],
) -> pd.DataFrame:
    required = {"replication", "model", "selection_roc_auc"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Model metrics missing: {sorted(missing)}")
    subset = frame[frame["model"].astype(str).isin(models)].copy()
    subset["model"] = subset["model"].astype(str)
    if subset.duplicated(["replication", "model"]).any():
        raise ValueError("Duplicate replication/model rows remain after filtering.")
    matrix = subset.pivot(
        index="replication", columns="model", values="selection_roc_auc"
    )
    matrix = matrix.reindex(columns=models).sort_index()
    if matrix.shape[1] != len(models):
        raise ValueError("Pivoted candidate dimension is incorrect.")
    if matrix.isna().any().any():
        # The locked engine records failed fits with a finite fallback score.
        raise ValueError("Nonfinite or missing candidate scores were found.")
    return matrix


def winner_indices_and_scores(
    score_matrix: np.ndarray,
    model_indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    subset = score_matrix[:, model_indices]
    safe = np.where(np.isfinite(subset), subset, -np.inf)
    local = np.argmax(safe, axis=1)
    winner_model_indices = model_indices[local]
    winner_scores = safe[np.arange(safe.shape[0]), local]
    if not np.all(np.isfinite(winner_scores)):
        raise ValueError("A replication has no finite winner score.")
    return winner_model_indices.astype(np.int64), winner_scores.astype(float)


def weighted_trigger(
    unique_values_ascending: np.ndarray,
    group_index: np.ndarray,
    reference_weights: np.ndarray,
    target_probability: float,
) -> tuple[float, float]:
    """Calibrate the exact weighted promising trigger.

    The reference bootstrap is represented by integer replication weights.
    The threshold is selected so that strictly-greater states plus randomized
    threshold ties have exactly target_probability times the weighted bank size.
    """
    total = int(reference_weights.sum())
    if total <= 0:
        raise ValueError("Reference weights sum to zero.")
    target_count = target_probability * total
    group_counts = np.bincount(
        group_index,
        weights=reference_weights.astype(float),
        minlength=len(unique_values_ascending),
    )
    reverse_counts = group_counts[::-1]
    cumulative = np.cumsum(reverse_counts)
    reverse_position = int(np.searchsorted(cumulative, target_count, side="left"))
    if reverse_position >= len(reverse_counts):
        raise RuntimeError("Unable to locate weighted trigger threshold.")
    threshold_group = len(unique_values_ascending) - 1 - reverse_position
    equal_count = float(group_counts[threshold_group])
    greater_count = (
        float(cumulative[reverse_position - 1]) if reverse_position > 0 else 0.0
    )
    if equal_count <= 0:
        raise RuntimeError("Weighted threshold group has zero mass.")
    tie_probability = (target_count - greater_count) / equal_count
    tie_probability = float(min(max(tie_probability, 0.0), 1.0))
    return float(unique_values_ascending[threshold_group]), tie_probability


def apply_trigger(
    base_scores: np.ndarray,
    tie_uniforms: np.ndarray,
    threshold: float,
    tie_probability: float,
) -> np.ndarray:
    activation = base_scores > threshold
    ties = np.isclose(base_scores, threshold, rtol=0.0, atol=1e-15)
    activation[ties] = tie_uniforms[ties] < tie_probability
    return activation.astype(bool)


@dataclass(frozen=True)
class PreparedBanks:
    replication_ids_reference: np.ndarray
    replication_ids_evaluation: np.ndarray
    reference_scores: np.ndarray
    evaluation_scores: np.ndarray
    full_models: tuple[str, ...]
    base_model_indices: np.ndarray
    full_model_indices: np.ndarray
    ref_order_by_model: np.ndarray
    ref_base_unique_values: np.ndarray
    ref_base_group_index: np.ndarray
    eval_base_winner_model: np.ndarray
    eval_base_winner_score: np.ndarray
    eval_full_winner_model: np.ndarray
    eval_full_winner_score: np.ndarray
    eval_base_reference_position: np.ndarray
    eval_full_reference_position: np.ndarray
    eval_base_max: np.ndarray
    eval_tie_uniform: np.ndarray

    @property
    def reference_n(self) -> int:
        return int(self.reference_scores.shape[0])

    @property
    def evaluation_n(self) -> int:
        return int(self.evaluation_scores.shape[0])

    @property
    def model_n(self) -> int:
        return int(self.reference_scores.shape[1])


def prepare_banks(run_dir: Path, config: dict[str, Any]) -> PreparedBanks:
    base_models, full_models = load_candidate_order(run_dir)
    reference = pd.read_csv(run_dir / "null_reference_model_metrics.csv")
    evaluation = pd.read_csv(run_dir / "evaluation_model_metrics.csv")
    reference = filter_locked_design(
        reference,
        target_auc=float(config["target_auc"]),
        selection_event_count=int(config["selection_event_count"]),
        feature_selection=str(config["feature_selection"]),
    )
    evaluation = filter_locked_design(
        evaluation,
        target_auc=float(config["target_auc"]),
        selection_event_count=int(config["selection_event_count"]),
        feature_selection=str(config["feature_selection"]),
    )
    reference_frame = pivot_score_matrix(reference, full_models)
    evaluation_frame = pivot_score_matrix(evaluation, full_models)

    expected_ref = int(config["reference_repetitions"])
    expected_eval = int(config["evaluation_repetitions"])
    if len(reference_frame) != expected_ref:
        raise ValueError(
            f"Expected {expected_ref} reference replications, found {len(reference_frame)}"
        )
    if len(evaluation_frame) != expected_eval:
        raise ValueError(
            f"Expected {expected_eval} evaluation replications, found {len(evaluation_frame)}"
        )

    ref_scores = reference_frame.to_numpy(float)
    eval_scores = evaluation_frame.to_numpy(float)
    full_index = np.arange(len(full_models), dtype=np.int64)
    model_to_index = {name: i for i, name in enumerate(full_models)}
    base_index = np.asarray([model_to_index[name] for name in base_models], dtype=np.int64)

    eval_base_model, eval_base_score = winner_indices_and_scores(eval_scores, base_index)
    eval_full_model, eval_full_score = winner_indices_and_scores(eval_scores, full_index)
    _, ref_base_max = winner_indices_and_scores(ref_scores, base_index)

    order_by_model = np.argsort(ref_scores, axis=0, kind="mergesort").T
    sorted_ref_scores = np.take_along_axis(
        ref_scores.T, order_by_model, axis=1
    )

    base_positions = np.empty(len(eval_scores), dtype=np.int64)
    full_positions = np.empty(len(eval_scores), dtype=np.int64)
    for m in range(len(full_models)):
        base_mask = eval_base_model == m
        if np.any(base_mask):
            base_positions[base_mask] = np.searchsorted(
                sorted_ref_scores[m], eval_base_score[base_mask], side="left"
            )
        full_mask = eval_full_model == m
        if np.any(full_mask):
            full_positions[full_mask] = np.searchsorted(
                sorted_ref_scores[m], eval_full_score[full_mask], side="left"
            )

    unique_base, base_group = np.unique(ref_base_max, return_inverse=True)
    eval_rep_ids = evaluation_frame.index.to_numpy()
    tie_seed = int(config["policy_random_seed"]) + 101
    tie_uniform = np.asarray(
        [deterministic_uniform(f"tie|{replication}", tie_seed) for replication in eval_rep_ids],
        dtype=float,
    )

    return PreparedBanks(
        replication_ids_reference=reference_frame.index.to_numpy(),
        replication_ids_evaluation=eval_rep_ids,
        reference_scores=ref_scores,
        evaluation_scores=eval_scores,
        full_models=tuple(full_models),
        base_model_indices=base_index,
        full_model_indices=full_index,
        ref_order_by_model=order_by_model,
        ref_base_unique_values=unique_base,
        ref_base_group_index=base_group.astype(np.int64),
        eval_base_winner_model=eval_base_model,
        eval_base_winner_score=eval_base_score,
        eval_full_winner_model=eval_full_model,
        eval_full_winner_score=eval_full_score,
        eval_base_reference_position=base_positions,
        eval_full_reference_position=full_positions,
        eval_base_max=eval_base_score,
        eval_tie_uniform=tie_uniform,
    )


def pvalues_from_reference_weights(
    prepared: PreparedBanks,
    reference_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Recompute base/full candidate-wise empirical p-values.

    A single reference replication-weight vector is shared across all 20
    candidates, preserving the candidate dependence within each reference
    replication. Candidate-specific sorted orders convert the common weights
    into weighted empirical upper tails.
    """
    b = prepared.reference_n
    if reference_weights.shape != (b,):
        raise ValueError("Reference weights have an unexpected shape.")
    if int(reference_weights.sum()) != b:
        raise ValueError("Reference bootstrap must preserve bank size.")

    ordered_weights = reference_weights[prepared.ref_order_by_model]
    weighted_tail = np.cumsum(ordered_weights[:, ::-1], axis=1)[:, ::-1]
    weighted_tail = np.concatenate(
        [weighted_tail, np.zeros((prepared.model_n, 1), dtype=weighted_tail.dtype)],
        axis=1,
    )

    base_counts = weighted_tail[
        prepared.eval_base_winner_model,
        prepared.eval_base_reference_position,
    ]
    full_counts = weighted_tail[
        prepared.eval_full_winner_model,
        prepared.eval_full_reference_position,
    ]
    p_base = (1.0 + base_counts.astype(float)) / (b + 1.0)
    p_full = (1.0 + full_counts.astype(float)) / (b + 1.0)
    return p_base, p_full


def compute_effect(
    prepared: PreparedBanks,
    reference_weights: np.ndarray,
    evaluation_weights: np.ndarray,
    *,
    alpha: float,
    target_expansion_probability: float,
) -> dict[str, float]:
    n = prepared.evaluation_n
    if evaluation_weights.shape != (n,):
        raise ValueError("Evaluation weights have an unexpected shape.")
    if int(evaluation_weights.sum()) != n:
        raise ValueError("Evaluation bootstrap must preserve bank size.")

    threshold, tie_probability = weighted_trigger(
        prepared.ref_base_unique_values,
        prepared.ref_base_group_index,
        reference_weights,
        target_expansion_probability,
    )
    activation = apply_trigger(
        prepared.eval_base_max,
        prepared.eval_tie_uniform,
        threshold,
        tie_probability,
    )
    p_base, p_full = pvalues_from_reference_weights(prepared, reference_weights)
    p_promising = np.where(activation, p_full, p_base)

    weights = evaluation_weights.astype(float)
    denominator = float(weights.sum())
    r0 = (p_base < alpha).astype(float)
    r1 = (p_full < alpha).astype(float)
    rp = (p_promising < alpha).astype(float)
    d = r1 - r0
    a = activation.astype(float)

    activation_rate = float(np.dot(weights, a) / denominator)
    pi_base = float(np.dot(weights, r0) / denominator)
    pi_full = float(np.dot(weights, r1) / denominator)
    mean_d = float(np.dot(weights, d) / denominator)
    pi_promising = float(np.dot(weights, rp) / denominator)
    pi_matched_random = pi_base + activation_rate * mean_d
    covariance = float(
        np.dot(weights, a * d) / denominator - activation_rate * mean_d
    )

    if not (0.0 <= pi_matched_random < 1.0):
        raise RuntimeError(
            f"Matched-random rejection probability is invalid: {pi_matched_random}"
        )

    tess_promising = tess(pi_promising, alpha)
    tess_matched_random = tess(pi_matched_random, alpha)
    delta = tess_promising - tess_matched_random

    return {
        "trigger_threshold": threshold,
        "trigger_tie_probability": tie_probability,
        "activation_rate": activation_rate,
        "pi_base": pi_base,
        "pi_full": pi_full,
        "mean_incremental_effect": mean_d,
        "pi_promising": pi_promising,
        "pi_matched_random": pi_matched_random,
        "tess_promising": tess_promising,
        "tess_matched_random": tess_matched_random,
        "delta_tess": delta,
        "cov_activation_increment": covariance,
        "incremental_gain_rate": float(np.dot(weights, d == 1) / denominator),
        "reverse_transition_rate": float(np.dot(weights, d == -1) / denominator),
    }


def integer_bootstrap_weights(rng: np.random.Generator, n: int) -> np.ndarray:
    sampled = rng.integers(0, n, size=n)
    return np.bincount(sampled, minlength=n).astype(np.int32)


def load_conditional_primary(path: Path | None) -> dict[str, float] | None:
    if path is None or not path.exists():
        return None
    frame = pd.read_csv(path)
    row = frame[
        (frame["library_or_contrast"].astype(str) == LIBRARY)
        & np.isclose(frame["local_alpha"].astype(float), 0.05)
        & (
            frame["metric"].astype(str)
            == "promising_tess_minus_matched_random"
        )
    ]
    if len(row) != 1:
        raise ValueError("Could not identify the locked conditional primary row.")
    item = row.iloc[0]
    return {
        "estimate": float(item["estimate"]),
        "bootstrap_se": float(item["bootstrap_se"]),
        "ci_low_95": float(item["ci_low_95"]),
        "ci_high_95": float(item["ci_high_95"]),
        "bootstrap_repetitions": int(item["bootstrap_repetitions"]),
    }


def summarize(
    replicates: pd.DataFrame,
    point: dict[str, float],
    conditional: dict[str, float] | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    values = replicates["delta_tess"].to_numpy(float)
    ci_low = float(np.quantile(values, 0.025))
    ci_high = float(np.quantile(values, 0.975))
    summary: dict[str, Any] = {
        "study_id": STUDY_ID,
        "status": "ROBUST" if ci_low > 0 else "INCONCLUSIVE_SENSITIVITY",
        "interpretation": (
            "Reference-bank and evaluation-bank uncertainty included; lower CI bound > 0."
            if ci_low > 0
            else "The locked primary remains confirmed, but the post hoc two-bank sensitivity interval includes zero."
        ),
        "library": LIBRARY,
        "alpha": float(config["alpha"]),
        "point_estimate_recomputed": float(point["delta_tess"]),
        "point_tess_promising": float(point["tess_promising"]),
        "point_tess_matched_random": float(point["tess_matched_random"]),
        "point_activation_rate": float(point["activation_rate"]),
        "two_bank_bootstrap_mean": float(values.mean()),
        "two_bank_bootstrap_se": float(values.std(ddof=1)),
        "two_bank_ci_low_95": ci_low,
        "two_bank_ci_high_95": ci_high,
        "two_bank_ci_width": ci_high - ci_low,
        "bootstrap_probability_gt_zero": float(np.mean(values > 0)),
        "bootstrap_probability_le_zero": float(np.mean(values <= 0)),
        "bootstrap_repetitions": int(len(values)),
        "reference_repetitions": int(config["reference_repetitions"]),
        "evaluation_repetitions": int(config["evaluation_repetitions"]),
        "bootstrap_seed": int(config["bootstrap_seed"]),
        "primary_adjudication_unchanged": True,
        "analysis_label": "post hoc sensitivity",
    }
    if conditional is not None:
        conditional_width = conditional["ci_high_95"] - conditional["ci_low_95"]
        summary["locked_conditional_estimate"] = conditional["estimate"]
        summary["locked_conditional_bootstrap_se"] = conditional["bootstrap_se"]
        summary["locked_conditional_ci_low_95"] = conditional["ci_low_95"]
        summary["locked_conditional_ci_high_95"] = conditional["ci_high_95"]
        summary["locked_conditional_ci_width"] = conditional_width
        summary["ci_width_inflation_ratio"] = (
            (ci_high - ci_low) / conditional_width
            if conditional_width > 0
            else float("nan")
        )
        summary["bootstrap_se_inflation_ratio"] = (
            summary["two_bank_bootstrap_se"] / conditional["bootstrap_se"]
            if conditional["bootstrap_se"] > 0
            else float("nan")
        )
    return summary


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# TESS Reference-Bank Uncertainty Sensitivity v1",
        "",
        f"**Sensitivity status: {summary['status']}**",
        "",
        "This post hoc sensitivity analysis does not change the locked primary adjudication.",
        "",
        "## Locked primary estimand",
        "",
        "Mixed-realistic library, alpha = 0.05, promising-triggered expansion minus budget-matched random expansion.",
        "",
        "## Results",
        "",
        f"- Recomputed point estimate: {summary['point_estimate_recomputed']:.6f}",
        f"- Two-bank bootstrap mean: {summary['two_bank_bootstrap_mean']:.6f}",
        f"- Two-bank bootstrap SE: {summary['two_bank_bootstrap_se']:.6f}",
        (
            f"- Two-bank percentile 95% CI: {summary['two_bank_ci_low_95']:.6f} "
            f"to {summary['two_bank_ci_high_95']:.6f}"
        ),
        f"- Bootstrap probability(delta > 0): {summary['bootstrap_probability_gt_zero']:.6f}",
        f"- Bootstrap repetitions: {summary['bootstrap_repetitions']:,}",
        "",
    ]
    if "locked_conditional_ci_low_95" in summary:
        lines.extend(
            [
                "## Comparison with locked conditional interval",
                "",
                (
                    f"- Locked conditional 95% CI: "
                    f"{summary['locked_conditional_ci_low_95']:.6f} to "
                    f"{summary['locked_conditional_ci_high_95']:.6f}"
                ),
                f"- CI-width inflation ratio: {summary['ci_width_inflation_ratio']:.3f}",
                f"- Bootstrap-SE inflation ratio: {summary['bootstrap_se_inflation_ratio']:.3f}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            summary["interpretation"],
            "",
            "Reference and evaluation replication IDs were resampled independently. Within each reference draw, all 20 candidate scores from a replication received the same bootstrap weight; the candidate-specific empirical p-value mappings and promising trigger were recalibrated before evaluating the policy contrast.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def save_checkpoint(
    path_npz: Path,
    path_json: Path,
    arrays: dict[str, np.ndarray],
    next_index: int,
    rng: np.random.Generator,
) -> None:
    np.savez_compressed(path_npz, **arrays)
    state = {
        "next_index": next_index,
        "rng_state": rng.bit_generator.state,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    path_json.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_checkpoint(
    path_npz: Path,
    path_json: Path,
    arrays: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> int:
    saved = np.load(path_npz)
    for name in arrays:
        if name not in saved:
            raise ValueError(f"Checkpoint missing array: {name}")
        if saved[name].shape != arrays[name].shape:
            raise ValueError(f"Checkpoint shape mismatch: {name}")
        arrays[name][:] = saved[name]
    state = json.loads(path_json.read_text(encoding="utf-8"))
    rng.bit_generator.state = state["rng_state"]
    return int(state["next_index"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--conditional-interaction",
        type=Path,
        default=Path(
            "simulations/ess/outputs/confirmatory_policy_v1/confirmatory_policy_interaction.csv"
        ),
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--no-checkpoint", action="store_true")
    args = parser.parse_args()

    repo = args.repo_root.expanduser().resolve()
    run_dir = args.run_dir.expanduser().resolve()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = repo / config_path
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    interaction_path = args.conditional_interaction
    if not interaction_path.is_absolute():
        interaction_path = repo / interaction_path

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("study_id") != STUDY_ID:
        raise SystemExit("Unexpected study_id in configuration.")
    if config.get("library") != LIBRARY:
        raise SystemExit("This v1 sensitivity is locked to mixed_realistic_20.")

    for name in REQUIRED_INPUT_FILES:
        if not (run_dir / name).is_file():
            raise FileNotFoundError(run_dir / name)

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_npz = output_dir / ".reference_bank_uncertainty_checkpoint.npz"
    checkpoint_json = output_dir / ".reference_bank_uncertainty_checkpoint.json"
    completed_marker = output_dir / "REFERENCE_BANK_UNCERTAINTY_SENSITIVITY.md"
    if completed_marker.exists():
        raise SystemExit(f"Completed output already exists: {completed_marker}")

    print(f"Preparing locked banks: {run_dir}", flush=True)
    prepared = prepare_banks(run_dir, config)
    ref_ones = np.ones(prepared.reference_n, dtype=np.int32)
    eval_ones = np.ones(prepared.evaluation_n, dtype=np.int32)
    point = compute_effect(
        prepared,
        ref_ones,
        eval_ones,
        alpha=float(config["alpha"]),
        target_expansion_probability=float(config["target_expansion_probability"]),
    )
    expected = float(config["expected_locked_point_estimate"])
    tolerance = float(config["point_estimate_tolerance"])
    difference = abs(point["delta_tess"] - expected)
    print(
        f"Point reconstruction: {point['delta_tess']:.12f} "
        f"(expected {expected:.12f}; abs diff {difference:.3g})",
        flush=True,
    )
    if difference > tolerance:
        raise SystemExit(
            "POINT RECONSTRUCTION FAILURE: raw-bank result does not match the locked primary estimate."
        )

    repetitions = int(config["bootstrap_repetitions"])
    checkpoint_every = int(config.get("checkpoint_every", 250))
    names = (
        "delta_tess",
        "tess_promising",
        "tess_matched_random",
        "pi_promising",
        "pi_matched_random",
        "pi_base",
        "pi_full",
        "activation_rate",
        "cov_activation_increment",
        "trigger_threshold",
        "trigger_tie_probability",
        "incremental_gain_rate",
        "reverse_transition_rate",
        "reference_unique_repetitions",
        "evaluation_unique_repetitions",
    )
    arrays = {name: np.full(repetitions, np.nan, dtype=float) for name in names}
    rng = np.random.default_rng(int(config["bootstrap_seed"]))
    start = 0
    if args.resume:
        if not checkpoint_npz.exists() or not checkpoint_json.exists():
            raise SystemExit("--resume requested but checkpoint files are absent.")
        start = load_checkpoint(checkpoint_npz, checkpoint_json, arrays, rng)
        print(f"Resuming at bootstrap repetition {start:,}", flush=True)
    elif checkpoint_npz.exists() or checkpoint_json.exists():
        raise SystemExit("Checkpoint exists. Use --resume or remove the incomplete output directory.")

    start_time = time.perf_counter()
    alpha = float(config["alpha"])
    target_probability = float(config["target_expansion_probability"])
    for b in range(start, repetitions):
        reference_weights = integer_bootstrap_weights(rng, prepared.reference_n)
        evaluation_weights = integer_bootstrap_weights(rng, prepared.evaluation_n)
        effect = compute_effect(
            prepared,
            reference_weights,
            evaluation_weights,
            alpha=alpha,
            target_expansion_probability=target_probability,
        )
        arrays["delta_tess"][b] = effect["delta_tess"]
        arrays["tess_promising"][b] = effect["tess_promising"]
        arrays["tess_matched_random"][b] = effect["tess_matched_random"]
        arrays["pi_promising"][b] = effect["pi_promising"]
        arrays["pi_matched_random"][b] = effect["pi_matched_random"]
        arrays["pi_base"][b] = effect["pi_base"]
        arrays["pi_full"][b] = effect["pi_full"]
        arrays["activation_rate"][b] = effect["activation_rate"]
        arrays["cov_activation_increment"][b] = effect[
            "cov_activation_increment"
        ]
        arrays["trigger_threshold"][b] = effect["trigger_threshold"]
        arrays["trigger_tie_probability"][b] = effect[
            "trigger_tie_probability"
        ]
        arrays["incremental_gain_rate"][b] = effect["incremental_gain_rate"]
        arrays["reverse_transition_rate"][b] = effect[
            "reverse_transition_rate"
        ]
        arrays["reference_unique_repetitions"][b] = np.count_nonzero(
            reference_weights
        )
        arrays["evaluation_unique_repetitions"][b] = np.count_nonzero(
            evaluation_weights
        )

        completed = b + 1
        if completed % 100 == 0 or completed == repetitions:
            elapsed = time.perf_counter() - start_time
            rate = (completed - start) / elapsed if elapsed > 0 else float("nan")
            remaining = (repetitions - completed) / rate if rate > 0 else float("nan")
            print(
                f"Bootstrap {completed:,}/{repetitions:,}; "
                f"{rate:.1f} rep/s; ETA {remaining/60:.1f} min",
                flush=True,
            )
        if (
            not args.no_checkpoint
            and checkpoint_every > 0
            and completed < repetitions
            and completed % checkpoint_every == 0
        ):
            save_checkpoint(
                checkpoint_npz,
                checkpoint_json,
                arrays,
                completed,
                rng,
            )

    if not all(np.all(np.isfinite(values)) for values in arrays.values()):
        raise RuntimeError("Nonfinite bootstrap output was produced.")

    replicates = pd.DataFrame(
        {"bootstrap_replication": np.arange(1, repetitions + 1), **arrays}
    )
    conditional = load_conditional_primary(interaction_path)
    summary = summarize(replicates, point, conditional, config)

    replicates_path = output_dir / "reference_bank_uncertainty_bootstrap_replicates.csv"
    summary_csv_path = output_dir / "reference_bank_uncertainty_summary.csv"
    summary_json_path = output_dir / "reference_bank_uncertainty_summary.json"
    markdown_path = output_dir / "REFERENCE_BANK_UNCERTAINTY_SENSITIVITY.md"
    manifest_path = output_dir / "reference_bank_uncertainty_manifest.json"

    replicates.to_csv(replicates_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_csv_path, index=False)
    summary_json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(summary, markdown_path)

    manifest = {
        "study_id": STUDY_ID,
        "analysis_label": "post hoc sensitivity",
        "primary_adjudication_unchanged": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_git_commit": git_output(repo, "rev-parse", "HEAD"),
        "repo_git_branch": git_output(repo, "branch", "--show-current"),
        "config_path": portable_path(config_path, repo),
        "config_sha256": sha256_file(config_path),
        "source_run_dir": str(run_dir),
        "input_files": [
            {
                "path": str(run_dir / name),
                "size_bytes": (run_dir / name).stat().st_size,
                "sha256": sha256_file(run_dir / name),
            }
            for name in REQUIRED_INPUT_FILES
        ],
        "outputs": [],
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "config": config,
    }
    for path in (replicates_path, summary_csv_path, summary_json_path, markdown_path):
        manifest["outputs"].append(
            {
                "path": portable_path(path, repo),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    checkpoint_npz.unlink(missing_ok=True)
    checkpoint_json.unlink(missing_ok=True)

    print("\nTwo-bank bootstrap sensitivity complete", flush=True)
    print(f"Status: {summary['status']}", flush=True)
    print(
        f"Two-bank 95% CI: {summary['two_bank_ci_low_95']:.6f} to "
        f"{summary['two_bank_ci_high_95']:.6f}",
        flush=True,
    )
    print(f"Summary: {markdown_path}", flush=True)


if __name__ == "__main__":
    main()
