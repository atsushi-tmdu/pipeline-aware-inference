#!/usr/bin/env python3
"""
SUPPORT2 Phase 4D: one-time opening of the untouched test set.

Safeguards
----------
1. Verifies the frozen Phase 4B ZIP hash recorded in Phase 4C.
2. Confirms that Phase 4C did not evaluate the test set.
3. Reproduces the locked winner's selection-set performance.
4. Stops before test evaluation when --dry-run is specified.
5. Requires --open-test CONFIRM for the actual test opening.
6. Evaluates only the prespecified AUROC winner on the test set.
7. Does not compare or reselect candidate algorithms using test performance.

Test evaluations
----------------
A. Locked training-only model
   Exact Phase 4C model fitted on training data and applied to test.

B. Final refit model
   Same locked algorithm and hyperparameters, fitted on training + selection,
   then applied once to test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
import warnings
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

import support2_phase4c_locked_search as phase4c


PRIMARY_METRIC = "roc_auc"

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open the frozen SUPPORT2 test set exactly once."
    )

    parser.add_argument("--frozen-zip", required=True)
    parser.add_argument("--phase4c-zip", required=True)

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify every lock but do not evaluate the test set.",
    )

    parser.add_argument(
        "--open-test",
        default=None,
        help="The actual opening requires: --open-test CONFIRM",
    )

    parser.add_argument(
        "--bootstrap-repetitions",
        type=int,
        default=5000,
    )

    parser.add_argument(
        "--bootstrap-seed",
        type=int,
        default=20260721,
    )

    parser.add_argument(
        "--reproduction-tolerance",
        type=float,
        default=1e-8,
    )

    parser.add_argument(
        "--output-root",
        default="results_support2_phase4d",
    )

    args = parser.parse_args()

    args.frozen_zip = str(
        Path(args.frozen_zip).expanduser().resolve()
    )
    args.phase4c_zip = str(
        Path(args.phase4c_zip).expanduser().resolve()
    )

    if args.bootstrap_repetitions < 200:
        parser.error("--bootstrap-repetitions must be at least 200.")

    if args.reproduction_tolerance <= 0:
        parser.error("--reproduction-tolerance must be positive.")

    if not args.dry_run and args.open_test != "CONFIRM":
        parser.error(
            "Actual test evaluation requires --open-test CONFIRM. "
            "Run --dry-run first."
        )

    return args


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def unique_zip_member(
    archive: zipfile.ZipFile,
    suffix: str,
) -> str:
    members = [
        name
        for name in archive.namelist()
        if name.endswith("/" + suffix)
    ]

    if len(members) != 1:
        raise RuntimeError(
            f"Expected exactly one {suffix}; found {len(members)}."
        )

    return members[0]


def read_phase4c_zip(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path, "r") as archive:
        config = json.loads(
            archive.read(
                unique_zip_member(archive, "config.json")
            ).decode("utf-8")
        )

        run_complete = json.loads(
            archive.read(
                unique_zip_member(
                    archive,
                    "run_complete.json",
                )
            ).decode("utf-8")
        )

        observed = pd.read_csv(
            archive.open(
                unique_zip_member(
                    archive,
                    "observed_selection_model_metrics.csv",
                )
            )
        )

        winners = pd.read_csv(
            archive.open(
                unique_zip_member(
                    archive,
                    "selected_winners.csv",
                )
            )
        )

        inference = pd.read_csv(
            archive.open(
                unique_zip_member(
                    archive,
                    "model_search_inference.csv",
                )
            )
        )

    return {
        "config": config,
        "run_complete": run_complete,
        "observed": observed,
        "winners": winners,
        "inference": inference,
    }


def validate_phase4c(
    frozen_zip: Path,
    phase4c_payload: dict[str, Any],
) -> str:
    config = phase4c_payload["config"]
    run_complete = phase4c_payload["run_complete"]
    winners = phase4c_payload["winners"]

    if config.get("phase") != "4C":
        raise RuntimeError(
            "The supplied model-search ZIP is not Phase 4C."
        )

    if not bool(run_complete.get("completed")):
        raise RuntimeError(
            "Phase 4C is not marked as completed."
        )

    if bool(config.get("test_set_evaluated")):
        raise RuntimeError(
            "Phase 4C config says the test set was evaluated."
        )

    if bool(run_complete.get("test_set_evaluated")):
        raise RuntimeError(
            "Phase 4C run says the test set was evaluated."
        )

    expected_hash = str(
        config.get("frozen_zip_sha256", "")
    )
    observed_hash = sha256_file(frozen_zip)

    if observed_hash != expected_hash:
        raise RuntimeError(
            "Phase 4B frozen ZIP hash mismatch.\n"
            f"Expected: {expected_hash}\n"
            f"Observed: {observed_hash}"
        )

    recorded_models = tuple(
        config.get("candidate_models", [])
    )

    if recorded_models != tuple(phase4c.MODEL_NAMES):
        raise RuntimeError(
            "Candidate model library differs from Phase 4C."
        )

    primary = winners[
        winners["metric"] == PRIMARY_METRIC
    ]

    if len(primary) != 1:
        raise RuntimeError(
            "Could not identify one AUROC winner."
        )

    winner = str(primary.iloc[0]["best_model"])

    if winner not in phase4c.MODEL_NAMES:
        raise RuntimeError(
            f"Unknown locked winner: {winner}"
        )

    return winner


def fit_locked_model(
    fit_data: pd.DataFrame,
    evaluation_data: pd.DataFrame,
    predictors: list[str],
    outcome: str,
    plan: dict[str, Any],
    model_name: str,
    master_seed: int,
) -> tuple[Any, Any, np.ndarray]:
    preprocessor = phase4c.build_preprocessor(plan)

    x_fit = np.asarray(
        preprocessor.fit_transform(
            fit_data[predictors]
        ),
        dtype=np.float64,
    )

    x_evaluation = np.asarray(
        preprocessor.transform(
            evaluation_data[predictors]
        ),
        dtype=np.float64,
    )

    if not np.isfinite(x_fit).all():
        raise RuntimeError(
            "Non-finite values detected in fitting predictors."
        )

    if not np.isfinite(x_evaluation).all():
        raise RuntimeError(
            "Non-finite values detected in evaluation predictors."
        )

    model_library = phase4c.build_models(master_seed)

    if model_name not in model_library:
        raise RuntimeError(
            f"Locked model is unavailable: {model_name}"
        )

    estimator = model_library[model_name]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        estimator.fit(
            x_fit,
            fit_data[outcome].to_numpy(int),
        )

    scores = phase4c.prediction_scores(
        estimator,
        x_evaluation,
    )

    return (
        preprocessor,
        estimator,
        np.asarray(scores, dtype=float),
    )


def calculate_metrics(
    y: np.ndarray,
    scores: np.ndarray,
    max_fpr: float,
) -> dict[str, float]:
    return phase4c.rank_metrics(
        np.asarray(y, dtype=int),
        np.asarray(scores, dtype=float),
        max_fpr,
    )


def stratified_bootstrap(
    y: np.ndarray,
    scores: np.ndarray,
    repetitions: int,
    seed: int,
    max_fpr: float,
) -> pd.DataFrame:
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)

    event_indices = np.flatnonzero(y == 1)
    non_event_indices = np.flatnonzero(y == 0)

    if len(event_indices) == 0:
        raise RuntimeError("No events in evaluation set.")

    if len(non_event_indices) == 0:
        raise RuntimeError("No non-events in evaluation set.")

    rng = np.random.default_rng(seed)
    rows = []

    for replication in range(repetitions):
        sampled_indices = np.concatenate(
            [
                rng.choice(
                    event_indices,
                    size=len(event_indices),
                    replace=True,
                ),
                rng.choice(
                    non_event_indices,
                    size=len(non_event_indices),
                    replace=True,
                ),
            ]
        )

        metrics = calculate_metrics(
            y[sampled_indices],
            scores[sampled_indices],
            max_fpr,
        )

        rows.append(
            {
                "replication": replication,
                **metrics,
            }
        )

    return pd.DataFrame(rows)


def summarize_bootstrap(
    point_estimates: dict[str, float],
    bootstrap: pd.DataFrame,
    model_version: str,
) -> pd.DataFrame:
    rows = []

    for metric in METRICS:
        values = bootstrap[metric].to_numpy(float)

        rows.append(
            {
                "model_version": model_version,
                "metric": metric,
                "metric_label": METRIC_LABELS[metric],
                "estimate": float(
                    point_estimates[metric]
                ),
                "ci95_low": float(
                    np.quantile(values, 0.025)
                ),
                "ci95_high": float(
                    np.quantile(values, 0.975)
                ),
                "bootstrap_repetitions": len(values),
            }
        )

    return pd.DataFrame(rows)


def compare_selection_to_test(
    selection_metrics: dict[str, float],
    test_metrics: dict[str, float],
    selection_bootstrap: pd.DataFrame,
    test_bootstrap: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for metric in METRICS:
        differences = (
            selection_bootstrap[metric].to_numpy(float)
            - test_bootstrap[metric].to_numpy(float)
        )

        rows.append(
            {
                "metric": metric,
                "metric_label": METRIC_LABELS[metric],
                "selection_estimate": float(
                    selection_metrics[metric]
                ),
                "test_estimate_locked_training_model": float(
                    test_metrics[metric]
                ),
                "selection_minus_test": float(
                    selection_metrics[metric]
                    - test_metrics[metric]
                ),
                "difference_ci95_low": float(
                    np.quantile(differences, 0.025)
                ),
                "difference_ci95_high": float(
                    np.quantile(differences, 0.975)
                ),
            }
        )

    return pd.DataFrame(rows)


def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    path.relative_to(directory.parent),
                )

    return zip_path


def main() -> None:
    args = parse_args()
    started = time.time()

    frozen_zip = Path(args.frozen_zip)
    phase4c_zip = Path(args.phase4c_zip)

    if not frozen_zip.exists():
        raise FileNotFoundError(
            f"Frozen Phase 4B ZIP not found: {frozen_zip}"
        )

    if not phase4c_zip.exists():
        raise FileNotFoundError(
            f"Phase 4C ZIP not found: {phase4c_zip}"
        )

    phase4c_payload = read_phase4c_zip(
        phase4c_zip
    )

    locked_model = validate_phase4c(
        frozen_zip,
        phase4c_payload,
    )

    data, plan, _ = phase4c.read_frozen_zip(
        frozen_zip
    )
    phase4c.validate_frozen_design(data, plan)

    config4c = phase4c_payload["config"]
    observed4c = phase4c_payload["observed"]
    winners4c = phase4c_payload["winners"]
    inference4c = phase4c_payload["inference"]

    predictors = list(plan["primary_predictors"])
    outcome = str(plan["outcome"])
    master_seed = int(config4c["master_seed"])
    max_fpr = float(config4c["pauc_max_fpr"])

    train = data[
        data["split"] == "train"
    ].copy()

    selection = data[
        data["split"] == "selection"
    ].copy()

    # Reproduce Phase 4C before any test evaluation.
    (
        locked_preprocessor,
        locked_estimator,
        selection_scores,
    ) = fit_locked_model(
        train,
        selection,
        predictors,
        outcome,
        plan,
        locked_model,
        master_seed,
    )

    selection_metrics = calculate_metrics(
        selection[outcome].to_numpy(int),
        selection_scores,
        max_fpr,
    )

    recorded_model = observed4c[
        observed4c["model"] == locked_model
    ]

    if len(recorded_model) != 1:
        raise RuntimeError(
            "Could not identify the recorded Phase 4C winner."
        )

    recorded_model = recorded_model.iloc[0]
    reproduction_rows = []

    for metric in METRICS:
        recorded = float(recorded_model[metric])
        reproduced = float(selection_metrics[metric])
        difference = reproduced - recorded

        reproduction_rows.append(
            {
                "metric": metric,
                "recorded_phase4c": recorded,
                "reproduced_before_test": reproduced,
                "difference": difference,
                "within_tolerance": (
                    abs(difference)
                    <= args.reproduction_tolerance
                ),
            }
        )

    reproduction = pd.DataFrame(
        reproduction_rows
    )

    print("")
    print("PHASE 4D LOCK VERIFICATION")
    print("=" * 48)
    print(f"Locked model: {locked_model}")
    print(reproduction.to_string(index=False))
    print("")

    if not bool(
        reproduction["within_tolerance"].all()
    ):
        raise RuntimeError(
            "Phase 4C results could not be reproduced. "
            "The test set remains unevaluated."
        )

    print("All locks were verified.")

    if args.dry_run:
        print(
            "Dry run completed. "
            "No test predictions or performance were calculated."
        )
        return

    # Explicit one-time opening starts here.
    test_opened_at = datetime.now(
        timezone.utc
    ).isoformat()

    test = data[
        data["split"] == "test"
    ].copy()

    y_test = test[outcome].to_numpy(int)

    # A. Exact training-only locked model.
    x_test_locked = np.asarray(
        locked_preprocessor.transform(
            test[predictors]
        ),
        dtype=np.float64,
    )

    locked_test_scores = (
        phase4c.prediction_scores(
            locked_estimator,
            x_test_locked,
        )
    )

    locked_test_metrics = calculate_metrics(
        y_test,
        locked_test_scores,
        max_fpr,
    )

    # B. Final refit using train + selection.
    development = pd.concat(
        [train, selection],
        axis=0,
        ignore_index=True,
    )

    (
        final_preprocessor,
        final_estimator,
        final_test_scores,
    ) = fit_locked_model(
        development,
        test,
        predictors,
        outcome,
        plan,
        locked_model,
        master_seed,
    )

    final_test_metrics = calculate_metrics(
        y_test,
        final_test_scores,
        max_fpr,
    )

    # Bootstrap confidence intervals.
    selection_bootstrap = stratified_bootstrap(
        selection[outcome].to_numpy(int),
        selection_scores,
        args.bootstrap_repetitions,
        args.bootstrap_seed + 1,
        max_fpr,
    )

    locked_test_bootstrap = stratified_bootstrap(
        y_test,
        locked_test_scores,
        args.bootstrap_repetitions,
        args.bootstrap_seed + 2,
        max_fpr,
    )

    final_test_bootstrap = stratified_bootstrap(
        y_test,
        final_test_scores,
        args.bootstrap_repetitions,
        args.bootstrap_seed + 3,
        max_fpr,
    )

    performance = pd.concat(
        [
            summarize_bootstrap(
                locked_test_metrics,
                locked_test_bootstrap,
                "locked_training_only",
            ),
            summarize_bootstrap(
                final_test_metrics,
                final_test_bootstrap,
                "final_refit_train_plus_selection",
            ),
        ],
        ignore_index=True,
    )

    comparison = compare_selection_to_test(
        selection_metrics,
        locked_test_metrics,
        selection_bootstrap,
        locked_test_bootstrap,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_root = Path(
        args.output_root
    ).expanduser().resolve()

    output_dir = (
        output_root
        / f"support2_phase4d_{timestamp}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    reproduction.to_csv(
        output_dir
        / "phase4c_reproduction_check.csv",
        index=False,
    )

    performance.to_csv(
        output_dir
        / "untouched_test_performance.csv",
        index=False,
    )

    comparison.to_csv(
        output_dir
        / "selection_to_test_comparison.csv",
        index=False,
    )

    winners4c.to_csv(
        output_dir
        / "phase4c_locked_winners.csv",
        index=False,
    )

    inference4c.to_csv(
        output_dir
        / "phase4c_model_search_inference.csv",
        index=False,
    )

    predictions = pd.DataFrame(
        {
            "id": test["id"].to_numpy(),
            "hospdead": y_test,
            "score_locked_training_only": (
                np.asarray(
                    locked_test_scores,
                    dtype=float,
                )
            ),
            "score_final_refit": (
                np.asarray(
                    final_test_scores,
                    dtype=float,
                )
            ),
        }
    )

    predictions.to_csv(
        output_dir
        / "untouched_test_predictions.csv",
        index=False,
    )

    selection_bootstrap.to_csv(
        output_dir
        / "bootstrap_selection_locked_model.csv",
        index=False,
    )

    locked_test_bootstrap.to_csv(
        output_dir
        / "bootstrap_test_locked_training_model.csv",
        index=False,
    )

    final_test_bootstrap.to_csv(
        output_dir
        / "bootstrap_test_final_refit.csv",
        index=False,
    )

    joblib.dump(
        final_preprocessor,
        output_dir
        / "final_refit_preprocessor.joblib",
    )

    joblib.dump(
        final_estimator,
        output_dir
        / "final_refit_model.joblib",
    )

    config_out = {
        "phase": "4D",
        "test_opened_once": True,
        "test_opened_at_utc": test_opened_at,
        "locked_primary_metric": PRIMARY_METRIC,
        "locked_algorithm": locked_model,
        "phase4b_frozen_zip": str(frozen_zip),
        "phase4b_frozen_zip_sha256": (
            sha256_file(frozen_zip)
        ),
        "phase4c_zip": str(phase4c_zip),
        "phase4c_zip_sha256": (
            sha256_file(phase4c_zip)
        ),
        "bootstrap_repetitions": (
            args.bootstrap_repetitions
        ),
        "bootstrap_seed": args.bootstrap_seed,
        "test_rows": len(test),
        "test_events": int(y_test.sum()),
        "final_refit_rows": len(development),
        "other_candidate_models_not_evaluated_on_test": [
            model
            for model in phase4c.MODEL_NAMES
            if model != locked_model
        ],
    }

    (
        output_dir / "config.json"
    ).write_text(
        json.dumps(
            config_out,
            indent=2,
        ),
        encoding="utf-8",
    )

    (
        output_dir / "environment.json"
    ).write_text(
        json.dumps(
            {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "scikit_learn": (
                    __import__("sklearn").__version__
                ),
                "joblib": joblib.__version__,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    elapsed = time.time() - started

    summary_lines = [
        "SUPPORT2 PHASE 4D: ONE-TIME TEST OPENING",
        "=" * 52,
        f"Locked algorithm: {locked_model}",
        f"Test rows: {len(test):,}",
        f"Test events: {int(y_test.sum()):,}",
        f"Bootstrap repetitions: {args.bootstrap_repetitions:,}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "UNTOUCHED-TEST PERFORMANCE",
        "--------------------------",
        performance.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        ),
        "",
        "SELECTION TO TEST",
        "-----------------",
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        ),
        "",
        "No alternative candidate algorithm was evaluated",
        "or selected using the test set.",
    ]

    (
        output_dir / "summary.txt"
    ).write_text(
        "\n".join(summary_lines),
        encoding="utf-8",
    )

    (
        output_dir / "run_complete.json"
    ).write_text(
        json.dumps(
            {
                "completed": True,
                "test_opened_once": True,
                "locked_algorithm": locked_model,
                "test_rows": len(test),
                "test_events": int(y_test.sum()),
                "elapsed_seconds": elapsed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    zip_path = zip_directory(
        output_dir
    )

    print("")
    print("PHASE 4D COMPLETED")
    print("=" * 48)
    print(f"Locked algorithm: {locked_model}")
    print(
        f"Test rows/events: "
        f"{len(test):,}/{int(y_test.sum()):,}"
    )
    print("")
    print(performance.to_string(index=False))
    print("")
    print(f"Upload this ZIP next: {zip_path}")


if __name__ == "__main__":
    main()
