#!/usr/bin/env python3
"""Generate SUPPORT2 outcome-permutation reference and evaluation model banks."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def make_preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median", add_indicator=True)),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", make_ohe()),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ], remainder="drop", sparse_threshold=0.0)


def make_model(candidate: dict, seed: int):
    family = candidate["family"]
    p = candidate["params"]
    if family == "logistic":
        return LogisticRegression(
            penalty=p["penalty"], C=float(p["C"]), solver="liblinear",
            max_iter=2000, random_state=seed,
        )
    if family == "linear_svm":
        return LinearSVC(C=float(p["C"]), max_iter=10000, random_state=seed)
    if family == "rbf_svm":
        return SVC(C=float(p["C"]), kernel="rbf", gamma="scale", probability=False, random_state=seed)
    if family == "decision_tree":
        return DecisionTreeClassifier(max_depth=int(p["max_depth"]), min_samples_leaf=5, random_state=seed)
    if family == "random_forest":
        return RandomForestClassifier(
            n_estimators=int(p["n_estimators"]), max_depth=int(p["max_depth"]),
            min_samples_leaf=int(p["min_samples_leaf"]), max_features="sqrt",
            n_jobs=1, random_state=seed,
        )
    if family == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=int(p["n_estimators"]), max_depth=int(p["max_depth"]),
            min_samples_leaf=int(p["min_samples_leaf"]), max_features="sqrt",
            n_jobs=1, random_state=seed,
        )
    if family == "gradient_boosting":
        return GradientBoostingClassifier(
            n_estimators=int(p["n_estimators"]), max_depth=int(p["max_depth"]),
            learning_rate=float(p["learning_rate"]), random_state=seed,
        )
    if family == "gaussian_nb":
        return GaussianNB(var_smoothing=float(p["var_smoothing"]))
    if family == "knn":
        return KNeighborsClassifier(n_neighbors=int(p["n_neighbors"]), weights=p["weights"], n_jobs=1)
    raise ValueError(f"Unknown candidate family: {family}")


def prediction_score(model, x: np.ndarray) -> np.ndarray:
    if hasattr(model, "decision_function"):
        score = model.decision_function(x)
    elif hasattr(model, "predict_proba"):
        score = model.predict_proba(x)[:, 1]
    else:
        score = model.predict(x)
    return np.asarray(score, dtype=float).reshape(-1)


def permuted_labels(y: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return y[rng.permutation(len(y))]


def candidate_seed(bank_seed: int, replication: int, order: int) -> int:
    seq = np.random.SeedSequence([int(bank_seed), int(replication), int(order), 99173])
    return int(seq.generate_state(1, dtype=np.uint32)[0])


def run_replication(
    replication: int,
    bank_seed: int,
    x_train: np.ndarray,
    x_selection: np.ndarray,
    y_train: np.ndarray,
    y_selection: np.ndarray,
    candidates: list[dict],
) -> list[dict]:
    rep_seq = np.random.SeedSequence([int(bank_seed), int(replication), 48121])
    label_seeds = rep_seq.generate_state(2, dtype=np.uint32)
    yt = permuted_labels(y_train, int(label_seeds[0]))
    ys = permuted_labels(y_selection, int(label_seeds[1]))

    rows = []
    for candidate in candidates:
        started = time.perf_counter()
        failed = False
        error_type = ""
        error_message = ""
        seed = candidate_seed(bank_seed, replication, int(candidate["order"]))
        try:
            model = make_model(candidate, seed)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(x_train, yt)
                scores = prediction_score(model, x_selection)
            if not np.all(np.isfinite(scores)) or np.unique(scores).size < 2:
                raise ValueError("non-finite or constant prediction score")
            auc = float(roc_auc_score(ys, scores))
            if not np.isfinite(auc):
                raise ValueError("non-finite ROC AUC")
        except Exception as exc:
            failed = True
            auc = 0.5
            error_type = type(exc).__name__
            error_message = str(exc).replace("\n", " ")[:500]
        rows.append({
            "replication": int(replication),
            "seed": int(bank_seed),
            "model": candidate["name"],
            "candidate_order": int(candidate["order"]),
            "included_in_k7": bool(candidate["base"]),
            "selection_roc_auc": auc,
            "fit_failed": failed,
            "error_type": error_type,
            "error_message": error_message,
            "fit_seconds": float(time.perf_counter() - started),
        })
    return rows


def run_bank(
    label: str,
    repetitions: int,
    bank_seed: int,
    x_train: np.ndarray,
    x_selection: np.ndarray,
    y_train: np.ndarray,
    y_selection: np.ndarray,
    candidates: list[dict],
    n_jobs: int,
) -> pd.DataFrame:
    nested = Parallel(n_jobs=n_jobs, verbose=10, batch_size=1)(
        delayed(run_replication)(
            rep, bank_seed, x_train, x_selection, y_train, y_selection, candidates
        )
        for rep in range(1, repetitions + 1)
    )
    rows = [row for group in nested for row in group]
    frame = pd.DataFrame(rows)
    frame.insert(0, "bank", label)
    return frame


def validate_bank(frame: pd.DataFrame, repetitions: int, candidates: list[dict], label: str) -> dict:
    expected = repetitions * len(candidates)
    if len(frame) != expected:
        raise ValueError(f"{label}: expected {expected} rows, found {len(frame)}")
    if frame.duplicated(["replication", "model"]).any():
        raise ValueError(f"{label}: duplicate replication/model rows")
    if frame["replication"].nunique() != repetitions:
        raise ValueError(f"{label}: unexpected replication count")
    if frame["model"].nunique() != len(candidates):
        raise ValueError(f"{label}: unexpected candidate count")
    if not np.all(np.isfinite(frame["selection_roc_auc"].to_numpy(float))):
        raise ValueError(f"{label}: non-finite AUC after failed-fit handling")
    return {
        "bank": label,
        "repetitions": repetitions,
        "rows": len(frame),
        "candidate_count": frame["model"].nunique(),
        "failed_fit_count": int(frame["fit_failed"].sum()),
        "failed_fit_rate": float(frame["fit_failed"].mean()),
        "mean_fit_seconds": float(frame["fit_seconds"].mean()),
        "total_recorded_fit_seconds": float(frame["fit_seconds"].sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=Path("data/support2/support2_analysis_v1.csv"))
    parser.add_argument("--data-manifest", type=Path, default=Path("data/support2/support2_data_manifest_v1.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-jobs", type=int, default=28)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    manifest = json.loads(args.data_manifest.read_text(encoding="utf-8"))
    if file_sha256(args.data) != manifest["canonical_sha256"]:
        raise SystemExit("DATA LOCK FAILURE: canonical SUPPORT2 hash differs from manifest")

    data = pd.read_csv(args.data)
    outcome = config["data"]["outcome"]
    numeric = config["data"]["numeric_predictors"]
    categorical = config["data"]["categorical_predictors"]
    predictors = numeric + categorical
    missing = sorted(set(predictors + [outcome]).difference(data.columns))
    if missing:
        raise ValueError(f"Prepared data missing columns: {missing}")

    x = data[predictors].copy()
    y = data[outcome].astype(int).to_numpy()
    indices = np.arange(len(data))
    design = config["design"]
    train_idx, selection_idx = train_test_split(
        indices,
        train_size=int(design["n_train"]),
        test_size=int(design["n_selection"]),
        stratify=y,
        random_state=int(design["split_seed"]),
    )
    x_train_df = x.iloc[train_idx].copy()
    x_selection_df = x.iloc[selection_idx].copy()
    y_train = y[train_idx]
    y_selection = y[selection_idx]

    preprocessor = make_preprocessor(numeric, categorical)
    x_train = np.asarray(preprocessor.fit_transform(x_train_df), dtype=float)
    x_selection = np.asarray(preprocessor.transform(x_selection_df), dtype=float)
    if not np.all(np.isfinite(x_train)) or not np.all(np.isfinite(x_selection)):
        raise ValueError("Preprocessed design matrices contain non-finite values")

    candidates = sorted(config["candidate_library"], key=lambda c: int(c["order"]))
    if len(candidates) != 20 or sum(bool(c["base"]) for c in candidates) != 7:
        raise ValueError("Locked library must contain 20 candidates with 7 base candidates")

    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=False)
    pd.DataFrame([
        {
            "candidate_order": c["order"],
            "candidate_name": c["name"],
            "candidate_family": c["family"],
            "included_in_k7": c["base"],
            "parameters_json": json.dumps(c["params"], sort_keys=True),
        }
        for c in candidates
    ]).to_csv(out / "candidate_library_manifest.csv", index=False)

    split = {
        "split_seed": int(design["split_seed"]),
        "train_row_ids": data.iloc[train_idx]["support2_row_id"].astype(int).tolist(),
        "selection_row_ids": data.iloc[selection_idx]["support2_row_id"].astype(int).tolist(),
        "n_train": len(train_idx),
        "n_selection": len(selection_idx),
        "train_events": int(y_train.sum()),
        "selection_events": int(y_selection.sum()),
        "transformed_feature_count": int(x_train.shape[1]),
        "data_sha256": manifest["canonical_sha256"],
    }
    (out / "fixed_split_manifest.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    reference = run_bank(
        "reference", int(design["reference_repetitions"]), int(design["reference_seed"]),
        x_train, x_selection, y_train, y_selection, candidates, args.n_jobs,
    )
    reference.to_csv(out / "null_reference_model_metrics.csv", index=False)
    ref_audit = validate_bank(reference, int(design["reference_repetitions"]), candidates, "reference")

    evaluation = run_bank(
        "evaluation", int(design["evaluation_repetitions"]), int(design["evaluation_seed"]),
        x_train, x_selection, y_train, y_selection, candidates, args.n_jobs,
    )
    evaluation.to_csv(out / "evaluation_model_metrics.csv", index=False)
    eval_audit = validate_bank(evaluation, int(design["evaluation_repetitions"]), candidates, "evaluation")

    audit = {
        "study_id": config["study_id"],
        "data_sha256": manifest["canonical_sha256"],
        "reference": ref_audit,
        "evaluation": eval_audit,
        "failed_fits_by_model_reference": reference.groupby("model")["fit_failed"].sum().astype(int).to_dict(),
        "failed_fits_by_model_evaluation": evaluation.groupby("model")["fit_failed"].sum().astype(int).to_dict(),
    }
    (out / "model_bank_audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("SUPPORT2 model banks complete")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
