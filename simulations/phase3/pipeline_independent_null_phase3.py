#!/usr/bin/env python3
"""
Phase 3: independent pipeline-null calibration for model-search inference.

Purpose
-------
This simulation validates a pipeline-aware empirical p-value using an
independent null reference bank. It compares:

1. Naive empirical p-value
   The selected winner is tested against the marginal null distribution of
   that algorithm, as if the algorithm had been prespecified.

2. Bonferroni empirical p-value
   Each algorithm is tested against its own marginal null distribution and
   the smallest p-value is multiplied by the number of candidate algorithms.

3. Pipeline-aware max-statistic p-value
   The observed best performance is tested against the independent null
   distribution of the best performance obtained after repeating the entire
   model-development and winner-selection pipeline.

For AUROC, two conventional rank-test comparators are also reported:

4. Naive one-sided Mann-Whitney p-value for the selected winner.
5. Bonferroni-adjusted minimum Mann-Whitney p-value across candidates.

The null reference bank and evaluation bank use separate random streams. The
same candidate models are fitted once per replication, and nested model pools
of size 1, 3, and 7 are evaluated from those fitted models.

Default quick design
--------------------
* Training set:                  500 observations, prevalence 10%
* Model-selection event counts: 20 and 100
* Model-selection prevalence:   10%
* Fresh-test set:               10,000 observations, prevalence 10%
* Candidate predictors:         30 (X1 signal + 29 noise variables)
* Feature selection:            LASSO and none
* Candidate model pools:        1, 3, and 7 algorithms
* Metrics:                      AUROC, average precision, pAUROC(FPR <= 0.10)
* Null reference replications:  2,000 per design
* Evaluation replications:      500 per target AUROC/design
* Evaluation target AUROCs:     0.50, 0.60, 0.70 for X1 alone

Shared dependencies are resolved from the repository simulation directories.

Example
-------
    python pipeline_independent_null_phase3.py --preset quick --n-jobs 16 \
        --output-root results_phase3
"""

from __future__ import annotations

import os

# Prevent nested BLAS/OpenMP parallelism inside joblib workers.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import json
import math
import platform
import sys
import time
import warnings
import zipfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

# Repository-local import paths for shared simulation code.
_REPO_ROOT = Path(__file__).resolve().parents[2]
for _shared_dir in (_REPO_ROOT / 'simulations' / 'phase1', _REPO_ROOT / 'simulations' / 'phase2'):
    if str(_shared_dir) not in sys.path:
        sys.path.insert(0, str(_shared_dir))
from typing import Any, Iterable

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from joblib import Parallel, delayed
from scipy.stats import mannwhitneyu
from sklearn.exceptions import ConvergenceWarning

try:
    import pipeline_null_pilot_v2 as base
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_null_pilot_v2.py was not found. Place it in the same "
        "directory as this script."
    ) from exc

try:
    import pipeline_event_prevalence_phase2b as phase2b
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_event_prevalence_phase2b.py was not found. Place it in the "
        "same directory as this script."
    ) from exc

try:
    import pipeline_metric_phase2c as phase2c
except ModuleNotFoundError as exc:
    raise SystemExit(
        "pipeline_metric_phase2c.py was not found. Place it in the same "
        "directory as this script."
    ) from exc


METRICS = (
    "roc_auc",
    "average_precision",
    "pauc_fpr_0_10",
)

METRIC_LABELS = {
    "roc_auc": "AUROC",
    "average_precision": "Average precision",
    "pauc_fpr_0_10": "Partial AUROC (FPR <= 0.10)",
}

METHOD_LABELS = {
    "naive_empirical": "Naive empirical",
    "bonferroni_empirical": "Bonferroni empirical",
    "pipeline_empirical": "Pipeline max-statistic",
    "naive_mannwhitney": "Naive Mann-Whitney",
    "bonferroni_mannwhitney": "Bonferroni Mann-Whitney",
}

# Nested pools. The three-model pool intentionally spans linear, tree, and
# ensemble families rather than taking the first three near-correlated models.
POOL_MODELS: dict[int, tuple[str, ...]] = {
    1: ("logistic_regression",),
    3: ("logistic_regression", "decision_tree", "random_forest"),
    7: tuple(base.MODEL_NAMES),
}

PRESETS: dict[str, dict[str, int]] = {
    "smoke": {
        "null_repetitions": 80,
        "evaluation_repetitions": 40,
        "n_train": 300,
        "n_test": 2_000,
        "cv_folds": 3,
    },
    "quick": {
        "null_repetitions": 2_000,
        "evaluation_repetitions": 500,
        "n_train": 500,
        "n_test": 10_000,
        "cv_folds": 5,
    },
    "full": {
        "null_repetitions": 10_000,
        "evaluation_repetitions": 2_000,
        "n_train": 500,
        "n_test": 20_000,
        "cv_folds": 5,
    },
}


def parse_int_list(value: str) -> tuple[int, ...]:
    try:
        parsed = tuple(sorted(set(int(x.strip()) for x in value.split(","))))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected comma-separated integers.") from exc
    if not parsed or any(x <= 0 for x in parsed):
        raise argparse.ArgumentTypeError("All values must be positive integers.")
    return parsed


def parse_float_list(value: str) -> tuple[float, ...]:
    try:
        parsed = tuple(sorted(set(float(x.strip()) for x in value.split(","))))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected comma-separated numbers.") from exc
    if not parsed:
        raise argparse.ArgumentTypeError("At least one value is required.")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Independent null-reference validation of pipeline-aware inference "
            "after clinical model search."
        )
    )
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--null-repetitions", type=int, default=None)
    parser.add_argument("--evaluation-repetitions", type=int, default=None)
    parser.add_argument("--n-train", type=int, default=None)
    parser.add_argument("--n-test", type=int, default=None)
    parser.add_argument("--train-prevalence", type=float, default=0.10)
    parser.add_argument("--selection-prevalence", type=float, default=0.10)
    parser.add_argument("--test-prevalence", type=float, default=0.10)
    parser.add_argument("--n-features", type=int, default=30)
    parser.add_argument("--binary-fraction", type=float, default=0.40)
    parser.add_argument("--correlation-rho", type=float, default=0.30)
    parser.add_argument("--cv-folds", type=int, default=None)
    parser.add_argument(
        "--event-counts",
        type=parse_int_list,
        default=(20, 100),
        help="Comma-separated event counts in each model-selection set.",
    )
    parser.add_argument(
        "--target-aurocs",
        type=parse_float_list,
        default=(0.50, 0.60, 0.70),
        help="X1-alone population AUROCs for the independent evaluation bank.",
    )
    parser.add_argument(
        "--feature-selection-methods",
        choices=("both", "lasso", "none"),
        default="both",
    )
    parser.add_argument(
        "--pool-sizes",
        type=parse_int_list,
        default=(1, 3, 7),
        help="Nested candidate-model pool sizes. Supported defaults: 1,3,7.",
    )
    parser.add_argument("--pauc-max-fpr", type=float, default=0.10)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--master-seed", type=int, default=20260718)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument(
        "--output-root",
        default="results_phase3",
        help="Parent directory for the timestamped result directory.",
    )
    args = parser.parse_args()

    preset = PRESETS[args.preset]
    args.null_repetitions = args.null_repetitions or preset["null_repetitions"]
    args.evaluation_repetitions = (
        args.evaluation_repetitions or preset["evaluation_repetitions"]
    )
    args.n_train = args.n_train or preset["n_train"]
    args.n_test = args.n_test or preset["n_test"]
    args.cv_folds = args.cv_folds or preset["cv_folds"]

    if args.feature_selection_methods == "both":
        args.feature_selection_methods = ("lasso", "none")
    else:
        args.feature_selection_methods = (args.feature_selection_methods,)

    if not 0.0 < args.train_prevalence < 1.0:
        parser.error("--train-prevalence must lie strictly between 0 and 1.")
    if not 0.0 < args.selection_prevalence < 1.0:
        parser.error("--selection-prevalence must lie strictly between 0 and 1.")
    if not 0.0 < args.test_prevalence < 1.0:
        parser.error("--test-prevalence must lie strictly between 0 and 1.")
    if not 0.0 <= args.binary_fraction <= 1.0:
        parser.error("--binary-fraction must lie in [0, 1].")
    if not -0.95 < args.correlation_rho < 0.95:
        parser.error("--correlation-rho must lie between -0.95 and 0.95.")
    if args.n_features < 2:
        parser.error("--n-features must be at least 2.")
    if args.null_repetitions < 20:
        parser.error("--null-repetitions must be at least 20.")
    if args.evaluation_repetitions < 10:
        parser.error("--evaluation-repetitions must be at least 10.")
    if not 0.0 < args.pauc_max_fpr <= 1.0:
        parser.error("--pauc-max-fpr must lie in (0, 1].")
    if not 0.0 < args.alpha < 1.0:
        parser.error("--alpha must lie in (0, 1).")
    if args.n_jobs == 0:
        parser.error("--n-jobs cannot be zero.")
    if any(not 0.50 <= x < 1.0 for x in args.target_aurocs):
        parser.error("Every target AUROC must lie in [0.50, 1.00).")
    if not any(math.isclose(x, 0.50) for x in args.target_aurocs):
        parser.error("--target-aurocs must include 0.50 for type-I error evaluation.")
    unsupported = [x for x in args.pool_sizes if x not in POOL_MODELS]
    if unsupported:
        parser.error(
            f"Unsupported pool size(s): {unsupported}. Supported sizes are "
            f"{sorted(POOL_MODELS)}."
        )

    n_train_events = base.event_count(args.n_train, args.train_prevalence)
    if min(n_train_events, args.n_train - n_train_events) < args.cv_folds:
        parser.error("Too few training observations per class for requested CV folds.")

    designs: list[dict[str, Any]] = []
    for event_count in args.event_counts:
        raw_n = event_count / args.selection_prevalence
        n_selection = int(round(raw_n))
        if not math.isclose(raw_n, n_selection, rel_tol=0.0, abs_tol=1e-9):
            parser.error(
                f"event_count={event_count} and selection prevalence="
                f"{args.selection_prevalence} do not produce an integer sample size."
            )
        observed = base.event_count(n_selection, args.selection_prevalence)
        if observed != event_count:
            parser.error(
                f"Internal event-count mismatch for n_selection={n_selection}."
            )
        designs.append(
            {
                "selection_event_count": int(event_count),
                "selection_non_event_count": int(n_selection - event_count),
                "selection_prevalence": float(args.selection_prevalence),
                "n_selection": int(n_selection),
            }
        )
    args.selection_designs = designs
    return args


def make_config(args: argparse.Namespace, feature_selection: str) -> base.SimulationConfig:
    first = args.selection_designs[0]
    return base.SimulationConfig(
        preset=args.preset,
        repetitions=args.evaluation_repetitions,
        n_train=args.n_train,
        n_selection=first["n_selection"],
        n_test=args.n_test,
        n_features=args.n_features,
        train_prevalence=args.train_prevalence,
        selection_prevalence=args.selection_prevalence,
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


def one_sided_mann_whitney_p(y: np.ndarray, scores: np.ndarray) -> float:
    """One-sided rank test that event scores exceed non-event scores."""
    event_scores = np.asarray(scores)[np.asarray(y) == 1]
    non_event_scores = np.asarray(scores)[np.asarray(y) == 0]
    if len(event_scores) == 0 or len(non_event_scores) == 0:
        return float("nan")
    if np.all(scores == scores[0]):
        return 1.0
    try:
        result = mannwhitneyu(
            event_scores,
            non_event_scores,
            alternative="greater",
            method="asymptotic",
        )
        return float(result.pvalue)
    except Exception:
        return float("nan")


def fit_model_pool(
    seed: int,
    target_auc: float,
    feature_selection: str,
    args: argparse.Namespace,
) -> tuple[
    np.ndarray,
    dict[str, Any],
    dict[str, dict[str, Any]],
    np.ndarray,
    np.ndarray,
]:
    """Generate training/test data, select variables, and fit all candidates."""
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
        args.test_prevalence,
        args.n_features,
        args.binary_fraction,
        args.correlation_rho,
        target_auc,
        phase2b.make_rng(seed, 2),
    )
    selected_indices, selector_info = base.select_predictors(
        x_train, y_train, config, seed
    )
    selected_count = int(len(selected_indices))

    fitted: dict[str, dict[str, Any]] = {}
    if selected_count == 0:
        dummy, _ = base.make_dummy_model(y_train)
        x_test_selected = np.zeros((args.n_test, 1), dtype=float)
        test_scores = base.continuous_prediction_scores(dummy, x_test_selected)
        test_metrics = phase2c.rank_metrics_from_scores(
            y_test, test_scores, args.test_prevalence, args.pauc_max_fpr
        )
        for name in base.MODEL_NAMES:
            fitted[name] = {
                "estimator": dummy,
                "intercept_only": True,
                "error": None,
                "test_metrics": test_metrics,
            }
    else:
        x_train_selected = x_train[:, selected_indices]
        x_test_selected = x_test[:, selected_indices]
        for name, estimator in base.build_candidate_models(seed).items():
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
                scores = base.continuous_prediction_scores(estimator, x_test_selected)
                info["test_metrics"] = phase2c.rank_metrics_from_scores(
                    y_test,
                    scores,
                    args.test_prevalence,
                    args.pauc_max_fpr,
                )
            except Exception as exc:
                info["error"] = f"{type(exc).__name__}: {exc}"
            fitted[name] = info

    return selected_indices, selector_info, fitted, x_test, y_test


def run_bank_replication(
    bank: str,
    replication: int,
    seed: int,
    target_auc: float,
    feature_selection: str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    """Run one complete pipeline replication and return model-level metrics."""
    selected_indices, selector_info, fitted, _, _ = fit_model_pool(
        seed, target_auc, feature_selection, args
    )
    selected_count = int(len(selected_indices))
    signal_included = bool(np.any(selected_indices == 0))

    rows: list[dict[str, Any]] = []
    for design in args.selection_designs:
        event_count = int(design["selection_event_count"])
        n_selection = int(design["n_selection"])
        prevalence = float(design["selection_prevalence"])
        x_selection, y_selection = phase2b.generate_signal_dataset(
            n_selection,
            prevalence,
            args.n_features,
            args.binary_fraction,
            args.correlation_rho,
            target_auc,
            phase2b.make_rng(seed, 100, event_count),
        )
        if selected_count == 0:
            x_selection_selected = np.zeros((n_selection, 1), dtype=float)
        else:
            x_selection_selected = x_selection[:, selected_indices]

        for model_name in base.MODEL_NAMES:
            info = fitted[model_name]
            row: dict[str, Any] = {
                "bank": bank,
                "replication": int(replication),
                "seed": int(seed),
                "target_auc": float(target_auc),
                "feature_selection": feature_selection,
                "selection_event_count": event_count,
                "selection_non_event_count": int(n_selection - event_count),
                "selection_prevalence": prevalence,
                "n_selection": n_selection,
                "model": model_name,
                "selected_feature_count": selected_count,
                "signal_included": signal_included,
                "noise_selected_count": int(selected_count - int(signal_included)),
                "lasso_selected_c": selector_info.get("lasso_selected_c"),
                "selector_error": selector_info.get("selector_error"),
                "intercept_only": bool(info["intercept_only"]),
                "error": info["error"],
            }
            if info["error"] is None:
                try:
                    scores = base.continuous_prediction_scores(
                        info["estimator"], x_selection_selected
                    )
                    selection_metrics = phase2c.rank_metrics_from_scores(
                        y_selection, scores, prevalence, args.pauc_max_fpr
                    )
                    test_metrics = info["test_metrics"]
                    for key, value in selection_metrics.items():
                        row[f"selection_{key}"] = float(value)
                    for key, value in test_metrics.items():
                        row[f"test_{key}"] = float(value)
                    row["selection_mannwhitney_p"] = one_sided_mann_whitney_p(
                        y_selection, scores
                    )
                except Exception as exc:
                    row["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(row)
    return rows


def empirical_upper_p(observed: float, reference: np.ndarray) -> float:
    reference = np.asarray(reference, dtype=float)
    reference = reference[np.isfinite(reference)]
    if not math.isfinite(float(observed)) or len(reference) == 0:
        return float("nan")
    return float((1 + np.count_nonzero(reference >= observed)) / (len(reference) + 1))


def winner_from_pool(
    group: pd.DataFrame,
    models: tuple[str, ...],
    metric: str,
) -> pd.Series:
    subset = group[group["model"].isin(models)].copy()
    subset = subset[subset["error"].isna()]
    value_col = f"selection_{metric}"
    subset = subset[np.isfinite(subset[value_col].astype(float))]
    if subset.empty:
        raise RuntimeError(f"No valid models for metric={metric}, pool={models}.")
    max_value = float(subset[value_col].max())
    tied = subset[np.isclose(subset[value_col], max_value, rtol=1e-12, atol=1e-12)]
    order = {name: i for i, name in enumerate(base.MODEL_NAMES)}
    tied = tied.assign(_order=tied["model"].map(order)).sort_values("_order")
    return tied.iloc[0]


def make_reference_lookup(reference_df: pd.DataFrame) -> dict[str, Any]:
    """Prepare model-specific and max-statistic null distributions."""
    lookup: dict[str, Any] = {"marginal": {}, "max": {}}
    group_cols = ["feature_selection", "selection_event_count"]
    for group_key, group in reference_df.groupby(group_cols, sort=False):
        fs, event_count = group_key
        for metric in METRICS:
            value_col = f"selection_{metric}"
            for model_name in base.MODEL_NAMES:
                values = group.loc[group["model"] == model_name, value_col].to_numpy(float)
                lookup["marginal"][(fs, int(event_count), metric, model_name)] = values

            # Build one row per replication, then nested maxima by pool.
            pivot = group.pivot_table(
                index="replication", columns="model", values=value_col, aggfunc="first"
            )
            for pool_size, models in POOL_MODELS.items():
                available = [m for m in models if m in pivot.columns]
                values = pivot[available].max(axis=1, skipna=True).to_numpy(float)
                lookup["max"][(fs, int(event_count), metric, pool_size)] = values
    return lookup


def evaluate_against_reference(
    evaluation_df: pd.DataFrame,
    reference_lookup: dict[str, Any],
    args: argparse.Namespace,
) -> pd.DataFrame:
    """Calculate independent-bank p-values for each evaluation replication."""
    rows: list[dict[str, Any]] = []
    group_cols = [
        "replication",
        "seed",
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "selection_non_event_count",
        "selection_prevalence",
        "n_selection",
    ]
    for keys, group in evaluation_df.groupby(group_cols, sort=False, dropna=False):
        metadata = dict(zip(group_cols, keys))
        fs = str(metadata["feature_selection"])
        event_count = int(metadata["selection_event_count"])

        for pool_size in args.pool_sizes:
            models = POOL_MODELS[int(pool_size)]
            pool = group[group["model"].isin(models)].copy()
            pool = pool[pool["error"].isna()]
            if pool.empty:
                continue

            for metric in METRICS:
                winner = winner_from_pool(group, models, metric)
                observed_max = float(winner[f"selection_{metric}"])
                winner_name = str(winner["model"])

                marginal_p_values: list[float] = []
                for model_name in models:
                    model_row = pool[pool["model"] == model_name]
                    if model_row.empty:
                        continue
                    observed = float(model_row.iloc[0][f"selection_{metric}"])
                    reference = reference_lookup["marginal"][
                        (fs, event_count, metric, model_name)
                    ]
                    marginal_p_values.append(empirical_upper_p(observed, reference))

                winner_reference = reference_lookup["marginal"][
                    (fs, event_count, metric, winner_name)
                ]
                naive_empirical = empirical_upper_p(observed_max, winner_reference)
                min_marginal = float(np.nanmin(marginal_p_values))
                bonferroni_empirical = min(1.0, pool_size * min_marginal)
                max_reference = reference_lookup["max"][
                    (fs, event_count, metric, int(pool_size))
                ]
                pipeline_empirical = empirical_upper_p(observed_max, max_reference)

                base_row: dict[str, Any] = {
                    **metadata,
                    "pool_size": int(pool_size),
                    "pool_models": "|".join(models),
                    "metric": metric,
                    "metric_label": METRIC_LABELS[metric],
                    "best_model": winner_name,
                    "best_selection_metric": observed_max,
                    "selected_model_test_metric": float(winner[f"test_{metric}"]),
                    "selection_induced_optimism": float(
                        observed_max - float(winner[f"test_{metric}"])
                    ),
                    "selected_feature_count": int(winner["selected_feature_count"]),
                    "signal_included": bool(winner["signal_included"]),
                }

                for method, p_value in (
                    ("naive_empirical", naive_empirical),
                    ("bonferroni_empirical", bonferroni_empirical),
                    ("pipeline_empirical", pipeline_empirical),
                ):
                    rows.append(
                        {
                            **base_row,
                            "method": method,
                            "method_label": METHOD_LABELS[method],
                            "p_value": float(p_value),
                            "reject": bool(p_value < args.alpha),
                        }
                    )

                if metric == "roc_auc":
                    winner_mw = float(winner["selection_mannwhitney_p"])
                    mw_values = pool["selection_mannwhitney_p"].to_numpy(float)
                    mw_values = mw_values[np.isfinite(mw_values)]
                    min_mw = float(np.min(mw_values)) if len(mw_values) else float("nan")
                    bonferroni_mw = min(1.0, pool_size * min_mw)
                    for method, p_value in (
                        ("naive_mannwhitney", winner_mw),
                        ("bonferroni_mannwhitney", bonferroni_mw),
                    ):
                        rows.append(
                            {
                                **base_row,
                                "method": method,
                                "method_label": METHOD_LABELS[method],
                                "p_value": float(p_value),
                                "reject": bool(p_value < args.alpha),
                            }
                        )
    return pd.DataFrame(rows)


def summarize_methods(results: pd.DataFrame, alpha: float) -> pd.DataFrame:
    grouping = [
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "pool_size",
        "metric",
        "method",
    ]
    summary = (
        results.groupby(grouping, dropna=False)
        .agg(
            n=("p_value", "size"),
            rejection_rate=("reject", "mean"),
            mean_p_value=("p_value", "mean"),
            median_p_value=("p_value", "median"),
            mean_selection_metric=("best_selection_metric", "mean"),
            mean_test_metric=("selected_model_test_metric", "mean"),
            mean_optimism=("selection_induced_optimism", "mean"),
        )
        .reset_index()
    )
    summary["alpha"] = alpha
    return summary


def monte_carlo_se(rate: float, n: int) -> float:
    if n <= 0 or not math.isfinite(rate):
        return float("nan")
    return float(math.sqrt(max(rate * (1.0 - rate), 0.0) / n))


def add_mc_intervals(summary: pd.DataFrame) -> pd.DataFrame:
    result = summary.copy()
    ses = [monte_carlo_se(float(r), int(n)) for r, n in zip(result["rejection_rate"], result["n"])]
    result["rejection_rate_mcse"] = ses
    result["rejection_rate_mc95_low"] = np.maximum(
        0.0, result["rejection_rate"] - 1.96 * result["rejection_rate_mcse"]
    )
    result["rejection_rate_mc95_high"] = np.minimum(
        1.0, result["rejection_rate"] + 1.96 * result["rejection_rate_mcse"]
    )
    return result


def plot_type1_error(summary: pd.DataFrame, output_dir: Path, alpha: float) -> None:
    null = summary[np.isclose(summary["target_auc"], 0.50)].copy()
    if null.empty:
        return
    metrics = list(METRICS)
    for metric in metrics:
        subset = null[null["metric"] == metric].copy()
        if subset.empty:
            continue
        labels = []
        values = []
        errors = []
        for _, row in subset.sort_values(
            ["feature_selection", "selection_event_count", "pool_size", "method"]
        ).iterrows():
            labels.append(
                f"{row['feature_selection']}\nE={int(row['selection_event_count'])}, "
                f"K={int(row['pool_size'])}\n{METHOD_LABELS.get(row['method'], row['method'])}"
            )
            values.append(float(row["rejection_rate"]))
            errors.append(1.96 * float(row["rejection_rate_mcse"]))
        fig_width = max(12, 0.48 * len(labels))
        fig, ax = plt.subplots(figsize=(fig_width, 6))
        x = np.arange(len(labels))
        ax.errorbar(x, values, yerr=errors, fmt="o", capsize=3)
        ax.axhline(alpha, linestyle="--", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=65, ha="right", fontsize=8)
        ax.set_ylim(0, max(0.20, max(values, default=0.1) * 1.25))
        ax.set_ylabel("Type I error rate")
        ax.set_title(f"Independent-bank type I error: {METRIC_LABELS[metric]}")
        fig.tight_layout()
        fig.savefig(output_dir / f"01_type1_error_{metric}.png", dpi=180)
        plt.close(fig)


def plot_power(summary: pd.DataFrame, output_dir: Path) -> None:
    signal = summary[summary["target_auc"] > 0.50].copy()
    if signal.empty:
        return
    for metric in METRICS:
        subset = signal[signal["metric"] == metric].copy()
        if subset.empty:
            continue
        for event_count in sorted(subset["selection_event_count"].unique()):
            for fs in sorted(subset["feature_selection"].unique()):
                data = subset[
                    (subset["selection_event_count"] == event_count)
                    & (subset["feature_selection"] == fs)
                ]
                fig, ax = plt.subplots(figsize=(9, 6))
                for (pool_size, method), group in data.groupby(["pool_size", "method"]):
                    group = group.sort_values("target_auc")
                    ax.plot(
                        group["target_auc"],
                        group["rejection_rate"],
                        marker="o",
                        label=f"K={int(pool_size)}: {METHOD_LABELS.get(method, method)}",
                    )
                ax.set_ylim(0, 1.02)
                ax.set_xlabel("Population AUROC of X1 alone")
                ax.set_ylabel("Rejection rate (power)")
                ax.set_title(
                    f"Power: {METRIC_LABELS[metric]}, {fs}, E={int(event_count)}"
                )
                ax.legend(fontsize=8, ncol=2)
                fig.tight_layout()
                fig.savefig(
                    output_dir / f"02_power_{metric}_{fs}_events{int(event_count)}.png",
                    dpi=180,
                )
                plt.close(fig)


def plot_null_pvalue_ecdf(results: pd.DataFrame, output_dir: Path) -> None:
    null = results[np.isclose(results["target_auc"], 0.50)].copy()
    if null.empty:
        return
    # One representative setting keeps the figure readable.
    max_events = int(null["selection_event_count"].max())
    max_pool = int(null["pool_size"].max())
    for metric in METRICS:
        subset = null[
            (null["metric"] == metric)
            & (null["selection_event_count"] == max_events)
            & (null["pool_size"] == max_pool)
            & (null["feature_selection"] == "none")
        ]
        if subset.empty:
            continue
        fig, ax = plt.subplots(figsize=(7, 6))
        for method, group in subset.groupby("method"):
            p = np.sort(group["p_value"].dropna().to_numpy(float))
            if len(p) == 0:
                continue
            ecdf = np.arange(1, len(p) + 1) / len(p)
            ax.step(p, ecdf, where="post", label=METHOD_LABELS.get(method, method))
        ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="Uniform(0,1)")
        ax.set_xlabel("p-value")
        ax.set_ylabel("Empirical cumulative probability")
        ax.set_title(
            f"Null p-value calibration: {METRIC_LABELS[metric]}\n"
            f"no feature selection, E={max_events}, K={max_pool}"
        )
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(output_dir / f"03_null_pvalue_ecdf_{metric}.png", dpi=180)
        plt.close(fig)


def plot_naive_vs_pipeline(results: pd.DataFrame, output_dir: Path) -> None:
    # Pivot paired p-values and display the most search-intensive null setting.
    null = results[np.isclose(results["target_auc"], 0.50)].copy()
    if null.empty:
        return
    max_events = int(null["selection_event_count"].max())
    max_pool = int(null["pool_size"].max())
    for metric in METRICS:
        subset = null[
            (null["metric"] == metric)
            & (null["selection_event_count"] == max_events)
            & (null["pool_size"] == max_pool)
            & (null["feature_selection"] == "none")
            & (null["method"].isin(["naive_empirical", "pipeline_empirical"]))
        ]
        if subset.empty:
            continue
        pivot = subset.pivot_table(
            index="replication", columns="method", values="p_value", aggfunc="first"
        ).dropna()
        if pivot.empty:
            continue
        fig, ax = plt.subplots(figsize=(6.5, 6))
        ax.scatter(
            pivot["naive_empirical"],
            pivot["pipeline_empirical"],
            s=12,
            alpha=0.45,
        )
        ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1)
        ax.set_xlabel("Naive empirical p-value")
        ax.set_ylabel("Pipeline-aware p-value")
        ax.set_title(
            f"Naive vs pipeline-aware inference: {METRIC_LABELS[metric]}\n"
            f"null, no feature selection, E={max_events}, K={max_pool}"
        )
        fig.tight_layout()
        fig.savefig(output_dir / f"04_naive_vs_pipeline_{metric}.png", dpi=180)
        plt.close(fig)


def write_summary_text(
    path: Path,
    args: argparse.Namespace,
    summary: pd.DataFrame,
    elapsed_seconds: float,
) -> None:
    lines: list[str] = []
    lines.append("PHASE 3: INDEPENDENT PIPELINE-NULL CALIBRATION")
    lines.append("=" * 58)
    lines.append(f"Preset: {args.preset}")
    lines.append(f"Independent null reference replications/design: {args.null_repetitions}")
    lines.append(f"Independent evaluation replications/signal/design: {args.evaluation_repetitions}")
    lines.append(f"Model-selection event counts: {list(args.event_counts)}")
    lines.append(f"Model-selection prevalence: {args.selection_prevalence:.3f}")
    lines.append(f"Target X1 AUROCs: {list(args.target_aurocs)}")
    lines.append(f"Feature-selection methods: {list(args.feature_selection_methods)}")
    lines.append(f"Candidate pool sizes: {list(args.pool_sizes)}")
    lines.append(f"Metrics: {[METRIC_LABELS[m] for m in METRICS]}")
    lines.append(f"Alpha: {args.alpha:.3f}")
    lines.append(f"Elapsed seconds: {elapsed_seconds:.1f}")
    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("- Naive empirical p-values ignore that the winning algorithm was selected.")
    lines.append("- Bonferroni empirical p-values adjust marginal model-specific tests.")
    lines.append("- Pipeline p-values use an independent null distribution of the maximum")
    lines.append("  metric after repeating the complete model-development and search process.")
    lines.append("- Under target AUROC 0.50, rejection rates estimate type I error.")
    lines.append("- Under target AUROC >0.50, rejection rates estimate power.")
    lines.append("")

    compact = summary[
        (summary["metric"] == "roc_auc")
        & (summary["pool_size"] == max(args.pool_sizes))
    ].copy()
    for target in sorted(compact["target_auc"].unique()):
        label = "TYPE I ERROR" if math.isclose(float(target), 0.50) else f"POWER AT X1 AUROC {target:.2f}"
        lines.append(label)
        lines.append("-" * len(label))
        table = compact[np.isclose(compact["target_auc"], target)][
            [
                "feature_selection",
                "selection_event_count",
                "method",
                "rejection_rate",
                "rejection_rate_mcse",
                "mean_selection_metric",
                "mean_test_metric",
            ]
        ].sort_values(["feature_selection", "selection_event_count", "method"])
        lines.append(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
        lines.append("")

    min_reference_p = 1.0 / (args.null_repetitions + 1)
    lines.append(
        f"Smallest attainable empirical reference-bank p-value: {min_reference_p:.6g}"
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory.parent))
    return zip_path


def flatten(list_of_lists: Iterable[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in list_of_lists:
        output.extend(item)
    return output


def main() -> None:
    args = parse_args()
    started = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"pipeline_phase3_{args.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    config_payload = vars(args).copy()
    config_payload["selection_designs"] = args.selection_designs
    config_payload["pool_models"] = {str(k): list(v) for k, v in POOL_MODELS.items()}
    (output_dir / "config.json").write_text(
        json.dumps(config_payload, indent=2, cls=base.NumpyJSONEncoder),
        encoding="utf-8",
    )
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }
    (output_dir / "environment.json").write_text(
        json.dumps(environment, indent=2), encoding="utf-8"
    )

    print("Phase 3 independent null calibration")
    print(f"Output: {output_dir}")
    print(
        f"Reference tasks: {args.null_repetitions * len(args.feature_selection_methods):,}"
    )
    print(
        "Evaluation tasks: "
        f"{args.evaluation_repetitions * len(args.target_aurocs) * len(args.feature_selection_methods):,}"
    )

    # Distinct seed namespaces guarantee independence of the two banks.
    reference_tasks: list[tuple[int, int, str]] = []
    for fs_index, fs in enumerate(args.feature_selection_methods):
        for replication in range(args.null_repetitions):
            seed = int(
                np.random.SeedSequence(
                    [args.master_seed, 31001, fs_index, replication]
                ).generate_state(1, dtype=np.uint32)[0]
            )
            reference_tasks.append((replication, seed, fs))

    reference_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(run_bank_replication)(
            "reference",
            replication,
            seed,
            0.50,
            fs,
            args,
        )
        for replication, seed, fs in reference_tasks
    )
    reference_df = pd.DataFrame(flatten(reference_results))

    evaluation_tasks: list[tuple[int, int, float, str]] = []
    for fs_index, fs in enumerate(args.feature_selection_methods):
        for target_index, target_auc in enumerate(args.target_aurocs):
            for replication in range(args.evaluation_repetitions):
                seed = int(
                    np.random.SeedSequence(
                        [args.master_seed, 32003, fs_index, target_index, replication]
                    ).generate_state(1, dtype=np.uint32)[0]
                )
                evaluation_tasks.append((replication, seed, float(target_auc), fs))

    evaluation_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(run_bank_replication)(
            "evaluation",
            replication,
            seed,
            target_auc,
            fs,
            args,
        )
        for replication, seed, target_auc, fs in evaluation_tasks
    )
    evaluation_df = pd.DataFrame(flatten(evaluation_results))

    # Recreate output directory immediately before all writes in case a synced
    # filesystem removed an empty timestamped directory during computation.
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_df.to_csv(output_dir / "null_reference_model_metrics.csv", index=False)
    evaluation_df.to_csv(output_dir / "evaluation_model_metrics.csv", index=False)

    reference_lookup = make_reference_lookup(reference_df)
    inference_df = evaluate_against_reference(evaluation_df, reference_lookup, args)
    inference_df.to_csv(output_dir / "independent_inference_results.csv", index=False)

    summary = add_mc_intervals(summarize_methods(inference_df, args.alpha))
    summary.to_csv(output_dir / "method_performance_summary.csv", index=False)

    type1 = summary[np.isclose(summary["target_auc"], 0.50)].copy()
    type1.to_csv(output_dir / "type1_error_summary.csv", index=False)
    power = summary[summary["target_auc"] > 0.50].copy()
    power.to_csv(output_dir / "power_summary.csv", index=False)

    plot_type1_error(summary, output_dir, args.alpha)
    plot_power(summary, output_dir)
    plot_null_pvalue_ecdf(inference_df, output_dir)
    plot_naive_vs_pipeline(inference_df, output_dir)

    elapsed = time.time() - started
    write_summary_text(output_dir / "summary.txt", args, summary, elapsed)
    (output_dir / "run_complete.json").write_text(
        json.dumps(
            {
                "completed": True,
                "elapsed_seconds": elapsed,
                "reference_rows": int(len(reference_df)),
                "evaluation_model_rows": int(len(evaluation_df)),
                "inference_rows": int(len(inference_df)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    zip_path = zip_directory(output_dir)
    print(f"Completed in {elapsed:.1f} seconds")
    print(f"Result directory: {output_dir}")
    print(f"Upload this ZIP next: {zip_path}")


if __name__ == "__main__":
    main()
