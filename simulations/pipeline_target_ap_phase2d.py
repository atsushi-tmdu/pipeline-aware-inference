#!/usr/bin/env python3
"""
Phase 2D: target-prevalence standardization of average precision.

This simulation extends Phase 2D by comparing four ways to select the apparent
best algorithm from the same fitted candidate-model pool:

    1) AUROC
    2) Raw average precision (AP) in the model-selection sample
    3) Target-prevalence-standardized AP
    4) Standardized partial AUROC for false-positive rates <= 0.10

Raw AP changes when the event prevalence of the evaluation sample changes. The
target-standardized AP reweights events and non-events in the model-selection
sample so that its implied prevalence equals a prespecified target-population
prevalence. This allows an artificially balanced model-selection sample to be
used without redefining the target AP estimand.

Within every Monte Carlo replication, the training data, fitted candidate
models, model-selection data, and untouched fresh-test data are shared across
all four selection rules. The fresh-test prevalence is fixed at the target
prevalence.

Primary questions
-----------------
* Does raw AP select a different winner after the model-selection prevalence is
  changed by under-sampling non-events?
* Does target-standardized AP recover the winner that performs better on target-
  population AP in untouched data?
* How much target-AP regret remains relative to the best candidate model in the
  fresh test set?
* Are metric-specific pipeline-null distributions still well behaved?

Default quick design
--------------------
Selection-set event counts: 20, 100
Selection-set prevalences:  0.05, 0.50
Target prevalence:          0.05
True X1 AUROCs:             0.50, 0.70
Feature selection:          LASSO, none
Candidate algorithms:       seven algorithms from pipeline_null_pilot_v2.py
Repetitions:                500 per base scenario

Required companion files
------------------------
Place this script in the same directory as:

    pipeline_null_pilot_v2.py
    pipeline_event_prevalence_phase2b.py

Example
-------
    python pipeline_target_ap_phase2d.py --preset quick --n-jobs 16 \
        --output-root results_phase2d
"""

from __future__ import annotations

import os

# Avoid nested BLAS/OpenMP parallelism inside joblib workers.
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
from scipy.stats import spearmanr
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import average_precision_score, roc_auc_score

try:
    import pipeline_null_pilot_v2 as base
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_null_pilot_v2.py was not found. Place this script in the "
        "same directory and run it there."
    ) from exc

try:
    import pipeline_event_prevalence_phase2b as phase2b
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_event_prevalence_phase2b.py was not found. Place this script "
        "in the same directory and run it there."
    ) from exc


SELECTION_METRICS = (
    "roc_auc",
    "average_precision_raw",
    "average_precision_target",
    "pauc_fpr_0_10",
)

METRIC_LABELS = {
    "roc_auc": "AUROC",
    "average_precision_raw": "Raw average precision",
    "average_precision_target": "Target-standardized average precision",
    "pauc_fpr_0_10": "Partial AUROC (FPR <= 0.10)",
}

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 2D paired comparison of raw and target-prevalence-"
            "standardized average precision for winner selection."
        )
    )
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--n-train", type=int, default=None)
    parser.add_argument("--train-prevalence", type=float, default=0.10)
    parser.add_argument("--n-test", type=int, default=None)
    parser.add_argument(
        "--target-prevalence",
        type=float,
        default=0.05,
        help=(
            "Target-population event prevalence. The untouched fresh-test set "
            "uses this prevalence, and selection-sample AP is standardized to it."
        ),
    )
    parser.add_argument("--n-features", type=int, default=30)
    parser.add_argument("--binary-fraction", type=float, default=0.40)
    parser.add_argument("--correlation-rho", type=float, default=0.30)
    parser.add_argument("--cv-folds", type=int, default=None)
    parser.add_argument(
        "--event-counts",
        type=phase2b.parse_int_list,
        default=phase2b.DEFAULT_EVENT_COUNTS,
    )
    parser.add_argument(
        "--selection-prevalences",
        type=phase2b.parse_prevalence_list,
        default=phase2b.DEFAULT_SELECTION_PREVALENCES,
    )
    parser.add_argument(
        "--target-aurocs",
        type=phase2b.parse_auc_list,
        default=phase2b.DEFAULT_TARGET_AUROCS,
    )
    parser.add_argument(
        "--feature-selection-methods",
        choices=("both", "lasso", "none"),
        default="both",
    )
    parser.add_argument(
        "--pauc-max-fpr",
        type=float,
        default=0.10,
        help="Upper FPR limit for standardized partial AUROC.",
    )
    parser.add_argument("--master-seed", type=int, default=20260718)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument(
        "--output-root",
        default="results_phase2d",
        help="Parent directory for the timestamped result directory.",
    )
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    args.repetitions = args.repetitions or preset["repetitions"]
    args.n_train = args.n_train or preset["n_train"]
    args.n_test = args.n_test or preset["n_test"]
    args.cv_folds = args.cv_folds or preset["cv_folds"]

    if args.feature_selection_methods == "both":
        args.feature_selection_methods = phase2b.DEFAULT_FEATURE_SELECTION_METHODS
    else:
        args.feature_selection_methods = (args.feature_selection_methods,)

    if not 0.0 < args.train_prevalence < 1.0:
        parser.error("--train-prevalence must lie strictly between 0 and 1.")
    if not 0.0 < args.target_prevalence < 1.0:
        parser.error("--target-prevalence must lie strictly between 0 and 1.")
    if not 0.0 < args.binary_fraction < 1.0:
        parser.error("--binary-fraction must lie strictly between 0 and 1.")
    if not 0.0 <= args.correlation_rho < 1.0:
        parser.error("--correlation-rho must lie in [0, 1).")
    if args.n_features < 2:
        parser.error("--n-features must be at least 2.")
    if args.repetitions < 2:
        parser.error("--repetitions must be at least 2.")
    if not 0.0 < args.pauc_max_fpr <= 1.0:
        parser.error("--pauc-max-fpr must lie in (0, 1].")

    selection_designs: list[dict[str, Any]] = []
    for event_count in args.event_counts:
        for prevalence in args.selection_prevalences:
            raw_n = event_count / prevalence
            n_selection = int(round(raw_n))
            if not math.isclose(raw_n, n_selection, rel_tol=0.0, abs_tol=1e-9):
                parser.error(
                    f"event_count={event_count} and prevalence={prevalence} do not "
                    "produce an integer model-selection sample size."
                )
            if n_selection <= event_count:
                parser.error(
                    "Every model-selection set must contain at least one non-event."
                )
            observed_events = base.event_count(n_selection, prevalence)
            if observed_events != event_count:
                parser.error(
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

def target_prevalence_sample_weights(
    y: np.ndarray,
    target_prevalence: float,
) -> np.ndarray:
    """Class-constant weights that map the sample prevalence to the target."""
    y = np.asarray(y, dtype=int)
    observed = float(np.mean(y))
    if not 0.0 < observed < 1.0:
        raise ValueError("Both outcome classes are required for AP standardization.")
    weights = np.empty(len(y), dtype=float)
    weights[y == 1] = target_prevalence / observed
    weights[y == 0] = (1.0 - target_prevalence) / (1.0 - observed)
    return weights


def rank_metrics_from_scores(
    y: np.ndarray,
    scores: np.ndarray,
    target_prevalence: float,
    pauc_max_fpr: float,
) -> dict[str, float]:
    """Calculate raw and target-standardized ranking metrics."""
    observed_prevalence = float(np.mean(y))
    roc = float(roc_auc_score(y, scores))
    raw_ap = float(average_precision_score(y, scores))
    weights = target_prevalence_sample_weights(y, target_prevalence)
    target_ap = float(average_precision_score(y, scores, sample_weight=weights))
    pauc = float(roc_auc_score(y, scores, max_fpr=pauc_max_fpr))
    normalized_target_ap = float(
        (target_ap - target_prevalence) / (1.0 - target_prevalence)
    )
    return {
        "roc_auc": roc,
        "average_precision_raw": raw_ap,
        "average_precision_target": target_ap,
        "normalized_average_precision_target": normalized_target_ap,
        "pauc_fpr_0_10": pauc,
        "observed_prevalence": observed_prevalence,
    }

def make_config(args: argparse.Namespace, feature_selection: str) -> base.SimulationConfig:
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
        test_prevalence=args.target_prevalence,
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


def choose_winner(
    rows: list[dict[str, Any]],
    metric: str,
) -> tuple[dict[str, Any], int, str]:
    """Select the highest-scoring model and report the complete tie set."""
    valid = [
        row
        for row in rows
        if row.get("error") is None
        and math.isfinite(float(row[f"selection_{metric}"]))
        and math.isfinite(float(row[f"test_{metric}"]))
    ]
    if not valid:
        raise RuntimeError(f"All candidate models failed for metric={metric}.")

    best_value = max(float(row[f"selection_{metric}"]) for row in valid)
    tied = [
        row
        for row in valid
        if math.isclose(
            float(row[f"selection_{metric}"]),
            best_value,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    ]
    # Deterministic tie handling; tie count is retained for interpretation.
    winner = min(tied, key=lambda row: base.MODEL_NAMES.index(row["model"]))
    tie_names = "|".join(row["model"] for row in tied)
    return winner, len(tied), tie_names


def run_replication(
    replication: int,
    seed: int,
    target_auc: float,
    feature_selection: str,
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Fit one model pool and select winners using four metric rules."""
    config = make_config(args, feature_selection)

    x_train, y_train = phase2b.generate_signal_dataset(
        args.n_train,
        args.train_prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        phase2b.make_rng(seed, 1),
    )
    x_test, y_test = phase2b.generate_signal_dataset(
        args.n_test,
        args.target_prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        phase2b.make_rng(seed, 2),
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
        score_test = base.continuous_prediction_scores(dummy, x_test_selected)
        test_rank_metrics = rank_metrics_from_scores(
            y_test, score_test, args.target_prevalence, args.pauc_max_fpr
        )
        for model_name in base.MODEL_NAMES:
            fitted_models[model_name] = {
                "estimator": dummy,
                "intercept_only": True,
                "error": None,
                "test_metrics": test_rank_metrics,
            }
    else:
        x_train_selected = x_train[:, selected_indices]
        x_test_selected = x_test[:, selected_indices]
        for model_name, estimator in base.build_candidate_models(seed).items():
            info: dict[str, Any] = {
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
                test_scores = base.continuous_prediction_scores(
                    estimator, x_test_selected
                )
                info["test_metrics"] = rank_metrics_from_scores(
                    y_test,
                    test_scores,
                    args.target_prevalence,
                    args.pauc_max_fpr,
                )
            except Exception as exc:
                info["error"] = f"{type(exc).__name__}: {exc}"
            fitted_models[model_name] = info

    winner_rows: list[dict[str, Any]] = []
    model_rows_all: list[dict[str, Any]] = []
    agreement_rows: list[dict[str, Any]] = []

    for design in args.selection_designs:
        event_count = int(design["selection_event_count"])
        prevalence = float(design["selection_prevalence"])
        n_selection = int(design["n_selection"])
        prevalence_key = int(round(prevalence * 1_000_000))

        x_selection, y_selection = phase2b.generate_signal_dataset(
            n_selection,
            prevalence,
            args.n_features,
            args.binary_fraction,
            args.correlation_rho,
            target_auc,
            phase2b.make_rng(seed, 100, event_count, prevalence_key),
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
                "target_prevalence": float(args.target_prevalence),
                "n_selection": n_selection,
                "model": model_name,
                "intercept_only": bool(info["intercept_only"]),
                "error": info["error"],
            }
            if info["error"] is None:
                try:
                    selection_scores = base.continuous_prediction_scores(
                        info["estimator"], x_selection_selected
                    )
                    selection_metrics = rank_metrics_from_scores(
                        y_selection,
                        selection_scores,
                        args.target_prevalence,
                        args.pauc_max_fpr,
                    )
                    test_metrics = info["test_metrics"]
                    row.update(
                        {f"selection_{key}": value for key, value in selection_metrics.items()}
                    )
                    row.update(
                        {f"test_{key}": value for key, value in test_metrics.items()}
                    )
                except Exception as exc:
                    row["error"] = f"{type(exc).__name__}: {exc}"
            scenario_model_rows.append(row)
            model_rows_all.append(row)

        valid_models = [row for row in scenario_model_rows if row["error"] is None]
        if not valid_models:
            raise RuntimeError("All candidate models failed in a selection design.")
        oracle_target_ap = max(
            float(row["test_average_precision_target"]) for row in valid_models
        )
        oracle_models = [
            row["model"]
            for row in valid_models
            if math.isclose(
                float(row["test_average_precision_target"]),
                oracle_target_ap,
                rel_tol=1e-12,
                abs_tol=1e-12,
            )
        ]

        metric_winners: dict[str, dict[str, Any]] = {}
        for metric in SELECTION_METRICS:
            winner, tie_count, tie_names = choose_winner(scenario_model_rows, metric)
            metric_winners[metric] = winner
            comparable_scale = not (
                metric == "average_precision_raw"
                and not math.isclose(prevalence, args.target_prevalence)
            )
            metric_gap = float(
                winner[f"selection_{metric}"] - winner[f"test_{metric}"]
            )
            row: dict[str, Any] = {
                "replication": replication,
                "seed": seed,
                "target_auc": float(target_auc),
                "delta": phase2b.delta_from_auc(target_auc),
                "feature_selection": feature_selection,
                "selection_event_count": event_count,
                "selection_non_event_count": int(n_selection - event_count),
                "selection_prevalence": prevalence,
                "target_prevalence": float(args.target_prevalence),
                "n_selection": n_selection,
                "selection_metric": metric,
                "selection_metric_label": METRIC_LABELS[metric],
                "best_model": winner["model"],
                "winner_tie_count": tie_count,
                "winner_tie_models": tie_names,
                "selected_feature_count": selected_feature_count,
                "signal_included": signal_included,
                "signal_selected": signal_selected,
                "noise_selected_count": noise_selected_count,
                "selected_features": "|".join(str(i + 1) for i in selected_indices),
                "lasso_selected_c": selector_info["lasso_selected_c"],
                "selector_error": selector_info["selector_error"],
                "best_selection_metric_value": float(winner[f"selection_{metric}"]),
                "selected_model_test_metric_value": float(winner[f"test_{metric}"]),
                "selection_minus_test_metric_gap": metric_gap,
                "same_target_scale_for_gap": comparable_scale,
                "selection_induced_optimism": metric_gap if comparable_scale else np.nan,
                "winner_test_target_average_precision": float(
                    winner["test_average_precision_target"]
                ),
                "oracle_test_target_average_precision": oracle_target_ap,
                "target_average_precision_regret": float(
                    oracle_target_ap - winner["test_average_precision_target"]
                ),
                "winner_is_target_ap_oracle": winner["model"] in oracle_models,
                "target_ap_oracle_models": "|".join(oracle_models),
            }
            for observed_metric in (
                "roc_auc",
                "average_precision_raw",
                "average_precision_target",
                "normalized_average_precision_target",
                "pauc_fpr_0_10",
            ):
                row[f"winner_selection_{observed_metric}"] = float(
                    winner[f"selection_{observed_metric}"]
                )
                row[f"winner_test_{observed_metric}"] = float(
                    winner[f"test_{observed_metric}"]
                )
            winner_rows.append(row)

        for i, metric_a in enumerate(SELECTION_METRICS):
            for metric_b in SELECTION_METRICS[i + 1 :]:
                winner_a = metric_winners[metric_a]
                winner_b = metric_winners[metric_b]
                agreement_rows.append(
                    {
                        "replication": replication,
                        "seed": seed,
                        "target_auc": float(target_auc),
                        "feature_selection": feature_selection,
                        "selection_event_count": event_count,
                        "selection_prevalence": prevalence,
                        "metric_a": metric_a,
                        "metric_b": metric_b,
                        "same_winner": winner_a["model"] == winner_b["model"],
                    }
                )

        for i, metric_a in enumerate(SELECTION_METRICS):
            for metric_b in SELECTION_METRICS[i + 1 :]:
                values_a = np.array(
                    [row[f"selection_{metric_a}"] for row in valid_models], dtype=float
                )
                values_b = np.array(
                    [row[f"selection_{metric_b}"] for row in valid_models], dtype=float
                )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    corr = spearmanr(values_a, values_b).statistic
                agreement_rows.append(
                    {
                        "replication": replication,
                        "seed": seed,
                        "target_auc": float(target_auc),
                        "feature_selection": feature_selection,
                        "selection_event_count": event_count,
                        "selection_prevalence": prevalence,
                        "metric_a": metric_a,
                        "metric_b": metric_b,
                        "same_winner": np.nan,
                        "model_score_spearman": float(corr)
                        if math.isfinite(float(corr))
                        else np.nan,
                    }
                )

    return winner_rows, model_rows_all, agreement_rows

def add_pipeline_null_calibration(winner_df: pd.DataFrame) -> pd.DataFrame:
    """Use the matching metric/design null bank to calibrate every result."""
    result = winner_df.copy()
    columns = (
        "pipeline_null_exceedance_p",
        "pipeline_null_percentile",
        "standardized_distance_from_null_median",
        "null_relative_gain",
        "matching_null_median",
        "matching_null_q95",
    )
    for column in columns:
        result[column] = np.nan

    grouping = [
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
        "selection_metric",
    ]
    for group_values, indices in result.groupby(grouping, sort=False).groups.items():
        group = result.loc[indices]
        null_mask = np.isclose(group["target_auc"].to_numpy(float), 0.50)
        null_indices = group.index[null_mask]
        null_scores = result.loc[
            null_indices, "best_selection_metric_value"
        ].to_numpy(float)
        if len(null_scores) < 2:
            raise RuntimeError(f"Insufficient null results for {group_values}.")
        null_median = float(np.median(null_scores))
        null_sd = float(np.std(null_scores, ddof=1))
        null_q95 = float(np.quantile(null_scores, 0.95))
        null_index_array = null_indices.to_numpy()

        for idx in group.index:
            score = float(result.at[idx, "best_selection_metric_value"])
            is_null = math.isclose(float(result.at[idx, "target_auc"]), 0.50)
            if is_null:
                reference = null_scores[null_index_array != idx]
            else:
                reference = null_scores
            exceed = int(np.sum(reference >= score))
            p_value = (1.0 + exceed) / (1.0 + len(reference))
            percentile = (
                np.sum(reference < score) + 0.5 * np.sum(reference == score)
            ) / len(reference)

            # For AP the perfect score is still 1, but its chance baseline is
            # prevalence-dependent and therefore estimated empirically here.
            denominator = 1.0 - null_median
            result.at[idx, "pipeline_null_exceedance_p"] = p_value
            result.at[idx, "pipeline_null_percentile"] = percentile
            result.at[idx, "standardized_distance_from_null_median"] = (
                (score - null_median) / null_sd if null_sd > 0 else np.nan
            )
            result.at[idx, "null_relative_gain"] = (
                (score - null_median) / denominator
                if denominator > 0
                else np.nan
            )
            result.at[idx, "matching_null_median"] = null_median
            result.at[idx, "matching_null_q95"] = null_q95
    return result


def make_summaries(
    winner_df: pd.DataFrame,
    agreement_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_cols = [
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
        "target_auc",
        "selection_metric",
    ]
    records: list[dict[str, Any]] = []
    for keys, group in winner_df.groupby(group_cols, sort=True):
        optimism = group["selection_induced_optimism"].dropna()
        record = dict(zip(group_cols, keys))
        record.update(
            {
                "n_replications": int(len(group)),
                "mean_selection_metric": float(group["best_selection_metric_value"].mean()),
                "mean_fresh_test_metric": float(group["selected_model_test_metric_value"].mean()),
                "mean_selection_minus_test_gap": float(
                    group["selection_minus_test_metric_gap"].mean()
                ),
                "mean_comparable_scale_optimism": float(optimism.mean())
                if len(optimism)
                else np.nan,
                "median_comparable_scale_optimism": float(optimism.median())
                if len(optimism)
                else np.nan,
                "pipeline_p_lt_0_05": float(
                    (group["pipeline_null_exceedance_p"] < 0.05).mean()
                ),
                "mean_null_relative_gain": float(group["null_relative_gain"].mean()),
                "unique_winner_rate": float((group["winner_tie_count"] == 1).mean()),
                "mean_fresh_test_roc_auc": float(group["winner_test_roc_auc"].mean()),
                "mean_fresh_test_raw_ap": float(
                    group["winner_test_average_precision_raw"].mean()
                ),
                "mean_fresh_test_target_ap": float(
                    group["winner_test_average_precision_target"].mean()
                ),
                "mean_target_ap_regret": float(
                    group["target_average_precision_regret"].mean()
                ),
                "median_target_ap_regret": float(
                    group["target_average_precision_regret"].median()
                ),
                "target_ap_oracle_selection_rate": float(
                    group["winner_is_target_ap_oracle"].mean()
                ),
                "mean_fresh_test_pauc": float(
                    group["winner_test_pauc_fpr_0_10"].mean()
                ),
            }
        )
        records.append(record)
    scenario_summary = pd.DataFrame(records)

    same_rows = agreement_df[agreement_df["same_winner"].notna()].copy()
    agreement_summary = (
        same_rows.groupby(
            [
                "feature_selection",
                "selection_event_count",
                "selection_prevalence",
                "target_auc",
                "metric_a",
                "metric_b",
            ],
            as_index=False,
        )["same_winner"]
        .mean()
        .rename(columns={"same_winner": "same_winner_rate"})
    )

    corr_rows = agreement_df[agreement_df.get("model_score_spearman").notna()].copy()
    rank_summary = (
        corr_rows.groupby(
            [
                "feature_selection",
                "selection_event_count",
                "selection_prevalence",
                "target_auc",
                "metric_a",
                "metric_b",
            ],
            as_index=False,
        )["model_score_spearman"]
        .mean()
        .rename(columns={"model_score_spearman": "mean_model_score_spearman"})
    )
    return scenario_summary, agreement_summary, rank_summary

def paired_prevalence_effects(winner_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate paired 50%-minus-5% changes within each replication."""
    if not ({0.05, 0.50} <= set(winner_df["selection_prevalence"].unique())):
        return pd.DataFrame()
    index_cols = [
        "replication",
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "selection_metric",
    ]
    value_cols = [
        "best_selection_metric_value",
        "selected_model_test_metric_value",
        "selection_minus_test_metric_gap",
        "winner_test_target_average_precision",
        "target_average_precision_regret",
        "winner_test_roc_auc",
        "winner_test_pauc_fpr_0_10",
    ]
    low = winner_df[np.isclose(winner_df["selection_prevalence"], 0.05)].set_index(
        index_cols
    )
    high = winner_df[np.isclose(winner_df["selection_prevalence"], 0.50)].set_index(
        index_cols
    )
    common = low.index.intersection(high.index)
    rows: list[dict[str, Any]] = []
    for idx in common:
        row = dict(zip(index_cols, idx if isinstance(idx, tuple) else (idx,)))
        for column in value_cols:
            row[f"diff_50pct_minus_5pct_{column}"] = float(
                high.loc[idx, column] - low.loc[idx, column]
            )
        rows.append(row)
    return pd.DataFrame(rows)


def paired_raw_vs_adjusted_ap(winner_df: pd.DataFrame) -> pd.DataFrame:
    """Paired target-population performance of raw-AP and adjusted-AP winners."""
    index_cols = [
        "replication",
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "selection_prevalence",
    ]
    raw = winner_df[winner_df["selection_metric"] == "average_precision_raw"].set_index(
        index_cols
    )
    adjusted = winner_df[
        winner_df["selection_metric"] == "average_precision_target"
    ].set_index(index_cols)
    common = raw.index.intersection(adjusted.index)
    rows: list[dict[str, Any]] = []
    for idx in common:
        r = raw.loc[idx]
        a = adjusted.loc[idx]
        row = dict(zip(index_cols, idx if isinstance(idx, tuple) else (idx,)))
        row.update(
            {
                "raw_ap_winner": r["best_model"],
                "adjusted_ap_winner": a["best_model"],
                "same_winner": r["best_model"] == a["best_model"],
                "raw_winner_fresh_target_ap": float(
                    r["winner_test_target_average_precision"]
                ),
                "adjusted_winner_fresh_target_ap": float(
                    a["winner_test_target_average_precision"]
                ),
                "adjusted_minus_raw_fresh_target_ap": float(
                    a["winner_test_target_average_precision"]
                    - r["winner_test_target_average_precision"]
                ),
                "raw_winner_target_ap_regret": float(
                    r["target_average_precision_regret"]
                ),
                "adjusted_winner_target_ap_regret": float(
                    a["target_average_precision_regret"]
                ),
                "raw_minus_adjusted_target_ap_regret": float(
                    r["target_average_precision_regret"]
                    - a["target_average_precision_regret"]
                ),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)

def save_plots(
    scenario_summary: pd.DataFrame,
    agreement_summary: pd.DataFrame,
    raw_vs_adjusted: pd.DataFrame,
    output_dir: Path,
) -> None:
    subset = scenario_summary[
        (scenario_summary["feature_selection"] == "none")
        & np.isclose(scenario_summary["target_auc"], 0.70)
    ].copy()

    # Plot 1: fresh target-population AP by winner-selection rule.
    fig, ax = plt.subplots(figsize=(9, 6))
    max_events = subset["selection_event_count"].max()
    for metric in SELECTION_METRICS:
        data = subset[
            (subset["selection_metric"] == metric)
            & (subset["selection_event_count"] == max_events)
        ].sort_values("selection_prevalence")
        if data.empty:
            continue
        ax.plot(
            data["selection_prevalence"],
            data["mean_fresh_test_target_ap"],
            marker="o",
            label=METRIC_LABELS[metric],
        )
    ax.set_xlabel("Prevalence in model-selection set")
    ax.set_ylabel("Fresh-test AP at target prevalence")
    ax.set_title("Target-population AP of metric-selected winners")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "01_fresh_target_ap_by_selection_rule.png", dpi=180)
    plt.close(fig)

    # Plot 2: target-AP regret relative to the test-set oracle candidate.
    fig, ax = plt.subplots(figsize=(9, 6))
    for metric in SELECTION_METRICS:
        data = subset[
            (subset["selection_metric"] == metric)
            & (subset["selection_event_count"] == max_events)
        ].sort_values("selection_prevalence")
        if data.empty:
            continue
        ax.plot(
            data["selection_prevalence"],
            data["mean_target_ap_regret"],
            marker="o",
            label=METRIC_LABELS[metric],
        )
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel("Prevalence in model-selection set")
    ax.set_ylabel("Mean target-AP regret")
    ax.set_title("Regret relative to the best candidate in untouched data")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "02_target_ap_regret_by_selection_rule.png", dpi=180)
    plt.close(fig)

    # Plot 3: paired benefit of AP standardization.
    if not raw_vs_adjusted.empty:
        summary = (
            raw_vs_adjusted.groupby(
                ["feature_selection", "selection_event_count", "selection_prevalence"],
                as_index=False,
            )["adjusted_minus_raw_fresh_target_ap"]
            .mean()
        )
        display = summary[summary["feature_selection"] == "none"]
        fig, ax = plt.subplots(figsize=(9, 6))
        for prevalence, data in display.groupby("selection_prevalence"):
            data = data.sort_values("selection_event_count")
            ax.plot(
                data["selection_event_count"],
                data["adjusted_minus_raw_fresh_target_ap"],
                marker="o",
                label=f"selection prevalence={prevalence:.0%}",
            )
        ax.axhline(0.0, linewidth=1)
        ax.set_xlabel("Events in model-selection set")
        ax.set_ylabel("Adjusted-AP winner minus raw-AP winner: fresh target AP")
        ax.set_title("Paired value of target-prevalence AP standardization")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "03_adjusted_vs_raw_ap_paired_difference.png", dpi=180)
        plt.close(fig)

    # Plot 4: agreement between raw and standardized AP winners.
    if not agreement_summary.empty:
        display = agreement_summary[
            (agreement_summary["feature_selection"] == "none")
            & (agreement_summary["metric_a"] == "average_precision_raw")
            & (agreement_summary["metric_b"] == "average_precision_target")
            & np.isclose(agreement_summary["target_auc"], 0.70)
        ]
        fig, ax = plt.subplots(figsize=(9, 6))
        for prevalence, data in display.groupby("selection_prevalence"):
            data = data.sort_values("selection_event_count")
            ax.plot(
                data["selection_event_count"],
                data["same_winner_rate"],
                marker="o",
                label=f"selection prevalence={prevalence:.0%}",
            )
        ax.set_xlabel("Events in model-selection set")
        ax.set_ylabel("Probability of selecting the same algorithm")
        ax.set_ylim(0, 1.02)
        ax.set_title("Agreement: raw AP versus target-standardized AP")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "04_raw_vs_adjusted_ap_winner_agreement.png", dpi=180)
        plt.close(fig)

    # Plot 5: metric-specific null calibration / detection.
    detect = scenario_summary[
        (scenario_summary["feature_selection"] == "none")
        & (scenario_summary["selection_event_count"] == scenario_summary["selection_event_count"].max())
        & np.isclose(scenario_summary["selection_prevalence"], 0.50)
    ]
    fig, ax = plt.subplots(figsize=(9, 6))
    for metric in SELECTION_METRICS:
        data = detect[detect["selection_metric"] == metric].sort_values("target_auc")
        if data.empty:
            continue
        ax.plot(
            data["target_auc"],
            data["pipeline_p_lt_0_05"],
            marker="o",
            label=METRIC_LABELS[metric],
        )
    ax.axhline(0.05, linewidth=1)
    ax.set_xlabel("Target AUROC of X1")
    ax.set_ylabel("P(pipeline-null p < 0.05)")
    ax.set_ylim(0, 1.02)
    ax.set_title("Metric-specific detection after balancing selection data")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "05_metric_specific_detection.png", dpi=180)
    plt.close(fig)

def write_summary_text(
    args: argparse.Namespace,
    scenario_summary: pd.DataFrame,
    agreement_summary: pd.DataFrame,
    raw_vs_adjusted: pd.DataFrame,
    runtime_seconds: float,
    output_dir: Path,
) -> None:
    lines = [
        "PHASE 2D: TARGET-PREVALENCE STANDARDIZATION OF AP",
        "=" * 62,
        f"Preset: {args.preset}",
        f"Repetitions per base scenario: {args.repetitions}",
        f"Runtime: {runtime_seconds:.1f} seconds",
        f"Target/fresh-test prevalence: {args.target_prevalence:.1%}",
        f"Partial-AUROC max FPR: {args.pauc_max_fpr:.2f}",
        "",
        "Winner-selection rules:",
        *[f"  - {METRIC_LABELS[m]}" for m in SELECTION_METRICS],
        "",
        "Key target-AUROC=0.70 results (no feature selection, maximum event count):",
    ]
    key = scenario_summary[
        (scenario_summary["feature_selection"] == "none")
        & (scenario_summary["selection_event_count"] == scenario_summary["selection_event_count"].max())
        & np.isclose(scenario_summary["target_auc"], 0.70)
    ].sort_values(["selection_prevalence", "selection_metric"])
    for _, row in key.iterrows():
        lines.append(
            "  "
            f"selection prevalence={row['selection_prevalence']:.0%}, "
            f"rule={METRIC_LABELS[row['selection_metric']]}, "
            f"fresh target AP={row['mean_fresh_test_target_ap']:.4f}, "
            f"target-AP regret={row['mean_target_ap_regret']:.4f}, "
            f"pipeline-p<0.05={row['pipeline_p_lt_0_05']:.3f}"
        )
    if not raw_vs_adjusted.empty:
        paired = raw_vs_adjusted[
            (raw_vs_adjusted["feature_selection"] == "none")
            & np.isclose(raw_vs_adjusted["target_auc"], 0.70)
        ]
        lines.extend(["", "Raw AP versus target-standardized AP (paired):"])
        for (events, prevalence), group in paired.groupby(
            ["selection_event_count", "selection_prevalence"], sort=True
        ):
            lines.append(
                "  "
                f"events={events}, selection prevalence={prevalence:.0%}: "
                f"adjusted-minus-raw fresh target AP="
                f"{group['adjusted_minus_raw_fresh_target_ap'].mean():.5f}; "
                f"same winner={group['same_winner'].mean():.3f}"
            )
    lines.extend(
        [
            "",
            "Interpretation guardrails:",
            "  * Raw AP estimates performance at the observed evaluation prevalence.",
            "  * Target-standardized AP uses class weights to estimate AP at the",
            "    prespecified target prevalence under class-conditional sampling.",
            "  * Raw AP measured at 50% and test AP measured at 5% are different",
            "    estimands; their numerical difference is not called optimism here.",
            "  * Standardization cannot repair spectrum shift, selection within outcome",
            "    classes, data leakage, or model misspecification.",
            "  * The fresh-test oracle is used only to quantify selection regret and is",
            "    not a deployable model-selection strategy.",
        ]
    )
    (output_dir / "summary.txt").write_text("\n".join(lines), encoding="utf-8")

def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(directory.parent))
    return zip_path


def main() -> None:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"pipeline_phase2d_{args.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    config_payload = vars(args).copy()
    config_payload["feature_selection_methods"] = list(args.feature_selection_methods)
    config_payload["target_aurocs"] = list(args.target_aurocs)
    config_payload["event_counts"] = list(args.event_counts)
    config_payload["selection_prevalences"] = list(args.selection_prevalences)
    config_payload["selection_designs"] = args.selection_designs
    config_payload["selection_metrics"] = list(SELECTION_METRICS)
    (output_dir / "config.json").write_text(
        json.dumps(config_payload, indent=2), encoding="utf-8"
    )

    environment = {
        "python": sys.version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
        "cpu_count": os.cpu_count(),
    }
    (output_dir / "environment.json").write_text(
        json.dumps(environment, indent=2), encoding="utf-8"
    )

    seed_sequence = np.random.SeedSequence(args.master_seed)
    child_sequences = seed_sequence.spawn(args.repetitions)
    seeds = [int(seq.generate_state(1, dtype=np.uint32)[0]) for seq in child_sequences]

    tasks = [
        (replication, seeds[replication - 1], target_auc, feature_selection)
        for replication in range(1, args.repetitions + 1)
        for target_auc in args.target_aurocs
        for feature_selection in args.feature_selection_methods
    ]

    print(
        f"Running {len(tasks):,} fitted-model tasks; each task evaluates "
        f"{len(args.selection_designs)} selection designs and "
        f"{len(SELECTION_METRICS)} winner rules."
    )
    start = time.time()
    results = Parallel(n_jobs=args.n_jobs, backend="loky", verbose=10)(
        delayed(run_replication)(rep, seed, auc, fs, args)
        for rep, seed, auc, fs in tasks
    )
    runtime_seconds = time.time() - start

    winner_rows: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []
    agreement_rows: list[dict[str, Any]] = []
    for winners, models, agreements in results:
        winner_rows.extend(winners)
        model_rows.extend(models)
        agreement_rows.extend(agreements)

    winner_df = pd.DataFrame(winner_rows)
    model_df = pd.DataFrame(model_rows)
    agreement_df = pd.DataFrame(agreement_rows)
    winner_df = add_pipeline_null_calibration(winner_df)
    scenario_summary, agreement_summary, rank_summary = make_summaries(
        winner_df, agreement_df
    )
    prevalence_effects = paired_prevalence_effects(winner_df)
    raw_vs_adjusted = paired_raw_vs_adjusted_ap(winner_df)

    output_dir.mkdir(parents=True, exist_ok=True)
    winner_df.to_csv(output_dir / "metric_winner_results.csv", index=False)
    model_df.to_csv(output_dir / "model_level_metric_results.csv", index=False)
    agreement_df.to_csv(output_dir / "metric_pair_replication_results.csv", index=False)
    scenario_summary.to_csv(output_dir / "metric_scenario_summary.csv", index=False)
    agreement_summary.to_csv(
        output_dir / "metric_winner_agreement_summary.csv", index=False
    )
    rank_summary.to_csv(output_dir / "metric_rank_correlation_summary.csv", index=False)
    prevalence_effects.to_csv(
        output_dir / "paired_selection_prevalence_effects.csv", index=False
    )
    raw_vs_adjusted.to_csv(
        output_dir / "paired_raw_vs_adjusted_ap_results.csv", index=False
    )

    save_plots(scenario_summary, agreement_summary, raw_vs_adjusted, output_dir)
    write_summary_text(
        args,
        scenario_summary,
        agreement_summary,
        raw_vs_adjusted,
        runtime_seconds,
        output_dir,
    )

    summary_json = {
        "runtime_seconds": runtime_seconds,
        "n_fitted_model_tasks": len(tasks),
        "n_metric_winner_rows": int(len(winner_df)),
        "n_model_level_rows": int(len(model_df)),
        "selection_metrics": list(SELECTION_METRICS),
        "target_prevalence": args.target_prevalence,
        "output_directory": str(output_dir),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary_json, indent=2), encoding="utf-8"
    )

    zip_path = zip_directory(output_dir)
    print(f"Completed in {runtime_seconds:.1f} seconds.")
    print(f"Results directory: {output_dir}")
    print(f"Upload this ZIP in the next turn: {zip_path}")

if __name__ == "__main__":
    main()
