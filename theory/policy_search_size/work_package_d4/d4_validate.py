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

from d4_core import estimate_d4
from d4_validation_core import benchmark_dgp, sample_dgp


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
        "unpaired_diagnostic",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Missing config keys: {missing}")
    if config["status"] not in {"smoke_not_scientific", "locked_before_run"}:
        raise ValueError(f"Unexpected config status: {config['status']}")
    if config["primary_interval"] != "centered paired complete-replication two-bank bootstrap-normal interval":
        raise ValueError("Unexpected primary interval")
    if int(config["outer_repetitions"]) < 10:
        raise ValueError("outer_repetitions must be at least 10")
    if int(config["bootstrap_repetitions"]) < 20:
        raise ValueError("bootstrap_repetitions must be at least 20")
    if not 0.0 < float(config["activation_rate"]) < 1.0:
        raise ValueError("activation_rate must lie in (0,1)")
    names = [item["name"] for item in config["data_generating_laws"]]
    required_names = {"independent_normal", "gaussian_factor", "nonlinear_smooth"}
    if set(names) != required_names or len(names) != len(set(names)):
        raise ValueError(f"DGP set must be {sorted(required_names)}")
    for alpha in config["alphas"]:
        if not 0.0 < float(alpha) < 1.0:
            raise ValueError("all alphas must lie in (0,1)")
    for design in config["designs"]:
        if int(design["B"]) < 100 or int(design["n"]) < 100:
            raise ValueError("all B and n values must be at least 100")
    unpaired = config["unpaired_diagnostic"]
    if int(unpaired["outer_repetitions_per_cell"]) < 0:
        raise ValueError("unpaired diagnostic outer repetitions must be nonnegative")
    if int(unpaired["bootstrap_repetitions"]) < 20:
        raise ValueError("unpaired diagnostic bootstrap repetitions must be at least 20")


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
    delta_pi = np.empty(repetitions, dtype=float)
    delta_tess = np.empty(repetitions, dtype=float)
    for j in range(repetitions):
        ref_idx = rng.integers(0, B, size=B)
        eval_idx = rng.integers(0, n, size=n)
        star = estimate_d4(
            reference[ref_idx],
            evaluation[eval_idx],
            alpha,
            activation_rate,
        )
        delta_pi[j] = star.delta_pi_hat
        delta_tess[j] = star.delta_tess_hat
    return {"delta_pi": delta_pi, "delta_tess": delta_tess}


def _unpaired_bootstrap_distribution(
    rng: np.random.Generator,
    reference: np.ndarray,
    evaluation: np.ndarray,
    *,
    alpha: float,
    activation_rate: float,
    repetitions: int,
) -> dict[str, np.ndarray]:
    """Diagnostic only: discard policy pairing by using independent resamples."""
    B, n = reference.shape[0], evaluation.shape[0]
    delta_pi = np.empty(repetitions, dtype=float)
    delta_tess = np.empty(repetitions, dtype=float)
    for j in range(repetitions):
        ref_a = rng.integers(0, B, size=B)
        eval_a = rng.integers(0, n, size=n)
        ref_c = rng.integers(0, B, size=B)
        eval_c = rng.integers(0, n, size=n)
        adaptive = estimate_d4(
            reference[ref_a], evaluation[eval_a], alpha, activation_rate
        )
        comparator = estimate_d4(
            reference[ref_c], evaluation[eval_c], alpha, activation_rate
        )
        delta_pi[j] = adaptive.pi_adaptive_hat - comparator.pi_comparator_hat
        delta_tess[j] = adaptive.tess_adaptive_hat - comparator.tess_comparator_hat
    return {"delta_pi": delta_pi, "delta_tess": delta_tess}


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
    unpaired_outer_repetitions: int,
    unpaired_bootstrap_repetitions: int,
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    seed_sequence = np.random.SeedSequence(
        [master_seed, dgp_index, cell_index, outer_index]
    )
    rng = np.random.default_rng(seed_sequence)
    reference = sample_dgp(rng, dgp_name, B)
    evaluation = sample_dgp(rng, dgp_name, n)
    observed = estimate_d4(reference, evaluation, alpha, activation_rate)
    boot = _bootstrap_distribution(
        rng,
        reference,
        evaluation,
        alpha=alpha,
        activation_rate=activation_rate,
        repetitions=bootstrap_repetitions,
    )

    pi_oracle_se = math.sqrt(benchmark["sigma_total_delta_pi_2_sqrt_n"] / n)
    tess_oracle_se = math.sqrt(benchmark["sigma_total_delta_tess_2_sqrt_n"] / n)
    pi_eval_se = math.sqrt(benchmark["sigma_e_delta_pi_2_sqrt_n"] / n)
    tess_eval_se = math.sqrt(benchmark["sigma_e_delta_tess_2_sqrt_n"] / n)

    pi_int = _intervals(
        observed.delta_pi_hat,
        benchmark["delta_pi"],
        boot["delta_pi"],
        pi_oracle_se,
        pi_eval_se,
    )
    tess_int = _intervals(
        observed.delta_tess_hat,
        benchmark["delta_tess"],
        boot["delta_tess"],
        tess_oracle_se,
        tess_eval_se,
    )

    unpaired_pi_sd = math.nan
    unpaired_tess_sd = math.nan
    if outer_index < unpaired_outer_repetitions:
        unpaired = _unpaired_bootstrap_distribution(
            rng,
            reference,
            evaluation,
            alpha=alpha,
            activation_rate=activation_rate,
            repetitions=unpaired_bootstrap_repetitions,
        )
        unpaired_pi_sd = float(np.std(unpaired["delta_pi"], ddof=1))
        unpaired_tess_sd = float(np.std(unpaired["delta_tess"], ddof=1))

    row: dict[str, Any] = {
        "dgp_index": dgp_index,
        "cell_index": cell_index,
        "outer_index": outer_index,
        "dgp": dgp_name,
        "B": B,
        "n": n,
        "alpha": alpha,
        "activation_rate_target": activation_rate,
        "delta_pi_truth": benchmark["delta_pi"],
        "delta_tess_truth": benchmark["delta_tess"],
        "exact_sqrt_n_variance_delta_pi": benchmark["sigma_total_delta_pi_2_sqrt_n"],
        "exact_sqrt_n_variance_delta_tess": benchmark["sigma_total_delta_tess_2_sqrt_n"],
        "exact_evaluation_variance_delta_pi": benchmark["sigma_e_delta_pi_2_sqrt_n"],
        "exact_evaluation_variance_delta_tess": benchmark["sigma_e_delta_tess_2_sqrt_n"],
        "exact_reference_variance_delta_pi": benchmark["sigma_r_delta_pi_2_sqrt_B"],
        "exact_reference_variance_delta_tess": benchmark["sigma_r_delta_tess_2_sqrt_B"],
        **observed.to_dict(),
        "unpaired_delta_pi_bootstrap_sd": unpaired_pi_sd,
        "unpaired_delta_tess_bootstrap_sd": unpaired_tess_sd,
    }
    row.update({f"delta_pi_{key}": value for key, value in pi_int.items()})
    row.update({f"delta_tess_{key}": value for key, value in tess_int.items()})
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
                unpaired_outer_repetitions=task["unpaired_outer_repetitions"],
                unpaired_bootstrap_repetitions=task["unpaired_bootstrap_repetitions"],
                benchmark=task["benchmark"],
            )
        )
    return rows


def _build_cells_tasks(
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    cells: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    benchmarks: list[dict[str, Any]] = []
    outer = int(config["outer_repetitions"])
    chunk_size = int(config["chunk_size"])
    q = config.get("quadrature", {})
    unpaired = config["unpaired_diagnostic"]
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
                benchmark_record = {
                    "cell_index": cell_index,
                    "B": B,
                    "n": n,
                    **benchmark,
                }
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
                            "unpaired_outer_repetitions": int(
                                unpaired["outer_repetitions_per_cell"]
                            ),
                            "unpaired_bootstrap_repetitions": int(
                                unpaired["bootstrap_repetitions"]
                            ),
                        }
                    )
                cell_index += 1
    return cells, tasks, benchmarks


def _run_tasks(config: dict[str, Any]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    _, tasks, benchmarks = _build_cells_tasks(config)
    n_jobs = max(
        1,
        min(int(config["n_jobs"]), os.cpu_count() or int(config["n_jobs"])),
    )
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
    frame = (
        pd.DataFrame(rows)
        .sort_values(["cell_index", "outer_index"])
        .reset_index(drop=True)
    )
    return frame, benchmarks


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0.0 or not math.isfinite(denominator):
        return math.nan
    return numerator / denominator


def _summarize_cell(group: pd.DataFrame) -> dict[str, Any]:
    first = group.iloc[0]
    n = int(first["n"])
    pi_var = float(group["delta_pi_hat"].var(ddof=1))
    tess_var = float(group["delta_tess_hat"].var(ddof=1))
    pi_sd = math.sqrt(pi_var)
    tess_sd = math.sqrt(tess_var)
    pi_bias = float(group["delta_pi_hat"].mean() - first["delta_pi_truth"])
    tess_bias = float(group["delta_tess_hat"].mean() - first["delta_tess_truth"])
    paired_pi_boot_sd = float(group["delta_pi_bootstrap_sd"].mean())
    paired_tess_boot_sd = float(group["delta_tess_bootstrap_sd"].mean())
    unpaired_pi = group["unpaired_delta_pi_bootstrap_sd"].dropna()
    unpaired_tess = group["unpaired_delta_tess_bootstrap_sd"].dropna()
    unpaired_pi_mean = float(unpaired_pi.mean()) if not unpaired_pi.empty else math.nan
    unpaired_tess_mean = float(unpaired_tess.mean()) if not unpaired_tess.empty else math.nan

    exact_pi_var = float(first["exact_sqrt_n_variance_delta_pi"]) / n
    exact_tess_var = float(first["exact_sqrt_n_variance_delta_tess"]) / n
    lambda_ratio = int(first["n"]) / int(first["B"])
    return {
        "cell_index": int(first["cell_index"]),
        "dgp": first["dgp"],
        "B": int(first["B"]),
        "n": n,
        "alpha": float(first["alpha"]),
        "outer_repetitions": int(len(group)),
        "delta_pi_truth": float(first["delta_pi_truth"]),
        "delta_pi_mean": float(group["delta_pi_hat"].mean()),
        "delta_pi_bias": pi_bias,
        "delta_pi_standardized_bias": abs(pi_bias) / pi_sd,
        "delta_pi_empirical_variance": pi_var,
        "delta_pi_exact_asymptotic_variance": exact_pi_var,
        "delta_pi_empirical_to_exact_variance_ratio": pi_var / exact_pi_var,
        "delta_pi_mean_bootstrap_sd": paired_pi_boot_sd,
        "delta_pi_bootstrap_sd_to_empirical_sd_ratio": paired_pi_boot_sd / pi_sd,
        "delta_pi_oracle_coverage": float(group["delta_pi_oracle_cover"].mean()),
        "delta_pi_bootstrap_normal_coverage": float(group["delta_pi_bootstrap_normal_cover"].mean()),
        "delta_pi_percentile_coverage": float(group["delta_pi_percentile_cover"].mean()),
        "delta_pi_basic_coverage": float(group["delta_pi_basic_cover"].mean()),
        "delta_pi_evaluation_only_coverage": float(group["delta_pi_evaluation_only_cover"].mean()),
        "delta_tess_truth": float(first["delta_tess_truth"]),
        "delta_tess_mean": float(group["delta_tess_hat"].mean()),
        "delta_tess_bias": tess_bias,
        "delta_tess_standardized_bias": abs(tess_bias) / tess_sd,
        "delta_tess_empirical_variance": tess_var,
        "delta_tess_exact_asymptotic_variance": exact_tess_var,
        "delta_tess_empirical_to_exact_variance_ratio": tess_var / exact_tess_var,
        "delta_tess_mean_bootstrap_sd": paired_tess_boot_sd,
        "delta_tess_bootstrap_sd_to_empirical_sd_ratio": paired_tess_boot_sd / tess_sd,
        "delta_tess_oracle_coverage": float(group["delta_tess_oracle_cover"].mean()),
        "delta_tess_bootstrap_normal_coverage": float(group["delta_tess_bootstrap_normal_cover"].mean()),
        "delta_tess_percentile_coverage": float(group["delta_tess_percentile_cover"].mean()),
        "delta_tess_basic_coverage": float(group["delta_tess_basic_cover"].mean()),
        "delta_tess_evaluation_only_coverage": float(group["delta_tess_evaluation_only_cover"].mean()),
        "mean_activation_rate_hat": float(group["activation_rate_hat"].mean()),
        "mean_pi_adaptive_hat": float(group["pi_adaptive_hat"].mean()),
        "mean_pi_comparator_hat": float(group["pi_comparator_hat"].mean()),
        "reference_variance_fraction_delta_pi": _safe_ratio(
            lambda_ratio * float(first["exact_reference_variance_delta_pi"]),
            float(first["exact_sqrt_n_variance_delta_pi"]),
        ),
        "reference_variance_fraction_delta_tess": _safe_ratio(
            lambda_ratio * float(first["exact_reference_variance_delta_tess"]),
            float(first["exact_sqrt_n_variance_delta_tess"]),
        ),
        "unpaired_diagnostic_outer_count": int(unpaired_pi.size),
        "delta_pi_mean_unpaired_bootstrap_sd": unpaired_pi_mean,
        "delta_pi_unpaired_to_paired_bootstrap_sd_ratio": _safe_ratio(
            unpaired_pi_mean, paired_pi_boot_sd
        ),
        "delta_tess_mean_unpaired_bootstrap_sd": unpaired_tess_mean,
        "delta_tess_unpaired_to_paired_bootstrap_sd_ratio": _safe_ratio(
            unpaired_tess_mean, paired_tess_boot_sd
        ),
    }


def _summarize(frame: pd.DataFrame) -> pd.DataFrame:
    rows = [
        _summarize_cell(group)
        for _, group in frame.groupby("cell_index", sort=True)
    ]
    return pd.DataFrame(rows).sort_values("cell_index").reset_index(drop=True)


def _within(value: float, bounds: list[float]) -> bool:
    return float(bounds[0]) <= float(value) <= float(bounds[1])


def _tier(row: pd.Series, config: dict[str, Any]) -> str:
    primary = config["primary_cells"]
    primary_designs = {
        (int(x["B"]), int(x["n"])) for x in primary["designs"]
    }
    if (
        row["dgp"] in primary["dgp_names"]
        and math.isclose(float(row["alpha"]), float(primary["alpha"]))
        and (int(row["B"]), int(row["n"])) in primary_designs
    ):
        return "primary"
    if int(row["B"]) >= int(config["main_regime"]["minimum_B"]):
        return "main"
    return "stress"


def _adjudicate(
    summary: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    criteria = config["success_criteria"]
    for _, row in summary.iterrows():
        tier = _tier(row, config)
        cell = {
            "dgp": row["dgp"],
            "B": int(row["B"]),
            "n": int(row["n"]),
            "alpha": float(row["alpha"]),
        }
        if tier == "stress":
            values = [
                row["delta_pi_mean"],
                row["delta_pi_empirical_variance"],
                row["delta_tess_mean"],
                row["delta_tess_empirical_variance"],
            ]
            finite = bool(np.isfinite(np.asarray(values, dtype=float)).all())
            checks.append(
                {
                    "cell": cell,
                    "tier": "stress_diagnostic",
                    "metric": "finite_outputs",
                    "value": finite,
                    "lower": None,
                    "upper": None,
                    "passed": finite,
                }
            )
            continue

        c = criteria[tier]
        metrics = {
            "delta_pi_standardized_bias": (
                row["delta_pi_standardized_bias"],
                [0.0, c["maximum_standardized_bias"]],
            ),
            "delta_tess_standardized_bias": (
                row["delta_tess_standardized_bias"],
                [0.0, c["maximum_standardized_bias"]],
            ),
            "delta_pi_variance_ratio": (
                row["delta_pi_empirical_to_exact_variance_ratio"],
                c["empirical_variance_ratio"],
            ),
            "delta_tess_variance_ratio": (
                row["delta_tess_empirical_to_exact_variance_ratio"],
                c["empirical_variance_ratio"],
            ),
            "delta_pi_bootstrap_sd_ratio": (
                row["delta_pi_bootstrap_sd_to_empirical_sd_ratio"],
                c["bootstrap_sd_ratio"],
            ),
            "delta_tess_bootstrap_sd_ratio": (
                row["delta_tess_bootstrap_sd_to_empirical_sd_ratio"],
                c["bootstrap_sd_ratio"],
            ),
            "delta_pi_oracle_coverage": (
                row["delta_pi_oracle_coverage"],
                c["coverage"],
            ),
            "delta_tess_oracle_coverage": (
                row["delta_tess_oracle_coverage"],
                c["coverage"],
            ),
            "delta_pi_bootstrap_normal_coverage": (
                row["delta_pi_bootstrap_normal_coverage"],
                c["coverage"],
            ),
            "delta_tess_bootstrap_normal_coverage": (
                row["delta_tess_bootstrap_normal_coverage"],
                c["coverage"],
            ),
        }
        for metric, (value, bounds) in metrics.items():
            checks.append(
                {
                    "cell": cell,
                    "tier": tier,
                    "metric": metric,
                    "value": float(value),
                    "lower": float(bounds[0]),
                    "upper": float(bounds[1]),
                    "passed": _within(float(value), bounds),
                }
            )

    summary_numeric = summary.select_dtypes(include=[np.number]).drop(
        columns=[
            "delta_pi_mean_unpaired_bootstrap_sd",
            "delta_pi_unpaired_to_paired_bootstrap_sd_ratio",
            "delta_tess_mean_unpaired_bootstrap_sd",
            "delta_tess_unpaired_to_paired_bootstrap_sd_ratio",
        ],
        errors="ignore",
    )
    finite_summary = bool(
        np.isfinite(summary_numeric.to_numpy(dtype=float)).all()
    )
    checks.append(
        {
            "cell": "global",
            "tier": "fatal",
            "metric": "all_required_summary_values_finite",
            "value": finite_summary,
            "lower": None,
            "upper": None,
            "passed": finite_summary,
        }
    )

    independent = summary[summary["dgp"] == "independent_normal"]
    max_independent_reference_fraction = float(
        independent["reference_variance_fraction_delta_tess"].abs().max()
    )
    near_zero = max_independent_reference_fraction <= float(
        criteria["global_diagnostics"]["independent_reference_fraction_tolerance"]
    )
    checks.append(
        {
            "cell": "global",
            "tier": "fatal",
            "metric": "independent_reference_fraction_near_zero",
            "value": max_independent_reference_fraction,
            "lower": 0.0,
            "upper": float(
                criteria["global_diagnostics"][
                    "independent_reference_fraction_tolerance"
                ]
            ),
            "passed": near_zero,
        }
    )

    gd = criteria["global_diagnostics"]
    dependent = summary[summary["dgp"] != "independent_normal"]
    below = int(
        (
            dependent["delta_tess_evaluation_only_coverage"]
            < gd["evaluation_only_coverage_below"]
        ).sum()
    )
    improved = int(
        (
            dependent["delta_tess_bootstrap_normal_coverage"]
            > dependent["delta_tess_evaluation_only_coverage"]
            + gd["minimum_bootstrap_normal_improvement"]
        ).sum()
    )
    checks.extend(
        [
            {
                "cell": "global",
                "tier": "diagnostic",
                "metric": "dependent_evaluation_only_cells_below_threshold",
                "value": below,
                "lower": int(gd["minimum_dependent_evaluation_only_cells_below"]),
                "upper": None,
                "passed": below
                >= int(gd["minimum_dependent_evaluation_only_cells_below"]),
            },
            {
                "cell": "global",
                "tier": "diagnostic",
                "metric": "dependent_paired_bootstrap_improvement_cell_count",
                "value": improved,
                "lower": int(gd["minimum_dependent_improved_cells"]),
                "upper": None,
                "passed": improved >= int(gd["minimum_dependent_improved_cells"]),
            },
        ]
    )

    failed_fatal = [
        x for x in checks if x["tier"] == "fatal" and not x["passed"]
    ]
    failed_science = [
        x
        for x in checks
        if x["tier"] in {"primary", "main"} and not x["passed"]
    ]
    status = "FAIL" if failed_fatal else ("REVIEW" if failed_science else "PASS")
    return status, checks


def _write_adjudication(
    path: Path,
    status: str,
    summary: pd.DataFrame,
    checks: list[dict[str, Any]],
    config: dict[str, Any],
    elapsed: float,
) -> None:
    failed = [
        x
        for x in checks
        if x["tier"] in {"primary", "main"} and not x["passed"]
    ]
    lines = [
        "# D4 Numerical Validation v1: Adjudication",
        "",
        f"**Status: {status}**",
        "",
        "This validation concerns the regular Work Package D4 paired budget-matched policy contrast. It is not direct evidence for the exact 20-candidate empirical pipeline.",
        "",
        "## Locked design",
        "",
        f"- DGPs: {[x['name'] for x in config['data_generating_laws']]}",
        f"- Outer repetitions per cell: {config['outer_repetitions']}",
        f"- Paired bootstrap repetitions per outer dataset: {config['bootstrap_repetitions']}",
        f"- Alpha grid: {config['alphas']}",
        f"- Designs: {config['designs']}",
        f"- Master seed: {config['master_seed']}",
        f"- Primary interval: {config['primary_interval']}",
        f"- Elapsed seconds: {elapsed:.3f}",
        "",
        "## Cell summary",
        "",
        "| DGP | B | n | alpha | Delta TESS truth | var ratio | paired boot SD ratio | paired boot-normal cov | eval-only cov | unpaired/paired SD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        unpaired_ratio = row["delta_tess_unpaired_to_paired_bootstrap_sd_ratio"]
        unpaired_text = "NA" if not math.isfinite(unpaired_ratio) else f"{unpaired_ratio:.3f}"
        lines.append(
            f"| {row['dgp']} | {int(row['B'])} | {int(row['n'])} | {row['alpha']:.3f} | "
            f"{row['delta_tess_truth']:.6f} | {row['delta_tess_empirical_to_exact_variance_ratio']:.3f} | "
            f"{row['delta_tess_bootstrap_sd_to_empirical_sd_ratio']:.3f} | "
            f"{row['delta_tess_bootstrap_normal_coverage']:.3f} | "
            f"{row['delta_tess_evaluation_only_coverage']:.3f} | {unpaired_text} |"
        )
    lines += ["", "## Failed primary/main checks", ""]
    if failed:
        lines.extend([f"- {x}" for x in failed])
    else:
        lines.append("None.")
    lines += [
        "",
        "## Interpretation",
        "",
        "PASS requires every prespecified primary and main-regime check for both the rejection-probability premium and the TESS contrast to pass. Stress cells and the deliberately unpaired bootstrap are diagnostic. REVIEW preserves all results for transparent inspection without automatically invalidating the theorem.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_manifest(
    outdir: Path,
    config_path: Path,
    config: dict[str, Any],
) -> None:
    manifest_path = outdir / "D4_VALIDATION_MANIFEST.json"
    files = []
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
        "source_git_commit": os.environ.get("D4_SOURCE_GIT_COMMIT", "unknown"),
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
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scientific numerical validation for Work Package D4"
    )
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

    frame.to_csv(
        outdir / "D4_VALIDATION_REPLICATIONS.csv.gz",
        index=False,
        compression="gzip",
    )
    summary.to_csv(outdir / "D4_VALIDATION_CELL_SUMMARY.csv", index=False)
    (outdir / "D4_VALIDATION_BENCHMARKS.json").write_text(
        json.dumps(benchmarks, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (outdir / "D4_VALIDATION_CHECKS.json").write_text(
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
            sum(
                1
                for x in checks
                if x["tier"] in {"primary", "main"} and not x["passed"]
            )
        ),
        "failed_diagnostic_check_count": int(
            sum(1 for x in checks if x["tier"] == "diagnostic" and not x["passed"])
        ),
        "master_seed": config["master_seed"],
    }
    (outdir / "D4_VALIDATION_SUMMARY.json").write_text(
        json.dumps(overall, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_adjudication(
        outdir / "D4_VALIDATION_ADJUDICATION.md",
        status,
        summary,
        checks,
        config,
        elapsed,
    )
    _write_manifest(outdir, config_path, config)

    print("D4 scientific numerical validation complete")
    print(f"Status: {status}")
    print(f"Cells: {len(summary)}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output directory: {outdir}")
    print(f"Adjudication: {outdir / 'D4_VALIDATION_ADJUDICATION.md'}")
    if status != "PASS" and config["status"] == "locked_before_run":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
