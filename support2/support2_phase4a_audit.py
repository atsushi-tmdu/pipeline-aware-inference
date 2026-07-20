#!/usr/bin/env python3
"""Phase 4A: download and audit the UCI SUPPORT2 dataset.

This script does not fit any prediction model. It creates a frozen audit package
for deciding the outcome, prediction time, predictor whitelist, missing-data
strategy, and data split before seeing model performance.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from ucimlrepo import fetch_ucirepo
except ModuleNotFoundError as exc:
    raise SystemExit(
        "ucimlrepo is not installed. Run:\n"
        "  python -m pip install --upgrade ucimlrepo pandas numpy\n"
        "and then rerun this script."
    ) from exc


DEFINITE_EXCLUSIONS: dict[str, str] = {
    "id": "Identifier; not a predictor.",
    "death": "Outcome/follow-up information beyond the hospital-death target.",
    "slos": "Days from study entry to discharge; post-prediction outcome information.",
    "d.time": "Follow-up time; post-prediction outcome information.",
    "charges": "Hospital resource use accumulated after prediction time.",
    "totcst": "Hospital resource use accumulated after prediction time.",
    "totmcst": "Hospital resource use accumulated after prediction time.",
    "avtisst": "Average treatment-intensity score over days 3-25; future information.",
    "sps": "Existing SUPPORT prognostic physiology score.",
    "aps": "Existing APACHE III physiology score.",
    "surv2m": "Existing model-derived survival prediction.",
    "surv6m": "Existing model-derived survival prediction.",
    "prg2m": "Physician prognostic estimate; excluded from the primary clinical-data model.",
    "prg6m": "Physician prognostic estimate; excluded from the primary clinical-data model.",
    "dnr": "Treatment-decision variable with strong indication/prognosis feedback.",
    "dnrday": "Treatment-decision timing variable; may contain future information.",
    "sfdm2": "Two-month functional outcome; occurs after prediction time.",
}

REVIEW_VARIABLES: dict[str, str] = {
    "adls": "Confirm that this ADL measure is available by the intended prediction time.",
    "adlsc": "Confirm timing and derivation of this ADL summary.",
    "scoma": "Derived day-3 coma score; decide whether derived clinical scores are allowed.",
    "race": "Sensitive attribute; consider primary exclusion or fairness sensitivity analysis.",
    "income": "Sensitive socioeconomic attribute; consider sensitivity analysis.",
    "edu": "Socioeconomic attribute; consider sensitivity analysis.",
}

PHASE_PATTERNS = ("phase", "study", "period", "year", "date", "site", "center", "centre", "hospital")


def json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    if isinstance(value, (pd.DataFrame, pd.Series)):
        return value.to_dict()
    return str(value)


def reconstruct_dataframe(dataset: Any) -> pd.DataFrame:
    original = getattr(dataset.data, "original", None)
    if isinstance(original, pd.DataFrame) and not original.empty:
        df = original.copy()
    else:
        parts: list[pd.DataFrame] = []
        for name in ("ids", "features", "targets"):
            part = getattr(dataset.data, name, None)
            if isinstance(part, pd.Series):
                part = part.to_frame()
            if isinstance(part, pd.DataFrame) and not part.empty:
                parts.append(part.reset_index(drop=True))
        if not parts:
            raise RuntimeError("Could not reconstruct a dataframe from ucimlrepo output.")
        df = pd.concat(parts, axis=1)

    df.columns = [str(column).strip() for column in df.columns]
    df = df.loc[:, ~df.columns.duplicated()].copy()
    return df


def classify_column(name: str) -> tuple[str, str]:
    if name == "hospdead":
        return "outcome", "Primary binary outcome: in-hospital death."
    if name in DEFINITE_EXCLUSIONS:
        return "exclude", DEFINITE_EXCLUSIONS[name]
    if name in REVIEW_VARIABLES:
        return "review", REVIEW_VARIABLES[name]
    return "candidate", "Provisional candidate; final inclusion requires timing/definition review."


def make_zip(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(directory.parent))
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and audit UCI SUPPORT2.")
    parser.add_argument(
        "--output-root",
        default="results_support2_phase4a",
        help="Parent directory for timestamped output.",
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = Path(args.output_root).expanduser().resolve()
    output_dir = output_root / f"support2_phase4a_audit_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading UCI SUPPORT2 (dataset id=880)...")
    dataset = fetch_ucirepo(id=880)
    df = reconstruct_dataframe(dataset)

    if "hospdead" not in df.columns:
        raise RuntimeError(
            "The downloaded dataframe does not contain 'hospdead'. Columns were:\n"
            + ", ".join(df.columns)
        )

    # Save raw and metadata before making any analytic decision.
    df.to_csv(output_dir / "support2_raw.csv", index=False)

    variables = getattr(dataset, "variables", None)
    if isinstance(variables, pd.DataFrame):
        variables.to_csv(output_dir / "uci_variable_metadata.csv", index=False)

    metadata = getattr(dataset, "metadata", None)
    (output_dir / "uci_dataset_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=json_default), encoding="utf-8"
    )

    # Basic integrity audit.
    y_numeric = pd.to_numeric(df["hospdead"], errors="coerce")
    outcome_counts = (
        y_numeric.value_counts(dropna=False)
        .rename_axis("hospdead")
        .rename("count")
        .reset_index()
    )
    outcome_counts["proportion"] = outcome_counts["count"] / len(df)
    outcome_counts.to_csv(output_dir / "outcome_summary.csv", index=False)

    missingness = pd.DataFrame(
        {
            "variable": df.columns,
            "dtype": [str(df[column].dtype) for column in df.columns],
            "n_missing": [int(df[column].isna().sum()) for column in df.columns],
            "missing_fraction": [float(df[column].isna().mean()) for column in df.columns],
            "n_unique_including_na": [int(df[column].nunique(dropna=False)) for column in df.columns],
        }
    ).sort_values(["missing_fraction", "variable"], ascending=[False, True])
    missingness.to_csv(output_dir / "missingness_and_types.csv", index=False)

    audit_rows: list[dict[str, Any]] = []
    for column in df.columns:
        status, reason = classify_column(column)
        audit_rows.append(
            {
                "variable": column,
                "provisional_status": status,
                "reason": reason,
                "dtype": str(df[column].dtype),
                "n_missing": int(df[column].isna().sum()),
                "missing_fraction": float(df[column].isna().mean()),
                "n_unique_including_na": int(df[column].nunique(dropna=False)),
            }
        )
    predictor_audit = pd.DataFrame(audit_rows)
    predictor_audit.to_csv(output_dir / "provisional_predictor_audit.csv", index=False)

    phase_like = [
        column
        for column in df.columns
        if any(pattern in column.lower() for pattern in PHASE_PATTERNS)
    ]
    (output_dir / "phase_split_audit.txt").write_text(
        "Columns whose names might encode phase/site/time:\n"
        + ("\n".join(phase_like) if phase_like else "NONE FOUND")
        + "\n\n"
        + "Do not infer Phase I/II membership from row order unless an authoritative "
          "source confirms that order. If no phase variable exists, use a prespecified "
          "stratified train/selection/test split.\n",
        encoding="utf-8",
    )

    duplicate_id_count = None
    if "id" in df.columns:
        duplicate_id_count = int(df["id"].duplicated().sum())

    integrity = {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "hospdead_missing": int(y_numeric.isna().sum()),
        "hospdead_unique_nonmissing": sorted(y_numeric.dropna().unique().tolist()),
        "hospdead_event_count": int((y_numeric == 1).sum()),
        "hospdead_event_fraction": float((y_numeric == 1).mean()),
        "duplicate_full_rows": int(df.duplicated().sum()),
        "duplicate_id_count": duplicate_id_count,
        "phase_like_columns": phase_like,
    }
    (output_dir / "integrity_summary.json").write_text(
        json.dumps(integrity, indent=2, default=json_default), encoding="utf-8"
    )

    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
    }
    (output_dir / "environment.json").write_text(
        json.dumps(environment, indent=2), encoding="utf-8"
    )

    candidate_count = int((predictor_audit["provisional_status"] == "candidate").sum())
    review_count = int((predictor_audit["provisional_status"] == "review").sum())
    exclude_count = int((predictor_audit["provisional_status"] == "exclude").sum())

    summary_lines = [
        "PHASE 4A: SUPPORT2 DATA AUDIT",
        "=" * 36,
        f"Rows: {len(df):,}",
        f"Columns: {df.shape[1]}",
        f"Hospital deaths: {integrity['hospdead_event_count']:,} "
        f"({integrity['hospdead_event_fraction']:.3%})",
        f"Missing hospdead values: {integrity['hospdead_missing']}",
        f"Duplicate full rows: {integrity['duplicate_full_rows']}",
        f"Duplicate IDs: {duplicate_id_count}",
        "",
        "PROVISIONAL VARIABLE STATUS",
        "-" * 28,
        f"Candidate: {candidate_count}",
        f"Review: {review_count}",
        f"Exclude: {exclude_count}",
        "Outcome: 1",
        "",
        "PHASE/SITE/TIME COLUMNS",
        "-" * 23,
        *(phase_like if phase_like else ["No obvious phase/site/time column was found."]),
        "",
        "NEXT DECISION",
        "-" * 13,
        "Review provisional_predictor_audit.csv and phase_split_audit.txt before modeling.",
        "Do not fit models yet.",
    ]
    (output_dir / "summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    zip_path = make_zip(output_dir)
    print("\n".join(summary_lines))
    print("\nCompleted.")
    print(f"Upload this ZIP next: {zip_path}")


if __name__ == "__main__":
    main()
