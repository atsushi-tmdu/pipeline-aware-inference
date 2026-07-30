#!/usr/bin/env python3
"""Aggregate Phase 3C pilot runs and issue the prespecified go/no-go decision."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

PRIMARY_METHODS = ("pipeline_empirical", "bonferroni_empirical", "naive_empirical")


def find_runs(root: Path) -> list[Path]:
    runs = []
    for path in root.rglob("independent_inference_results.csv"):
        run = path.parent
        if (run / "null_reference_model_metrics.csv").exists():
            runs.append(run)
    if not runs:
        raise SystemExit(f"No completed Phase 3C run directories found under {root}")
    return sorted(runs)


def load_metadata(run: Path) -> dict:
    path = run / "phase3c_metadata.json"
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def effective_count(correlation: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(correlation)
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    denominator = float(np.sum(eigenvalues ** 2))
    if denominator <= 0:
        return float("nan")
    return float(np.sum(eigenvalues) ** 2 / denominator)


def percentile_ci(values: np.ndarray, reps: int, seed: int = 20260724) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    if n == 0:
        return float("nan"), float("nan")
    boot = np.empty(reps, dtype=float)
    for i in range(reps):
        boot[i] = values[rng.integers(0, n, size=n)].mean()
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--go-threshold", type=float, default=0.05)
    args = parser.parse_args()

    output = args.output_root.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    inference_frames = []
    null_frames = []
    manifests = []
    for run in find_runs(args.results_root.expanduser().resolve()):
        metadata = load_metadata(run)
        library = metadata["library"]
        inf = pd.read_csv(run / "independent_inference_results.csv")
        ref = pd.read_csv(run / "null_reference_model_metrics.csv")
        inf["library"] = library
        ref["library"] = library
        inference_frames.append(inf)
        null_frames.append(ref)
        manifest_path = run / "candidate_library_manifest.csv"
        if manifest_path.exists():
            manifests.append(pd.read_csv(manifest_path))

    inference = pd.concat(inference_frames, ignore_index=True)
    null = pd.concat(null_frames, ignore_index=True)
    inference = inference[(inference["metric"] == "roc_auc") & inference["method"].isin(PRIMARY_METHODS)].copy()
    null = null[np.isclose(null["target_auc"], 0.50)].copy()

    # Type I error and power summaries.
    summary = (
        inference.groupby(["library", "target_auc", "pool_size", "method"], dropna=False)
        .agg(n=("reject", "size"), rejection_rate=("reject", "mean"), mean_p_value=("p_value", "mean"))
        .reset_index()
    )
    summary["mcse"] = np.sqrt(summary["rejection_rate"] * (1 - summary["rejection_rate"]) / summary["n"])
    summary.to_csv(output / "phase3c_pilot_master_summary.csv", index=False)
    summary[np.isclose(summary["target_auc"], 0.50)].to_csv(output / "phase3c_type1_error.csv", index=False)
    summary[summary["target_auc"] > 0.50].to_csv(output / "phase3c_power.csv", index=False)

    # Dependence and null maximum summaries.
    dep_rows = []
    max_rows = []
    for library, group in null.groupby("library"):
        metadata = next(load_metadata(run) for run in find_runs(args.results_root.expanduser().resolve()) if load_metadata(run)["library"] == library)
        names20 = metadata["candidate_models_k20"]
        names7 = metadata["candidate_models_k7"]
        for k, names in ((7, names7), (20, names20)):
            pivot = group[group["model"].isin(names)].pivot_table(index="replication", columns="model", values="selection_roc_auc", aggfunc="first")
            pivot = pivot.reindex(columns=names).dropna(axis=0, how="any")
            # Very small smoke runs can contain candidates with zero empirical
            # variance. Exclude only those degenerate columns from the
            # correlation/eigenvalue diagnostic; the null maximum still uses
            # the full declared candidate pool.
            variances = pivot.var(axis=0, ddof=1)
            valid_names = list(variances[(variances > 0) & np.isfinite(variances)].index)
            if len(valid_names) >= 2:
                corr_df = pivot[valid_names].corr().replace([np.inf, -np.inf], np.nan).fillna(0.0)
                corr = corr_df.to_numpy(float)
                corr = (corr + corr.T) / 2.0
                np.fill_diagonal(corr, 1.0)
                off = corr[np.triu_indices_from(corr, k=1)]
                mean_corr = float(np.mean(off))
                min_corr = float(np.min(off))
                max_corr = float(np.max(off))
                eff = effective_count(corr)
            else:
                corr_df = pd.DataFrame(index=valid_names, columns=valid_names, dtype=float)
                mean_corr = min_corr = max_corr = eff = float("nan")
            maxima = pivot.max(axis=1).to_numpy(float)
            dep_rows.append({
                "library": library,
                "pool_size": k,
                "complete_replications": len(pivot),
                "nondegenerate_candidates": len(valid_names),
                "mean_pairwise_correlation": mean_corr,
                "minimum_pairwise_correlation": min_corr,
                "maximum_pairwise_correlation": max_corr,
                "effective_candidate_count": eff,
            })
            max_rows.append({
                "library": library,
                "pool_size": k,
                "n": len(maxima),
                "null_max_mean": float(np.mean(maxima)),
                "null_max_sd": float(np.std(maxima, ddof=1)),
                "null_max_q90": float(np.quantile(maxima, 0.90, method="higher")),
                "null_max_q95": float(np.quantile(maxima, 0.95, method="higher")),
                "null_max_q99": float(np.quantile(maxima, 0.99, method="higher")),
                "null_max_maximum": float(np.max(maxima)),
            })
            corr_df.to_csv(output / f"correlation_{library}_k{k}.csv")
    pd.DataFrame(dep_rows).to_csv(output / "candidate_dependence_summary.csv", index=False)
    pd.DataFrame(max_rows).to_csv(output / "null_maximum_summary.csv", index=False)

    # Paired power contrasts.
    key_cols = ["library", "target_auc", "pool_size", "replication"]
    paired = inference.pivot_table(index=key_cols, columns="method", values="reject", aggfunc="first").reset_index()
    contrast_rows = []
    for (library, target_auc, pool_size), group in paired.groupby(["library", "target_auc", "pool_size"]):
        if target_auc <= 0.50:
            continue
        values = group["pipeline_empirical"].astype(float).to_numpy() - group["bonferroni_empirical"].astype(float).to_numpy()
        low, high = percentile_ci(values, args.bootstrap_repetitions)
        contrast_rows.append({
            "library": library,
            "target_auc": target_auc,
            "pool_size": int(pool_size),
            "n": len(group),
            "power_pipeline": float(group["pipeline_empirical"].mean()),
            "power_bonferroni": float(group["bonferroni_empirical"].mean()),
            "power_naive": float(group["naive_empirical"].mean()),
            "delta_pipeline_minus_bonferroni": float(values.mean()),
            "paired_ci95_low": low,
            "paired_ci95_high": high,
            "pipeline_only_rejections": int(np.sum(values == 1)),
            "bonferroni_only_rejections": int(np.sum(values == -1)),
        })
    contrasts = pd.DataFrame(contrast_rows)
    contrasts.to_csv(output / "paired_power_contrasts.csv", index=False)

    # Candidate failure summary.
    failures = (
        pd.concat(null_frames, ignore_index=True)
        .assign(failed=lambda x: x["error"].notna())
        .groupby(["library", "model"], dropna=False)
        .agg(n=("failed", "size"), failures=("failed", "sum"), failure_rate=("failed", "mean"))
        .reset_index()
    )
    failures.to_csv(output / "candidate_failure_summary.csv", index=False)
    if manifests:
        pd.concat(manifests, ignore_index=True).drop_duplicates(["library", "candidate_name"]).to_csv(output / "candidate_library_manifest.csv", index=False)

    # Prespecified go/no-go decision.
    null_pipeline = summary[(np.isclose(summary["target_auc"], 0.50)) & (summary["method"] == "pipeline_empirical")]
    type1_gate = bool((null_pipeline["rejection_rate"] <= 0.075).all())
    primary = contrasts[
        (contrasts["library"] == "high_dependency_linear_20")
        & (contrasts["pool_size"] == 20)
        & np.isclose(contrasts["target_auc"], 0.60)
    ]
    if len(primary) != 1:
        raise SystemExit("Primary contrast was not found exactly once.")
    delta = float(primary.iloc[0]["delta_pipeline_minus_bonferroni"])
    if not type1_gate:
        decision = "NO-GO: TYPE-I ERROR AUDIT REQUIRED"
    elif delta >= args.go_threshold:
        decision = "GO TO FULL"
    elif delta >= 0.03:
        decision = "BORDERLINE: ADD 500 EVALUATION REPLICATIONS"
    else:
        decision = "NO-GO: RETAIN V3.8"

    result = {
        "decision": decision,
        "type1_gate_passed": type1_gate,
        "primary_delta_power": delta,
        "go_threshold": args.go_threshold,
    }
    (output / "go_no_go_decision.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# Phase 3C pilot go/no-go report",
        "",
        f"- Decision: **{decision}**",
        f"- Type I error gate passed: `{type1_gate}`",
        f"- Primary delta power (pipeline minus Bonferroni): `{delta:.3f}`",
        f"- Prespecified GO threshold: `{args.go_threshold:.3f}`",
        "",
        "Primary cell: high_dependency_linear_20, K=20, oracle AUROC=0.60.",
    ]
    (output / "go_no_go_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Summary directory: {output}")


if __name__ == "__main__":
    main()
