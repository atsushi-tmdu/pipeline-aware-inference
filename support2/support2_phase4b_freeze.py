#!/usr/bin/env python3
"""
Phase 4B: freeze the SUPPORT2 real-data example before fitting any model.

This script:
1. locates or reads the Phase 4A audit ZIP;
2. verifies the raw SUPPORT2 data;
3. freezes the prediction time, outcome, predictor sets, exclusions, and seed;
4. creates a prespecified 60/20/20 train/selection/untouched-test split;
5. writes split and missingness audits;
6. DOES NOT fit or evaluate any prediction model.

Primary analysis
----------------
Prediction time:
    SUPPORT study day 3 / study entry assessment window.

Outcome:
    hospdead (in-hospital death).

Primary predictor set:
    age, sex, dzgroup, num.co, scoma, hday, diabetes, dementia, ca,
    meanbp, wblc, hrt, resp, temp, pafi, alb, bili, crea, sod, ph,
    glucose, bun, urine.

Sensitivity predictor sets:
    primary_plus_socioeconomic:
        primary + race + edu + income
    primary_plus_adl:
        primary + adlsc

The split is stratified on the joint label hospdead × dzgroup using a fixed
random seed. The untouched test split must not be used for model selection,
threshold selection, preprocessing choices, or code debugging.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split


OUTCOME = "hospdead"
ID_COLUMN = "id"
SEED = 20260719

PRIMARY_PREDICTORS = [
    "age",
    "sex",
    "dzgroup",
    "num.co",
    "scoma",
    "hday",
    "diabetes",
    "dementia",
    "ca",
    "meanbp",
    "wblc",
    "hrt",
    "resp",
    "temp",
    "pafi",
    "alb",
    "bili",
    "crea",
    "sod",
    "ph",
    "glucose",
    "bun",
    "urine",
]

SOCIOECONOMIC_SENSITIVITY = ["race", "edu", "income"]
ADL_SENSITIVITY = ["adlsc"]

CATEGORICAL_PRIMARY = [
    "sex",
    "dzgroup",
    "ca",
]

BINARY_PRIMARY = [
    "diabetes",
    "dementia",
]

NUMERIC_PRIMARY = [
    x
    for x in PRIMARY_PREDICTORS
    if x not in CATEGORICAL_PRIMARY + BINARY_PRIMARY
]

EXCLUSIONS = {
    "id": "Identifier; retained only for split tracking.",
    "death": "Death at any time; not the prespecified in-hospital outcome.",
    "slos": "Post-prediction length from study entry to discharge.",
    "d.time": "Post-prediction follow-up time.",
    "charges": "Post-prediction resource use.",
    "totcst": "Post-prediction resource use.",
    "totmcst": "Post-prediction resource use.",
    "avtisst": "Treatment-intensity score averaged over days 3-25; future information.",
    "sps": "Existing SUPPORT prognostic physiology score.",
    "aps": "Existing APACHE III physiology score.",
    "surv2m": "Existing model-derived survival probability.",
    "surv6m": "Existing model-derived survival probability.",
    "prg2m": "Physician prognostic estimate; prognosis-feedback variable.",
    "prg6m": "Physician prognostic estimate; prognosis-feedback variable.",
    "dnr": "Treatment-decision variable with prognosis feedback.",
    "dnrday": "DNR timing; may contain post-prediction information.",
    "sfdm2": "Two-month functional outcome.",
    "dzclass": "Coarser deterministic grouping of dzgroup; excluded to avoid duplication.",
    "adlp": "Highly missing patient ADL; excluded from primary analysis.",
    "adls": "Highly missing surrogate ADL; excluded from primary analysis.",
    "adlsc": "Precomputed/imputed ADL summary; sensitivity analysis only.",
    "race": "Sensitive attribute; socioeconomic/fairness sensitivity analysis only.",
    "edu": "Socioeconomic attribute; sensitivity analysis only.",
    "income": "Socioeconomic attribute; sensitivity analysis only.",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the SUPPORT2 Phase 4 real-data analysis design."
    )
    parser.add_argument(
        "--audit-zip",
        default=None,
        help=(
            "Path to support2_phase4a_audit_*.zip. If omitted, the newest ZIP "
            "under --search-root is used."
        ),
    )
    parser.add_argument(
        "--search-root",
        default="results_support2_phase4a",
        help="Directory searched recursively when --audit-zip is omitted.",
    )
    parser.add_argument(
        "--output-root",
        default="results_support2_phase4b",
        help="Parent directory for timestamped output.",
    )
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_audit_zip(args: argparse.Namespace) -> Path:
    if args.audit_zip:
        path = Path(args.audit_zip).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Audit ZIP not found: {path}")
        return path

    root = Path(args.search_root).expanduser().resolve()
    candidates = sorted(
        root.rglob("support2_phase4a_audit_*.zip"),
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No support2_phase4a_audit_*.zip found under {root}"
        )
    return candidates[-1]


def read_member_from_zip(
    archive: zipfile.ZipFile,
    suffix: str,
) -> tuple[str, bytes]:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one ZIP member ending in {suffix!r}; found {matches}"
        )
    name = matches[0]
    return name, archive.read(name)


def validate_dataset(df: pd.DataFrame) -> None:
    required = set(
        [ID_COLUMN, OUTCOME]
        + PRIMARY_PREDICTORS
        + SOCIOECONOMIC_SENSITIVITY
        + ADL_SENSITIVITY
    )
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"Required columns are missing: {missing}")

    if len(df) != 9105:
        raise RuntimeError(f"Expected 9,105 rows; found {len(df):,}")

    if df[ID_COLUMN].isna().any():
        raise RuntimeError("ID contains missing values.")
    if df[ID_COLUMN].duplicated().any():
        raise RuntimeError("ID is not unique.")

    outcome_values = sorted(df[OUTCOME].dropna().unique().tolist())
    if outcome_values != [0, 1]:
        raise RuntimeError(
            f"{OUTCOME} must contain only 0 and 1; observed {outcome_values}"
        )
    if df[OUTCOME].isna().any():
        raise RuntimeError(f"{OUTCOME} contains missing values.")


def joint_strata(df: pd.DataFrame) -> pd.Series:
    strata = (
        df[OUTCOME].astype(int).astype(str)
        + "__"
        + df["dzgroup"].astype("string").fillna("MISSING")
    )
    counts = strata.value_counts()
    if (counts < 5).any():
        small = counts[counts < 5]
        raise RuntimeError(
            "Joint outcome × dzgroup strata are too small:\n"
            + small.to_string()
        )
    return strata


def make_split(df: pd.DataFrame, seed: int) -> pd.Series:
    strata = joint_strata(df)

    train_index, temp_index = train_test_split(
        df.index.to_numpy(),
        test_size=0.40,
        random_state=seed,
        shuffle=True,
        stratify=strata,
    )

    temp = df.loc[temp_index]
    temp_strata = joint_strata(temp)

    selection_index, test_index = train_test_split(
        temp.index.to_numpy(),
        test_size=0.50,
        random_state=seed + 1,
        shuffle=True,
        stratify=temp_strata,
    )

    split = pd.Series(index=df.index, dtype="string")
    split.loc[train_index] = "train"
    split.loc[selection_index] = "selection"
    split.loc[test_index] = "test"

    if split.isna().any():
        raise RuntimeError("Some observations were not assigned to a split.")
    if split.value_counts().to_dict() != {
        "train": 5463,
        "selection": 1821,
        "test": 1821,
    }:
        raise RuntimeError(
            "Unexpected split sizes: " + str(split.value_counts().to_dict())
        )
    return split


def split_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for split_name, group in df.groupby("split", sort=False):
        rows.append(
            {
                "split": split_name,
                "n": int(len(group)),
                "events": int(group[OUTCOME].sum()),
                "non_events": int(len(group) - group[OUTCOME].sum()),
                "event_fraction": float(group[OUTCOME].mean()),
                "n_disease_groups": int(group["dzgroup"].nunique(dropna=False)),
            }
        )
    return pd.DataFrame(rows)


def disease_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["split", "dzgroup"], dropna=False)
        .agg(
            n=(OUTCOME, "size"),
            events=(OUTCOME, "sum"),
            event_fraction=(OUTCOME, "mean"),
        )
        .reset_index()
    )
    summary["non_events"] = summary["n"] - summary["events"]
    return summary


def missingness_summary(
    df: pd.DataFrame,
    variables: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for split_name, group in df.groupby("split", sort=False):
        for variable in variables:
            rows.append(
                {
                    "split": split_name,
                    "variable": variable,
                    "n": int(len(group)),
                    "n_missing": int(group[variable].isna().sum()),
                    "missing_fraction": float(group[variable].isna().mean()),
                    "n_unique_including_na": int(
                        group[variable].nunique(dropna=False)
                    ),
                }
            )
    return pd.DataFrame(rows)


def predictor_manifest() -> pd.DataFrame:
    rows: list[dict[str, str]] = []

    for variable in PRIMARY_PREDICTORS:
        if variable in CATEGORICAL_PRIMARY:
            data_class = "categorical"
        elif variable in BINARY_PRIMARY:
            data_class = "binary"
        else:
            data_class = "numeric"
        rows.append(
            {
                "variable": variable,
                "status": "primary",
                "data_class": data_class,
                "reason": "Available by the prespecified day-3 prediction time.",
            }
        )

    for variable in SOCIOECONOMIC_SENSITIVITY:
        rows.append(
            {
                "variable": variable,
                "status": "sensitivity_socioeconomic",
                "data_class": (
                    "categorical" if variable in ["race", "income"] else "numeric"
                ),
                "reason": (
                    "Sensitive/socioeconomic attribute; excluded from primary "
                    "analysis and added only in sensitivity analysis."
                ),
            }
        )

    for variable in ADL_SENSITIVITY:
        rows.append(
            {
                "variable": variable,
                "status": "sensitivity_adl",
                "data_class": "numeric",
                "reason": (
                    "Precomputed/imputed ADL summary; excluded from primary "
                    "analysis and added only in sensitivity analysis."
                ),
            }
        )

    for variable, reason in EXCLUSIONS.items():
        if variable in PRIMARY_PREDICTORS:
            continue
        rows.append(
            {
                "variable": variable,
                "status": "exclude",
                "data_class": "",
                "reason": reason,
            }
        )

    rows.append(
        {
            "variable": OUTCOME,
            "status": "outcome",
            "data_class": "binary",
            "reason": "Primary outcome: in-hospital death.",
        }
    )
    return pd.DataFrame(rows).drop_duplicates("variable", keep="first")


def write_protocol(path: Path, audit_zip: Path, seed: int) -> None:
    text = f"""# SUPPORT2 Phase 4B frozen analysis protocol

## Purpose

This is a methodological real-data illustration of pipeline-aware null
calibration after model search. It is not intended to create a new clinical
prediction model for contemporary practice.

## Data

- Dataset: SUPPORT2
- Observations: 9,105
- Outcome: `hospdead`
- Hospital deaths in the complete dataset: 2,360
- Phase 4A source ZIP: `{audit_zip}`
- Split seed: `{seed}`

## Prediction time

The prediction time is the SUPPORT day-3/study-entry assessment window.
Only variables available by this time are eligible for the primary analysis.

## Primary predictors

{", ".join(PRIMARY_PREDICTORS)}

`dzgroup` is retained and the coarser redundant variable `dzclass` is excluded.

`scoma` is included because it is a day-3 neurological clinical summary, not
an existing fitted mortality/survival probability.

## Sensitivity predictor sets

1. Primary plus socioeconomic/sensitive attributes:
   `{", ".join(SOCIOECONOMIC_SENSITIVITY)}`

2. Primary plus precomputed ADL summary:
   `{", ".join(ADL_SENSITIVITY)}`

## Data split

A fixed 60%/20%/20% split is generated using stratification on the joint
label `hospdead × dzgroup`.

- Training: model fitting and all preprocessing estimation
- Selection: choosing the best candidate model and metric-specific winner
- Test: completely untouched until the final locked evaluation

The test set must not be used for model selection, preprocessing decisions,
debugging, threshold selection, or changes to the analysis plan.

## Planned preprocessing for Phase 4C

Preprocessing will be learned using the training set only.

- Numeric variables: median imputation plus missingness indicators
- Categorical variables: most-frequent imputation and one-hot encoding
- Scaling: applied inside models requiring scaling
- Unknown categories: ignored at transformation time

All preprocessing, feature handling, model fitting, and model selection will
be repeated inside every null-bank replication.

## Planned candidate library

The primary real-data illustration will use the seven heterogeneous core
models from Phase 3:

- Logistic regression
- Linear SVM
- RBF-SVM
- Gaussian naive Bayes
- Decision tree
- Random forest
- Histogram gradient boosting

## Planned metrics

- Primary: AUROC
- Secondary: average precision and partial AUROC at FPR <= 0.10

## Null calibration

The split is fixed. Within each null replication, outcome labels will be
permuted separately within the training and selection sets, thereby preserving
their event counts. The complete preprocessing, fitting, and winner-selection
pipeline will then be repeated.

The untouched test labels are not used to construct the null reference bank.
"""
    path.write_text(text, encoding="utf-8")


def zip_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory.parent))
    return zip_path


def main() -> None:
    args = parse_args()
    audit_zip = find_audit_zip(args)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"support2_phase4b_frozen_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(audit_zip) as archive:
        raw_member, raw_bytes = read_member_from_zip(
            archive, "support2_raw.csv"
        )
        integrity_member, integrity_bytes = read_member_from_zip(
            archive, "integrity_summary.json"
        )

    with tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False
    ) as temp_file:
        temp_file.write(raw_bytes)
        temp_path = Path(temp_file.name)

    try:
        df = pd.read_csv(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)

    validate_dataset(df)
    split = make_split(df, args.seed)
    df = df.copy()
    df["split"] = split

    primary_columns = [
        ID_COLUMN,
        "split",
        OUTCOME,
        *PRIMARY_PREDICTORS,
    ]
    primary_data = df[primary_columns].copy()

    split_assignments = df[
        [ID_COLUMN, "split", OUTCOME, "dzgroup"]
    ].copy()

    split_assignments.to_csv(
        output_dir / "split_assignments.csv", index=False
    )
    primary_data.to_csv(
        output_dir / "analysis_dataset_primary.csv", index=False
    )
    split_summary(df).to_csv(
        output_dir / "split_summary.csv", index=False
    )
    disease_summary(df).to_csv(
        output_dir / "split_by_disease_group.csv", index=False
    )

    all_audited_predictors = (
        PRIMARY_PREDICTORS
        + SOCIOECONOMIC_SENSITIVITY
        + ADL_SENSITIVITY
    )
    missingness_summary(df, all_audited_predictors).to_csv(
        output_dir / "missingness_by_split.csv", index=False
    )
    predictor_manifest().to_csv(
        output_dir / "predictor_manifest.csv", index=False
    )

    plan = {
        "phase": "4B",
        "frozen": True,
        "dataset": "SUPPORT2",
        "prediction_time": "SUPPORT day-3/study-entry assessment window",
        "outcome": OUTCOME,
        "seed": int(args.seed),
        "split_fractions": {
            "train": 0.60,
            "selection": 0.20,
            "test": 0.20,
        },
        "split_stratification": "joint hospdead x dzgroup",
        "primary_predictors": PRIMARY_PREDICTORS,
        "primary_numeric": NUMERIC_PRIMARY,
        "primary_binary": BINARY_PRIMARY,
        "primary_categorical": CATEGORICAL_PRIMARY,
        "sensitivity_socioeconomic": SOCIOECONOMIC_SENSITIVITY,
        "sensitivity_adl": ADL_SENSITIVITY,
        "primary_metric": "roc_auc",
        "secondary_metrics": [
            "average_precision",
            "pauc_fpr_0_10",
        ],
        "candidate_library": [
            "logistic_regression",
            "linear_svm",
            "rbf_svm",
            "gaussian_nb",
            "decision_tree",
            "random_forest",
            "hist_gradient_boosting",
        ],
        "null_permutation": (
            "permute outcome separately within fixed training and selection "
            "splits; repeat all preprocessing, fitting, and winner selection"
        ),
        "test_set_rule": (
            "untouched until the complete pipeline and inference method are locked"
        ),
        "source_audit_zip": str(audit_zip),
        "source_audit_zip_sha256": sha256_file(audit_zip),
        "source_raw_member": raw_member,
        "source_raw_csv_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_integrity_member": integrity_member,
    }
    (output_dir / "analysis_plan.json").write_text(
        json.dumps(plan, indent=2),
        encoding="utf-8",
    )

    write_protocol(
        output_dir / "FROZEN_PROTOCOL.md",
        audit_zip,
        args.seed,
    )

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
    }
    (output_dir / "environment.json").write_text(
        json.dumps(environment, indent=2),
        encoding="utf-8",
    )

    summary = split_summary(df)
    lines = [
        "SUPPORT2 PHASE 4B: FROZEN DESIGN",
        "=" * 39,
        f"Source audit ZIP: {audit_zip}",
        f"Rows: {len(df):,}",
        f"Hospital deaths: {int(df[OUTCOME].sum()):,} "
        f"({df[OUTCOME].mean():.3%})",
        f"Primary predictors: {len(PRIMARY_PREDICTORS)}",
        f"Seed: {args.seed}",
        "",
        "SPLIT SUMMARY",
        "-------------",
        summary.to_string(index=False),
        "",
        "NO PREDICTION MODEL WAS FIT.",
        "The untouched test split is now frozen.",
    ]
    (output_dir / "summary.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    (output_dir / "run_complete.json").write_text(
        json.dumps(
            {
                "completed": True,
                "models_fitted": False,
                "output_directory": str(output_dir),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    zip_path = zip_directory(output_dir)
    print((output_dir / "summary.txt").read_text())
    print("")
    print("Upload this ZIP next:")
    print(zip_path)


if __name__ == "__main__":
    main()
