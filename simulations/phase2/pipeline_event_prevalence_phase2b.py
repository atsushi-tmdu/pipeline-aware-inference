#!/usr/bin/env python3
"""
Phase 2B: separate the effects of model-selection event count and outcome prevalence.

Purpose
-------
This simulation asks whether selection-induced performance inflation is driven
primarily by:

    1) the number of outcome events available in the model-selection set, or
    2) the event prevalence / class balance in that set.

The training set and untouched fresh-test set are held FIXED across all
model-selection-set designs within each Monte Carlo replication. Only the
model-selection set changes. This makes the comparison deliberately paired and
isolates the information available for choosing the apparent "best" algorithm.

Default pilot design
--------------------
Selection-set event counts: 20, 100
Selection-set prevalences:  0.05, 0.50
True-predictor AUROCs:      0.50, 0.70
Feature selection:          LASSO, none
Candidate algorithms:       seven algorithms from pipeline_null_pilot_v2.py

The resulting selection-set sample sizes are:

    20 events at 5%   -> N = 400
    20 events at 50%  -> N = 40
    100 events at 5%  -> N = 2,000
    100 events at 50% -> N = 200

For each replication and target signal strength, the same training and fresh-
test data are used for every event-count/prevalence condition. The same fitted
candidate models are then evaluated in each model-selection set. The winning
model is selected separately in each model-selection set and evaluated in the
same untouched fresh-test set.

IMPORTANT
---------
Shared dependencies are resolved from the repository simulation directories.

Example
-------
    python pipeline_event_prevalence_phase2b.py --preset quick --n-jobs 16 \
        --output-root results_phase2b
"""

from __future__ import annotations

import os

# Prevent nested BLAS / OpenMP parallelism inside joblib worker processes.
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
from datetime import datetime
from pathlib import Path

# Repository-local import path for shared simulation code.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_PHASE1_DIR = _REPO_ROOT / 'simulations' / 'phase1'
if str(_PHASE1_DIR) not in sys.path:
    sys.path.insert(0, str(_PHASE1_DIR))
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
from sklearn.exceptions import ConvergenceWarning

try:
    import pipeline_null_pilot_v2 as base
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_null_pilot_v2.py was not found. Place this Phase 2B script "
        "in the same directory as pipeline_null_pilot_v2.py and run it there."
    ) from exc


DEFAULT_EVENT_COUNTS = (20, 100)
DEFAULT_SELECTION_PREVALENCES = (0.05, 0.50)
DEFAULT_TARGET_AUROCS = (0.50, 0.70)
DEFAULT_FEATURE_SELECTION_METHODS = ("lasso", "none")

PRESETS: dict[str, dict[str, int]] = {
    "smoke": {
        "repetitions": 10,
        "n_train": 300,
        "n_test": 2_000,
        "cv_folds": 3,
    },
    "quick": {
        "repetitions": 500,
        "n_train": 500,
        "n_test": 10_000,
        "cv_folds": 5,
    },
    "full": {
        "repetitions": 2_000,
        "n_train": 500,
        "n_test": 20_000,
        "cv_folds": 5,
    },
}


def parse_int_list(value: str) -> tuple[int, ...]:
    try:
        values = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Values must be comma-separated positive integers."
        ) from exc
    if not values or any(item <= 0 for item in values):
        raise argparse.ArgumentTypeError("All event counts must be positive integers.")
    return tuple(sorted(set(values)))


def parse_prevalence_list(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Prevalences must be comma-separated numbers."
        ) from exc
    if not values or any(not 0.0 < item < 1.0 for item in values):
        raise argparse.ArgumentTypeError("Every prevalence must lie strictly between 0 and 1.")
    return tuple(sorted(set(values)))


def parse_auc_list(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("AUROCs must be comma-separated numbers.") from exc
    if not values:
        raise argparse.ArgumentTypeError("At least one target AUROC is required.")
    if any(not 0.50 <= item < 1.0 for item in values):
        raise argparse.ArgumentTypeError("Each target AUROC must be in [0.50, 1.00).")
    if not any(math.isclose(item, 0.50) for item in values):
        raise argparse.ArgumentTypeError(
            "The target list must include 0.50 to define each pipeline-null distribution."
        )
    return tuple(sorted(set(values)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 2B factorial pilot separating model-selection event count "
            "from model-selection outcome prevalence."
        )
    )
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--n-train", type=int, default=None)
    parser.add_argument("--train-prevalence", type=float, default=0.10)
    parser.add_argument("--n-test", type=int, default=None)
    parser.add_argument("--test-prevalence", type=float, default=0.10)
    parser.add_argument("--n-features", type=int, default=30)
    parser.add_argument("--binary-fraction", type=float, default=0.40)
    parser.add_argument("--correlation-rho", type=float, default=0.30)
    parser.add_argument("--cv-folds", type=int, default=None)
    parser.add_argument(
        "--event-counts",
        type=parse_int_list,
        default=DEFAULT_EVENT_COUNTS,
        help="Comma-separated event counts in each model-selection set.",
    )
    parser.add_argument(
        "--selection-prevalences",
        type=parse_prevalence_list,
        default=DEFAULT_SELECTION_PREVALENCES,
        help="Comma-separated event prevalences in each model-selection set.",
    )
    parser.add_argument(
        "--target-aurocs",
        type=parse_auc_list,
        default=DEFAULT_TARGET_AUROCS,
        help="Comma-separated AUROCs of X1 alone; must include 0.50.",
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
        default="results_phase2b",
        help="Parent directory for the timestamped result directory.",
    )
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    args.repetitions = args.repetitions or preset["repetitions"]
    args.n_train = args.n_train or preset["n_train"]
    args.n_test = args.n_test or preset["n_test"]
    args.cv_folds = args.cv_folds or preset["cv_folds"]

    if args.feature_selection_methods == "both":
        args.feature_selection_methods = DEFAULT_FEATURE_SELECTION_METHODS
    else:
        args.feature_selection_methods = (args.feature_selection_methods,)

    if args.repetitions < 2:
        raise ValueError("repetitions must be at least 2.")
    if args.n_features < 2:
        raise ValueError("n_features must include X1 plus at least one noise predictor.")
    if not 0.0 < args.train_prevalence < 1.0:
        raise ValueError("train_prevalence must be between 0 and 1.")
    if not 0.0 < args.test_prevalence < 1.0:
        raise ValueError("test_prevalence must be between 0 and 1.")
    if not 0.0 <= args.binary_fraction <= 1.0:
        raise ValueError("binary_fraction must lie in [0, 1].")
    if not -0.95 < args.correlation_rho < 0.95:
        raise ValueError("correlation_rho must lie between -0.95 and 0.95.")
    if args.n_jobs == 0:
        raise ValueError("n_jobs cannot be 0.")

    n_train_events = base.event_count(args.n_train, args.train_prevalence)
    if min(n_train_events, args.n_train - n_train_events) < args.cv_folds:
        raise ValueError("Too few training observations in one class for the requested CV folds.")

    selection_designs: list[dict[str, Any]] = []
    for event_count in args.event_counts:
        for prevalence in args.selection_prevalences:
            raw_n = event_count / prevalence
            n_selection = int(round(raw_n))
            if not math.isclose(raw_n, n_selection, rel_tol=0.0, abs_tol=1e-9):
                raise ValueError(
                    f"event_count={event_count} and prevalence={prevalence} do not "
                    "produce an integer model-selection sample size."
                )
            if n_selection <= event_count:
                raise ValueError("Every model-selection set must contain at least one non-event.")
            observed_events = base.event_count(n_selection, prevalence)
            if observed_events != event_count:
                raise ValueError(
                    f"Internal rounding mismatch: requested {event_count} events but "
                    f"generated count would be {observed_events}."
                )
            selection_designs.append(
                {
                    "selection_event_count": int(event_count),
                    "selection_prevalence": float(prevalence),
                    "n_selection": int(n_selection),
                    "selection_non_event_count": int(n_selection - event_count),
                }
            )
    args.selection_designs = selection_designs
    return args


def delta_from_auc(target_auc: float) -> float:
    """Normal-location shift satisfying AUC = Phi(delta / sqrt(2))."""
    if math.isclose(target_auc, 0.50):
        return 0.0
    return float(math.sqrt(2.0) * norm.ppf(target_auc))


def make_rng(seed: int, *keys: int) -> np.random.Generator:
    """Create a deterministic independent random stream from integer keys."""
    sequence = np.random.SeedSequence([int(seed), *[int(key) for key in keys]])
    return np.random.default_rng(sequence)


def generate_noise_predictors(
    n: int,
    n_noise_features: int,
    total_features: int,
    binary_fraction: float,
    rho: float,
    rng: np.random.Generator,
) -> np.ndarray:
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
    """Generate X1 with a known univariable AUROC plus independent noise features."""
    y = base.generate_fixed_outcome(n, prevalence, rng)
    signal = rng.normal(size=n) + delta_from_auc(target_auc) * y
    noise = generate_noise_predictors(
        n=n,
        n_noise_features=n_features - 1,
        total_features=n_features,
        binary_fraction=binary_fraction,
        rho=rho,
        rng=rng,
    )
    return np.column_stack([signal, noise]), y


def make_base_config(args: argparse.Namespace, feature_selection: str) -> base.SimulationConfig:
    # n_selection and selection prevalence are placeholders because selection
    # designs are handled explicitly in this script.
    first_design = args.selection_designs[0]
    return base.SimulationConfig(
        preset=args.preset,
        repetitions=args.repetitions,
        n_train=args.n_train,
        n_selection=first_design["n_selection"],
        n_test=args.n_test,
        n_features=args.n_features,
        train_prevalence=args.train_prevalence,
        selection_prevalence=first_design["selection_prevalence"],
        test_prevalence=args.test_prevalence,
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


def blank_metrics(prefix: str) -> dict[str, float]:
    return {f"{prefix}_{metric}": float("nan") for metric in base.METRIC_COLUMNS}


def run_replication_bundle(
    replication: int,
    seed: int,
    target_auc: float,
    feature_selection: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Fit one candidate-model pool, then select a winner separately in every
    event-count/prevalence model-selection set.
    """
    config = make_base_config(args, feature_selection)

    # Training and fresh-test data are identical across all selection designs.
    # Their underlying random draws are also paired across target-AUC and
    # feature-selection conditions; only delta or the selection method changes.
    x_train, y_train = generate_signal_dataset(
        args.n_train,
        args.train_prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        make_rng(seed, 1),
    )
    x_test, y_test = generate_signal_dataset(
        args.n_test,
        args.test_prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        make_rng(seed, 2),
    )

    selected_indices, selector_info = base.select_predictors(
        x_train, y_train, config, seed
    )
    selected_feature_count = int(len(selected_indices))
    signal_included = bool(np.any(selected_indices == 0))
    signal_selected = signal_included if feature_selection == "lasso" else np.nan
    noise_selected_count = int(selected_feature_count - int(signal_included))

    fitted_models: dict[str, dict[str, Any]] = {}
    if selected_feature_count == 0:
        dummy, _ = base.make_dummy_model(y_train)
        x_test_selected = np.zeros((args.n_test, 1), dtype=float)
        test_metrics = base.evaluate_model(dummy, x_test_selected, y_test)
        for model_name in base.MODEL_NAMES:
            fitted_models[model_name] = {
                "estimator": dummy,
                "intercept_only": True,
                "error": None,
                "test_metrics": test_metrics,
            }
    else:
        x_train_selected = x_train[:, selected_indices]
        x_test_selected = x_test[:, selected_indices]
        candidate_models = base.build_candidate_models(seed)
        for model_name in base.MODEL_NAMES:
            estimator = candidate_models[model_name]
            model_info: dict[str, Any] = {
                "estimator": estimator,
                "intercept_only": False,
                "error": None,
                "test_metrics": None,
            }
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=ConvergenceWarning)
                    warnings.simplefilter("ignore", category=FutureWarning)
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    estimator.fit(x_train_selected, y_train)
                model_info["test_metrics"] = base.evaluate_model(
                    estimator, x_test_selected, y_test
                )
            except Exception as exc:
                model_info["error"] = f"{type(exc).__name__}: {exc}"
            fitted_models[model_name] = model_info

    rep_rows: list[dict[str, Any]] = []
    all_model_rows: list[dict[str, Any]] = []
    all_pool_rows: list[dict[str, Any]] = []

    for design_index, design in enumerate(args.selection_designs, start=1):
        event_count = int(design["selection_event_count"])
        prevalence = float(design["selection_prevalence"])
        n_selection = int(design["n_selection"])

        # Exclude target_auc and feature-selection method from this seed so the
        # same base selection data are paired across those conditions.
        prevalence_key = int(round(prevalence * 1_000_000))
        x_selection, y_selection = generate_signal_dataset(
            n_selection,
            prevalence,
            args.n_features,
            args.binary_fraction,
            args.correlation_rho,
            target_auc,
            make_rng(seed, 100, event_count, prevalence_key),
        )

        if selected_feature_count == 0:
            x_selection_selected = np.zeros((n_selection, 1), dtype=float)
        else:
            x_selection_selected = x_selection[:, selected_indices]

        scenario_model_rows: list[dict[str, Any]] = []
        for model_name in base.MODEL_NAMES:
            info = fitted_models[model_name]
            row: dict[str, Any] = {
                "replication": replication,
                "seed": seed,
                "target_auc": float(target_auc),
                "feature_selection": feature_selection,
                "selection_event_count": event_count,
                "selection_non_event_count": int(n_selection - event_count),
                "selection_prevalence": prevalence,
                "n_selection": n_selection,
                "model": model_name,
                "intercept_only": bool(info["intercept_only"]),
                "error": info["error"],
            }
            if info["error"] is None:
                try:
                    selection_metrics = base.evaluate_model(
                        info["estimator"], x_selection_selected, y_selection
                    )
                    test_metrics = info["test_metrics"]
                    row.update(
                        {f"selection_{key}": value for key, value in selection_metrics.items()}
                    )
                    row.update({f"test_{key}": value for key, value in test_metrics.items()})
                except Exception as exc:
                    row["error"] = f"{type(exc).__name__}: {exc}"
                    row.update(blank_metrics("selection"))
                    row.update(blank_metrics("test"))
            else:
                row.update(blank_metrics("selection"))
                row.update(blank_metrics("test"))
            scenario_model_rows.append(row)
            all_model_rows.append(row)

        valid_rows = [
            row
            for row in scenario_model_rows
            if row["error"] is None
            and math.isfinite(float(row["selection_roc_auc"]))
            and math.isfinite(float(row["test_roc_auc"]))
        ]
        if not valid_rows:
            raise RuntimeError(
                "All models failed for "
                f"replication={replication}, target_auc={target_auc}, "
                f"feature_selection={feature_selection}, events={event_count}, "
                f"prevalence={prevalence}."
            )

        best_row = max(valid_rows, key=lambda row: float(row["selection_roc_auc"]))
        best_selection_score = float(best_row["selection_roc_auc"])
        selected_test_score = float(best_row["test_roc_auc"])

        rep_row: dict[str, Any] = {
            "replication": replication,
            "seed": seed,
            "target_auc": float(target_auc),
            "delta": delta_from_auc(target_auc),
            "feature_selection": feature_selection,
            "selection_event_count": event_count,
            "selection_non_event_count": int(n_selection - event_count),
            "selection_prevalence": prevalence,
            "n_selection": n_selection,
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
            "n_model_failures": len(scenario_model_rows) - len(valid_rows),
        }
        for metric in base.METRIC_COLUMNS:
            rep_row[f"best_model_selection_{metric}"] = best_row[f"selection_{metric}"]
            rep_row[f"best_model_test_{metric}"] = best_row[f"test_{metric}"]
        rep_rows.append(rep_row)

        pool_rows = base.pool_size_analysis(
            scenario_model_rows, "roc_auc", replication
        )
        for row in pool_rows:
            row.update(
                {
                    "target_auc": float(target_auc),
                    "feature_selection": feature_selection,
                    "selection_event_count": event_count,
                    "selection_prevalence": prevalence,
                    "n_selection": n_selection,
                }
            )
        all_pool_rows.extend(pool_rows)

    return rep_rows, all_model_rows, all_pool_rows


def add_cell_specific_null_calibration(rep_df: pd.DataFrame) -> pd.DataFrame:
    """Empirically calibrate each row to the matching design-cell null."""
    result = rep_df.copy()
    new_columns = (
        "pipeline_null_exceedance_p",
        "pipeline_null_percentile",
        "standardized_distance_from_null_median",
        "null_relative_gain",
        "matching_null_median",
        "matching_null_q95",
    )
    for column in new_columns:
        result[column] = np.nan

    grouping = [
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
    ]
    for group_values, group_idx in result.groupby(grouping, sort=False).groups.items():
        group_rows = result.loc[group_idx]
        null_mask = np.isclose(group_rows["target_auc"].to_numpy(dtype=float), 0.50)
        null_index = group_rows.index[null_mask]
        null_scores = result.loc[null_index, "best_selection_score"].to_numpy(dtype=float)
        if len(null_scores) < 2:
            raise RuntimeError(f"Insufficient null replications for design cell {group_values}.")
        null_median = float(np.median(null_scores))
        null_sd = float(np.std(null_scores, ddof=1))
        null_q95 = float(np.quantile(null_scores, 0.95))
        null_indices_array = null_index.to_numpy()

        for idx in group_rows.index:
            score = float(result.at[idx, "best_selection_score"])
            is_null = math.isclose(float(result.at[idx, "target_auc"]), 0.50)
            if is_null:
                others = null_scores[null_indices_array != idx]
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
            result.at[idx, "matching_null_median"] = null_median
            result.at[idx, "matching_null_q95"] = null_q95
    return result


def quantile(series: pd.Series, q: float) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    return float(clean.quantile(q)) if not clean.empty else float("nan")


def build_scenario_summary(rep_df: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
        "n_selection",
    ]
    rows: list[dict[str, Any]] = []
    for keys, group in rep_df.groupby(group_cols, sort=True):
        target_auc, method, event_count, prevalence, n_selection = keys
        rows.append(
            {
                "target_auc": float(target_auc),
                "feature_selection": method,
                "selection_event_count": int(event_count),
                "selection_prevalence": float(prevalence),
                "n_selection": int(n_selection),
                "selection_non_event_count": int(n_selection - event_count),
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
                "q025_optimism": quantile(group["selection_induced_optimism"], 0.025),
                "q975_optimism": quantile(group["selection_induced_optimism"], 0.975),
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
                "matching_null_median": float(group["matching_null_median"].iloc[0]),
                "matching_null_q95": float(group["matching_null_q95"].iloc[0]),
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
                "mean_selection_average_precision": float(
                    group["best_model_selection_average_precision"].mean()
                ),
                "mean_test_average_precision": float(
                    group["best_model_test_average_precision"].mean()
                ),
                "mean_selection_accuracy": float(
                    group["best_model_selection_accuracy"].mean()
                ),
                "mean_test_accuracy": float(group["best_model_test_accuracy"].mean()),
                "mean_selection_balanced_accuracy": float(
                    group["best_model_selection_balanced_accuracy"].mean()
                ),
                "mean_test_balanced_accuracy": float(
                    group["best_model_test_balanced_accuracy"].mean()
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(group_cols)


def build_pool_summary(pool_df: pd.DataFrame) -> pd.DataFrame:
    grouping = [
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
        "n_selection",
        "pool_size",
    ]
    return (
        pool_df.groupby(grouping, as_index=False)
        .agg(
            mean_max_selection_auc=("mean_max_selection_score", "mean"),
            mean_selected_test_auc=("mean_selected_test_score", "mean"),
            mean_optimism=("mean_optimism", "mean"),
        )
        .sort_values(grouping)
    )


def summarize_difference(values: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    return {
        "n_paired": int(clean.size),
        "mean_difference": float(clean.mean()),
        "sd_difference": float(clean.std(ddof=1)) if clean.size > 1 else 0.0,
        "median_difference": float(clean.median()),
        "q025_difference": float(clean.quantile(0.025)),
        "q975_difference": float(clean.quantile(0.975)),
        "proportion_difference_gt_zero": float((clean > 0).mean()),
    }


def build_paired_factor_contrasts(rep_df: pd.DataFrame) -> pd.DataFrame:
    """Create paired prevalence and event-count contrasts within replications."""
    rows: list[dict[str, Any]] = []
    metrics = {
        "best_selection_score": "selection_auc",
        "selected_model_test_score": "fresh_test_auc",
        "selection_induced_optimism": "optimism",
        "pipeline_null_percentile": "null_percentile",
    }

    prevalences = sorted(rep_df["selection_prevalence"].unique())
    event_counts = sorted(rep_df["selection_event_count"].unique())

    if len(prevalences) >= 2:
        low_prev, high_prev = prevalences[0], prevalences[-1]
        for (target_auc, method, event_count), group in rep_df.groupby(
            ["target_auc", "feature_selection", "selection_event_count"], sort=True
        ):
            for metric, metric_label in metrics.items():
                wide = group.pivot(index="replication", columns="selection_prevalence", values=metric)
                if low_prev in wide.columns and high_prev in wide.columns:
                    diff = wide[high_prev] - wide[low_prev]
                    row: dict[str, Any] = {
                        "contrast_type": "prevalence_high_minus_low_at_fixed_event_count",
                        "target_auc": float(target_auc),
                        "feature_selection": method,
                        "selection_event_count": int(event_count),
                        "fixed_selection_prevalence": np.nan,
                        "low_level": float(low_prev),
                        "high_level": float(high_prev),
                        "metric": metric_label,
                    }
                    row.update(summarize_difference(diff))
                    rows.append(row)

    if len(event_counts) >= 2:
        low_events, high_events = event_counts[0], event_counts[-1]
        for (target_auc, method, prevalence), group in rep_df.groupby(
            ["target_auc", "feature_selection", "selection_prevalence"], sort=True
        ):
            for metric, metric_label in metrics.items():
                wide = group.pivot(index="replication", columns="selection_event_count", values=metric)
                if low_events in wide.columns and high_events in wide.columns:
                    diff = wide[high_events] - wide[low_events]
                    row = {
                        "contrast_type": "event_count_high_minus_low_at_fixed_prevalence",
                        "target_auc": float(target_auc),
                        "feature_selection": method,
                        "selection_event_count": np.nan,
                        "fixed_selection_prevalence": float(prevalence),
                        "low_level": int(low_events),
                        "high_level": int(high_events),
                        "metric": metric_label,
                    }
                    row.update(summarize_difference(diff))
                    rows.append(row)

    return pd.DataFrame(rows)


def create_plots(
    scenario_df: pd.DataFrame,
    pool_summary_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    # One plot per method and signal strength: the cleanest view of the factorial result.
    for method in sorted(scenario_df["feature_selection"].unique()):
        for target_auc in sorted(scenario_df["target_auc"].unique()):
            data = scenario_df[
                (scenario_df["feature_selection"] == method)
                & np.isclose(scenario_df["target_auc"], target_auc)
            ]

            plt.figure(figsize=(8, 5))
            for prevalence in sorted(data["selection_prevalence"].unique()):
                line = data[np.isclose(data["selection_prevalence"], prevalence)].sort_values(
                    "selection_event_count"
                )
                plt.plot(
                    line["selection_event_count"],
                    line["mean_optimism"],
                    marker="o",
                    label=f"Prevalence {prevalence:.0%}",
                )
            plt.axhline(0.0, linestyle="--", linewidth=1.2)
            plt.xlabel("Events in model-selection set")
            plt.ylabel("Mean selection-induced AUROC optimism")
            plt.title(f"Optimism: {method}, true-predictor AUC {target_auc:.2f}")
            plt.xticks(sorted(data["selection_event_count"].unique()))
            plt.legend()
            plt.tight_layout()
            plt.savefig(
                output_dir / f"01_optimism_{method}_auc_{target_auc:.2f}.png",
                dpi=180,
            )
            plt.close()

            plt.figure(figsize=(8, 5))
            for prevalence in sorted(data["selection_prevalence"].unique()):
                line = data[np.isclose(data["selection_prevalence"], prevalence)].sort_values(
                    "selection_event_count"
                )
                plt.plot(
                    line["selection_event_count"],
                    line["mean_best_selection_auc"],
                    marker="o",
                    label=f"Selection AUC, prevalence {prevalence:.0%}",
                )
                plt.plot(
                    line["selection_event_count"],
                    line["mean_fresh_test_auc"],
                    marker="x",
                    linestyle="--",
                    label=f"Fresh-test AUC, prevalence {prevalence:.0%}",
                )
            plt.xlabel("Events in model-selection set")
            plt.ylabel("Mean AUROC")
            plt.title(f"Selection versus fresh test: {method}, signal AUC {target_auc:.2f}")
            plt.xticks(sorted(data["selection_event_count"].unique()))
            plt.legend(fontsize=8)
            plt.tight_layout()
            plt.savefig(
                output_dir / f"02_selection_vs_test_{method}_auc_{target_auc:.2f}.png",
                dpi=180,
            )
            plt.close()

            plt.figure(figsize=(8, 5))
            for prevalence in sorted(data["selection_prevalence"].unique()):
                line = data[np.isclose(data["selection_prevalence"], prevalence)].sort_values(
                    "selection_event_count"
                )
                plt.plot(
                    line["selection_event_count"],
                    line["pipeline_detection_rate_p_lt_0_05"],
                    marker="o",
                    label=f"Prevalence {prevalence:.0%}",
                )
            plt.axhline(0.05, linestyle="--", linewidth=1.2, label="Nominal 5%")
            plt.xlabel("Events in model-selection set")
            plt.ylabel("Proportion with pipeline-null p < 0.05")
            plt.title(f"Null-calibrated detection: {method}, signal AUC {target_auc:.2f}")
            plt.xticks(sorted(data["selection_event_count"].unique()))
            plt.ylim(-0.02, 1.02)
            plt.legend()
            plt.tight_layout()
            plt.savefig(
                output_dir / f"03_detection_{method}_auc_{target_auc:.2f}.png",
                dpi=180,
            )
            plt.close()

    # LASSO recovery is identical across selection-set designs by construction;
    # summarize it once per target AUROC.
    lasso = scenario_df[scenario_df["feature_selection"] == "lasso"].copy()
    if not lasso.empty:
        recovery = (
            lasso.groupby("target_auc", as_index=False)["signal_selection_rate"]
            .mean()
            .sort_values("target_auc")
        )
        plt.figure(figsize=(8, 5))
        plt.plot(recovery["target_auc"], recovery["signal_selection_rate"], marker="o")
        plt.xlabel("Prespecified AUROC of X1")
        plt.ylabel("Probability LASSO retained X1")
        plt.title("Recovery of the true predictor in the fixed training set")
        plt.ylim(-0.02, 1.02)
        plt.tight_layout()
        plt.savefig(output_dir / "04_lasso_signal_recovery.png", dpi=180)
        plt.close()

    # Candidate-pool effect under the four selection designs.
    for method in sorted(pool_summary_df["feature_selection"].unique()):
        for target_auc in sorted(pool_summary_df["target_auc"].unique()):
            data = pool_summary_df[
                (pool_summary_df["feature_selection"] == method)
                & np.isclose(pool_summary_df["target_auc"], target_auc)
            ]
            plt.figure(figsize=(8, 5))
            for _, design in data[[
                "selection_event_count", "selection_prevalence"
            ]].drop_duplicates().sort_values([
                "selection_event_count", "selection_prevalence"
            ]).iterrows():
                events = int(design["selection_event_count"])
                prevalence = float(design["selection_prevalence"])
                line = data[
                    (data["selection_event_count"] == events)
                    & np.isclose(data["selection_prevalence"], prevalence)
                ].sort_values("pool_size")
                plt.plot(
                    line["pool_size"],
                    line["mean_optimism"],
                    marker="o",
                    label=f"{events} events, {prevalence:.0%}",
                )
            plt.axhline(0.0, linestyle="--", linewidth=1.2)
            plt.xlabel("Number of candidate algorithms")
            plt.ylabel("Mean selection-induced optimism")
            plt.title(f"Algorithm-pool effect: {method}, signal AUC {target_auc:.2f}")
            plt.xticks(sorted(data["pool_size"].unique()))
            plt.legend()
            plt.tight_layout()
            plt.savefig(
                output_dir / f"05_pool_size_{method}_auc_{target_auc:.2f}.png",
                dpi=180,
            )
            plt.close()


def write_summary_text(
    args: argparse.Namespace,
    scenario_df: pd.DataFrame,
    contrast_df: pd.DataFrame,
    elapsed_seconds: float,
    output_path: Path,
) -> None:
    lines = [
        "PHASE 2B: EVENT COUNT VERSUS OUTCOME PREVALENCE",
        "=" * 52,
        "",
        f"Preset: {args.preset}",
        f"Replications per target-AUC / feature-selection bundle: {args.repetitions}",
        f"Fixed training N / prevalence: {args.n_train} / {args.train_prevalence:.3f}",
        f"Fixed fresh-test N / prevalence: {args.n_test} / {args.test_prevalence:.3f}",
        f"Candidate predictors: {args.n_features} (X1 signal + {args.n_features - 1} noise)",
        f"Candidate algorithms: {len(base.MODEL_NAMES)}",
        f"Target AUROCs: {', '.join(f'{x:.2f}' for x in args.target_aurocs)}",
        f"Feature-selection methods: {', '.join(args.feature_selection_methods)}",
        "",
        "Model-selection-set designs",
        "---------------------------",
    ]
    for design in args.selection_designs:
        lines.append(
            f"{design['selection_event_count']} events, prevalence "
            f"{design['selection_prevalence']:.0%}: N={design['n_selection']} "
            f"({design['selection_non_event_count']} non-events)"
        )

    lines.extend(["", "Scenario results", "----------------"])
    for _, row in scenario_df.iterrows():
        lines.append(
            f"AUC {row['target_auc']:.2f}; {row['feature_selection']}; "
            f"events={int(row['selection_event_count'])}; "
            f"prevalence={row['selection_prevalence']:.0%}; N={int(row['n_selection'])}: "
            f"selection={row['mean_best_selection_auc']:.4f}, "
            f"fresh test={row['mean_fresh_test_auc']:.4f}, "
            f"optimism={row['mean_optimism']:.4f}, "
            f"P(p_pipeline<0.05)={row['pipeline_detection_rate_p_lt_0_05']:.3f}"
        )

    lines.extend(
        [
            "",
            "Primary paired contrasts",
            "------------------------",
        ]
    )
    primary = contrast_df[
        (contrast_df["metric"] == "optimism")
    ] if not contrast_df.empty else contrast_df
    for _, row in primary.iterrows():
        lines.append(
            f"{row['contrast_type']}; AUC={row['target_auc']:.2f}; "
            f"{row['feature_selection']}: mean difference={row['mean_difference']:.4f} "
            f"(2.5th to 97.5th percentile {row['q025_difference']:.4f} to "
            f"{row['q975_difference']:.4f})"
        )

    lines.extend(
        [
            "",
            f"Elapsed time: {elapsed_seconds:.1f} seconds",
            "",
            "Design guardrail:",
            "Training data, fitted candidate models, and fresh-test data are held fixed",
            "within each replication while only the model-selection set changes. Thus,",
            "differences across event-count/prevalence cells reflect the information and",
            "class composition available for winner selection rather than refitting noise.",
            "",
            "Interpretation guardrail:",
            "Target AUROC is the population discrimination of X1 alone. The fitted",
            "multivariable pipeline may have a different fresh-test AUROC because it uses",
            "finite training data and may retain noise predictors.",
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
    output_dir = output_root / f"pipeline_phase2b_{args.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=False)

    config_for_json = vars(args).copy()
    config_for_json["event_counts"] = list(args.event_counts)
    config_for_json["selection_prevalences"] = list(args.selection_prevalences)
    config_for_json["target_aurocs"] = list(args.target_aurocs)
    config_for_json["feature_selection_methods"] = list(args.feature_selection_methods)
    config_for_json["selection_designs"] = args.selection_designs
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

    bundle_conditions = [
        (target_auc, method)
        for target_auc in args.target_aurocs
        for method in args.feature_selection_methods
    ]
    total_scenarios = (
        len(bundle_conditions)
        * len(args.event_counts)
        * len(args.selection_prevalences)
    )

    print("Starting Phase 2B event-count versus prevalence simulation")
    print(f"  paired fit bundles={len(bundle_conditions)}")
    print(f"  reported scenario cells={total_scenarios}")
    print(f"  repetitions per bundle={args.repetitions}")
    print(f"  n_jobs={args.n_jobs}")
    print(f"  output={output_dir}")
    print()

    start = time.perf_counter()
    all_results: list[
        tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]
    ] = []

    # Fit candidate models once per replication/target/method, then reuse them
    # across all model-selection-set designs.
    for condition_number, (target_auc, method) in enumerate(bundle_conditions, start=1):
        print(
            f"Bundle {condition_number}/{len(bundle_conditions)}: "
            f"target_auc={target_auc:.2f}, feature_selection={method}"
        )
        condition_results = Parallel(n_jobs=args.n_jobs, backend="loky", verbose=3)(
            delayed(run_replication_bundle)(
                replication=i + 1,
                seed=seeds[i],
                target_auc=target_auc,
                feature_selection=method,
                args=args,
            )
            for i in range(args.repetitions)
        )
        all_results.extend(condition_results)

    elapsed = time.perf_counter() - start

    rep_rows = [row for item in all_results for row in item[0]]
    model_rows = [row for item in all_results for row in item[1]]
    pool_rows = [row for item in all_results for row in item[2]]

    rep_df = pd.DataFrame(rep_rows).sort_values(
        [
            "feature_selection",
            "target_auc",
            "selection_event_count",
            "selection_prevalence",
            "replication",
        ]
    )
    model_df = pd.DataFrame(model_rows).sort_values(
        [
            "feature_selection",
            "target_auc",
            "selection_event_count",
            "selection_prevalence",
            "replication",
            "model",
        ]
    )
    pool_df = pd.DataFrame(pool_rows).sort_values(
        [
            "feature_selection",
            "target_auc",
            "selection_event_count",
            "selection_prevalence",
            "replication",
            "pool_size",
        ]
    )

    rep_df = add_cell_specific_null_calibration(rep_df)
    scenario_df = build_scenario_summary(rep_df)
    pool_summary_df = build_pool_summary(pool_df)
    contrast_df = build_paired_factor_contrasts(rep_df)

    # Safeguard against an output directory being removed during a long run.
    output_dir.mkdir(parents=True, exist_ok=True)
    rep_df.to_csv(output_dir / "replication_results.csv", index=False)
    model_df.to_csv(output_dir / "model_level_results.csv", index=False)
    pool_df.to_csv(output_dir / "pool_size_results.csv", index=False)
    scenario_df.to_csv(output_dir / "scenario_summary.csv", index=False)
    pool_summary_df.to_csv(output_dir / "pool_size_summary.csv", index=False)
    contrast_df.to_csv(output_dir / "paired_factor_contrasts.csv", index=False)

    create_plots(scenario_df, pool_summary_df, output_dir)
    write_summary_text(
        args,
        scenario_df,
        contrast_df,
        elapsed,
        output_dir / "summary.txt",
    )

    summary_json = {
        "study": "Phase 2B event-count versus prevalence factorial pilot",
        "design_note": (
            "Training data, fitted candidate models, and fresh-test data are fixed "
            "within replication; only the model-selection set changes."
        ),
        "config": config_for_json,
        "elapsed_seconds": elapsed,
        "scenario_summary": scenario_df.to_dict(orient="records"),
        "paired_factor_contrasts": contrast_df.to_dict(orient="records"),
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
