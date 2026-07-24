#!/usr/bin/env python3
"""Phase 3C: K=7 versus K=20 candidate-search simulation wrapper.

This script reuses the validated Phase 3 engine while replacing the model
library with one of two prespecified 20-candidate libraries. The first seven
candidates in each library reproduce the corresponding Phase 3B/Phase 3
anchor library, so K=7 and K=20 are paired within every replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import joblib

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import (
    AdaBoostClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings(
    "ignore",
    message=r"Inconsistent values: penalty=.*",
    category=UserWarning,
)

# Make the existing repository modules importable when this file is executed
# from simulations/phase3c/.
REPO_ROOT = Path(__file__).resolve().parents[2]
for relative in ("simulations/phase1", "simulations/phase2", "simulations/phase3"):
    sys.path.insert(0, str(REPO_ROOT / relative))

import pipeline_null_pilot_v2 as base  # noqa: E402
import pipeline_event_prevalence_phase2b as phase2b  # noqa: E402
import pipeline_independent_null_phase3 as phase3  # noqa: E402

LIBRARIES = ("high_dependency_linear_20", "mixed_realistic_20")
ORIGINAL_BUILD_MODELS = base.build_candidate_models
ORIGINAL_GENERATE_SIGNAL = phase2b.generate_signal_dataset


def scaled_pipeline(model: Any) -> Pipeline:
    return Pipeline(
        [
            ("variance", VarianceThreshold()),
            ("scale", StandardScaler()),
            ("model", model),
        ]
    )


def _logreg(*, penalty: str, c_value: float, seed: int, l1_ratio: float | None = None) -> Pipeline:
    if penalty == "elasticnet":
        estimator = LogisticRegression(
            penalty="elasticnet",
            C=c_value,
            l1_ratio=l1_ratio,
            solver="saga",
            max_iter=3000,
            n_jobs=1,
            random_state=seed,
        )
    else:
        estimator = LogisticRegression(
            penalty=penalty,
            C=c_value,
            solver="liblinear",
            max_iter=3000,
            random_state=seed,
        )
    return scaled_pipeline(estimator)


def build_high_dependency_library(seed: int) -> OrderedDict[str, Any]:
    """Twenty deliberately correlated linear classifiers.

    The first seven reproduce the existing similar_linear_7 library.
    """
    return OrderedDict(
        [
            ("logreg_l2_c003", _logreg(penalty="l2", c_value=0.03, seed=seed + 101)),
            ("logreg_l2_c01", _logreg(penalty="l2", c_value=0.10, seed=seed + 103)),
            ("logreg_l2_c1", _logreg(penalty="l2", c_value=1.0, seed=seed + 107)),
            ("logreg_l2_c10", _logreg(penalty="l2", c_value=10.0, seed=seed + 109)),
            ("logreg_l1_c01", _logreg(penalty="l1", c_value=0.10, seed=seed + 113)),
            ("elastic_net_logreg", _logreg(penalty="elasticnet", c_value=1.0, l1_ratio=0.5, seed=seed + 127)),
            (
                "linear_svm_c1",
                scaled_pipeline(
                    LinearSVC(C=1.0, dual=False, max_iter=8000, random_state=seed + 131)
                ),
            ),
            ("logreg_l2_c001", _logreg(penalty="l2", c_value=0.01, seed=seed + 137)),
            ("logreg_l2_c03", _logreg(penalty="l2", c_value=0.30, seed=seed + 139)),
            ("logreg_l2_c3", _logreg(penalty="l2", c_value=3.0, seed=seed + 149)),
            ("logreg_l2_c30", _logreg(penalty="l2", c_value=30.0, seed=seed + 151)),
            ("logreg_l2_c100", _logreg(penalty="l2", c_value=100.0, seed=seed + 157)),
            ("logreg_l1_c003", _logreg(penalty="l1", c_value=0.03, seed=seed + 163)),
            ("logreg_l1_c03", _logreg(penalty="l1", c_value=0.30, seed=seed + 167)),
            ("logreg_l1_c1", _logreg(penalty="l1", c_value=1.0, seed=seed + 173)),
            ("logreg_l1_c3", _logreg(penalty="l1", c_value=3.0, seed=seed + 179)),
            ("elastic_net_c01_r025", _logreg(penalty="elasticnet", c_value=0.10, l1_ratio=0.25, seed=seed + 181)),
            ("elastic_net_c1_r025", _logreg(penalty="elasticnet", c_value=1.0, l1_ratio=0.25, seed=seed + 191)),
            ("elastic_net_c1_r075", _logreg(penalty="elasticnet", c_value=1.0, l1_ratio=0.75, seed=seed + 193)),
            (
                "linear_svm_c01",
                scaled_pipeline(
                    LinearSVC(C=0.10, dual=False, max_iter=8000, random_state=seed + 197)
                ),
            ),
        ]
    )


def build_mixed_library(seed: int) -> OrderedDict[str, Any]:
    """Twenty realistic mixed candidates.

    The first seven reproduce the existing heterogeneous Phase 3 library.
    """
    models: OrderedDict[str, Any] = OrderedDict(ORIGINAL_BUILD_MODELS(seed).items())
    if len(models) != 7:
        raise RuntimeError(f"Expected the original Phase 3 library to contain 7 models; found {len(models)}.")

    additions: OrderedDict[str, Any] = OrderedDict(
        [
            ("logreg_l1_c01", _logreg(penalty="l1", c_value=0.10, seed=seed + 301)),
            ("elastic_net_c1_r05", _logreg(penalty="elasticnet", c_value=1.0, l1_ratio=0.5, seed=seed + 307)),
            ("logreg_l2_c01", _logreg(penalty="l2", c_value=0.10, seed=seed + 311)),
            (
                "rbf_svm_c03",
                scaled_pipeline(SVC(C=0.30, kernel="rbf", gamma="scale", cache_size=500, random_state=seed + 313)),
            ),
            (
                "rbf_svm_c3",
                scaled_pipeline(SVC(C=3.0, kernel="rbf", gamma="scale", cache_size=500, random_state=seed + 317)),
            ),
            (
                "extra_trees",
                ExtraTreesClassifier(
                    n_estimators=100,
                    max_features="sqrt",
                    min_samples_leaf=2,
                    n_jobs=1,
                    random_state=seed + 331,
                ),
            ),
            (
                "random_forest_shallow",
                RandomForestClassifier(
                    n_estimators=100,
                    max_depth=5,
                    min_samples_leaf=5,
                    n_jobs=1,
                    random_state=seed + 337,
                ),
            ),
            (
                "random_forest_tuned",
                RandomForestClassifier(
                    n_estimators=100,
                    max_features=0.70,
                    min_samples_leaf=2,
                    n_jobs=1,
                    random_state=seed + 347,
                ),
            ),
            (
                "gradient_boosting",
                GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.05,
                    max_depth=2,
                    min_samples_leaf=5,
                    random_state=seed + 349,
                ),
            ),
            (
                "adaboost_stump",
                AdaBoostClassifier(
                    estimator=DecisionTreeClassifier(max_depth=1, random_state=seed + 353),
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=seed + 359,
                ),
            ),
            (
                "hist_gb_shallow",
                HistGradientBoostingClassifier(
                    max_iter=120,
                    max_leaf_nodes=15,
                    learning_rate=0.05,
                    l2_regularization=0.5,
                    random_state=seed + 367,
                ),
            ),
            (
                "linear_discriminant_shrinkage",
                scaled_pipeline(LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")),
            ),
            (
                "knn_15_distance",
                scaled_pipeline(
                    KNeighborsClassifier(
                        n_neighbors=15,
                        weights="distance",
                        metric="minkowski",
                        p=2,
                        n_jobs=1,
                    )
                ),
            ),
        ]
    )
    models.update(additions)
    return models


def build_library(library: str, seed: int) -> OrderedDict[str, Any]:
    if library == "high_dependency_linear_20":
        models = build_high_dependency_library(seed)
    elif library == "mixed_realistic_20":
        models = build_mixed_library(seed)
    else:
        raise ValueError(f"Unknown library: {library}")
    if len(models) != 20:
        raise RuntimeError(f"{library} must contain exactly 20 models; found {len(models)}.")
    if len(set(models)) != 20:
        raise RuntimeError(f"{library} contains duplicate candidate names.")
    return models


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    required = ("target_aurocs", "null_repetitions", "evaluation_repetitions")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Config is missing required keys: {missing}")
    return config


def comma(values: list[Any] | tuple[Any, ...]) -> str:
    return ",".join(str(value) for value in values)


def latest_run_directory(root: Path) -> Path:
    candidates = [path for path in root.glob("pipeline_phase3_*") if path.is_dir()]
    if not candidates:
        raise RuntimeError(f"Could not find a generated Phase 3 run directory under {root}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def write_manifest(run_dir: Path, library: str, models: OrderedDict[str, Any], k7_names: tuple[str, ...]) -> None:
    import csv

    rows = []
    for order, (name, estimator) in enumerate(models.items(), start=1):
        rows.append(
            {
                "library": library,
                "candidate_order": order,
                "candidate_name": name,
                "included_in_k7": name in k7_names,
                "included_in_k20": True,
                "estimator_class": type(estimator).__name__,
                "parameters_json": json.dumps(estimator.get_params(deep=True), default=str, sort_keys=True),
            }
        )
    manifest_path = run_dir / "candidate_library_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    metadata = {
        "phase": "3C",
        "library": library,
        "candidate_models_k7": list(k7_names),
        "candidate_models_k20": list(models.keys()),
        "manifest_sha256": digest,
    }
    (run_dir / "phase3c_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 3C K=7 versus K=20 wrapper")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--library", choices=LIBRARIES, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("results_phase3c/pilot"))
    parser.add_argument("--null-repetitions", type=int)
    parser.add_argument("--evaluation-repetitions", type=int)
    parser.add_argument("--n-jobs", type=int)
    args = parser.parse_args()

    config = load_config(args.config.resolve())
    library = args.library
    models = build_library(library, seed=1)
    all_names = tuple(models.keys())
    k7_names = all_names[:7]

    configured_libraries = tuple(config.get("libraries", LIBRARIES))
    if library not in configured_libraries:
        raise ValueError(f"Library {library} is not listed in config libraries={configured_libraries}")

    pool_sizes = tuple(int(x) for x in config.get("pool_sizes", [7, 20]))
    if pool_sizes != (7, 20):
        raise ValueError(f"Phase 3C requires pool_sizes [7, 20]; received {pool_sizes}")

    target_aurocs = [float(x) for x in config["target_aurocs"]]
    event_counts = config.get("selection_event_counts", config.get("selection_events", [100]))
    feature_methods = config.get("feature_selection_methods", ["none"])
    if feature_methods != ["none"] and tuple(feature_methods) != ("none",):
        raise ValueError("Phase 3C pilot requires feature_selection_methods=['none']")
    if str(config.get("selection_metric", "roc_auc")) != "roc_auc":
        raise ValueError("Phase 3C pilot requires selection_metric='roc_auc'")

    null_repetitions = args.null_repetitions or int(config["null_repetitions"])
    evaluation_repetitions = args.evaluation_repetitions or int(config["evaluation_repetitions"])
    n_jobs = args.n_jobs or int(config.get("n_jobs", 18))

    # Patch the validated Phase 3 engine. Patch both the module imported here
    # and the module object held by phase3; these can differ when multiple
    # repository clones or import paths are active in the same environment.
    def build_phase3c_models(seed: int) -> OrderedDict[str, Any]:
        return build_library(library, seed)

    for base_module in (base, phase3.base):
        base_module.MODEL_NAMES = all_names
        base_module.build_candidate_models = build_phase3c_models

    phase3.POOL_MODELS = {7: k7_names, 20: all_names}
    phase2b.generate_signal_dataset = ORIGINAL_GENERATE_SIGNAL
    phase3.phase2b.generate_signal_dataset = ORIGINAL_GENERATE_SIGNAL

    # Phase 3C is an AUROC-primary analysis. Restricting the engine to AUROC
    # also makes the pilot faster and avoids generating unused metric outputs.
    phase3.METRICS = ("roc_auc",)

    engine_names = tuple(phase3.base.build_candidate_models(1).keys())
    if engine_names != all_names:
        raise RuntimeError(
            "Phase 3 engine did not receive the Phase 3C candidate library. "
            f"Expected {all_names}; received {engine_names}."
        )

    result_root = args.output_root.expanduser().resolve() / library
    result_root.mkdir(parents=True, exist_ok=True)

    phase3_args = [
        "--preset", "quick",
        "--null-repetitions", str(null_repetitions),
        "--evaluation-repetitions", str(evaluation_repetitions),
        "--n-train", str(int(config.get("n_train", 500))),
        "--n-test", str(int(config.get("n_test", 2000))),
        "--train-prevalence", str(float(config.get("train_prevalence", 0.10))),
        "--selection-prevalence", str(float(config.get("selection_prevalence", 0.10))),
        "--test-prevalence", str(float(config.get("test_prevalence", 0.10))),
        "--n-features", str(int(config.get("n_features", 30))),
        "--binary-fraction", str(float(config.get("binary_fraction", 0.40))),
        "--correlation-rho", str(float(config.get("correlation_rho", 0.30))),
        "--cv-folds", str(int(config.get("cv_folds", 5))),
        "--event-counts", comma(event_counts),
        "--target-aurocs", comma(target_aurocs),
        "--feature-selection-methods", "none",
        "--pool-sizes", "7,20",
        "--pauc-max-fpr", str(float(config.get("pauc_max_fpr", 0.10))),
        "--alpha", str(float(config.get("alpha", 0.05))),
        "--master-seed", str(int(config.get("master_seed", 20260723))),
        "--n-jobs", str(n_jobs),
        "--output-root", str(result_root),
    ]

    print("=" * 78)
    print("PHASE 3C")
    print(f"Config:              {args.config.resolve()}")
    print(f"Library:             {library}")
    print(f"K=7 candidates:      {list(k7_names)}")
    print(f"K=20 candidate count:{len(all_names)}")
    print(f"Null repetitions:    {null_repetitions}")
    print(f"Evaluation reps:     {evaluation_repetitions} per target AUROC")
    print(f"n_jobs:              {n_jobs}")
    print(f"Output root:         {result_root}")
    print("=" * 78)

    sys.argv = [sys.argv[0], *phase3_args]
    with joblib.parallel_backend("threading"):
        phase3.main()

    run_dir = latest_run_directory(result_root)
    write_manifest(run_dir, library, build_library(library, seed=1), k7_names)

    zip_candidates = sorted(result_root.glob("pipeline_phase3_*.zip"), key=lambda p: p.stat().st_mtime)
    if zip_candidates:
        source_zip = zip_candidates[-1]
        with zipfile.ZipFile(source_zip, "a", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(run_dir / "candidate_library_manifest.csv", arcname="candidate_library_manifest.csv")
            archive.write(run_dir / "phase3c_metadata.json", arcname="phase3c_metadata.json")
        renamed = source_zip.with_name(source_zip.name.replace("pipeline_phase3_", f"pipeline_phase3c_{library}_", 1))
        source_zip.rename(renamed)
        print(f"Phase 3C ZIP: {renamed}")
    print(f"Phase 3C run directory: {run_dir}")


if __name__ == "__main__":
    main()
