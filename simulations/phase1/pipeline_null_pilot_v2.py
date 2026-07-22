#!/usr/bin/env python3
"""
Pipeline-aware null simulation for clinical prediction models.

Purpose
-------
This script estimates how much apparent predictive performance can arise under
an exact null hypothesis (X independent of Y) after repeating an entire model-
development pipeline:

    synthetic predictors -> optional LASSO selection -> fit several algorithms
    -> choose the best algorithm in a model-selection set -> re-evaluate the
    chosen algorithm in a completely untouched fresh test set.

The first-stage pilot is intentionally generic and uses rounded design values.
It is not intended to reproduce any unpublished manuscript.

Outputs
-------
A timestamped results directory and a ZIP archive containing:
- config.json
- environment.json
- replication_results.csv
- model_level_results.csv
- pool_size_results.csv
- feature_selection_frequency.csv
- summary.json
- summary.txt
- diagnostic plots

Example
-------
    python pipeline_null_pilot.py --preset quick --n-jobs -1
"""

from __future__ import annotations

# Prevent nested BLAS/OpenMP parallelism when joblib parallelizes replications.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import itertools
import json
import math
import platform
import sys
import time
import warnings
import zipfile
from dataclasses import asdict, dataclass
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
from scipy.stats import norm
from sklearn.base import BaseEstimator
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold


MODEL_NAMES = (
    "logistic_regression",
    "linear_svm",
    "rbf_svm",
    "gaussian_nb",
    "decision_tree",
    "random_forest",
    "hist_gradient_boosting",
)

METRIC_COLUMNS = (
    "roc_auc",
    "average_precision",
    "accuracy",
    "balanced_accuracy",
    "sensitivity",
    "specificity",
    "ppv",
    "npv",
)

PRESETS: dict[str, dict[str, Any]] = {
    "smoke": {
        "repetitions": 10,
        "n_train": 300,
        "n_selection": 120,
        "n_test": 1_000,
        "n_features": 20,
        "train_prevalence": 0.10,
        "selection_prevalence": 0.10,
        "test_prevalence": 0.10,
        "cv_folds": 3,
    },
    "quick": {
        "repetitions": 200,
        "n_train": 500,
        "n_selection": 200,
        "n_test": 5_000,
        "n_features": 30,
        "train_prevalence": 0.10,
        "selection_prevalence": 0.10,
        "test_prevalence": 0.10,
        "cv_folds": 5,
    },
    "full": {
        "repetitions": 2_000,
        "n_train": 500,
        "n_selection": 200,
        "n_test": 20_000,
        "n_features": 30,
        "train_prevalence": 0.10,
        "selection_prevalence": 0.10,
        "test_prevalence": 0.10,
        "cv_folds": 5,
    },
}


@dataclass(frozen=True)
class SimulationConfig:
    preset: str
    repetitions: int
    n_train: int
    n_selection: int
    n_test: int
    n_features: int
    train_prevalence: float
    selection_prevalence: float
    test_prevalence: float
    binary_fraction: float
    correlation_rho: float
    feature_selection: str
    cv_folds: int
    selection_metric: str
    master_seed: int
    n_jobs: int
    reference_performance: float | None
    output_root: str


class NumpyJSONEncoder(json.JSONEncoder):
    """Convert NumPy/scalar/path objects into JSON-compatible values."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            value = float(obj)
            return None if not math.isfinite(value) else value
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Run a pipeline-aware null simulation: LASSO feature selection, "
            "seven candidate algorithms, selection-set winner, and untouched test evaluation."
        )
    )
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--repetitions", type=int, default=None)
    parser.add_argument("--n-train", type=int, default=None)
    parser.add_argument("--n-selection", type=int, default=None)
    parser.add_argument("--n-test", type=int, default=None)
    parser.add_argument("--n-features", type=int, default=None)
    parser.add_argument("--train-prevalence", type=float, default=None)
    parser.add_argument("--selection-prevalence", type=float, default=None)
    parser.add_argument("--test-prevalence", type=float, default=None)
    parser.add_argument(
        "--binary-fraction",
        type=float,
        default=0.40,
        help="Fraction of predictors converted to binary variables (default: 0.40).",
    )
    parser.add_argument(
        "--correlation-rho",
        type=float,
        default=0.30,
        help="AR(1) latent correlation between adjacent predictors (default: 0.30).",
    )
    parser.add_argument(
        "--feature-selection",
        choices=("lasso", "none"),
        default="lasso",
    )
    parser.add_argument("--cv-folds", type=int, default=None)
    parser.add_argument(
        "--selection-metric",
        choices=("roc_auc", "average_precision", "accuracy", "balanced_accuracy"),
        default="roc_auc",
        help="Metric used to choose the winning algorithm in the selection set.",
    )
    parser.add_argument("--master-seed", type=int, default=20260717)
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=4,
        help="Parallel replications (default: 4). Use -1 only if you intentionally want all cores.",
    )
    parser.add_argument(
        "--reference-performance",
        type=float,
        default=None,
        help=(
            "Optional PUBLIC benchmark on the selected metric. The script estimates "
            "the null exceedance probability P(max selection performance >= benchmark)."
        ),
    )
    parser.add_argument(
        "--output-root",
        default="results",
        help="Parent directory for timestamped results (default: results).",
    )

    args = parser.parse_args()
    preset = dict(PRESETS[args.preset])

    overrides = {
        "repetitions": args.repetitions,
        "n_train": args.n_train,
        "n_selection": args.n_selection,
        "n_test": args.n_test,
        "n_features": args.n_features,
        "train_prevalence": args.train_prevalence,
        "selection_prevalence": args.selection_prevalence,
        "test_prevalence": args.test_prevalence,
        "cv_folds": args.cv_folds,
    }
    for key, value in overrides.items():
        if value is not None:
            preset[key] = value

    config = SimulationConfig(
        preset=args.preset,
        repetitions=preset["repetitions"],
        n_train=preset["n_train"],
        n_selection=preset["n_selection"],
        n_test=preset["n_test"],
        n_features=preset["n_features"],
        train_prevalence=preset["train_prevalence"],
        selection_prevalence=preset["selection_prevalence"],
        test_prevalence=preset["test_prevalence"],
        binary_fraction=args.binary_fraction,
        correlation_rho=args.correlation_rho,
        feature_selection=args.feature_selection,
        cv_folds=preset["cv_folds"],
        selection_metric=args.selection_metric,
        master_seed=args.master_seed,
        n_jobs=args.n_jobs,
        reference_performance=args.reference_performance,
        output_root=args.output_root,
    )
    validate_config(config)
    return config


def validate_config(config: SimulationConfig) -> None:
    integer_positive = {
        "repetitions": config.repetitions,
        "n_train": config.n_train,
        "n_selection": config.n_selection,
        "n_test": config.n_test,
        "n_features": config.n_features,
        "cv_folds": config.cv_folds,
    }
    for name, value in integer_positive.items():
        if value < 1:
            raise ValueError(f"{name} must be >= 1; got {value}.")

    for name, value in {
        "train_prevalence": config.train_prevalence,
        "selection_prevalence": config.selection_prevalence,
        "test_prevalence": config.test_prevalence,
    }.items():
        if not 0.0 < value < 1.0:
            raise ValueError(f"{name} must be between 0 and 1; got {value}.")

    if not 0.0 <= config.binary_fraction <= 1.0:
        raise ValueError("binary_fraction must be in [0, 1].")
    if not -0.95 < config.correlation_rho < 0.95:
        raise ValueError("correlation_rho must be between -0.95 and 0.95.")
    if config.n_jobs == 0:
        raise ValueError("n_jobs cannot be 0.")

    n_train_events = event_count(config.n_train, config.train_prevalence)
    n_train_nonevents = config.n_train - n_train_events
    if min(n_train_events, n_train_nonevents) < config.cv_folds:
        raise ValueError(
            "The training set has too few observations in one class for the requested "
            f"{config.cv_folds}-fold CV: events={n_train_events}, non-events={n_train_nonevents}."
        )

    if config.reference_performance is not None and not 0.0 <= config.reference_performance <= 1.0:
        raise ValueError("reference_performance must be in [0, 1].")


def event_count(n: int, prevalence: float) -> int:
    return max(1, min(n - 1, int(round(n * prevalence))))


def generate_fixed_outcome(n: int, prevalence: float, rng: np.random.Generator) -> np.ndarray:
    n_events = event_count(n, prevalence)
    y = np.zeros(n, dtype=np.int8)
    y[:n_events] = 1
    rng.shuffle(y)
    return y


def generate_latent_ar1(
    n: int, n_features: int, rho: float, rng: np.random.Generator
) -> np.ndarray:
    innovations = rng.normal(size=(n, n_features))
    latent = np.empty_like(innovations)
    latent[:, 0] = innovations[:, 0]
    innovation_scale = math.sqrt(1.0 - rho**2)
    for j in range(1, n_features):
        latent[:, j] = rho * latent[:, j - 1] + innovation_scale * innovations[:, j]
    return latent


def binary_probabilities(n_binary: int) -> np.ndarray:
    if n_binary == 0:
        return np.empty(0, dtype=float)
    # Deterministic marginal frequencies spanning reasonably common clinical variables.
    return np.linspace(0.10, 0.50, n_binary)


def generate_predictors(
    n: int,
    n_features: int,
    binary_fraction: float,
    rho: float,
    rng: np.random.Generator,
) -> np.ndarray:
    latent = generate_latent_ar1(n, n_features, rho, rng)
    n_binary = int(round(n_features * binary_fraction))
    n_continuous = n_features - n_binary
    x = latent.copy()

    if n_binary > 0:
        probabilities = binary_probabilities(n_binary)
        thresholds = norm.ppf(1.0 - probabilities)
        x[:, n_continuous:] = (
            latent[:, n_continuous:] > thresholds[np.newaxis, :]
        ).astype(float)
    return x.astype(np.float64, copy=False)


def select_predictors(
    x_train: np.ndarray,
    y_train: np.ndarray,
    config: SimulationConfig,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    if config.feature_selection == "none":
        selected = np.arange(x_train.shape[1], dtype=int)
        return selected, {"lasso_selected_c": None, "selector_error": None}

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_train)
    cv = StratifiedKFold(n_splits=config.cv_folds, shuffle=True, random_state=seed)
    selector = LogisticRegressionCV(
        Cs=np.logspace(-3, 2, 10),
        cv=cv,
        penalty="l1",
        solver="liblinear",
        scoring="roc_auc",
        max_iter=3_000,
        refit=True,
        random_state=seed,
        n_jobs=1,
    )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ConvergenceWarning)
            warnings.simplefilter("ignore", category=FutureWarning)
            selector.fit(x_scaled, y_train)
        coefficients = np.asarray(selector.coef_).ravel()
        selected = np.flatnonzero(np.abs(coefficients) > 1e-8)
        selected_c = float(np.asarray(selector.C_).ravel()[0])
        return selected.astype(int), {
            "lasso_selected_c": selected_c,
            "selector_error": None,
        }
    except Exception as exc:  # Defensive: preserve the replication and record failure.
        return np.empty(0, dtype=int), {
            "lasso_selected_c": None,
            "selector_error": f"{type(exc).__name__}: {exc}",
        }


def build_candidate_models(seed: int) -> dict[str, BaseEstimator]:
    return {
        "logistic_regression": Pipeline(
            [
                ("variance", VarianceThreshold()),
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        penalty="l2",
                        C=1.0,
                        solver="liblinear",
                        max_iter=2_000,
                        random_state=seed + 11,
                    ),
                ),
            ]
        ),
        "linear_svm": Pipeline(
            [
                ("variance", VarianceThreshold()),
                ("scale", StandardScaler()),
                (
                    "model",
                    LinearSVC(
                        C=1.0,
                        dual=False,
                        max_iter=5_000,
                        random_state=seed + 23,
                    ),
                ),
            ]
        ),
        "rbf_svm": Pipeline(
            [
                ("variance", VarianceThreshold()),
                ("scale", StandardScaler()),
                (
                    "model",
                    SVC(
                        C=1.0,
                        kernel="rbf",
                        gamma="scale",
                        probability=False,
                        cache_size=500,
                        random_state=seed + 37,
                    ),
                ),
            ]
        ),
        "gaussian_nb": Pipeline(
            [
                ("variance", VarianceThreshold()),
                ("model", GaussianNB(var_smoothing=1e-9)),
            ]
        ),
        "decision_tree": DecisionTreeClassifier(
            min_samples_leaf=5,
            random_state=seed + 41,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_features="sqrt",
            min_samples_leaf=2,
            n_jobs=1,
            random_state=seed + 53,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=100,
            max_leaf_nodes=15,
            learning_rate=0.10,
            l2_regularization=1.0,
            random_state=seed + 67,
        ),
    }


def continuous_prediction_scores(estimator: BaseEstimator, x: np.ndarray) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        probabilities = np.asarray(estimator.predict_proba(x))
        if probabilities.ndim == 2 and probabilities.shape[1] >= 2:
            return probabilities[:, 1]
        return probabilities.ravel()
    if hasattr(estimator, "decision_function"):
        return np.asarray(estimator.decision_function(x)).ravel()
    return np.asarray(estimator.predict(x), dtype=float).ravel()


def safe_ratio(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator > 0 else float("nan")


def evaluate_model(estimator: BaseEstimator, x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    score = continuous_prediction_scores(estimator, x)
    predicted = np.asarray(estimator.predict(x)).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()

    return {
        "roc_auc": float(roc_auc_score(y, score)),
        "average_precision": float(average_precision_score(y, score)),
        "accuracy": float(accuracy_score(y, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "sensitivity": safe_ratio(tp, tp + fn),
        "specificity": safe_ratio(tn, tn + fp),
        "ppv": safe_ratio(tp, tp + fp),
        "npv": safe_ratio(tn, tn + fn),
    }


def make_dummy_model(y_train: np.ndarray) -> tuple[DummyClassifier, np.ndarray]:
    x_dummy = np.zeros((len(y_train), 1), dtype=float)
    model = DummyClassifier(strategy="prior")
    model.fit(x_dummy, y_train)
    return model, x_dummy


def pool_size_analysis(
    model_rows: list[dict[str, Any]],
    selection_metric: str,
    replication: int,
) -> list[dict[str, Any]]:
    valid_rows = [
        row
        for row in model_rows
        if row.get("error") is None
        and math.isfinite(float(row[f"selection_{selection_metric}"]))
        and math.isfinite(float(row[f"test_{selection_metric}"]))
    ]
    output: list[dict[str, Any]] = []
    m = len(valid_rows)
    for pool_size in range(1, m + 1):
        selection_scores: list[float] = []
        test_scores: list[float] = []
        optimisms: list[float] = []
        for subset in itertools.combinations(valid_rows, pool_size):
            winner = max(subset, key=lambda row: row[f"selection_{selection_metric}"])
            selection_value = float(winner[f"selection_{selection_metric}"])
            test_value = float(winner[f"test_{selection_metric}"])
            selection_scores.append(selection_value)
            test_scores.append(test_value)
            optimisms.append(selection_value - test_value)

        output.append(
            {
                "replication": replication,
                "pool_size": pool_size,
                "n_subsets": len(selection_scores),
                "mean_max_selection_score": float(np.mean(selection_scores)),
                "mean_selected_test_score": float(np.mean(test_scores)),
                "mean_optimism": float(np.mean(optimisms)),
            }
        )
    return output


def run_replication(
    replication: int,
    seed: int,
    config: SimulationConfig,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = np.random.default_rng(seed)

    x_train = generate_predictors(
        config.n_train,
        config.n_features,
        config.binary_fraction,
        config.correlation_rho,
        rng,
    )
    x_selection = generate_predictors(
        config.n_selection,
        config.n_features,
        config.binary_fraction,
        config.correlation_rho,
        rng,
    )
    x_test = generate_predictors(
        config.n_test,
        config.n_features,
        config.binary_fraction,
        config.correlation_rho,
        rng,
    )

    # Under the exact null, each outcome is generated independently of every predictor.
    y_train = generate_fixed_outcome(config.n_train, config.train_prevalence, rng)
    y_selection = generate_fixed_outcome(
        config.n_selection, config.selection_prevalence, rng
    )
    y_test = generate_fixed_outcome(config.n_test, config.test_prevalence, rng)

    selected_indices, selector_info = select_predictors(x_train, y_train, config, seed)
    selected_feature_count = int(len(selected_indices))

    model_rows: list[dict[str, Any]] = []
    if selected_feature_count == 0:
        # An honest intercept-only fallback: no noise variable is silently reintroduced.
        dummy, x_train_selected = make_dummy_model(y_train)
        x_selection_selected = np.zeros((config.n_selection, 1), dtype=float)
        x_test_selected = np.zeros((config.n_test, 1), dtype=float)
        for model_name in MODEL_NAMES:
            selection_metrics = evaluate_model(dummy, x_selection_selected, y_selection)
            test_metrics = evaluate_model(dummy, x_test_selected, y_test)
            row: dict[str, Any] = {
                "replication": replication,
                "seed": seed,
                "model": model_name,
                "intercept_only": True,
                "error": None,
            }
            row.update({f"selection_{key}": value for key, value in selection_metrics.items()})
            row.update({f"test_{key}": value for key, value in test_metrics.items()})
            model_rows.append(row)
    else:
        x_train_selected = x_train[:, selected_indices]
        x_selection_selected = x_selection[:, selected_indices]
        x_test_selected = x_test[:, selected_indices]
        candidate_models = build_candidate_models(seed)

        for model_name in MODEL_NAMES:
            estimator = candidate_models[model_name]
            row = {
                "replication": replication,
                "seed": seed,
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
                selection_metrics = evaluate_model(estimator, x_selection_selected, y_selection)
                test_metrics = evaluate_model(estimator, x_test_selected, y_test)
                row.update(
                    {f"selection_{key}": value for key, value in selection_metrics.items()}
                )
                row.update({f"test_{key}": value for key, value in test_metrics.items()})
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                for metric in METRIC_COLUMNS:
                    row[f"selection_{metric}"] = float("nan")
                    row[f"test_{metric}"] = float("nan")
            model_rows.append(row)

    valid_rows = [
        row
        for row in model_rows
        if row["error"] is None
        and math.isfinite(float(row[f"selection_{config.selection_metric}"]))
    ]
    if not valid_rows:
        raise RuntimeError(f"All candidate models failed in replication {replication}.")

    best_row = max(
        valid_rows,
        key=lambda row: float(row[f"selection_{config.selection_metric}"]),
    )
    best_selection_score = float(best_row[f"selection_{config.selection_metric}"])
    selected_test_score = float(best_row[f"test_{config.selection_metric}"])

    replication_row: dict[str, Any] = {
        "replication": replication,
        "seed": seed,
        "selected_feature_count": selected_feature_count,
        "selected_features": "|".join(str(i + 1) for i in selected_indices),
        "lasso_selected_c": selector_info["lasso_selected_c"],
        "selector_error": selector_info["selector_error"],
        "best_model": best_row["model"],
        "selection_metric": config.selection_metric,
        "best_selection_score": best_selection_score,
        "selected_model_test_score": selected_test_score,
        "selection_induced_optimism": best_selection_score - selected_test_score,
        "selection_majority_accuracy": max(
            config.selection_prevalence, 1.0 - config.selection_prevalence
        ),
        "test_majority_accuracy": max(config.test_prevalence, 1.0 - config.test_prevalence),
        "n_model_failures": len(model_rows) - len(valid_rows),
    }
    for metric in METRIC_COLUMNS:
        replication_row[f"best_model_selection_{metric}"] = best_row[f"selection_{metric}"]
        replication_row[f"best_model_test_{metric}"] = best_row[f"test_{metric}"]

    pool_rows = pool_size_analysis(model_rows, config.selection_metric, replication)
    return replication_row, model_rows, pool_rows


def series_summary(series: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {"n": 0, "mean": None, "sd": None, "q025": None, "q50": None, "q975": None}
    return {
        "n": int(clean.size),
        "mean": float(clean.mean()),
        "sd": float(clean.std(ddof=1)) if clean.size > 1 else 0.0,
        "q025": float(clean.quantile(0.025)),
        "q05": float(clean.quantile(0.05)),
        "q25": float(clean.quantile(0.25)),
        "q50": float(clean.quantile(0.50)),
        "q75": float(clean.quantile(0.75)),
        "q95": float(clean.quantile(0.95)),
        "q975": float(clean.quantile(0.975)),
        "min": float(clean.min()),
        "max": float(clean.max()),
    }


def build_summary(
    rep_df: pd.DataFrame,
    model_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    config: SimulationConfig,
    elapsed_seconds: float,
) -> dict[str, Any]:
    best_selection = rep_df["best_selection_score"]
    selected_test = rep_df["selected_model_test_score"]
    optimism = rep_df["selection_induced_optimism"]

    thresholds = np.round(np.arange(0.50, 0.91, 0.05), 2)
    exceedance_table: dict[str, Any] = {}
    for threshold in thresholds:
        count = int((best_selection >= threshold).sum())
        probability = count / len(rep_df)
        mcse = math.sqrt(probability * (1.0 - probability) / len(rep_df))
        exceedance_table[f"{threshold:.2f}"] = {
            "count": count,
            "probability": probability,
            "monte_carlo_se": mcse,
        }

    reference_result: dict[str, Any] | None = None
    if config.reference_performance is not None:
        reference = float(config.reference_performance)
        count = int((best_selection >= reference).sum())
        plus_one_p = (count + 1.0) / (len(rep_df) + 1.0)
        mcse = math.sqrt(plus_one_p * (1.0 - plus_one_p) / (len(rep_df) + 1.0))
        null_median = float(best_selection.median())
        null_sd = float(best_selection.std(ddof=1))
        reference_result = {
            "reference_performance": reference,
            "exceedance_count": count,
            "pipeline_null_exceedance_probability_plus_one": plus_one_p,
            "monte_carlo_se": mcse,
            "null_median": null_median,
            "standardized_distance_from_null_median": (
                (reference - null_median) / null_sd if null_sd > 0 else None
            ),
            "null_relative_gain": (
                (reference - null_median) / (1.0 - null_median)
                if null_median < 1.0
                else None
            ),
        }

    by_model: dict[str, Any] = {}
    for model_name, group in model_df.groupby("model", sort=False):
        by_model[model_name] = {
            "selection_score": series_summary(group[f"selection_{config.selection_metric}"]),
            "test_score": series_summary(group[f"test_{config.selection_metric}"]),
            "failure_count": int(group["error"].notna().sum()),
        }

    pool_summary: dict[str, Any] = {}
    for pool_size, group in pool_df.groupby("pool_size"):
        pool_summary[str(int(pool_size))] = {
            "mean_max_selection_score": series_summary(group["mean_max_selection_score"]),
            "mean_selected_test_score": series_summary(group["mean_selected_test_score"]),
            "mean_optimism": series_summary(group["mean_optimism"]),
        }

    best_model_counts = rep_df["best_model"].value_counts(dropna=False).to_dict()

    return {
        "study_description": (
            "Exact-null Monte Carlo simulation of a full prediction pipeline: "
            "optional LASSO selection, seven candidate algorithms, winner selection in a "
            "model-selection set, and re-evaluation in an untouched fresh test set."
        ),
        "elapsed_seconds": elapsed_seconds,
        "config": asdict(config),
        "event_counts": {
            "train": event_count(config.n_train, config.train_prevalence),
            "selection": event_count(config.n_selection, config.selection_prevalence),
            "test": event_count(config.n_test, config.test_prevalence),
        },
        "primary_results": {
            "best_selection_score": series_summary(best_selection),
            "selected_model_fresh_test_score": series_summary(selected_test),
            "selection_induced_optimism": series_summary(optimism),
            "selected_feature_count": series_summary(rep_df["selected_feature_count"]),
            "proportion_no_features_selected": float(
                (rep_df["selected_feature_count"] == 0).mean()
            ),
            "best_model_counts": {str(key): int(value) for key, value in best_model_counts.items()},
        },
        "null_exceedance_probabilities": exceedance_table,
        "public_reference_comparison": reference_result,
        "model_level_summary": by_model,
        "candidate_pool_size_summary": pool_summary,
    }


def write_summary_text(summary: dict[str, Any], output_path: Path) -> None:
    primary = summary["primary_results"]
    config = summary["config"]
    score_name = config["selection_metric"]
    best = primary["best_selection_score"]
    test = primary["selected_model_fresh_test_score"]
    optimism = primary["selection_induced_optimism"]
    features = primary["selected_feature_count"]

    lines = [
        "PIPELINE-AWARE NULL SIMULATION: SUMMARY",
        "=" * 46,
        "",
        f"Preset: {config['preset']}",
        f"Replications: {config['repetitions']}",
        f"Selection metric: {score_name}",
        f"Feature selection: {config['feature_selection']}",
        f"Train / selection / test N: {config['n_train']} / {config['n_selection']} / {config['n_test']}",
        (
            "Train / selection / test prevalence: "
            f"{config['train_prevalence']:.3f} / {config['selection_prevalence']:.3f} / "
            f"{config['test_prevalence']:.3f}"
        ),
        f"Candidate predictors: {config['n_features']}",
        f"Candidate algorithms: {len(MODEL_NAMES)}",
        "",
        "Primary null distributions",
        "--------------------------",
        (
            f"Best selection-set {score_name}: mean={best['mean']:.4f}, "
            f"median={best['q50']:.4f}, 95% interval=[{best['q025']:.4f}, {best['q975']:.4f}]"
        ),
        (
            f"Fresh-test {score_name} of selected winner: mean={test['mean']:.4f}, "
            f"median={test['q50']:.4f}, 95% interval=[{test['q025']:.4f}, {test['q975']:.4f}]"
        ),
        (
            f"Selection-induced optimism: mean={optimism['mean']:.4f}, "
            f"median={optimism['q50']:.4f}, 95% interval=[{optimism['q025']:.4f}, {optimism['q975']:.4f}]"
        ),
        (
            f"Selected feature count: mean={features['mean']:.2f}, "
            f"median={features['q50']:.1f}; no-feature proportion="
            f"{primary['proportion_no_features_selected']:.3f}"
        ),
        "",
        "Best-model counts",
        "-----------------",
    ]
    for model_name, count in primary["best_model_counts"].items():
        lines.append(f"{model_name}: {count}")

    lines.extend(["", "Null exceedance probabilities", "-----------------------------"])
    for threshold, values in summary["null_exceedance_probabilities"].items():
        lines.append(
            f"P(best selection score >= {threshold}) = {values['probability']:.5f} "
            f"(MCSE {values['monte_carlo_se']:.5f}; count {values['count']})"
        )

    reference = summary["public_reference_comparison"]
    if reference is not None:
        lines.extend(
            [
                "",
                "Public reference comparison",
                "---------------------------",
                f"Reference performance: {reference['reference_performance']:.4f}",
                (
                    "Pipeline-null exceedance probability (plus-one estimate): "
                    f"{reference['pipeline_null_exceedance_probability_plus_one']:.6f}"
                ),
                f"Monte Carlo SE: {reference['monte_carlo_se']:.6f}",
                f"Null median: {reference['null_median']:.4f}",
            ]
        )

    lines.extend(
        [
            "",
            f"Elapsed time: {summary['elapsed_seconds']:.1f} seconds",
            "",
            "Interpretation note:",
            "These are null-distribution results, not evidence that any specific published or",
            "unpublished study is invalid. A public benchmark can be compared only after its",
            "development and model-selection pipeline has been represented appropriately.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_feature_frequency(rep_df: pd.DataFrame, n_features: int, path: Path) -> None:
    counts = np.zeros(n_features, dtype=int)
    for value in rep_df["selected_features"].fillna(""):
        if not value:
            continue
        for item in str(value).split("|"):
            if item:
                index = int(item) - 1
                if 0 <= index < n_features:
                    counts[index] += 1
    frequency = pd.DataFrame(
        {
            "feature": [f"X{i + 1}" for i in range(n_features)],
            "selection_count": counts,
            "selection_frequency": counts / len(rep_df),
        }
    )
    frequency.to_csv(path, index=False)


def create_plots(
    rep_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    config: SimulationConfig,
    output_dir: Path,
) -> None:
    score_name = config.selection_metric
    best_selection = rep_df["best_selection_score"]
    selected_test = rep_df["selected_model_test_score"]
    optimism = rep_df["selection_induced_optimism"]

    plt.figure(figsize=(8, 5))
    plt.hist(best_selection.dropna(), bins=30)
    if score_name in {"roc_auc", "balanced_accuracy"}:
        plt.axvline(0.5, linestyle="--", linewidth=1.5, label="Nominal chance reference")
    if config.reference_performance is not None:
        plt.axvline(
            config.reference_performance,
            linestyle=":",
            linewidth=2,
            label="Public reference performance",
        )
    plt.xlabel(f"Maximum selection-set {score_name}")
    plt.ylabel("Replications")
    plt.title("Pipeline-null distribution of the selected maximum performance")
    if (score_name in {"roc_auc", "balanced_accuracy"}) or config.reference_performance is not None:
        plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "01_max_selection_score_null_distribution.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 6))
    plt.scatter(best_selection, selected_test, alpha=0.55, s=20)
    lower = float(min(best_selection.min(), selected_test.min()))
    upper = float(max(best_selection.max(), selected_test.max()))
    plt.plot([lower, upper], [lower, upper], linestyle="--", linewidth=1.2)
    if score_name in {"roc_auc", "balanced_accuracy"}:
        plt.axhline(0.5, linestyle=":", linewidth=1.2)
    plt.xlabel(f"Best selection-set {score_name}")
    plt.ylabel(f"Fresh-test {score_name} of selected model")
    plt.title("Selection-set performance versus untouched-test performance")
    plt.tight_layout()
    plt.savefig(output_dir / "02_selection_vs_fresh_test_score.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(optimism.dropna(), bins=30)
    plt.axvline(0.0, linestyle="--", linewidth=1.5)
    plt.xlabel(f"Selection-set {score_name} minus fresh-test {score_name}")
    plt.ylabel("Replications")
    plt.title("Distribution of selection-induced optimism")
    plt.tight_layout()
    plt.savefig(output_dir / "03_selection_induced_optimism.png", dpi=180)
    plt.close()

    pool_aggregate = (
        pool_df.groupby("pool_size", as_index=False)
        .agg(
            mean_max_selection_score=("mean_max_selection_score", "mean"),
            mean_selected_test_score=("mean_selected_test_score", "mean"),
            mean_optimism=("mean_optimism", "mean"),
        )
        .sort_values("pool_size")
    )

    plt.figure(figsize=(8, 5))
    plt.plot(
        pool_aggregate["pool_size"],
        pool_aggregate["mean_max_selection_score"],
        marker="o",
        label="Maximum selection-set score",
    )
    plt.plot(
        pool_aggregate["pool_size"],
        pool_aggregate["mean_selected_test_score"],
        marker="o",
        label="Fresh-test score of selected model",
    )
    plt.xlabel("Number of candidate algorithms")
    plt.ylabel(score_name)
    plt.title("Effect of algorithm-pool size")
    plt.xticks(pool_aggregate["pool_size"])
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "04_candidate_pool_size_effect.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(
        pool_aggregate["pool_size"],
        pool_aggregate["mean_optimism"],
        marker="o",
    )
    plt.axhline(0.0, linestyle="--", linewidth=1.2)
    plt.xlabel("Number of candidate algorithms")
    plt.ylabel(f"Mean selection-induced optimism in {score_name}")
    plt.title("Algorithm shopping and performance inflation")
    plt.xticks(pool_aggregate["pool_size"])
    plt.tight_layout()
    plt.savefig(output_dir / "05_pool_size_vs_optimism.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    bins = np.arange(rep_df["selected_feature_count"].max() + 2) - 0.5
    plt.hist(rep_df["selected_feature_count"], bins=bins)
    plt.xlabel("Number of predictors retained by LASSO")
    plt.ylabel("Replications")
    plt.title("Null distribution of the selected predictor count")
    plt.tight_layout()
    plt.savefig(output_dir / "06_selected_feature_count.png", dpi=180)
    plt.close()


def environment_info() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
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
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in directory.rglob("*"):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(directory.parent))
    return zip_path


def main() -> None:
    config = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(config.output_root).expanduser().resolve()
    output_dir = output_root / f"pipeline_null_{config.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=False)

    (output_dir / "config.json").write_text(
        json.dumps(asdict(config), indent=2, cls=NumpyJSONEncoder),
        encoding="utf-8",
    )
    (output_dir / "environment.json").write_text(
        json.dumps(environment_info(), indent=2, cls=NumpyJSONEncoder),
        encoding="utf-8",
    )

    seed_sequence = np.random.SeedSequence(config.master_seed)
    child_sequences = seed_sequence.spawn(config.repetitions)
    seeds = [int(sequence.generate_state(1, dtype=np.uint32)[0]) for sequence in child_sequences]

    print("Starting pipeline-aware null simulation")
    print(f"  preset={config.preset}")
    print(f"  repetitions={config.repetitions}")
    print(f"  selection_metric={config.selection_metric}")
    print(f"  feature_selection={config.feature_selection}")
    print(f"  n_jobs={config.n_jobs}")
    print(f"  output={output_dir}")
    print()

    start = time.perf_counter()
    results = Parallel(n_jobs=config.n_jobs, backend="loky", verbose=5)(
        delayed(run_replication)(replication=i + 1, seed=seeds[i], config=config)
        for i in range(config.repetitions)
    )
    elapsed = time.perf_counter() - start

    replication_rows = [item[0] for item in results]
    model_rows = [row for item in results for row in item[1]]
    pool_rows = [row for item in results for row in item[2]]

    rep_df = pd.DataFrame(replication_rows).sort_values("replication")
    model_df = pd.DataFrame(model_rows).sort_values(["replication", "model"])
    pool_df = pd.DataFrame(pool_rows).sort_values(["replication", "pool_size"])

    # The output folder may become unavailable during a long run on synced or
    # externally managed folders. Recreate it immediately before final writes.
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "config.json").write_text(
        json.dumps(asdict(config), indent=2, cls=NumpyJSONEncoder),
        encoding="utf-8",
    )
    (output_dir / "environment.json").write_text(
        json.dumps(environment_info(), indent=2, cls=NumpyJSONEncoder),
        encoding="utf-8",
    )

    rep_df.to_csv(output_dir / "replication_results.csv", index=False)
    model_df.to_csv(output_dir / "model_level_results.csv", index=False)
    pool_df.to_csv(output_dir / "pool_size_results.csv", index=False)
    save_feature_frequency(
        rep_df,
        config.n_features,
        output_dir / "feature_selection_frequency.csv",
    )

    summary = build_summary(rep_df, model_df, pool_df, config, elapsed)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, cls=NumpyJSONEncoder),
        encoding="utf-8",
    )
    write_summary_text(summary, output_dir / "summary.txt")
    create_plots(rep_df, pool_df, config, output_dir)

    zip_path = zip_directory(output_dir)
    primary = summary["primary_results"]
    best = primary["best_selection_score"]
    test = primary["selected_model_fresh_test_score"]
    optimism = primary["selection_induced_optimism"]

    print()
    print("Completed successfully.")
    print(
        f"Best selection-set {config.selection_metric}: "
        f"median={best['q50']:.4f}, 95% interval=[{best['q025']:.4f}, {best['q975']:.4f}]"
    )
    print(
        f"Fresh-test {config.selection_metric} of selected model: "
        f"median={test['q50']:.4f}, 95% interval=[{test['q025']:.4f}, {test['q975']:.4f}]"
    )
    print(
        f"Selection-induced optimism: median={optimism['q50']:.4f}, "
        f"95% interval=[{optimism['q025']:.4f}, {optimism['q975']:.4f}]"
    )
    print(f"Results directory: {output_dir}")
    print(f"Shareable ZIP:      {zip_path}")


if __name__ == "__main__":
    main()
