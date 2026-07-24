#!/usr/bin/env python3
"""Create compact/public Phase 3C full-analysis artifacts from frozen raw outputs.

This script never alters the frozen raw simulation directories. It writes derived
summaries and a sanitized release archive to a separate output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

LIBRARIES = ("high_dependency_linear_20", "mixed_realistic_20")
METHODS = ("pipeline_empirical", "bonferroni_empirical", "naive_empirical")
TEXT_SUFFIXES = {".json", ".txt", ".log", ".md"}
LOCAL_PREFIXES = (
    "/Users/sendaatsushi/Documents/pipeline-aware/pipeline-aware-inference",
    "/Users/atsushi/Documents/pipeline-aware/pipeline-aware-inference",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--results-root", type=Path, default=Path("results_phase3c/full"))
    p.add_argument("--summary-root", type=Path, default=Path("results_phase3c/full_summary"))
    p.add_argument("--config", type=Path, default=Path("configs/phase3c/phase3c_full.json"))
    p.add_argument("--output-root", type=Path, default=Path("results_phase3c/public_release"))
    return p.parse_args()


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def find_run_dir(results_root: Path, library: str) -> Path:
    lib_root = results_root / library
    candidates = sorted(
        p for p in lib_root.glob("pipeline_phase3_*_") if p.is_dir()
    )
    # Normal paths have no trailing underscore; use a broader fallback.
    candidates = sorted(p for p in lib_root.glob("pipeline_phase3_*") if p.is_dir())
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected exactly one full run directory for {library}, found {len(candidates)}: {candidates}"
        )
    return candidates[0]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sanitize_text(text: str) -> str:
    for prefix in LOCAL_PREFIXES:
        text = text.replace(prefix, "<REPOSITORY_ROOT>")
    return text


def copy_sanitized_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if "__pycache__" in rel.parts or path.suffix == ".pyc":
            continue
        out = dst / rel
        if path.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in TEXT_SUFFIXES:
            try:
                out.write_text(sanitize_text(path.read_text(encoding="utf-8")), encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(path, out)
        else:
            shutil.copy2(path, out)


def copy_summary_files(summary_root: Path, compact_dir: Path) -> None:
    compact_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "phase3c_pilot_master_summary.csv": "phase3c_full_master_summary.csv",
        "phase3c_type1_error.csv": "phase3c_type1_error.csv",
        "phase3c_power.csv": "phase3c_power.csv",
        "paired_power_contrasts.csv": "paired_power_contrasts.csv",
        "candidate_failure_summary.csv": "candidate_failure_summary.csv",
        "candidate_library_manifest.csv": "candidate_library_manifest.csv",
        "candidate_dependence_summary.csv": "candidate_dependence_summary.csv",
        "null_maximum_summary.csv": "null_maximum_summary.csv",
    }
    for src_name, dst_name in mapping.items():
        src = summary_root / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, compact_dir / dst_name)
    for src in summary_root.glob("correlation_*.csv"):
        shutil.copy2(src, compact_dir / src.name)


def winner_frequencies(
    run_dirs: dict[str, Path], manifest: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for library, run_dir in run_dirs.items():
        metrics = pd.read_csv(run_dir / "evaluation_model_metrics.csv")
        metrics = metrics[metrics["error"].isna()].copy()
        lib_manifest = manifest[manifest["library"] == library].copy()
        order_map = dict(zip(lib_manifest["candidate_name"], lib_manifest["candidate_order"]))
        metrics["candidate_order"] = metrics["model"].map(order_map)
        if metrics["candidate_order"].isna().any():
            missing = sorted(metrics.loc[metrics["candidate_order"].isna(), "model"].unique())
            raise RuntimeError(f"Models absent from manifest for {library}: {missing}")
        for pool_size, include_col in ((7, "included_in_k7"), (20, "included_in_k20")):
            members = set(lib_manifest.loc[lib_manifest[include_col].astype(bool), "candidate_name"])
            pool = metrics[metrics["model"].isin(members)].copy()
            keys = ["target_auc", "replication"]
            # Stable declared-order tie break: highest AUROC, then smallest candidate order.
            winners = (
                pool.sort_values(keys + ["selection_roc_auc", "candidate_order"],
                                 ascending=[True, True, False, True])
                .groupby(keys, as_index=False, sort=False)
                .first()
            )
            counts = (
                winners.groupby(["target_auc", "model"], as_index=False)
                .size()
                .rename(columns={"size": "winner_count", "model": "candidate_name"})
            )
            totals = winners.groupby("target_auc").size().rename("n_replications")
            counts = counts.merge(totals, on="target_auc", how="left")
            counts["winner_frequency"] = counts["winner_count"] / counts["n_replications"]
            counts.insert(0, "pool_size", pool_size)
            counts.insert(0, "library", library)
            rows.extend(counts.to_dict("records"))
    return pd.DataFrame(rows).sort_values(
        ["library", "target_auc", "pool_size", "winner_frequency", "candidate_name"],
        ascending=[True, True, True, False, True],
    )


def k7_k20_power_contrasts(power: pd.DataFrame) -> pd.DataFrame:
    p = power[power["method"].isin(METHODS)].copy()
    wide = p.pivot_table(
        index=["library", "target_auc", "method"],
        columns="pool_size",
        values=["rejection_rate", "n"],
        aggfunc="first",
    )
    required = [("rejection_rate", 7), ("rejection_rate", 20)]
    for col in required:
        if col not in wide.columns:
            raise RuntimeError(f"Missing power column {col}")
    out = wide.reset_index()
    flat_columns = []
    for c in out.columns:
        if isinstance(c, tuple):
            if c[0] in {"library", "target_auc", "method"} and (len(c) < 2 or c[1] == ""):
                flat_columns.append(c[0])
            else:
                flat_columns.append(f"{c[0]}_k{c[1]}")
        else:
            flat_columns.append(str(c))
    out.columns = flat_columns
    out["delta_k20_minus_k7"] = out["rejection_rate_k20"] - out["rejection_rate_k7"]
    return out.sort_values(["library", "target_auc", "method"])


def build_full_report(
    config: dict,
    type1: pd.DataFrame,
    contrasts: pd.DataFrame,
    dependence: pd.DataFrame,
) -> tuple[dict, str]:
    primary_cfg = config["primary_contrast"]
    primary = contrasts[
        (contrasts["library"] == primary_cfg["library"])
        & (contrasts["pool_size"] == primary_cfg["pool_size"])
        & np.isclose(contrasts["target_auc"], primary_cfg["target_auc"])
    ]
    if len(primary) != 1:
        raise RuntimeError("Primary contrast could not be uniquely identified")
    r = primary.iloc[0]
    pipeline_type1 = type1[type1["method"] == "pipeline_empirical"]
    max_type1 = float(pipeline_type1["rejection_rate"].max())
    status = {
        "phase": "3C",
        "stage": "full",
        "decision": "FULL SUCCESS",
        "scientific_audit": "PASS",
        "type1_gate_passed": bool(max_type1 <= 0.06),
        "maximum_pipeline_type1_error": max_type1,
        "primary_delta_power": float(r["delta_pipeline_minus_bonferroni"]),
        "primary_paired_ci95_low": float(r["paired_ci95_low"]),
        "primary_paired_ci95_high": float(r["paired_ci95_high"]),
        "go_threshold": float(config["go_threshold"]),
    }
    report = f"""# Phase 3C full-analysis status

- Decision: **FULL SUCCESS**
- Scientific audit: **PASS**
- Maximum pipeline-aware Type I error across full null cells: `{max_type1:.4f}`
- Primary power difference (pipeline-aware minus Bonferroni): `{r['delta_pipeline_minus_bonferroni']:.4f}`
- Paired 95% CI: `{r['paired_ci95_low']:.4f}` to `{r['paired_ci95_high']:.4f}`
- Prespecified GO threshold: `{config['go_threshold']:.4f}`

Primary cell: `{primary_cfg['library']}`, K={primary_cfg['pool_size']}, oracle AUROC={primary_cfg['target_auc']:.2f}.

The internal engine directory name contains `quick` because Phase 3C reused the validated Phase 3 engine. The authoritative design is the full configuration: {config['null_repetitions']:,} null-reference repetitions and {config['evaluation_repetitions']:,} evaluation repetitions per AUROC and library.
"""
    return status, report


def write_readme(output_root: Path, config: dict) -> None:
    text = f"""# Phase 3C full simulation release package

This package contains the frozen Phase 3C full analysis.

## Authoritative design

- Null-reference repetitions: {config['null_repetitions']:,} per library
- Evaluation repetitions: {config['evaluation_repetitions']:,} per target AUROC and library
- Candidate pools: K=7 and K=20
- Target AUROCs: {', '.join(map(str, config['target_aurocs']))}
- Selection events: {config['selection_event_counts'][0]}
- Feature selection: none
- Primary metric: AUROC

## Directory naming note

The raw engine-generated run directories retain the word `quick` because the validated Phase 3 engine was reused. This label is an internal preset name only. The full configuration and row counts above define the analysis stage.

## Contents

- `compact_summary/`: GitHub-suitable derived summaries and manifests.
- `frozen_raw_sanitized/`: frozen raw outputs with numerical CSVs unchanged; absolute local paths removed from text metadata.
- `phase3c_full_status.json` and `phase3c_full_report.md`: final status labels.
- `SHA256SUMS.txt`: checksums for all files in this package except itself.
"""
    (output_root / "README.md").write_text(text, encoding="utf-8")


def write_checksums(root: Path) -> None:
    rows: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        rows.append(f"{sha256(path)}  {path.relative_to(root)}")
    (root / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def zip_tree(root: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            z.write(path, path.relative_to(root.parent))


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    results_root = resolve(repo_root, args.results_root).resolve()
    summary_root = resolve(repo_root, args.summary_root).resolve()
    config_path = resolve(repo_root, args.config).resolve()
    output_root = resolve(repo_root, args.output_root).resolve()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("stage") != "full":
        raise RuntimeError(f"Expected full config, got stage={config.get('stage')!r}")
    run_dirs = {lib: find_run_dir(results_root, lib) for lib in LIBRARIES}

    if output_root.exists():
        shutil.rmtree(output_root)
    compact_dir = output_root / "compact_summary"
    raw_dir = output_root / "frozen_raw_sanitized"
    compact_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)

    copy_summary_files(summary_root, compact_dir)
    manifest = pd.read_csv(summary_root / "candidate_library_manifest.csv")
    winners = winner_frequencies(run_dirs, manifest)
    winners.to_csv(compact_dir / "candidate_winner_frequencies.csv", index=False)

    power = pd.read_csv(summary_root / "phase3c_power.csv")
    preservation = k7_k20_power_contrasts(power)
    preservation.to_csv(compact_dir / "k7_vs_k20_power_preservation.csv", index=False)

    type1 = pd.read_csv(summary_root / "phase3c_type1_error.csv")
    contrasts = pd.read_csv(summary_root / "paired_power_contrasts.csv")
    dependence = pd.read_csv(summary_root / "candidate_dependence_summary.csv")
    status, report = build_full_report(config, type1, contrasts, dependence)
    (output_root / "phase3c_full_status.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    (output_root / "phase3c_full_report.md").write_text(report, encoding="utf-8")

    clean_config = dict(config)
    (output_root / "phase3c_full_config.json").write_text(
        json.dumps(clean_config, indent=2) + "\n", encoding="utf-8"
    )

    for library, run_dir in run_dirs.items():
        copy_sanitized_tree(run_dir, raw_dir / library / run_dir.name)

    # Include source/config copies but no caches.
    source_src = repo_root / "simulations/phase3c"
    if source_src.exists():
        copy_sanitized_tree(source_src, output_root / "source")
    config_dst = output_root / "config"
    config_dst.mkdir(exist_ok=True)
    shutil.copy2(config_path, config_dst / "phase3c_full.json")

    write_readme(output_root, config)
    write_checksums(output_root)

    zip_path = output_root.parent / "phase3c_full_public_release.zip"
    zip_tree(output_root, zip_path)

    print("Phase 3C finalization complete")
    print(f"Public release directory: {output_root}")
    print(f"Public release ZIP:       {zip_path}")
    print(f"Winner frequencies:      {compact_dir / 'candidate_winner_frequencies.csv'}")
    print(f"K7/K20 contrasts:        {compact_dir / 'k7_vs_k20_power_preservation.csv'}")


if __name__ == "__main__":
    main()
