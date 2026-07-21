#!/usr/bin/env python3
"""
Phase 3B: model-library and signal-structure sensitivity analysis.

This wrapper reuses pipeline_independent_null_phase3.py while changing:

Model libraries, each containing exactly seven models:
  1. similar_linear_7
  2. heterogeneous_core_7
  3. extended_sklearn_7

Signal structures:
  1. single_linear
  2. multi_weak_linear
  3. xor_interaction

A separate pipeline-specific null reference bank is constructed for every
library and signal structure.

Required files in the same directory:
  pipeline_null_pilot_v2.py
  pipeline_event_prevalence_phase2b.py
  pipeline_metric_phase2c.py
  pipeline_independent_null_phase3.py
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import zipfile
from collections import OrderedDict
from pathlib import Path

# Ensure repository-local package imports work when this file is run directly.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

import joblib
import numpy as np

from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, SVC

from simulations.phase1 import pipeline_null_pilot_v2 as base
from simulations.phase2 import pipeline_event_prevalence_phase2b as phase2b
from simulations.phase3 import pipeline_independent_null_phase3 as phase3


LIBRARIES = (
    "similar_linear_7",
    "heterogeneous_core_7",
    "extended_sklearn_7",
)

SIGNAL_STRUCTURES = (
    "single_linear",
    "multi_weak_linear",
    "xor_interaction",
)

ORIGINAL_BUILD_MODELS = base.build_candidate_models
ORIGINAL_GENERATE_SIGNAL = phase2b.generate_signal_dataset


def scaled_pipeline(model):
    return Pipeline(
        [
            ("variance", VarianceThreshold()),
            ("scale", StandardScaler()),
            ("model", model),
        ]
    )


def build_similar_linear_library(seed: int):
    """Seven deliberately similar linear classifiers."""

    return OrderedDict(
        [
            (
                "logreg_l2_c003",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="l2",
                        C=0.03,
                        solver="liblinear",
                        max_iter=3000,
                        random_state=seed + 101,
                    )
                ),
            ),
            (
                "logreg_l2_c01",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="l2",
                        C=0.10,
                        solver="liblinear",
                        max_iter=3000,
                        random_state=seed + 103,
                    )
                ),
            ),
            (
                "logreg_l2_c1",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="l2",
                        C=1.0,
                        solver="liblinear",
                        max_iter=3000,
                        random_state=seed + 107,
                    )
                ),
            ),
            (
                "logreg_l2_c10",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="l2",
                        C=10.0,
                        solver="liblinear",
                        max_iter=3000,
                        random_state=seed + 109,
                    )
                ),
            ),
            (
                "logreg_l1_c01",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="l1",
                        C=0.10,
                        solver="liblinear",
                        max_iter=3000,
                        random_state=seed + 113,
                    )
                ),
            ),
            (
                "elastic_net_logreg",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="elasticnet",
                        C=1.0,
                        l1_ratio=0.5,
                        solver="saga",
                        max_iter=3000,
                        n_jobs=1,
                        random_state=seed + 127,
                    )
                ),
            ),
            (
                "linear_svm_c1",
                scaled_pipeline(
                    LinearSVC(
                        C=1.0,
                        dual=False,
                        max_iter=8000,
                        random_state=seed + 131,
                    )
                ),
            ),
        ]
    )


def build_heterogeneous_core_library(seed: int):
    """The original seven-model Phase 3 library."""

    return OrderedDict(ORIGINAL_BUILD_MODELS(seed).items())


def build_extended_sklearn_library(seed: int):
    """A stronger nonlinear library using only scikit-learn."""

    return OrderedDict(
        [
            (
                "elastic_net_logreg",
                scaled_pipeline(
                    LogisticRegression(
                        penalty="elasticnet",
                        C=1.0,
                        l1_ratio=0.5,
                        solver="saga",
                        max_iter=3000,
                        n_jobs=1,
                        random_state=seed + 211,
                    )
                ),
            ),
            (
                "rbf_svm_c3",
                scaled_pipeline(
                    SVC(
                        C=3.0,
                        kernel="rbf",
                        gamma="scale",
                        probability=False,
                        cache_size=500,
                        random_state=seed + 223,
                    )
                ),
            ),
            (
                "extra_trees",
                ExtraTreesClassifier(
                    n_estimators=150,
                    max_features="sqrt",
                    min_samples_leaf=2,
                    n_jobs=1,
                    random_state=seed + 227,
                ),
            ),
            (
                "random_forest_tuned",
                RandomForestClassifier(
                    n_estimators=150,
                    max_features=0.70,
                    min_samples_leaf=2,
                    n_jobs=1,
                    random_state=seed + 229,
                ),
            ),
            (
                "hist_gradient_boosting_tuned",
                HistGradientBoostingClassifier(
                    max_iter=180,
                    max_leaf_nodes=31,
                    learning_rate=0.06,
                    l2_regularization=0.5,
                    random_state=seed + 233,
                ),
            ),
            (
                "gradient_boosting",
                GradientBoostingClassifier(
                    n_estimators=150,
                    learning_rate=0.05,
                    max_depth=2,
                    min_samples_leaf=5,
                    random_state=seed + 239,
                ),
            ),
            (
                "mlp",
                scaled_pipeline(
                    MLPClassifier(
                        hidden_layer_sizes=(32, 16),
                        activation="relu",
                        alpha=1e-3,
                        learning_rate_init=1e-3,
                        max_iter=250,
                        early_stopping=True,
                        validation_fraction=0.15,
                        n_iter_no_change=12,
                        random_state=seed + 241,
                    )
                ),
            ),
        ]
    )


def build_library(library: str, seed: int):
    if library == "similar_linear_7":
        models = build_similar_linear_library(seed)
    elif library == "heterogeneous_core_7":
        models = build_heterogeneous_core_library(seed)
    elif library == "extended_sklearn_7":
        models = build_extended_sklearn_library(seed)
    else:
        raise ValueError(f"Unknown model library: {library}")

    if len(models) != 7:
        raise RuntimeError(
            f"Every Phase 3B library must contain exactly 7 models; "
            f"{library} contained {len(models)}."
        )

    return models


def make_multi_weak_dataset(
    n: int,
    prevalence: float,
    n_features: int,
    binary_fraction: float,
    rho: float,
    target_auc: float,
    rng: np.random.Generator,
):
    """
    Generate five weak Gaussian signal variables.

    Their equally weighted oracle sum has the requested population AUROC.
    """

    y = base.generate_fixed_outcome(n, prevalence, rng)

    n_signal = min(5, n_features)
    total_delta = phase2b.delta_from_auc(target_auc)
    component_delta = total_delta / math.sqrt(n_signal)

    signal = rng.normal(size=(n, n_signal))
    signal += component_delta * y[:, np.newaxis]

    noise = phase2b.generate_noise_predictors(
        n=n,
        n_noise_features=n_features - n_signal,
        total_features=n_features,
        binary_fraction=binary_fraction,
        rho=rho,
        rng=rng,
    )

    return np.column_stack([signal, noise]), y


def make_xor_dataset(
    n: int,
    prevalence: float,
    n_features: int,
    binary_fraction: float,
    rho: float,
    target_auc: float,
    rng: np.random.Generator,
):
    """
    Generate an interaction-only signal.

    The sign of X1 * X2 is the oracle binary score. Its population AUROC
    equals target_auc. X1 and X2 individually have no marginal linear
    association with the outcome.
    """

    y = base.generate_fixed_outcome(n, prevalence, rng)

    agrees_with_outcome = rng.random(n) < target_auc

    # For events, product is positive with probability target_auc.
    # For non-events, product is negative with probability target_auc.
    product_positive = np.where(
        y == 1,
        agrees_with_outcome,
        ~agrees_with_outcome,
    )

    sign1 = np.where(rng.random(n) < 0.5, -1.0, 1.0)
    sign2 = np.where(product_positive, sign1, -sign1)

    magnitude1 = 0.25 + np.abs(rng.normal(size=n))
    magnitude2 = 0.25 + np.abs(rng.normal(size=n))

    x1 = sign1 * magnitude1
    x2 = sign2 * magnitude2

    noise = phase2b.generate_noise_predictors(
        n=n,
        n_noise_features=n_features - 2,
        total_features=n_features,
        binary_fraction=binary_fraction,
        rho=rho,
        rng=rng,
    )

    return np.column_stack([x1, x2, noise]), y


def make_signal_generator(structure: str):
    def generate(
        n: int,
        prevalence: float,
        n_features: int,
        binary_fraction: float,
        rho: float,
        target_auc: float,
        rng: np.random.Generator,
    ):
        if structure == "single_linear":
            return ORIGINAL_GENERATE_SIGNAL(
                n,
                prevalence,
                n_features,
                binary_fraction,
                rho,
                target_auc,
                rng,
            )

        if structure == "multi_weak_linear":
            return make_multi_weak_dataset(
                n,
                prevalence,
                n_features,
                binary_fraction,
                rho,
                target_auc,
                rng,
            )

        if structure == "xor_interaction":
            return make_xor_dataset(
                n,
                prevalence,
                n_features,
                binary_fraction,
                rho,
                target_auc,
                rng,
            )

        raise ValueError(f"Unknown signal structure: {structure}")

    return generate


def option_present(arguments: list[str], option: str) -> bool:
    return any(
        argument == option or argument.startswith(option + "=")
        for argument in arguments
    )


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3B model-library sensitivity wrapper.",
        add_help=True,
    )

    parser.add_argument(
        "--library",
        choices=LIBRARIES,
        required=True,
    )
    parser.add_argument(
        "--signal-structure",
        choices=SIGNAL_STRUCTURES,
        required=True,
    )
    parser.add_argument(
        "--output-root",
        default="results_phase3b",
    )

    wrapper_args, phase3_args = parser.parse_known_args()

    if option_present(phase3_args, "--pool-sizes"):
        raise SystemExit(
            "Do not specify --pool-sizes in Phase 3B. "
            "The candidate-model count is fixed at 7."
        )

    library = wrapper_args.library
    signal_structure = wrapper_args.signal_structure

    prototype = build_library(library, seed=1)
    model_names = tuple(prototype.keys())

    # Patch the model library used by the existing Phase 3 pipeline.
    base.MODEL_NAMES = model_names
    base.build_candidate_models = lambda seed: build_library(library, seed)

    # Phase 3 uses this mapping for winner selection and max statistics.
    phase3.POOL_MODELS = {7: model_names}

    # Patch the data-generating mechanism.
    phase2b.generate_signal_dataset = make_signal_generator(signal_structure)

    result_root = (
        Path(wrapper_args.output_root)
        .expanduser()
        .resolve()
        / library
        / signal_structure
    )
    result_root.mkdir(parents=True, exist_ok=True)

    if not option_present(phase3_args, "--feature-selection-methods"):
        phase3_args.extend(["--feature-selection-methods", "none"])

    phase3_args.extend(
        [
            "--pool-sizes",
            "7",
            "--output-root",
            str(result_root),
        ]
    )

    print("=" * 72)
    print("PHASE 3B")
    print(f"Library:          {library}")
    print(f"Signal structure: {signal_structure}")
    print(f"Candidate models: {list(model_names)}")
    print(f"Output root:      {result_root}")
    print("=" * 72)

    sys.argv = [sys.argv[0], *phase3_args]
    # Phase 3B modifies the model library and data generator at runtime.
    # Thread workers share these patched module objects; process workers do not.
    with joblib.parallel_backend("threading"):
        phase3.main()

    # Attach Phase 3B metadata to the newly generated ZIP.
    zip_files = sorted(
        result_root.glob("pipeline_phase3_*.zip"),
        key=lambda path: path.stat().st_mtime,
    )

    if not zip_files:
        print("Warning: generated ZIP could not be located.")
        return

    source_zip = zip_files[-1]
    metadata = {
        "phase": "3B",
        "library": library,
        "signal_structure": signal_structure,
        "candidate_models": list(model_names),
        "nominal_model_count": len(model_names),
    }

    with zipfile.ZipFile(
        source_zip,
        mode="a",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "phase3b_metadata.json",
            json.dumps(metadata, indent=2),
        )

    new_zip = source_zip.with_name(
        source_zip.name.replace(
            "pipeline_phase3_",
            f"pipeline_phase3b_{library}_{signal_structure}_",
            1,
        )
    )

    if new_zip != source_zip:
        source_zip.rename(new_zip)

    print("")
    print(f"Upload this ZIP next: {new_zip}")


if __name__ == "__main__":
    main()
