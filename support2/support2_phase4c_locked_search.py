#!/usr/bin/env python3
"""
SUPPORT2 Phase 4C: locked model search and independent pipeline-null inference.

This phase uses only the frozen TRAIN and MODEL-SELECTION splits. The TEST
split is not evaluated. It:

1. validates the Phase 4B frozen design;
2. fits a common X-only preprocessing recipe on the training split;
3. fits seven prespecified candidate algorithms;
4. selects the winner on the model-selection split;
5. constructs a null reference bank by independently permuting outcomes in
   the training and model-selection splits and repeating model fitting and
   winner selection;
6. compares naive, Bonferroni, and pipeline-aware max-statistic inference.

The test split remains sealed for Phase 4D.

Example
-------
python support2_phase4c_locked_search.py \
    --frozen-zip results_support2_phase4b/support2_phase4b_frozen_YYYYMMDD_HHMMSS.zip \
    --preset quick \
    --n-jobs 16 \
    --output-root results_support2_phase4c
"""

from __future__ import annotations

import os

# Avoid nested parallelism inside joblib workers.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import sys
import tempfile
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
from scipy.stats import mannwhitneyu
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier


MODEL_NAMES = (
    "logistic_regression",
    "linear_svm",
    "rbf_svm",
    "gaussian_nb",
    "decision_tree",
    "random_forest",
    "hist_gradient_boosting",
)

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

PRESETS = {
    "smoke": 20,
    "quick": 500,
    "full": 5_000,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Locked SUPPORT2 model search and pipeline-null inference."
    )
    parser.add_argument("--frozen-zip", default=None)
    parser.add_argument("--preset", choices=PRESETS, default="quick")
    parser.add_argument("--null-repetitions", type=int, default=None)
    parser.add_argument("--pauc-max-fpr", type=float, default=0.10)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--master-seed", type=int, default=20260720)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument(
        "--parallel-backend",
        choices=("loky", "threading"),
        default="loky",
        help=(
            "Joblib backend for null replications. Use 'threading' for "
            "low-memory smoke tests; the frozen full analysis used 'loky'."
        ),
    )
    parser.add_argument(
        "--output-root",
        default="results_support2_phase4c",
    )
    args = parser.parse_args()

    args.null_repetitions = (
        args.null_repetitions
        if args.null_repetitions is not None
        else PRESETS[args.preset]
    )

    if args.null_repetitions < 20:
        parser.error("--null-repetitions must be at least 20.")
    if not 0.0 < args.pauc_max_fpr <= 1.0:
        parser.error("--pauc-max-fpr must lie in (0, 1].")
    if not 0.0 < args.alpha < 1.0:
        parser.error("--alpha must lie in (0, 1).")
    if args.n_jobs == 0:
        parser.error("--n-jobs cannot be zero.")

    if args.frozen_zip is None:
        search_roots = [
            Path.cwd(),
            Path(__file__).resolve().parents[1],
        ]
        candidates = sorted(
            {
                candidate.resolve()
                for root in search_roots
                for candidate in root.rglob(
                    "support2_phase4b_frozen_*.zip"
                )
                if candidate.is_file()
            },
            key=lambda p: p.stat().st_mtime,
        )
        if not candidates:
            parser.error(
                "No Phase 4B frozen ZIP was found. Supply --frozen-zip."
            )
        args.frozen_zip = str(candidates[-1])

    args.frozen_zip = str(Path(args.frozen_zip).expanduser().resolve())
    return args


def read_frozen_zip(path: Path) -> tuple[pd.DataFrame, dict[str, Any], str]:
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        plan_members = [x for x in names if x.endswith("/analysis_plan.json")]
        data_members = [
            x for x in names if x.endswith("/analysis_dataset_primary.csv")
        ]
        if len(plan_members) != 1 or len(data_members) != 1:
            raise RuntimeError(
                "Frozen ZIP must contain exactly one analysis_plan.json and "
                "one analysis_dataset_primary.csv."
            )
        plan = json.loads(archive.read(plan_members[0]).decode("utf-8"))
        with archive.open(data_members[0]) as handle:
            data = pd.read_csv(handle)
        root = plan_members[0].split("/")[0]
    return data, plan, root


def validate_frozen_design(data: pd.DataFrame, plan: dict[str, Any]) -> None:
    if plan.get("phase") != "4B" or not bool(plan.get("frozen")):
        raise RuntimeError("Input does not contain a frozen Phase 4B plan.")
    if plan.get("outcome") != "hospdead":
        raise RuntimeError("Unexpected outcome in frozen plan.")
    expected_models = tuple(plan.get("candidate_library", []))
    if expected_models != MODEL_NAMES:
        raise RuntimeError(
            "Candidate model library does not match the frozen plan.\n"
            f"Frozen: {expected_models}\nCode:   {MODEL_NAMES}"
        )

    required = {
        "id",
        "split",
        "hospdead",
        *plan["primary_predictors"],
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise RuntimeError(f"Frozen data are missing columns: {missing}")

    expected_splits = {"train", "selection", "test"}
    observed_splits = set(data["split"].dropna().astype(str))
    if observed_splits != expected_splits:
        raise RuntimeError(
            f"Unexpected split labels: {sorted(observed_splits)}"
        )
    if data["id"].duplicated().any():
        raise RuntimeError("Duplicate IDs detected.")
    if data["hospdead"].isna().any():
        raise RuntimeError("Outcome missingness detected.")
    if not set(data["hospdead"].unique()).issubset({0, 1}):
        raise RuntimeError("Outcome is not binary.")


def make_one_hot_encoder() -> OneHotEncoder:
    # sparse_output is available in current sklearn; fallback aids older installs.
    try:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,
        )
    except TypeError:
        return OneHotEncoder(
            handle_unknown="ignore",
            sparse=False,
        )


def build_preprocessor(plan: dict[str, Any]) -> ColumnTransformer:
    numeric = list(plan["primary_numeric"]) + list(plan["primary_binary"])
    categorical = list(plan["primary_categorical"])

    numeric_pipe = Pipeline(
        [
            (
                "impute",
                SimpleImputer(
                    strategy="median",
                    add_indicator=True,
                ),
            ),
            ("scale", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            (
                "impute",
                SimpleImputer(strategy="most_frequent"),
            ),
            ("onehot", make_one_hot_encoder()),
        ]
    )

    return ColumnTransformer(
        [
            ("numeric", numeric_pipe, numeric),
            ("categorical", categorical_pipe, categorical),
        ],
        remainder="drop",
        sparse_threshold=0.0,
        verbose_feature_names_out=True,
    )


def build_models(seed: int) -> dict[str, Any]:
    return {
        "logistic_regression": LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="liblinear",
            max_iter=2_000,
            random_state=seed + 11,
        ),
        "linear_svm": LinearSVC(
            C=1.0,
            dual=False,
            max_iter=5_000,
            random_state=seed + 23,
        ),
        "rbf_svm": SVC(
            C=1.0,
            kernel="rbf",
            gamma="scale",
            probability=False,
            cache_size=1_000,
            random_state=seed + 37,
        ),
        "gaussian_nb": GaussianNB(var_smoothing=1e-9),
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


def prediction_scores(estimator: Any, x: np.ndarray) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        p = np.asarray(estimator.predict_proba(x))
        if p.ndim == 2 and p.shape[1] >= 2:
            return p[:, 1]
        return p.ravel()
    if hasattr(estimator, "decision_function"):
        return np.asarray(estimator.decision_function(x)).ravel()
    return np.asarray(estimator.predict(x), dtype=float).ravel()


def rank_metrics(
    y: np.ndarray,
    scores: np.ndarray,
    max_fpr: float,
) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y, scores)),
        "average_precision": float(
            average_precision_score(y, scores)
        ),
        "pauc_fpr_0_10": float(
            roc_auc_score(y, scores, max_fpr=max_fpr)
        ),
    }


def one_sided_mann_whitney_p(
    y: np.ndarray,
    scores: np.ndarray,
) -> float:
    event_scores = np.asarray(scores)[np.asarray(y) == 1]
    non_event_scores = np.asarray(scores)[np.asarray(y) == 0]
    if len(event_scores) == 0 or len(non_event_scores) == 0:
        return float("nan")
    if np.all(np.asarray(scores) == np.asarray(scores)[0]):
        return 1.0
    return float(
        mannwhitneyu(
            event_scores,
            non_event_scores,
            alternative="greater",
            method="asymptotic",
        ).pvalue
    )


def fit_all_models(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_selection: np.ndarray,
    y_selection: np.ndarray,
    seed: int,
    max_fpr: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    models = build_models(seed)

    for model_name in MODEL_NAMES:
        estimator = models[model_name]
        row: dict[str, Any] = {
            "model": model_name,
            "error": None,
        }
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=ConvergenceWarning)
                warnings.simplefilter("ignore", category=FutureWarning)
                warnings.simplefilter("ignore", category=RuntimeWarning)
                estimator.fit(x_train, y_train)
            scores = prediction_scores(estimator, x_selection)
            metrics = rank_metrics(y_selection, scores, max_fpr)
            row.update(metrics)
            row["mannwhitney_p"] = one_sided_mann_whitney_p(
                y_selection, scores
            )
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    return rows


def run_null_replication(
    replication: int,
    seed: int,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_selection: np.ndarray,
    y_selection: np.ndarray,
    max_fpr: float,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    permuted_train = rng.permutation(y_train)
    permuted_selection = rng.permutation(y_selection)

    rows = fit_all_models(
        x_train,
        permuted_train,
        x_selection,
        permuted_selection,
        seed,
        max_fpr,
    )
    for row in rows:
        row["replication"] = int(replication)
        row["seed"] = int(seed)
    return rows


def empirical_upper_p(
    observed: float,
    reference: np.ndarray,
) -> float:
    values = np.asarray(reference, dtype=float)
    values = values[np.isfinite(values)]
    if not math.isfinite(float(observed)) or len(values) == 0:
        return float("nan")
    return float(
        (1 + np.count_nonzero(values >= observed))
        / (len(values) + 1)
    )


def winner_row(
    frame: pd.DataFrame,
    metric: str,
) -> pd.Series:
    valid = frame[
        frame["error"].isna()
        & np.isfinite(frame[metric].astype(float))
    ].copy()
    if valid.empty:
        raise RuntimeError(f"No valid model for metric={metric}.")
    max_value = float(valid[metric].max())
    tied = valid[
        np.isclose(
            valid[metric],
            max_value,
            rtol=1e-12,
            atol=1e-12,
        )
    ].copy()
    order = {name: i for i, name in enumerate(MODEL_NAMES)}
    tied["_order"] = tied["model"].map(order)
    return tied.sort_values("_order").iloc[0]


def infer_methods(
    observed: pd.DataFrame,
    null_df: pd.DataFrame,
    alpha: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for metric in METRICS:
        winner = winner_row(observed, metric)
        observed_max = float(winner[metric])
        winner_name = str(winner["model"])

        marginal_p_values = []
        for model_name in MODEL_NAMES:
            model_observed = observed.loc[
                observed["model"] == model_name, metric
            ]
            if model_observed.empty:
                continue
            reference = null_df.loc[
                null_df["model"] == model_name, metric
            ].to_numpy(float)
            marginal_p_values.append(
                empirical_upper_p(
                    float(model_observed.iloc[0]),
                    reference,
                )
            )

        winner_reference = null_df.loc[
            null_df["model"] == winner_name, metric
        ].to_numpy(float)
        naive_empirical = empirical_upper_p(
            observed_max,
            winner_reference,
        )
        bonferroni_empirical = min(
            1.0,
            len(MODEL_NAMES) * float(np.nanmin(marginal_p_values)),
        )

        max_reference = (
            null_df.pivot_table(
                index="replication",
                columns="model",
                values=metric,
                aggfunc="first",
            )[list(MODEL_NAMES)]
            .max(axis=1)
            .to_numpy(float)
        )
        pipeline_empirical = empirical_upper_p(
            observed_max,
            max_reference,
        )

        base_row = {
            "metric": metric,
            "metric_label": METRIC_LABELS[metric],
            "best_model": winner_name,
            "best_selection_metric": observed_max,
        }

        for method, value in (
            ("naive_empirical", naive_empirical),
            ("bonferroni_empirical", bonferroni_empirical),
            ("pipeline_empirical", pipeline_empirical),
        ):
            rows.append(
                {
                    **base_row,
                    "method": method,
                    "method_label": METHOD_LABELS[method],
                    "p_value": float(value),
                    "reject": bool(value < alpha),
                }
            )

        if metric == "roc_auc":
            naive_mw = float(winner["mannwhitney_p"])
            valid_mw = observed["mannwhitney_p"].to_numpy(float)
            valid_mw = valid_mw[np.isfinite(valid_mw)]
            bonferroni_mw = min(
                1.0,
                len(MODEL_NAMES) * float(np.min(valid_mw)),
            )
            for method, value in (
                ("naive_mannwhitney", naive_mw),
                ("bonferroni_mannwhitney", bonferroni_mw),
            ):
                rows.append(
                    {
                        **base_row,
                        "method": method,
                        "method_label": METHOD_LABELS[method],
                        "p_value": float(value),
                        "reject": bool(value < alpha),
                    }
                )

    return pd.DataFrame(rows)


def plot_null_distribution(
    observed: pd.DataFrame,
    null_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    for metric in METRICS:
        pivot = null_df.pivot_table(
            index="replication",
            columns="model",
            values=metric,
            aggfunc="first",
        )
        null_max = pivot[list(MODEL_NAMES)].max(axis=1)
        observed_max = float(observed[metric].max())

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(null_max, bins=35, edgecolor="black", linewidth=0.4)
        ax.axvline(
            observed_max,
            linestyle="--",
            linewidth=2,
            label=f"Observed maximum = {observed_max:.3f}",
        )
        ax.set_xlabel(f"Maximum selection-set {METRIC_LABELS[metric]}")
        ax.set_ylabel("Null replications")
        ax.set_title(
            f"Pipeline-specific null distribution: {METRIC_LABELS[metric]}"
        )
        ax.legend()
        fig.tight_layout()
        fig.savefig(
            output_dir / f"01_null_max_{metric}.png",
            dpi=180,
        )
        plt.close(fig)


def plot_observed_models(
    observed: pd.DataFrame,
    output_dir: Path,
) -> None:
    for metric in METRICS:
        data = observed.sort_values(metric, ascending=False)
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.bar(data["model"], data[metric])
        ax.set_ylabel(f"Selection-set {METRIC_LABELS[metric]}")
        ax.set_title(
            f"Observed candidate-model performance: {METRIC_LABELS[metric]}"
        )
        ax.tick_params(axis="x", rotation=50)
        fig.tight_layout()
        fig.savefig(
            output_dir / f"02_observed_models_{metric}.png",
            dpi=180,
        )
        plt.close(fig)


def plot_pvalues(
    inference: pd.DataFrame,
    output_dir: Path,
    alpha: float,
) -> None:
    for metric in METRICS:
        data = inference[inference["metric"] == metric].copy()
        fig, ax = plt.subplots(figsize=(8, 5.5))
        display = np.maximum(
            data["p_value"].to_numpy(float),
            1e-8,
        )
        ax.bar(data["method_label"], -np.log10(display))
        ax.axhline(
            -math.log10(alpha),
            linestyle="--",
            linewidth=1,
            label=f"alpha = {alpha}",
        )
        ax.set_ylabel("-log10(p-value)")
        ax.set_title(
            f"Inference after model search: {METRIC_LABELS[metric]}"
        )
        ax.tick_params(axis="x", rotation=40)
        ax.legend()
        fig.tight_layout()
        fig.savefig(
            output_dir / f"03_pvalues_{metric}.png",
            dpi=180,
        )
        plt.close(fig)


def zip_directory(directory: Path) -> Path:
    target = directory.with_suffix(".zip")
    with zipfile.ZipFile(
        target,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    path.relative_to(directory.parent),
                )
    return target


def write_summary(
    path: Path,
    args: argparse.Namespace,
    plan: dict[str, Any],
    train: pd.DataFrame,
    selection: pd.DataFrame,
    transformed_features: int,
    observed: pd.DataFrame,
    inference: pd.DataFrame,
    elapsed: float,
) -> None:
    lines = [
        "SUPPORT2 PHASE 4C: LOCKED MODEL SEARCH",
        "=" * 48,
        f"Preset: {args.preset}",
        f"Null repetitions: {args.null_repetitions}",
        f"Training rows: {len(train):,}",
        f"Selection rows: {len(selection):,}",
        f"Training events: {int(train['hospdead'].sum()):,}",
        f"Selection events: {int(selection['hospdead'].sum()):,}",
        f"Frozen predictors: {len(plan['primary_predictors'])}",
        f"Transformed features: {transformed_features}",
        f"Candidate models: {len(MODEL_NAMES)}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "IMPORTANT",
        "---------",
        "The untouched test split was not evaluated in this phase.",
        "Preprocessing uses only X and was fitted once on the training split.",
        "Because it is outcome-independent, refitting it after each outcome",
        "permutation would yield the same transformed matrices.",
        "",
        "OBSERVED SELECTION-SET PERFORMANCE",
        "----------------------------------",
        observed[
            ["model", *METRICS, "mannwhitney_p", "error"]
        ].to_string(index=False, float_format=lambda x: f"{x:.6g}"),
        "",
        "INFERENCE AFTER MODEL SEARCH",
        "----------------------------",
        inference[
            [
                "metric_label",
                "best_model",
                "best_selection_metric",
                "method_label",
                "p_value",
                "reject",
            ]
        ].to_string(index=False, float_format=lambda x: f"{x:.6g}"),
        "",
        f"Smallest attainable empirical p-value: "
        f"{1.0 / (args.null_repetitions + 1):.6g}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    started = time.time()

    frozen_zip = Path(args.frozen_zip)
    if not frozen_zip.exists():
        raise FileNotFoundError(f"Frozen ZIP not found: {frozen_zip}")

    data, plan, _ = read_frozen_zip(frozen_zip)
    validate_frozen_design(data, plan)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"support2_phase4c_{args.preset}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Seal the test set: do not calculate any model output or performance on it.
    train = data[data["split"] == "train"].copy()
    selection = data[data["split"] == "selection"].copy()
    test_count = int((data["split"] == "test").sum())

    predictors = list(plan["primary_predictors"])
    outcome = str(plan["outcome"])

    x_train_raw = train[predictors]
    y_train = train[outcome].to_numpy(int)
    x_selection_raw = selection[predictors]
    y_selection = selection[outcome].to_numpy(int)

    preprocessor = build_preprocessor(plan)
    x_train = np.asarray(
        preprocessor.fit_transform(x_train_raw),
        dtype=np.float64,
    )
    x_selection = np.asarray(
        preprocessor.transform(x_selection_raw),
        dtype=np.float64,
    )

    if not np.isfinite(x_train).all() or not np.isfinite(x_selection).all():
        raise RuntimeError("Non-finite transformed predictor values detected.")

    try:
        feature_names = preprocessor.get_feature_names_out().tolist()
    except Exception:
        feature_names = [f"x{i}" for i in range(x_train.shape[1])]

    pd.DataFrame(
        {"transformed_feature": feature_names}
    ).to_csv(
        output_dir / "transformed_feature_names.csv",
        index=False,
    )

    observed_rows = fit_all_models(
        x_train,
        y_train,
        x_selection,
        y_selection,
        args.master_seed,
        args.pauc_max_fpr,
    )
    observed_df = pd.DataFrame(observed_rows)
    observed_df.to_csv(
        output_dir / "observed_selection_model_metrics.csv",
        index=False,
    )

    if observed_df["error"].notna().any():
        failures = observed_df.loc[
            observed_df["error"].notna(),
            ["model", "error"],
        ]
        raise RuntimeError(
            "An observed candidate model failed:\n"
            + failures.to_string(index=False)
        )

    seeds = [
        int(
            np.random.SeedSequence(
                [args.master_seed, 44001, replication]
            ).generate_state(1, dtype=np.uint32)[0]
        )
        for replication in range(args.null_repetitions)
    ]

    print("SUPPORT2 Phase 4C locked search")
    print(f"Output: {output_dir}")
    print(f"Training: {len(train):,} rows, {int(y_train.sum()):,} events")
    print(
        f"Selection: {len(selection):,} rows, "
        f"{int(y_selection.sum()):,} events"
    )
    print(f"Sealed test rows: {test_count:,}")
    print(f"Transformed features: {x_train.shape[1]}")
    print(f"Null replications: {args.null_repetitions:,}")

    null_results = Parallel(
        n_jobs=args.n_jobs,
        verbose=5,
        max_nbytes=None if args.parallel_backend == "threading" else "10M",
        backend=args.parallel_backend,
    )(
        delayed(run_null_replication)(
            replication,
            seed,
            x_train,
            y_train,
            x_selection,
            y_selection,
            args.pauc_max_fpr,
        )
        for replication, seed in enumerate(seeds)
    )
    null_rows = [
        row
        for replication_rows in null_results
        for row in replication_rows
    ]
    null_df = pd.DataFrame(null_rows)
    null_df.to_csv(
        output_dir / "null_reference_model_metrics.csv",
        index=False,
    )

    if null_df["error"].notna().any():
        failures = null_df.loc[
            null_df["error"].notna(),
            ["replication", "model", "error"],
        ]
        failures.to_csv(
            output_dir / "null_model_failures.csv",
            index=False,
        )

    inference = infer_methods(
        observed_df,
        null_df,
        args.alpha,
    )
    inference.to_csv(
        output_dir / "model_search_inference.csv",
        index=False,
    )

    winners = []
    for metric in METRICS:
        winner = winner_row(observed_df, metric)
        winners.append(
            {
                "metric": metric,
                "metric_label": METRIC_LABELS[metric],
                "best_model": str(winner["model"]),
                "selection_metric": float(winner[metric]),
            }
        )
    pd.DataFrame(winners).to_csv(
        output_dir / "selected_winners.csv",
        index=False,
    )

    plot_null_distribution(observed_df, null_df, output_dir)
    plot_observed_models(observed_df, output_dir)
    plot_pvalues(inference, output_dir, args.alpha)

    elapsed = time.time() - started
    write_summary(
        output_dir / "summary.txt",
        args,
        plan,
        train,
        selection,
        x_train.shape[1],
        observed_df,
        inference,
        elapsed,
    )

    config = {
        "phase": "4C",
        "test_set_evaluated": False,
        "sealed_test_rows": test_count,
        "frozen_zip": str(frozen_zip),
        "frozen_zip_sha256": sha256_file(frozen_zip),
        "preset": args.preset,
        "null_repetitions": args.null_repetitions,
        "master_seed": args.master_seed,
        "alpha": args.alpha,
        "pauc_max_fpr": args.pauc_max_fpr,
        "candidate_models": list(MODEL_NAMES),
        "primary_predictors": predictors,
        "preprocessing": {
            "numeric_and_binary": (
                "training-median imputation with missingness indicators, "
                "then standardization"
            ),
            "categorical": (
                "training-mode imputation and one-hot encoding with "
                "unknown categories ignored"
            ),
            "optimization_note": (
                "Preprocessing is outcome-independent and therefore fitted "
                "once; outcome permutations repeat all outcome-dependent "
                "model fitting and winner selection."
            ),
        },
        "transformed_feature_count": int(x_train.shape[1]),
    }
    (output_dir / "config.json").write_text(
        json.dumps(config, indent=2),
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
        json.dumps(environment, indent=2),
        encoding="utf-8",
    )

    (output_dir / "run_complete.json").write_text(
        json.dumps(
            {
                "completed": True,
                "elapsed_seconds": elapsed,
                "observed_model_rows": int(len(observed_df)),
                "null_model_rows": int(len(null_df)),
                "inference_rows": int(len(inference)),
                "test_set_evaluated": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    zip_path = zip_directory(output_dir)
    print(f"Completed in {elapsed:.1f} seconds")
    print("The test split remains sealed.")
    print(f"Upload this ZIP next: {zip_path}")


if __name__ == "__main__":
    main()
