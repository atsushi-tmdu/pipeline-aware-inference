#!/usr/bin/env python3
"""
Phase 2A: signal-strength ladder for pipeline-aware performance calibration.

This script extends the exact-null pilot by adding ONE genuine continuous
predictor (X1) and keeping the remaining predictors unrelated to the outcome.
The theoretical univariable AUROC of X1 is prespecified as one of:

    0.50, 0.60, 0.70, 0.80, 0.95

For every signal strength, the complete analysis pipeline is repeated with:

    (a) LASSO feature selection
    (b) no feature selection

Seven candidate algorithms are trained, the winner is selected in the model-
selection set, and that same winner is re-evaluated in an untouched fresh test
set. The target-AUROC 0.50 scenario supplies the empirical pipeline-null
distribution used to calculate null-calibrated exceedance probabilities for
all other scenarios.

IMPORTANT
---------
Place this script in the same directory as:

    pipeline_null_pilot_v2.py

Example
-------
    python pipeline_signal_phase2.py --preset quick --n-jobs 16 \
        --output-root results_signal_phase2
"""

from __future__ import annotations

import os

# Avoid nested numerical-library parallelism when joblib parallelizes replicates.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time
import warnings
import zipfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

# Ensure repository-local package imports work when this file is run directly.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from joblib import Parallel, delayed
from scipy.stats import norm
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning

from simulations.phase1 import pipeline_null_pilot_v2 as base


TARGET_AUROCS = (0.50, 0.60, 0.70, 0.80, 0.95)
FEATURE_SELECTION_METHODS = ("lasso", "none")

PRESETS: dict[str, dict[str, int]] = {
    "smoke": {
        "repetitions": 20,
        "n_train": 300,
        "n_selection": 120,
        "n_test": 2_000,
        "cv_folds": 3,
    },
    "quick": {
        "repetitions": 500,
        "n_train": 500,
        "n_selection": 200,
        "n_test": 10_000,
        "cv_folds": 5,
    },
    "full": {
        "repetitions": 2_000,
        "n_train": 500,
        "n_selection": 200,
        "n_test": 20_000,
        "cv_folds": 5,
    },
}


def parse_float_list(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("AUROCs must be comma-separated numbers.") from exc
    if not values:
        raise argparse.ArgumentTypeError("At least one target AUROC is required.")
    for item in values:
        if not 0.5 <= item < 1.0:
            raise argparse.ArgumentTypeError(
                f"Each target AUROC must be in [0.50, 1.00); got {item}."
            )
    if 0.50 not in values:
        raise argparse.ArgumentTypeError(
            "The target list must include 0.50 because it defines the pipeline-null distribution."
        )
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Phase 2A one-signal-predictor simulation."
    )
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--n-train", type=int, default=None)
    parser.add_argument("--n-selection", type=int, default=None)
    parser.add_argument("--n-test", type=int, default=None)
    parser.add_argument("--n-features", type=int, default=30)
    parser.add_argument("--prevalence", type=float, default=0.10)
    parser.add_argument("--binary-fraction", type=float, default=0.40)
    parser.add_argument("--correlation-rho", type=float, default=0.30)
    parser.add_argument("--cv-folds", type=int, default=None)
    parser.add_argument(
        "--target-aurocs",
        type=parse_float_list,
        default=TARGET_AUROCS,
        help="Comma-separated target AUROCs; must include 0.50.",
    )
    parser.add_argument(
        "--feature-selection-methods",
        choices=("both", "lasso", "none"),
        default="both",
    )
    parser.add_argument("--master-seed", type=int, default=20260718)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument(
        "--output-root",
        default="results_signal_phase2",
        help="Parent folder for the timestamped result directory.",
    )
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    args.repetitions = args.repetitions or preset["repetitions"]
    args.n_train = args.n_train or preset["n_train"]
    args.n_selection = args.n_selection or preset["n_selection"]
    args.n_test = args.n_test or preset["n_test"]
    args.cv_folds = args.cv_folds or preset["cv_folds"]

    if args.feature_selection_methods == "both":
        args.feature_selection_methods = FEATURE_SELECTION_METHODS
    else:
        args.feature_selection_methods = (args.feature_selection_methods,)

    if args.repetitions < 2:
        raise ValueError("repetitions must be at least 2.")
    if args.n_features < 2:
        raise ValueError("n_features must be at least 2: one signal plus at least one noise predictor.")
    if not 0.0 < args.prevalence < 1.0:
        raise ValueError("prevalence must be between 0 and 1.")
    if not 0.0 <= args.binary_fraction <= 1.0:
        raise ValueError("binary_fraction must be in [0, 1].")
    if not -0.95 < args.correlation_rho < 0.95:
        raise ValueError("correlation_rho must be between -0.95 and 0.95.")
    if args.n_jobs == 0:
        raise ValueError("n_jobs cannot be 0.")

    n_train_events = base.event_count(args.n_train, args.prevalence)
    if min(n_train_events, args.n_train - n_train_events) < args.cv_folds:
        raise ValueError("Too few training observations in one class for the requested CV folds.")
    return args


def delta_from_auc(target_auc: float) -> float:
    """Normal-location shift giving AUC = Phi(delta / sqrt(2))."""
    if math.isclose(target_auc, 0.5):
        return 0.0
    return float(math.sqrt(2.0) * norm.ppf(target_auc))


def generate_noise_predictors(
    n: int,
    n_noise_features: int,
    total_features: int,
    binary_fraction: float,
    rho: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate outcome-independent correlated noise predictors."""
    latent = base.generate_latent_ar1(n, n_noise_features, rho, rng)
    desired_binary_total = int(round(total_features * binary_fraction))
    n_binary = min(n_noise_features, desired_binary_total)
    n_continuous = n_noise_features - n_binary
    x = latent.copy()
    if n_binary > 0:
        probabilities = base.binary_probabilities(n_binary)
        thresholds = norm.ppf(1.0 - probabilities)
        x[:, n_continuous:] = (
            latent[:, n_continuous:] > thresholds[np.newaxis, :]
        ).astype(float)
    return x.astype(np.float64, copy=False)


def generate_signal_dataset(
    n: int,
    prevalence: float,
    n_features: int,
    binary_fraction: float,
    rho: float,
    target_auc: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate one continuous signal predictor X1 plus outcome-independent noise.

    X1 | Y=0 ~ Normal(0, 1)
    X1 | Y=1 ~ Normal(delta, 1)
    """
    y = base.generate_fixed_outcome(n, prevalence, rng)
    delta = delta_from_auc(target_auc)
    signal = rng.normal(size=n) + delta * y
    noise = generate_noise_predictors(
        n=n,
        n_noise_features=n_features - 1,
        total_features=n_features,
        binary_fraction=binary_fraction,
        rho=rho,
        rng=rng,
    )
    x = np.column_stack([signal, noise])
    return x, y


def make_base_config(args: argparse.Namespace, feature_selection: str) -> base.SimulationConfig:
    return base.SimulationConfig(
        preset=args.preset,
        repetitions=args.repetitions,
        n_train=args.n_train,
        n_selection=args.n_selection,
        n_test=args.n_test,
        n_features=args.n_features,
        train_prevalence=args.prevalence,
        selection_prevalence=args.prevalence,
        test_prevalence=args.prevalence,
        binary_fraction=args.binary_fraction,
        correlation_rho=args.correlation_rho,
        feature_selection=feature_selection,
        cv_folds=args.cv_folds,
        selection_metric="roc_auc",
        master_seed=args.master_seed,
        n_jobs=args.n_jobs,
        reference_performance=None,
        output_root=args.output_root,
    )


def run_signal_replication(
    replication: int,
    seed: int,
    target_auc: float,
    feature_selection: str,
    args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed)
    config = make_base_config(args, feature_selection)

    x_train, y_train = generate_signal_dataset(
        args.n_train,
        args.prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        rng,
    )
    x_selection, y_selection = generate_signal_dataset(
        args.n_selection,
        args.prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        rng,
    )
    x_test, y_test = generate_signal_dataset(
        args.n_test,
        args.prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        rng,
    )

    selected_indices, selector_info = base.select_predictors(
        x_train, y_train, config, seed
    )
    selected_feature_count = int(len(selected_indices))
    signal_included = bool(np.any(selected_indices == 0))
    signal_selected = signal_included if feature_selection == "lasso" else np.nan
    noise_selected_count = int(selected_feature_count - int(signal_included))

    model_rows: list[dict[str, Any]] = []
    if selected_feature_count == 0:
        dummy, _ = base.make_dummy_model(y_train)
        x_selection_selected = np.zeros((args.n_selection, 1), dtype=float)
        x_test_selected = np.zeros((args.n_test, 1), dtype=float)
        for model_name in base.MODEL_NAMES:
            selection_metrics = base.evaluate_model(dummy, x_selection_selected, y_selection)
            test_metrics = base.evaluate_model(dummy, x_test_selected, y_test)
            row: dict[str, Any] = {
                "replication": replication,
                "seed": seed,
                "target_auc": target_auc,
                "feature_selection": feature_selection,
                "model": model_name,
                "intercept_only": True,
                "error": None,
            }
            row.update({f"selection_{k}": v for k, v in selection_metrics.items()})
            row.update({f"test_{k}": v for k, v in test_metrics.items()})
            model_rows.append(row)
    else:
        x_train_selected = x_train[:, selected_indices]
        x_selection_selected = x_selection[:, selected_indices]
        x_test_selected = x_test[:, selected_indices]
        candidate_models = base.build_candidate_models(seed)

        for model_name in base.MODEL_NAMES:
            estimator = candidate_models[model_name]
            row = {
                "replication": replication,
                "seed": seed,
                "target_auc": target_auc,
                "feature_selection": feature_selection,
                "model": model_name,
                "intercept_only": False,
                "error": None,
            }
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=ConvergenceWarning)
                    warnings.simplefilter("ignore", category=FutureWarning)
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    estimator.fit(x_train_selected, y_train)
                selection_metrics = base.evaluate_model(
                    estimator, x_selection_selected, y_selection
                )
                test_metrics = base.evaluate_model(estimator, x_test_selected, y_test)
                row.update({f"selection_{k}": v for k, v in selection_metrics.items()})
                row.update({f"test_{k}": v for k, v in test_metrics.items()})
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                for metric in base.METRIC_COLUMNS:
                    row[f"selection_{metric}"] = float("nan")
                    row[f"test_{metric}"] = float("nan")
            model_rows.append(row)

    valid_rows = [
        row
        for row in model_rows
        if row["error"] is None and math.isfinite(float(row["selection_roc_auc"]))
    ]
    if not valid_rows:
        raise RuntimeError(
            f"All models failed: target_auc={target_auc}, feature_selection={feature_selection}, "
            f"replication={replication}."
        )

    best_row = max(valid_rows, key=lambda row: float(row["selection_roc_auc"]))
    best_selection_score = float(best_row["selection_roc_auc"])
    selected_test_score = float(best_row["test_roc_auc"])

    rep_row: dict[str, Any] = {
        "replication": replication,
        "seed": seed,
        "target_auc": target_auc,
        "delta": delta_from_auc(target_auc),
        "feature_selection": feature_selection,
        "selected_feature_count": selected_feature_count,
        "signal_included": signal_included,
        "signal_selected": signal_selected,
        "noise_selected_count": noise_selected_count,
        "selected_features": "|".join(str(i + 1) for i in selected_indices),
        "lasso_selected_c": selector_info["lasso_selected_c"],
        "selector_error": selector_info["selector_error"],
        "best_model": best_row["model"],
        "best_selection_score": best_selection_score,
        "selected_model_test_score": selected_test_score,
        "selection_induced_optimism": best_selection_score - selected_test_score,
        "fresh_test_bias_from_target": selected_test_score - target_auc,
        "n_model_failures": len(model_rows) - len(valid_rows),
    }
    for metric in base.METRIC_COLUMNS:
        rep_row[f"best_model_selection_{metric}"] = best_row[f"selection_{metric}"]
        rep_row[f"best_model_test_{metric}"] = best_row[f"test_{metric}"]

    pool_rows = base.pool_size_analysis(model_rows, "roc_auc", replication)
    for row in pool_rows:
        row["target_auc"] = target_auc
        row["feature_selection"] = feature_selection
    return rep_row, model_rows, pool_rows


def add_null_calibration(rep_df: pd.DataFrame) -> pd.DataFrame:
    """Add empirical pipeline-null p values separately by feature-selection method."""
    result = rep_df.copy()
    result["pipeline_null_exceedance_p"] = np.nan
    result["pipeline_null_percentile"] = np.nan
    result["standardized_distance_from_null_median"] = np.nan
    result["null_relative_gain"] = np.nan

    for method, method_idx in result.groupby("feature_selection").groups.items():
        method_rows = result.loc[method_idx]
        null_mask = np.isclose(method_rows["target_auc"].to_numpy(dtype=float), 0.50)
        null_index = method_rows.index[null_mask]
        null_scores = result.loc[null_index, "best_selection_score"].to_numpy(dtype=float)
        if len(null_scores) < 2:
            raise RuntimeError(f"Insufficient null replications for {method}.")
        null_median = float(np.median(null_scores))
        null_sd = float(np.std(null_scores, ddof=1))

        for idx in method_rows.index:
            score = float(result.at[idx, "best_selection_score"])
            is_null_row = math.isclose(float(result.at[idx, "target_auc"]), 0.50)
            if is_null_row:
                others = null_scores[result.loc[null_index].index.to_numpy() != idx]
                exceed = int(np.sum(others >= score))
                p_value = (1.0 + exceed) / (1.0 + len(others))
                percentile = (
                    np.sum(others < score) + 0.5 * np.sum(others == score)
                ) / len(others)
            else:
                exceed = int(np.sum(null_scores >= score))
                p_value = (1.0 + exceed) / (1.0 + len(null_scores))
                percentile = (
                    np.sum(null_scores < score) + 0.5 * np.sum(null_scores == score)
                ) / len(null_scores)

            result.at[idx, "pipeline_null_exceedance_p"] = p_value
            result.at[idx, "pipeline_null_percentile"] = percentile
            result.at[idx, "standardized_distance_from_null_median"] = (
                (score - null_median) / null_sd if null_sd > 0 else np.nan
            )
            result.at[idx, "null_relative_gain"] = (
                (score - null_median) / (1.0 - null_median)
                if null_median < 1.0
                else np.nan
            )
    return result


def quantile(series: pd.Series, q: float) -> float:
    return float(pd.to_numeric(series, errors="coerce").dropna().quantile(q))


def build_scenario_summary(rep_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (target_auc, method), group in rep_df.groupby(
        ["target_auc", "feature_selection"], sort=True
    ):
        rows.append(
            {
                "target_auc": float(target_auc),
                "feature_selection": method,
                "repetitions": int(len(group)),
                "mean_best_selection_auc": float(group["best_selection_score"].mean()),
                "median_best_selection_auc": float(group["best_selection_score"].median()),
                "q025_best_selection_auc": quantile(group["best_selection_score"], 0.025),
                "q975_best_selection_auc": quantile(group["best_selection_score"], 0.975),
                "mean_fresh_test_auc": float(group["selected_model_test_score"].mean()),
                "median_fresh_test_auc": float(group["selected_model_test_score"].median()),
                "q025_fresh_test_auc": quantile(group["selected_model_test_score"], 0.025),
                "q975_fresh_test_auc": quantile(group["selected_model_test_score"], 0.975),
                "mean_optimism": float(group["selection_induced_optimism"].mean()),
                "median_optimism": float(group["selection_induced_optimism"].median()),
                "mean_fresh_test_bias_from_target": float(
                    group["fresh_test_bias_from_target"].mean()
                ),
                "pipeline_detection_rate_p_lt_0_05": float(
                    (group["pipeline_null_exceedance_p"] < 0.05).mean()
                ),
                "pipeline_detection_rate_p_lt_0_01": float(
                    (group["pipeline_null_exceedance_p"] < 0.01).mean()
                ),
                "median_pipeline_null_p": float(
                    group["pipeline_null_exceedance_p"].median()
                ),
                "median_null_percentile": float(
                    group["pipeline_null_percentile"].median()
                ),
                "mean_null_relative_gain": float(group["null_relative_gain"].mean()),
                "signal_selection_rate": (
                    float(group["signal_selected"].mean())
                    if group["signal_selected"].notna().any()
                    else np.nan
                ),
                "mean_noise_selected": float(group["noise_selected_count"].mean()),
                "mean_total_selected": float(group["selected_feature_count"].mean()),
                "proportion_no_features_selected": float(
                    (group["selected_feature_count"] == 0).mean()
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["feature_selection", "target_auc"])


def build_pool_summary(pool_df: pd.DataFrame) -> pd.DataFrame:
    return (
        pool_df.groupby(["target_auc", "feature_selection", "pool_size"], as_index=False)
        .agg(
            mean_max_selection_auc=("mean_max_selection_score", "mean"),
            mean_selected_test_auc=("mean_selected_test_score", "mean"),
            mean_optimism=("mean_optimism", "mean"),
        )
        .sort_values(["feature_selection", "target_auc", "pool_size"])
    )


def create_plots(
    scenario_df: pd.DataFrame,
    pool_summary_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    for method in scenario_df["feature_selection"].unique():
        data = scenario_df[scenario_df["feature_selection"] == method].sort_values(
            "target_auc"
        )
        plt.figure(figsize=(8, 5))
        plt.plot(data["target_auc"], data["mean_best_selection_auc"], marker="o", label="Selected maximum in model-selection set")
        plt.plot(data["target_auc"], data["mean_fresh_test_auc"], marker="o", label="Untouched fresh-test AUROC")
        plt.plot(data["target_auc"], data["target_auc"], linestyle="--", label="Prespecified signal AUROC")
        plt.xlabel("Prespecified AUROC of the true predictor")
        plt.ylabel("AUROC")
        plt.title(f"Signal ladder: {method} feature selection")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"01_signal_ladder_{method}.png", dpi=180)
        plt.close()

    plt.figure(figsize=(8, 5))
    for method in scenario_df["feature_selection"].unique():
        data = scenario_df[scenario_df["feature_selection"] == method].sort_values(
            "target_auc"
        )
        plt.plot(data["target_auc"], data["mean_optimism"], marker="o", label=method)
    plt.axhline(0.0, linestyle="--", linewidth=1.2)
    plt.xlabel("Prespecified AUROC of the true predictor")
    plt.ylabel("Mean selection-induced optimism")
    plt.title("Performance inflation across signal strengths")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "02_signal_strength_vs_optimism.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    for method in scenario_df["feature_selection"].unique():
        data = scenario_df[scenario_df["feature_selection"] == method].sort_values(
            "target_auc"
        )
        plt.plot(
            data["target_auc"],
            data["pipeline_detection_rate_p_lt_0_05"],
            marker="o",
            label=method,
        )
    plt.axhline(0.05, linestyle="--", linewidth=1.2, label="Nominal 5%")
    plt.xlabel("Prespecified AUROC of the true predictor")
    plt.ylabel("Proportion with pipeline-null p < 0.05")
    plt.title("Null-calibrated detection across signal strengths")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "03_signal_strength_vs_detection_rate.png", dpi=180)
    plt.close()

    lasso = scenario_df[scenario_df["feature_selection"] == "lasso"].sort_values(
        "target_auc"
    )
    if not lasso.empty:
        plt.figure(figsize=(8, 5))
        plt.plot(lasso["target_auc"], lasso["signal_selection_rate"], marker="o")
        plt.xlabel("Prespecified AUROC of the true predictor")
        plt.ylabel("Probability LASSO retained X1")
        plt.title("Recovery of the genuine predictor by LASSO")
        plt.ylim(-0.02, 1.02)
        plt.tight_layout()
        plt.savefig(output_dir / "04_lasso_signal_recovery.png", dpi=180)
        plt.close()

    for method in pool_summary_df["feature_selection"].unique():
        plt.figure(figsize=(8, 5))
        method_data = pool_summary_df[
            pool_summary_df["feature_selection"] == method
        ]
        for target_auc in sorted(method_data["target_auc"].unique()):
            data = method_data[method_data["target_auc"] == target_auc].sort_values(
                "pool_size"
            )
            plt.plot(
                data["pool_size"],
                data["mean_optimism"],
                marker="o",
                label=f"True-predictor AUC {target_auc:.2f}",
            )
        plt.axhline(0.0, linestyle="--", linewidth=1.2)
        plt.xlabel("Number of candidate algorithms")
        plt.ylabel("Mean selection-induced optimism")
        plt.title(f"Algorithm-pool size and optimism: {method}")
        plt.xticks(sorted(method_data["pool_size"].unique()))
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"05_pool_size_optimism_{method}.png", dpi=180)
        plt.close()


def write_summary_text(
    args: argparse.Namespace,
    scenario_df: pd.DataFrame,
    elapsed_seconds: float,
    output_path: Path,
) -> None:
    lines = [
        "PHASE 2A: ONE TRUE PREDICTOR SIGNAL LADDER",
        "=" * 49,
        "",
        f"Preset: {args.preset}",
        f"Replications per scenario: {args.repetitions}",
        f"Train / selection / test N: {args.n_train} / {args.n_selection} / {args.n_test}",
        f"Prevalence: {args.prevalence:.3f}",
        f"Candidate predictors: {args.n_features} (X1 signal + {args.n_features - 1} noise)",
        f"Candidate algorithms: {len(base.MODEL_NAMES)}",
        f"Target AUROCs: {', '.join(f'{x:.2f}' for x in args.target_aurocs)}",
        f"Feature-selection methods: {', '.join(args.feature_selection_methods)}",
        "",
        "Scenario results",
        "----------------",
    ]
    for _, row in scenario_df.iterrows():
        lines.extend(
            [
                (
                    f"Target AUC {row['target_auc']:.2f}; {row['feature_selection']}: "
                    f"selection={row['mean_best_selection_auc']:.4f}, "
                    f"fresh test={row['mean_fresh_test_auc']:.4f}, "
                    f"optimism={row['mean_optimism']:.4f}, "
                    f"P(p_pipeline<0.05)={row['pipeline_detection_rate_p_lt_0_05']:.3f}"
                    + (
                        f", signal selected={row['signal_selection_rate']:.3f}"
                        if row['feature_selection'] == 'lasso'
                        else ", signal included by design"
                    )
                )
            ]
        )
    lines.extend(
        [
            "",
            f"Elapsed time: {elapsed_seconds:.1f} seconds",
            "",
            "Interpretation guardrail:",
            "The target AUROC describes the population-level discrimination of X1 alone.",
            "The selected multivariable pipeline may have a different fresh-test AUROC because",
            "the fitted algorithms use finite training data and may include noise predictors.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def environment_info() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": base.platform.platform(),
        "processor": base.platform.processor(),
        "cpu_count": os.cpu_count(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "matplotlib": matplotlib.__version__,
        "joblib": joblib.__version__,
    }


def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in directory.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(directory.parent))
    return zip_path


def main() -> None:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"pipeline_signal_{args.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=False)

    config_for_json = vars(args).copy()
    config_for_json["target_aurocs"] = list(args.target_aurocs)
    config_for_json["feature_selection_methods"] = list(args.feature_selection_methods)
    (output_dir / "config.json").write_text(
        json.dumps(config_for_json, indent=2, cls=base.NumpyJSONEncoder),
        encoding="utf-8",
    )
    (output_dir / "environment.json").write_text(
        json.dumps(environment_info(), indent=2, cls=base.NumpyJSONEncoder),
        encoding="utf-8",
    )

    seed_sequence = np.random.SeedSequence(args.master_seed)
    child_sequences = seed_sequence.spawn(args.repetitions)
    seeds = [int(s.generate_state(1, dtype=np.uint32)[0]) for s in child_sequences]

    scenario_list = [
        (target_auc, method)
        for target_auc in args.target_aurocs
        for method in args.feature_selection_methods
    ]

    print("Starting Phase 2A signal-strength simulation")
    print(f"  scenarios={len(scenario_list)}")
    print(f"  repetitions per scenario={args.repetitions}")
    print(f"  n_jobs={args.n_jobs}")
    print(f"  output={output_dir}")
    print()

    start = time.perf_counter()
    all_results: list[
        tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]
    ] = []

    for scenario_number, (target_auc, method) in enumerate(scenario_list, start=1):
        print(
            f"Scenario {scenario_number}/{len(scenario_list)}: "
            f"target_auc={target_auc:.2f}, feature_selection={method}"
        )
        scenario_results = Parallel(n_jobs=args.n_jobs, backend="loky", verbose=3)(
            delayed(run_signal_replication)(
                replication=i + 1,
                seed=seeds[i],
                target_auc=target_auc,
                feature_selection=method,
                args=args,
            )
            for i in range(args.repetitions)
        )
        all_results.extend(scenario_results)

    elapsed = time.perf_counter() - start

    rep_rows = [item[0] for item in all_results]
    model_rows = [row for item in all_results for row in item[1]]
    pool_rows = [row for item in all_results for row in item[2]]

    rep_df = pd.DataFrame(rep_rows).sort_values(
        ["feature_selection", "target_auc", "replication"]
    )
    model_df = pd.DataFrame(model_rows).sort_values(
        ["feature_selection", "target_auc", "replication", "model"]
    )
    pool_df = pd.DataFrame(pool_rows).sort_values(
        ["feature_selection", "target_auc", "replication", "pool_size"]
    )

    rep_df = add_null_calibration(rep_df)
    scenario_df = build_scenario_summary(rep_df)
    pool_summary_df = build_pool_summary(pool_df)

    # Recreate the directory immediately before final writes, matching v2 safeguards.
    output_dir.mkdir(parents=True, exist_ok=True)
    rep_df.to_csv(output_dir / "replication_results.csv", index=False)
    model_df.to_csv(output_dir / "model_level_results.csv", index=False)
    pool_df.to_csv(output_dir / "pool_size_results.csv", index=False)
    scenario_df.to_csv(output_dir / "scenario_summary.csv", index=False)
    pool_summary_df.to_csv(output_dir / "pool_size_summary.csv", index=False)

    create_plots(scenario_df, pool_summary_df, output_dir)
    write_summary_text(args, scenario_df, elapsed, output_dir / "summary.txt")

    summary_json = {
        "study": "Phase 2A one-true-predictor signal-strength ladder",
        "config": config_for_json,
        "elapsed_seconds": elapsed,
        "scenario_summary": scenario_df.to_dict(orient="records"),
        "pool_size_summary": pool_summary_df.to_dict(orient="records"),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary_json, indent=2, cls=base.NumpyJSONEncoder),
        encoding="utf-8",
    )

    zip_path = zip_directory(output_dir)
    print()
    print("Completed successfully.")
    print(f"Results directory: {output_dir}")
    print(f"Shareable ZIP:      {zip_path}")


if __name__ == "__main__":
    main()
