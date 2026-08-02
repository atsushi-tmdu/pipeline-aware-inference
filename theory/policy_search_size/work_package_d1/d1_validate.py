from __future__ import annotations

import argparse
import concurrent.futures as cf
import gzip
import hashlib
import json
import math
import os
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd

from d1_core import estimate_policy, independent_normal_benchmark


Z975 = NormalDist().inv_cdf(0.975)


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _validate_config(config: dict[str, Any]) -> None:
    required = {
        "study_id",
        "analysis_label",
        "status",
        "master_seed",
        "activation_rate",
        "alphas",
        "designs",
        "outer_repetitions",
        "bootstrap_repetitions",
        "n_jobs",
        "chunk_size",
        "success_criteria",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Missing config keys: {missing}")
    if config["status"] not in {"smoke_not_scientific", "locked_before_run"}:
        raise ValueError(f"Unexpected config status: {config['status']}")
    if not 0 < float(config["activation_rate"]) < 1:
        raise ValueError("activation_rate must lie in (0,1)")
    if int(config["outer_repetitions"]) < 10:
        raise ValueError("outer_repetitions must be at least 10")
    if int(config["bootstrap_repetitions"]) < 20:
        raise ValueError("bootstrap_repetitions must be at least 20")
    for alpha in config["alphas"]:
        if not 0 < float(alpha) < 1:
            raise ValueError("all alphas must lie in (0,1)")
    for design in config["designs"]:
        if int(design["B"]) < 100 or int(design["n"]) < 100:
            raise ValueError("all B and n values must be at least 100")


def _bootstrap_distribution(
    rng: np.random.Generator,
    reference: np.ndarray,
    evaluation: np.ndarray,
    *,
    alpha: float,
    activation_rate: float,
    repetitions: int,
) -> tuple[np.ndarray, np.ndarray]:
    B = reference.shape[0]
    n = evaluation.shape[0]
    pi_values = np.empty(repetitions, dtype=float)
    tess_values = np.empty(repetitions, dtype=float)
    for j in range(repetitions):
        ref_idx = rng.integers(0, B, size=B)
        eval_idx = rng.integers(0, n, size=n)
        pi_star, tess_star, _, _ = estimate_policy(
            reference[ref_idx],
            evaluation[eval_idx],
            alpha=alpha,
            activation_rate=activation_rate,
        )
        pi_values[j] = pi_star
        tess_values[j] = tess_star
    return pi_values, tess_values


def _intervals(
    estimate: float,
    truth: float,
    bootstrap_values: np.ndarray,
    oracle_se: float,
    evaluation_only_se: float,
) -> dict[str, float | int]:
    diff = bootstrap_values - estimate
    q025, q975 = np.quantile(diff, [0.025, 0.975], method="linear")
    p025, p975 = np.quantile(bootstrap_values, [0.025, 0.975], method="linear")
    boot_sd = float(np.std(bootstrap_values, ddof=1))

    basic_low = estimate - float(q975)
    basic_high = estimate - float(q025)
    percentile_low = float(p025)
    percentile_high = float(p975)
    boot_normal_low = estimate - Z975 * boot_sd
    boot_normal_high = estimate + Z975 * boot_sd
    oracle_low = estimate - Z975 * oracle_se
    oracle_high = estimate + Z975 * oracle_se
    evaluation_only_low = estimate - Z975 * evaluation_only_se
    evaluation_only_high = estimate + Z975 * evaluation_only_se

    return {
        "bootstrap_sd": boot_sd,
        "basic_low": basic_low,
        "basic_high": basic_high,
        "basic_cover": int(basic_low <= truth <= basic_high),
        "basic_width": basic_high - basic_low,
        "percentile_low": percentile_low,
        "percentile_high": percentile_high,
        "percentile_cover": int(percentile_low <= truth <= percentile_high),
        "percentile_width": percentile_high - percentile_low,
        "bootstrap_normal_low": boot_normal_low,
        "bootstrap_normal_high": boot_normal_high,
        "bootstrap_normal_cover": int(boot_normal_low <= truth <= boot_normal_high),
        "oracle_low": oracle_low,
        "oracle_high": oracle_high,
        "oracle_cover": int(oracle_low <= truth <= oracle_high),
        "evaluation_only_low": evaluation_only_low,
        "evaluation_only_high": evaluation_only_high,
        "evaluation_only_cover": int(evaluation_only_low <= truth <= evaluation_only_high),
    }


def _one_outer(
    *,
    master_seed: int,
    cell_index: int,
    outer_index: int,
    B: int,
    n: int,
    alpha: float,
    activation_rate: float,
    bootstrap_repetitions: int,
) -> dict[str, Any]:
    seed_sequence = np.random.SeedSequence([master_seed, cell_index, outer_index])
    rng = np.random.default_rng(seed_sequence)

    reference = rng.normal(size=(B, 3))
    evaluation = rng.normal(size=(n, 3))
    pi_hat, tess_hat, q0_hat, q1_hat = estimate_policy(
        reference,
        evaluation,
        alpha=alpha,
        activation_rate=activation_rate,
    )

    benchmark = independent_normal_benchmark(
        alpha=alpha,
        activation_rate=activation_rate,
        lambda_ratio=n / B,
    )
    oracle_se_pi = math.sqrt(benchmark.total_variance_sqrt_n / n)
    oracle_se_tess = math.sqrt(benchmark.tess_variance_sqrt_n / n)
    evaluation_only_se_pi = math.sqrt(benchmark.evaluation_variance / n)
    gp = math.sqrt(benchmark.tess_variance_sqrt_n / benchmark.total_variance_sqrt_n)
    evaluation_only_se_tess = gp * evaluation_only_se_pi

    boot_pi, boot_tess = _bootstrap_distribution(
        rng,
        reference,
        evaluation,
        alpha=alpha,
        activation_rate=activation_rate,
        repetitions=bootstrap_repetitions,
    )

    pi_int = _intervals(
        pi_hat,
        benchmark.rejection_probability,
        boot_pi,
        oracle_se_pi,
        evaluation_only_se_pi,
    )
    tess_int = _intervals(
        tess_hat,
        benchmark.tess,
        boot_tess,
        oracle_se_tess,
        evaluation_only_se_tess,
    )

    row: dict[str, Any] = {
        "cell_index": cell_index,
        "outer_index": outer_index,
        "B": B,
        "n": n,
        "alpha": alpha,
        "activation_rate": activation_rate,
        "pi_truth": benchmark.rejection_probability,
        "tess_truth": benchmark.tess,
        "exact_sqrt_n_variance_pi": benchmark.total_variance_sqrt_n,
        "exact_sqrt_n_variance_tess": benchmark.tess_variance_sqrt_n,
        "exact_evaluation_variance_pi": benchmark.evaluation_variance,
        "exact_reference_variance_pi": benchmark.reference_variance,
        "pi_hat": pi_hat,
        "tess_hat": tess_hat,
        "q0_hat": q0_hat,
        "q1_hat": q1_hat,
    }
    row.update({f"pi_{key}": value for key, value in pi_int.items()})
    row.update({f"tess_{key}": value for key, value in tess_int.items()})
    return row


def _chunk_worker(task: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for outer_index in task["outer_indices"]:
        rows.append(
            _one_outer(
                master_seed=task["master_seed"],
                cell_index=task["cell_index"],
                outer_index=outer_index,
                B=task["B"],
                n=task["n"],
                alpha=task["alpha"],
                activation_rate=task["activation_rate"],
                bootstrap_repetitions=task["bootstrap_repetitions"],
            )
        )
    return rows


def _build_tasks(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cells: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    outer = int(config["outer_repetitions"])
    chunk_size = int(config["chunk_size"])
    cell_index = 0
    for design in config["designs"]:
        for alpha in config["alphas"]:
            cell = {
                "cell_index": cell_index,
                "B": int(design["B"]),
                "n": int(design["n"]),
                "alpha": float(alpha),
            }
            cells.append(cell)
            for start in range(0, outer, chunk_size):
                stop = min(start + chunk_size, outer)
                tasks.append(
                    {
                        **cell,
                        "outer_indices": list(range(start, stop)),
                        "master_seed": int(config["master_seed"]),
                        "activation_rate": float(config["activation_rate"]),
                        "bootstrap_repetitions": int(config["bootstrap_repetitions"]),
                    }
                )
            cell_index += 1
    return cells, tasks


def _run_tasks(config: dict[str, Any]) -> pd.DataFrame:
    _, tasks = _build_tasks(config)
    n_jobs = int(config["n_jobs"])
    if n_jobs < 0:
        n_jobs = max(1, (os.cpu_count() or 2) + 1 + n_jobs)
    n_jobs = max(1, min(n_jobs, os.cpu_count() or n_jobs))

    rows: list[dict[str, Any]] = []
    print(f"Validation tasks: {len(tasks)}; worker processes: {n_jobs}")
    if n_jobs == 1:
        for i, task in enumerate(tasks, 1):
            rows.extend(_chunk_worker(task))
            if i % max(1, len(tasks) // 20) == 0 or i == len(tasks):
                print(f"Completed task {i}/{len(tasks)}", flush=True)
    else:
        with cf.ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = [executor.submit(_chunk_worker, task) for task in tasks]
            completed = 0
            for future in cf.as_completed(futures):
                rows.extend(future.result())
                completed += 1
                if completed % max(1, len(tasks) // 20) == 0 or completed == len(tasks):
                    print(f"Completed task {completed}/{len(tasks)}", flush=True)

    frame = pd.DataFrame(rows)
    return frame.sort_values(["cell_index", "outer_index"]).reset_index(drop=True)


def _summarize_cell(group: pd.DataFrame) -> dict[str, Any]:
    first = group.iloc[0]
    n = int(first["n"])
    pi_truth = float(first["pi_truth"])
    tess_truth = float(first["tess_truth"])
    exact_var_pi = float(first["exact_sqrt_n_variance_pi"]) / n
    exact_var_tess = float(first["exact_sqrt_n_variance_tess"]) / n
    empirical_var_pi = float(group["pi_hat"].var(ddof=1))
    empirical_var_tess = float(group["tess_hat"].var(ddof=1))
    bias_pi = float(group["pi_hat"].mean() - pi_truth)
    bias_tess = float(group["tess_hat"].mean() - tess_truth)

    return {
        "cell_index": int(first["cell_index"]),
        "B": int(first["B"]),
        "n": n,
        "alpha": float(first["alpha"]),
        "activation_rate": float(first["activation_rate"]),
        "outer_repetitions": int(len(group)),
        "pi_truth": pi_truth,
        "pi_mean": float(group["pi_hat"].mean()),
        "pi_bias": bias_pi,
        "pi_standardized_bias": abs(bias_pi) / math.sqrt(exact_var_pi),
        "pi_empirical_variance": empirical_var_pi,
        "pi_exact_asymptotic_variance": exact_var_pi,
        "pi_empirical_to_exact_variance_ratio": empirical_var_pi / exact_var_pi,
        "pi_mean_bootstrap_sd": float(group["pi_bootstrap_sd"].mean()),
        "pi_bootstrap_sd_to_empirical_sd_ratio": float(group["pi_bootstrap_sd"].mean()) / math.sqrt(empirical_var_pi),
        "pi_oracle_coverage": float(group["pi_oracle_cover"].mean()),
        "pi_basic_bootstrap_coverage": float(group["pi_basic_cover"].mean()),
        "pi_percentile_bootstrap_coverage": float(group["pi_percentile_cover"].mean()),
        "pi_bootstrap_normal_coverage": float(group["pi_bootstrap_normal_cover"].mean()),
        "pi_evaluation_only_coverage": float(group["pi_evaluation_only_cover"].mean()),
        "pi_mean_basic_width": float(group["pi_basic_width"].mean()),
        "tess_truth": tess_truth,
        "tess_mean": float(group["tess_hat"].mean()),
        "tess_bias": bias_tess,
        "tess_standardized_bias": abs(bias_tess) / math.sqrt(exact_var_tess),
        "tess_empirical_variance": empirical_var_tess,
        "tess_exact_asymptotic_variance": exact_var_tess,
        "tess_empirical_to_exact_variance_ratio": empirical_var_tess / exact_var_tess,
        "tess_mean_bootstrap_sd": float(group["tess_bootstrap_sd"].mean()),
        "tess_bootstrap_sd_to_empirical_sd_ratio": float(group["tess_bootstrap_sd"].mean()) / math.sqrt(empirical_var_tess),
        "tess_oracle_coverage": float(group["tess_oracle_cover"].mean()),
        "tess_basic_bootstrap_coverage": float(group["tess_basic_cover"].mean()),
        "tess_percentile_bootstrap_coverage": float(group["tess_percentile_cover"].mean()),
        "tess_bootstrap_normal_coverage": float(group["tess_bootstrap_normal_cover"].mean()),
        "tess_evaluation_only_coverage": float(group["tess_evaluation_only_cover"].mean()),
        "tess_mean_basic_width": float(group["tess_basic_width"].mean()),
    }


def _summarize(frame: pd.DataFrame) -> pd.DataFrame:
    rows = [_summarize_cell(group) for _, group in frame.groupby("cell_index", sort=True)]
    return pd.DataFrame(rows).sort_values("cell_index").reset_index(drop=True)


def _within(value: float, bounds: list[float]) -> bool:
    return float(bounds[0]) <= float(value) <= float(bounds[1])


def _adjudicate(summary: pd.DataFrame, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    criteria = config["success_criteria"]
    checks: list[dict[str, Any]] = []

    primary_keys = {
        (int(item["B"]), int(item["n"]), float(item["alpha"]))
        for item in criteria["primary_cells"]
    }

    for _, row in summary.iterrows():
        key = (int(row["B"]), int(row["n"]), float(row["alpha"]))
        tier = "primary" if key in primary_keys else "all"
        c = criteria[tier]
        metrics = {
            "pi_standardized_bias": (row["pi_standardized_bias"], [0.0, c["maximum_standardized_bias"]]),
            "tess_standardized_bias": (row["tess_standardized_bias"], [0.0, c["maximum_standardized_bias"]]),
            "pi_variance_ratio": (row["pi_empirical_to_exact_variance_ratio"], c["empirical_variance_ratio"]),
            "tess_variance_ratio": (row["tess_empirical_to_exact_variance_ratio"], c["empirical_variance_ratio"]),
            "pi_bootstrap_sd_ratio": (row["pi_bootstrap_sd_to_empirical_sd_ratio"], c["bootstrap_sd_ratio"]),
            "tess_bootstrap_sd_ratio": (row["tess_bootstrap_sd_to_empirical_sd_ratio"], c["bootstrap_sd_ratio"]),
            "pi_oracle_coverage": (row["pi_oracle_coverage"], c["coverage"]),
            "tess_oracle_coverage": (row["tess_oracle_coverage"], c["coverage"]),
            "pi_basic_bootstrap_coverage": (row["pi_basic_bootstrap_coverage"], c["coverage"]),
            "tess_basic_bootstrap_coverage": (row["tess_basic_bootstrap_coverage"], c["coverage"]),
        }
        for metric, (value, bounds) in metrics.items():
            checks.append(
                {
                    "cell": {"B": key[0], "n": key[1], "alpha": key[2]},
                    "tier": tier,
                    "metric": metric,
                    "value": float(value),
                    "lower": float(bounds[0]),
                    "upper": float(bounds[1]),
                    "passed": _within(float(value), bounds),
                }
            )

    diagnostic = criteria["evaluation_only_diagnostic"]
    below = int((summary["pi_evaluation_only_coverage"] < diagnostic["coverage_below"]).sum())
    improvement = int(
        (
            summary["pi_basic_bootstrap_coverage"]
            > summary["pi_evaluation_only_coverage"] + diagnostic["minimum_improvement"]
        ).sum()
    )
    checks.append(
        {
            "cell": "global",
            "tier": "diagnostic",
            "metric": "evaluation_only_cells_below_threshold",
            "value": below,
            "lower": int(diagnostic["minimum_cells_below"]),
            "upper": None,
            "passed": below >= int(diagnostic["minimum_cells_below"]),
        }
    )
    checks.append(
        {
            "cell": "global",
            "tier": "diagnostic",
            "metric": "two_bank_improvement_cell_count",
            "value": improvement,
            "lower": int(diagnostic["minimum_improved_cells"]),
            "upper": None,
            "passed": improvement >= int(diagnostic["minimum_improved_cells"]),
        }
    )

    failed_scientific = [check for check in checks if check["tier"] != "diagnostic" and not check["passed"]]
    status = "PASS" if not failed_scientific else "REVIEW"
    return status, checks


def _write_adjudication(
    path: Path,
    status: str,
    summary: pd.DataFrame,
    checks: list[dict[str, Any]],
    config: dict[str, Any],
    elapsed: float,
) -> None:
    failed = [item for item in checks if not item["passed"]]
    lines = [
        "# D1 Numerical Validation v1: Adjudication",
        "",
        f"**Status: {status}**",
        "",
        "This validation concerns the regular Work Package D1 model with a known activation trigger and reference-estimated candidate quantiles. It is numerical validation of the theorem, not evidence for the empirical TESS application.",
        "",
        "## Locked design",
        "",
        f"- Outer Monte Carlo repetitions per cell: {config['outer_repetitions']}",
        f"- Two-bank bootstrap repetitions per outer dataset: {config['bootstrap_repetitions']}",
        f"- Activation rate: {config['activation_rate']}",
        f"- Alpha grid: {config['alphas']}",
        f"- Designs: {config['designs']}",
        f"- Master seed: {config['master_seed']}",
        f"- Elapsed seconds: {elapsed:.3f}",
        "",
        "## Cell summary",
        "",
        "| B | n | alpha | pi variance ratio | pi bootstrap coverage | TESS variance ratio | TESS bootstrap coverage | eval-only pi coverage |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {int(row['B'])} | {int(row['n'])} | {row['alpha']:.3f} | "
            f"{row['pi_empirical_to_exact_variance_ratio']:.3f} | "
            f"{row['pi_basic_bootstrap_coverage']:.3f} | "
            f"{row['tess_empirical_to_exact_variance_ratio']:.3f} | "
            f"{row['tess_basic_bootstrap_coverage']:.3f} | "
            f"{row['pi_evaluation_only_coverage']:.3f} |"
        )
    lines.extend(["", "## Failed checks", ""])
    if failed:
        for item in failed:
            lines.append(f"- {item}")
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "PASS means that the prespecified Monte Carlo agreement criteria for bias, asymptotic variance, bootstrap standard error, and 95% coverage were met in every declared validation cell. REVIEW means that one or more scientific agreement criteria require inspection; it does not by itself invalidate the analytic theorem.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_manifest(outdir: Path, config_path: Path, config: dict[str, Any]) -> None:
    files = []
    manifest_path = outdir / "D1_VALIDATION_MANIFEST.json"
    for path in sorted(outdir.iterdir()):
        if path == manifest_path or not path.is_file():
            continue
        files.append(
            {
                "file": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    payload = {
        "study_id": config["study_id"],
        "analysis_label": config["analysis_label"],
        "source_git_commit": os.environ.get("D1_SOURCE_GIT_COMMIT", "unknown"),
        "source_git_tag": config.get("required_lock_tag"),
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "files": files,
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scientific numerical validation for Work Package D1.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    outdir = args.outdir.expanduser().resolve()
    config = _json_load(config_path)
    _validate_config(config)
    outdir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    frame = _run_tasks(config)
    elapsed = time.perf_counter() - start
    summary = _summarize(frame)
    status, checks = _adjudicate(summary, config)

    replications_path = outdir / "D1_VALIDATION_REPLICATIONS.csv.gz"
    frame.to_csv(replications_path, index=False, compression="gzip")
    summary.to_csv(outdir / "D1_VALIDATION_CELL_SUMMARY.csv", index=False)
    (outdir / "D1_VALIDATION_CHECKS.json").write_text(
        json.dumps(checks, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    overall = {
        "study_id": config["study_id"],
        "analysis_label": config["analysis_label"],
        "status": status,
        "elapsed_seconds": elapsed,
        "outer_repetitions_per_cell": config["outer_repetitions"],
        "bootstrap_repetitions_per_outer": config["bootstrap_repetitions"],
        "cell_count": int(len(summary)),
        "failed_scientific_check_count": int(
            sum(1 for item in checks if item["tier"] != "diagnostic" and not item["passed"])
        ),
        "failed_diagnostic_check_count": int(
            sum(1 for item in checks if item["tier"] == "diagnostic" and not item["passed"])
        ),
        "master_seed": config["master_seed"],
    }
    (outdir / "D1_VALIDATION_SUMMARY.json").write_text(
        json.dumps(overall, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_adjudication(
        outdir / "D1_VALIDATION_ADJUDICATION.md",
        status,
        summary,
        checks,
        config,
        elapsed,
    )
    _write_manifest(outdir, config_path, config)

    print("D1 scientific numerical validation complete")
    print(f"Status: {status}")
    print(f"Cells: {len(summary)}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output directory: {outdir}")
    print(f"Adjudication: {outdir / 'D1_VALIDATION_ADJUDICATION.md'}")

    if status != "PASS" and config["status"] == "locked_before_run":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
