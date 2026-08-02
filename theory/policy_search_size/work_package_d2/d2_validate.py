from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import os
import platform
import sys
import time
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd
import scipy

from d2_core import (
    empirical_generalized_inverse,
    policy_rejection,
    tess_from_rejection,
)
from d2_validation_core import (
    benchmark_dgp,
    finite_reference_independent,
    sample_dgp,
)


Z975 = NormalDist().inv_cdf(0.975)


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _validate_config(config: dict[str, Any]) -> None:
    required = {
        "study_id",
        "analysis_label",
        "status",
        "activation_rate",
        "alphas",
        "designs",
        "data_generating_laws",
        "outer_repetitions",
        "bootstrap_repetitions",
        "master_seed",
        "n_jobs",
        "chunk_size",
        "primary_interval",
        "success_criteria",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Missing config keys: {missing}")
    if config["status"] not in {"smoke_not_scientific", "locked_before_run"}:
        raise ValueError(f"Unexpected config status: {config['status']}")
    if config["primary_interval"] != "centered complete-replication two-bank bootstrap-normal interval":
        raise ValueError("Unexpected primary interval")
    if int(config["outer_repetitions"]) < 10:
        raise ValueError("outer_repetitions must be at least 10")
    if int(config["bootstrap_repetitions"]) < 20:
        raise ValueError("bootstrap_repetitions must be at least 20")
    if not 0.0 < float(config["activation_rate"]) < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    names = [item["name"] for item in config["data_generating_laws"]]
    if len(names) != len(set(names)):
        raise ValueError("DGP names must be unique")
    required_names = {"independent_normal", "gaussian_factor", "nonlinear_smooth"}
    if set(names) != required_names:
        raise ValueError(f"DGP set must be {sorted(required_names)}")
    for alpha in config["alphas"]:
        if not 0.0 < float(alpha) < 1.0:
            raise ValueError("all alphas must lie in (0,1)")
    for design in config["designs"]:
        if int(design["B"]) < 100 or int(design["n"]) < 100:
            raise ValueError("all B and n values must be at least 100")


def _estimate_pair(reference: np.ndarray, evaluation: np.ndarray, alpha: float, r: float) -> dict[str, float]:
    p = 1.0 - alpha
    q0 = empirical_generalized_inverse(reference[:, 1], p)
    q1 = empirical_generalized_inverse(reference[:, 2], p)
    c_hat = empirical_generalized_inverse(reference[:, 0], 1.0 - r)
    c_pop = NormalDist().inv_cdf(1.0 - r)
    pi_d2 = policy_rejection(evaluation, q0, q1, c_hat)
    pi_d1 = policy_rejection(evaluation, q0, q1, c_pop)
    tess_d2 = tess_from_rejection(pi_d2, alpha)
    tess_d1 = tess_from_rejection(pi_d1, alpha)
    return {
        "q0_hat": q0,
        "q1_hat": q1,
        "c_hat": c_hat,
        "pi_hat": pi_d2,
        "tess_hat": tess_d2,
        "known_trigger_pi_hat": pi_d1,
        "known_trigger_tess_hat": tess_d1,
        "trigger_delta_pi_hat": pi_d2 - pi_d1,
        "trigger_delta_tess_hat": tess_d2 - tess_d1,
    }


def _bootstrap_distribution(
    rng: np.random.Generator,
    reference: np.ndarray,
    evaluation: np.ndarray,
    *,
    alpha: float,
    activation_rate: float,
    repetitions: int,
) -> dict[str, np.ndarray]:
    B, n = reference.shape[0], evaluation.shape[0]
    values = {
        "pi": np.empty(repetitions),
        "tess": np.empty(repetitions),
        "known_pi": np.empty(repetitions),
        "known_tess": np.empty(repetitions),
        "delta_pi": np.empty(repetitions),
        "delta_tess": np.empty(repetitions),
    }
    for j in range(repetitions):
        ref_idx = rng.integers(0, B, size=B)
        eval_idx = rng.integers(0, n, size=n)
        star = _estimate_pair(
            reference[ref_idx],
            evaluation[eval_idx],
            alpha=alpha,
            r=activation_rate,
        )
        values["pi"][j] = star["pi_hat"]
        values["tess"][j] = star["tess_hat"]
        values["known_pi"][j] = star["known_trigger_pi_hat"]
        values["known_tess"][j] = star["known_trigger_tess_hat"]
        values["delta_pi"][j] = star["trigger_delta_pi_hat"]
        values["delta_tess"][j] = star["trigger_delta_tess_hat"]
    return values


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
    bootstrap_normal_low = estimate - Z975 * boot_sd
    bootstrap_normal_high = estimate + Z975 * boot_sd
    oracle_low = estimate - Z975 * oracle_se
    oracle_high = estimate + Z975 * oracle_se
    eval_low = estimate - Z975 * evaluation_only_se
    eval_high = estimate + Z975 * evaluation_only_se

    return {
        "bootstrap_sd": boot_sd,
        "bootstrap_normal_low": bootstrap_normal_low,
        "bootstrap_normal_high": bootstrap_normal_high,
        "bootstrap_normal_cover": int(bootstrap_normal_low <= truth <= bootstrap_normal_high),
        "percentile_low": percentile_low,
        "percentile_high": percentile_high,
        "percentile_cover": int(percentile_low <= truth <= percentile_high),
        "basic_low": basic_low,
        "basic_high": basic_high,
        "basic_cover": int(basic_low <= truth <= basic_high),
        "oracle_low": oracle_low,
        "oracle_high": oracle_high,
        "oracle_cover": int(oracle_low <= truth <= oracle_high),
        "evaluation_only_low": eval_low,
        "evaluation_only_high": eval_high,
        "evaluation_only_cover": int(eval_low <= truth <= eval_high),
    }


def _delta_interval(estimate: float, bootstrap_values: np.ndarray) -> dict[str, float | int]:
    boot_sd = float(np.std(bootstrap_values, ddof=1))
    low = estimate - Z975 * boot_sd
    high = estimate + Z975 * boot_sd
    return {
        "bootstrap_sd": boot_sd,
        "bootstrap_normal_low": low,
        "bootstrap_normal_high": high,
        "bootstrap_normal_cover_zero": int(low <= 0.0 <= high),
    }


def _one_outer(
    *,
    master_seed: int,
    dgp_index: int,
    cell_index: int,
    outer_index: int,
    dgp_name: str,
    B: int,
    n: int,
    alpha: float,
    activation_rate: float,
    bootstrap_repetitions: int,
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    seed_sequence = np.random.SeedSequence([master_seed, dgp_index, cell_index, outer_index])
    rng = np.random.default_rng(seed_sequence)
    reference = sample_dgp(rng, dgp_name, B)
    evaluation = sample_dgp(rng, dgp_name, n)
    observed = _estimate_pair(reference, evaluation, alpha, activation_rate)
    boot = _bootstrap_distribution(
        rng,
        reference,
        evaluation,
        alpha=alpha,
        activation_rate=activation_rate,
        repetitions=bootstrap_repetitions,
    )

    oracle_pi_se = math.sqrt(benchmark["sigma_pi_d2_2_sqrt_n"] / n)
    oracle_tess_se = math.sqrt(benchmark["sigma_tess_d2_2_sqrt_n"] / n)
    eval_pi_se = math.sqrt(benchmark["sigma_e2_sqrt_n"] / n)
    gp = math.sqrt(benchmark["sigma_tess_d2_2_sqrt_n"] / benchmark["sigma_pi_d2_2_sqrt_n"])
    eval_tess_se = gp * eval_pi_se

    pi_int = _intervals(observed["pi_hat"], benchmark["pi"], boot["pi"], oracle_pi_se, eval_pi_se)
    tess_int = _intervals(observed["tess_hat"], benchmark["tess"], boot["tess"], oracle_tess_se, eval_tess_se)
    delta_pi_int = _delta_interval(observed["trigger_delta_pi_hat"], boot["delta_pi"])
    delta_tess_int = _delta_interval(observed["trigger_delta_tess_hat"], boot["delta_tess"])

    row: dict[str, Any] = {
        "dgp_index": dgp_index,
        "cell_index": cell_index,
        "outer_index": outer_index,
        "dgp": dgp_name,
        "B": B,
        "n": n,
        "alpha": alpha,
        "activation_rate": activation_rate,
        "pi_truth": benchmark["pi"],
        "tess_truth": benchmark["tess"],
        "exact_sqrt_n_variance_pi_d2": benchmark["sigma_pi_d2_2_sqrt_n"],
        "exact_sqrt_n_variance_tess_d2": benchmark["sigma_tess_d2_2_sqrt_n"],
        "exact_sqrt_n_variance_pi_d1": benchmark["sigma_pi_d1_2_sqrt_n"],
        "exact_sqrt_n_variance_trigger_delta_pi": benchmark["sigma_trigger_delta_2_sqrt_n"],
        "exact_sqrt_n_variance_trigger_delta_tess": benchmark["sigma_trigger_delta_tess_2_sqrt_n"],
        "exact_evaluation_variance_pi": benchmark["sigma_e2_sqrt_n"],
        "exact_reference_variance_pi_d2": benchmark["sigma_r_d2_2_sqrt_B"],
        "exact_reference_variance_pi_d1": benchmark["sigma_r_d1_2_sqrt_B"],
        "exact_trigger_variance_sqrt_B": benchmark["sigma_trigger_2_sqrt_B"],
        **observed,
    }
    row.update({f"pi_{key}": value for key, value in pi_int.items()})
    row.update({f"tess_{key}": value for key, value in tess_int.items()})
    row.update({f"trigger_delta_pi_{key}": value for key, value in delta_pi_int.items()})
    row.update({f"trigger_delta_tess_{key}": value for key, value in delta_tess_int.items()})
    return row


def _chunk_worker(task: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for outer_index in task["outer_indices"]:
        rows.append(
            _one_outer(
                master_seed=task["master_seed"],
                dgp_index=task["dgp_index"],
                cell_index=task["cell_index"],
                outer_index=outer_index,
                dgp_name=task["dgp_name"],
                B=task["B"],
                n=task["n"],
                alpha=task["alpha"],
                activation_rate=task["activation_rate"],
                bootstrap_repetitions=task["bootstrap_repetitions"],
                benchmark=task["benchmark"],
            )
        )
    return rows


def _build_cells_tasks(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    cells, tasks, benchmarks = [], [], []
    outer = int(config["outer_repetitions"])
    chunk_size = int(config["chunk_size"])
    q = config.get("quadrature", {})
    cell_index = 0
    for dgp_index, dgp in enumerate(config["data_generating_laws"]):
        name = dgp["name"]
        for design in config["designs"]:
            B, n = int(design["B"]), int(design["n"])
            for alpha in config["alphas"]:
                benchmark = benchmark_dgp(
                    name,
                    float(alpha),
                    float(config["activation_rate"]),
                    n / B,
                    float(q.get("epsabs", 1e-10)),
                    float(q.get("epsrel", 1e-10)),
                    int(q.get("limit", 300)),
                )
                benchmark_record = {"cell_index": cell_index, "B": B, "n": n, **benchmark}
                if name == "independent_normal":
                    benchmark_record["finite_reference"] = finite_reference_independent(
                        float(alpha), float(config["activation_rate"]), B
                    )
                benchmarks.append(benchmark_record)
                cell = {
                    "dgp_index": dgp_index,
                    "cell_index": cell_index,
                    "dgp_name": name,
                    "B": B,
                    "n": n,
                    "alpha": float(alpha),
                    "benchmark": benchmark,
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
    return cells, tasks, benchmarks


def _run_tasks(config: dict[str, Any]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    _, tasks, benchmarks = _build_cells_tasks(config)
    n_jobs = max(1, min(int(config["n_jobs"]), os.cpu_count() or int(config["n_jobs"])))
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
    frame = pd.DataFrame(rows).sort_values(["cell_index", "outer_index"]).reset_index(drop=True)
    return frame, benchmarks


def _summarize_cell(group: pd.DataFrame) -> dict[str, Any]:
    first = group.iloc[0]
    n = int(first["n"])
    pi_var = float(group["pi_hat"].var(ddof=1))
    tess_var = float(group["tess_hat"].var(ddof=1))
    delta_pi_var = float(group["trigger_delta_pi_hat"].var(ddof=1))
    delta_tess_var = float(group["trigger_delta_tess_hat"].var(ddof=1))
    pi_sd = math.sqrt(pi_var)
    tess_sd = math.sqrt(tess_var)
    delta_pi_sd = math.sqrt(delta_pi_var)
    delta_tess_sd = math.sqrt(delta_tess_var)
    pi_bias = float(group["pi_hat"].mean() - first["pi_truth"])
    tess_bias = float(group["tess_hat"].mean() - first["tess_truth"])
    return {
        "cell_index": int(first["cell_index"]),
        "dgp": first["dgp"],
        "B": int(first["B"]),
        "n": n,
        "alpha": float(first["alpha"]),
        "outer_repetitions": int(len(group)),
        "pi_truth": float(first["pi_truth"]),
        "pi_mean": float(group["pi_hat"].mean()),
        "pi_bias": pi_bias,
        "pi_standardized_bias": abs(pi_bias) / pi_sd,
        "pi_empirical_variance": pi_var,
        "pi_exact_asymptotic_variance": float(first["exact_sqrt_n_variance_pi_d2"]) / n,
        "pi_empirical_to_exact_variance_ratio": pi_var / (float(first["exact_sqrt_n_variance_pi_d2"]) / n),
        "pi_mean_bootstrap_sd": float(group["pi_bootstrap_sd"].mean()),
        "pi_bootstrap_sd_to_empirical_sd_ratio": float(group["pi_bootstrap_sd"].mean()) / pi_sd,
        "pi_oracle_coverage": float(group["pi_oracle_cover"].mean()),
        "pi_bootstrap_normal_coverage": float(group["pi_bootstrap_normal_cover"].mean()),
        "pi_percentile_coverage": float(group["pi_percentile_cover"].mean()),
        "pi_basic_coverage": float(group["pi_basic_cover"].mean()),
        "pi_evaluation_only_coverage": float(group["pi_evaluation_only_cover"].mean()),
        "tess_truth": float(first["tess_truth"]),
        "tess_mean": float(group["tess_hat"].mean()),
        "tess_bias": tess_bias,
        "tess_standardized_bias": abs(tess_bias) / tess_sd,
        "tess_empirical_variance": tess_var,
        "tess_exact_asymptotic_variance": float(first["exact_sqrt_n_variance_tess_d2"]) / n,
        "tess_empirical_to_exact_variance_ratio": tess_var / (float(first["exact_sqrt_n_variance_tess_d2"]) / n),
        "tess_mean_bootstrap_sd": float(group["tess_bootstrap_sd"].mean()),
        "tess_bootstrap_sd_to_empirical_sd_ratio": float(group["tess_bootstrap_sd"].mean()) / tess_sd,
        "tess_oracle_coverage": float(group["tess_oracle_cover"].mean()),
        "tess_bootstrap_normal_coverage": float(group["tess_bootstrap_normal_cover"].mean()),
        "tess_percentile_coverage": float(group["tess_percentile_cover"].mean()),
        "tess_basic_coverage": float(group["tess_basic_cover"].mean()),
        "tess_evaluation_only_coverage": float(group["tess_evaluation_only_cover"].mean()),
        "known_trigger_pi_mean": float(group["known_trigger_pi_hat"].mean()),
        "trigger_delta_pi_mean": float(group["trigger_delta_pi_hat"].mean()),
        "trigger_delta_pi_empirical_variance": delta_pi_var,
        "trigger_delta_pi_exact_variance": float(first["exact_sqrt_n_variance_trigger_delta_pi"]) / n,
        "trigger_delta_pi_variance_ratio": delta_pi_var / (float(first["exact_sqrt_n_variance_trigger_delta_pi"]) / n),
        "trigger_delta_pi_mean_bootstrap_sd": float(group["trigger_delta_pi_bootstrap_sd"].mean()),
        "trigger_delta_pi_bootstrap_sd_ratio": float(group["trigger_delta_pi_bootstrap_sd"].mean()) / delta_pi_sd,
        "trigger_delta_pi_bootstrap_normal_coverage_zero": float(group["trigger_delta_pi_bootstrap_normal_cover_zero"].mean()),
        "trigger_delta_tess_mean": float(group["trigger_delta_tess_hat"].mean()),
        "trigger_delta_tess_empirical_variance": delta_tess_var,
        "trigger_delta_tess_exact_variance": float(first["exact_sqrt_n_variance_trigger_delta_tess"]) / n,
        "trigger_delta_tess_variance_ratio": delta_tess_var / (float(first["exact_sqrt_n_variance_trigger_delta_tess"]) / n),
        "trigger_delta_tess_mean_bootstrap_sd": float(group["trigger_delta_tess_bootstrap_sd"].mean()),
        "trigger_delta_tess_bootstrap_sd_ratio": float(group["trigger_delta_tess_bootstrap_sd"].mean()) / delta_tess_sd,
        "trigger_delta_tess_bootstrap_normal_coverage_zero": float(group["trigger_delta_tess_bootstrap_normal_cover_zero"].mean()),
        "reference_variance_fraction_d2": float(first["exact_reference_variance_pi_d2"] * (int(first["n"]) / int(first["B"])) / first["exact_sqrt_n_variance_pi_d2"]),
        "trigger_only_fraction_of_reference_variance": float(first["exact_trigger_variance_sqrt_B"] / first["exact_reference_variance_pi_d2"]),
    }


def _summarize(frame: pd.DataFrame) -> pd.DataFrame:
    rows = [_summarize_cell(group) for _, group in frame.groupby("cell_index", sort=True)]
    return pd.DataFrame(rows).sort_values("cell_index").reset_index(drop=True)


def _within(value: float, bounds: list[float]) -> bool:
    return float(bounds[0]) <= float(value) <= float(bounds[1])


def _tier(row: pd.Series, config: dict[str, Any]) -> str:
    primary = config["primary_cells"]
    primary_designs = {(int(x["B"]), int(x["n"])) for x in primary["designs"]}
    if (
        row["dgp"] in primary["dgp_names"]
        and math.isclose(float(row["alpha"]), float(primary["alpha"]))
        and (int(row["B"]), int(row["n"])) in primary_designs
    ):
        return "primary"
    if int(row["B"]) >= int(config["main_regime"]["minimum_B"]):
        return "main"
    return "stress"


def _adjudicate(summary: pd.DataFrame, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    criteria = config["success_criteria"]
    for _, row in summary.iterrows():
        tier = _tier(row, config)
        if tier == "stress":
            values = [
                row["pi_mean"], row["pi_empirical_variance"],
                row["tess_mean"], row["tess_empirical_variance"],
                row["trigger_delta_pi_empirical_variance"],
                row["trigger_delta_tess_empirical_variance"],
            ]
            finite = bool(np.isfinite(np.asarray(values, dtype=float)).all())
            checks.append({
                "cell": {"dgp": row["dgp"], "B": int(row["B"]), "n": int(row["n"]), "alpha": float(row["alpha"])},
                "tier": "stress_diagnostic",
                "metric": "finite_outputs",
                "value": finite,
                "lower": None,
                "upper": None,
                "passed": finite,
            })
            continue
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
            "pi_bootstrap_normal_coverage": (row["pi_bootstrap_normal_coverage"], c["coverage"]),
            "tess_bootstrap_normal_coverage": (row["tess_bootstrap_normal_coverage"], c["coverage"]),
        }
        for metric, (value, bounds) in metrics.items():
            checks.append({
                "cell": {"dgp": row["dgp"], "B": int(row["B"]), "n": int(row["n"]), "alpha": float(row["alpha"])},
                "tier": tier,
                "metric": metric,
                "value": float(value),
                "lower": float(bounds[0]),
                "upper": float(bounds[1]),
                "passed": _within(float(value), bounds),
            })

    summary_numeric = summary.select_dtypes(include=[np.number]).to_numpy(dtype=float)
    finite_summary = bool(np.isfinite(summary_numeric).all())
    checks.append({
        "cell": "global",
        "tier": "fatal",
        "metric": "all_summary_values_finite",
        "value": finite_summary,
        "lower": None,
        "upper": None,
        "passed": finite_summary,
    })

    gd = criteria["global_diagnostics"]
    below = int((summary["pi_evaluation_only_coverage"] < gd["evaluation_only_coverage_below"]).sum())
    improved = int((summary["pi_bootstrap_normal_coverage"] > summary["pi_evaluation_only_coverage"] + gd["minimum_bootstrap_normal_improvement"]).sum())
    checks.extend([
        {
            "cell": "global", "tier": "diagnostic", "metric": "evaluation_only_cells_below_threshold",
            "value": below, "lower": int(gd["minimum_evaluation_only_cells_below"]), "upper": None,
            "passed": below >= int(gd["minimum_evaluation_only_cells_below"]),
        },
        {
            "cell": "global", "tier": "diagnostic", "metric": "bootstrap_normal_improvement_cell_count",
            "value": improved, "lower": int(gd["minimum_improved_cells"]), "upper": None,
            "passed": improved >= int(gd["minimum_improved_cells"]),
        },
    ])
    failed_fatal = [x for x in checks if x["tier"] == "fatal" and not x["passed"]]
    failed_science = [x for x in checks if x["tier"] in {"primary", "main"} and not x["passed"]]
    status = "FAIL" if failed_fatal else ("REVIEW" if failed_science else "PASS")
    return status, checks


def _write_adjudication(path: Path, status: str, summary: pd.DataFrame, checks: list[dict[str, Any]], config: dict[str, Any], elapsed: float) -> None:
    failed = [x for x in checks if x["tier"] in {"primary", "main"} and not x["passed"]]
    lines = [
        "# D2 Numerical Validation v1: Adjudication", "", f"**Status: {status}**", "",
        "This validation concerns the regular Work Package D2 model with reference-estimated candidate and activation thresholds. It is not evidence for the empirical TESS application.", "",
        "## Locked design", "",
        f"- DGPs: {[x['name'] for x in config['data_generating_laws']]}",
        f"- Outer repetitions per cell: {config['outer_repetitions']}",
        f"- Bootstrap repetitions per outer dataset: {config['bootstrap_repetitions']}",
        f"- Alpha grid: {config['alphas']}",
        f"- Designs: {config['designs']}",
        f"- Master seed: {config['master_seed']}",
        f"- Primary interval: {config['primary_interval']}",
        f"- Elapsed seconds: {elapsed:.3f}", "",
        "## Cell summary", "",
        "| DGP | B | n | alpha | pi var ratio | pi boot-normal cov | TESS var ratio | TESS boot-normal cov | trigger var ratio | eval-only pi cov |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['dgp']} | {int(row['B'])} | {int(row['n'])} | {row['alpha']:.3f} | "
            f"{row['pi_empirical_to_exact_variance_ratio']:.3f} | {row['pi_bootstrap_normal_coverage']:.3f} | "
            f"{row['tess_empirical_to_exact_variance_ratio']:.3f} | {row['tess_bootstrap_normal_coverage']:.3f} | "
            f"{row['trigger_delta_pi_variance_ratio']:.3f} | {row['pi_evaluation_only_coverage']:.3f} |"
        )
    lines += ["", "## Failed primary/main checks", ""]
    if failed:
        lines.extend([f"- {x}" for x in failed])
    else:
        lines.append("None.")
    lines += ["", "## Interpretation", "", "PASS requires all prespecified primary and main-regime checks to pass. Stress cells are reported diagnostically. REVIEW preserves every result and triggers transparent inspection without automatically invalidating the D2 theorem.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_manifest(outdir: Path, config_path: Path, config: dict[str, Any]) -> None:
    manifest_path = outdir / "D2_VALIDATION_MANIFEST.json"
    files = []
    for path in sorted(outdir.iterdir()):
        if path == manifest_path or not path.is_file():
            continue
        files.append({"file": path.name, "size_bytes": path.stat().st_size, "sha256": _sha256(path)})
    payload = {
        "study_id": config["study_id"],
        "analysis_label": config["analysis_label"],
        "source_git_commit": os.environ.get("D2_SOURCE_GIT_COMMIT", "unknown"),
        "source_git_tag": config.get("required_lock_tag"),
        "config_path": str(config_path),
        "config_sha256": _sha256(config_path),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "files": files,
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scientific numerical validation for Work Package D2")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.expanduser().resolve()
    outdir = args.outdir.expanduser().resolve()
    config = _json_load(config_path)
    _validate_config(config)
    outdir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    frame, benchmarks = _run_tasks(config)
    elapsed = time.perf_counter() - started
    summary = _summarize(frame)
    status, checks = _adjudicate(summary, config)

    frame.to_csv(outdir / "D2_VALIDATION_REPLICATIONS.csv.gz", index=False, compression="gzip")
    summary.to_csv(outdir / "D2_VALIDATION_CELL_SUMMARY.csv", index=False)
    (outdir / "D2_VALIDATION_BENCHMARKS.json").write_text(json.dumps(benchmarks, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    (outdir / "D2_VALIDATION_CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    overall = {
        "study_id": config["study_id"],
        "analysis_label": config["analysis_label"],
        "status": status,
        "elapsed_seconds": elapsed,
        "outer_repetitions_per_cell": config["outer_repetitions"],
        "bootstrap_repetitions_per_outer": config["bootstrap_repetitions"],
        "cell_count": int(len(summary)),
        "failed_scientific_check_count": int(sum(1 for x in checks if x["tier"] in {"primary", "main"} and not x["passed"])),
        "failed_diagnostic_check_count": int(sum(1 for x in checks if x["tier"] == "diagnostic" and not x["passed"])),
        "master_seed": config["master_seed"],
    }
    (outdir / "D2_VALIDATION_SUMMARY.json").write_text(json.dumps(overall, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_adjudication(outdir / "D2_VALIDATION_ADJUDICATION.md", status, summary, checks, config, elapsed)
    _write_manifest(outdir, config_path, config)

    print("D2 scientific numerical validation complete")
    print(f"Status: {status}")
    print(f"Cells: {len(summary)}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output directory: {outdir}")
    print(f"Adjudication: {outdir / 'D2_VALIDATION_ADJUDICATION.md'}")
    if status != "PASS" and config["status"] == "locked_before_run":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
