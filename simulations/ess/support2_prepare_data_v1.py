#!/usr/bin/env python3
"""Download/canonicalize SUPPORT2 and write a versioned data manifest."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

PRIMARY_URL = "https://hbiostat.org/data/repo/support2csv.zip"
REQUIRED = [
    "age", "num.co", "scoma", "meanbp", "wblc", "hrt", "resp", "temp",
    "pafi", "alb", "bili", "crea", "sod", "ph", "glucose", "bun", "urine",
    "sex", "dzgroup", "ca", "diabetes", "dementia", "hospdead",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_hbiostat_zip(raw: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))]
        if not csv_names:
            raise ValueError("No CSV/TXT file found in SUPPORT2 archive")
        name = sorted(csv_names, key=lambda x: (not x.lower().endswith('.csv'), len(x)))[0]
        with zf.open(name) as f:
            return pd.read_csv(f)


def download_hbiostat() -> tuple[pd.DataFrame, str, bytes]:
    req = urllib.request.Request(PRIMARY_URL, headers={"User-Agent": "TESS-SUPPORT2-validation/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read()
    return read_hbiostat_zip(raw), "hbiostat_support2csv_zip", raw


def fetch_uci() -> tuple[pd.DataFrame, str, bytes | None]:
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:
        raise RuntimeError(
            "HBiostat download failed and ucimlrepo is unavailable. Install it "
            "with `python3 -m pip install ucimlrepo`, or pass --local-file."
        ) from exc
    data = fetch_ucirepo(id=880)
    parts = [data.data.features, data.data.targets]
    frame = pd.concat(parts, axis=1)
    frame = frame.loc[:, ~frame.columns.duplicated()].copy()
    return frame, "uci_fetch_ucirepo_880", None


def load_local(path: Path) -> tuple[pd.DataFrame, str, bytes | None]:
    if path.suffix.lower() == ".zip":
        raw = path.read_bytes()
        return read_hbiostat_zip(raw), f"local_zip:{path}", raw
    return pd.read_csv(path), f"local_csv:{path}", None


def normalize_outcome(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        result = pd.to_numeric(series, errors="coerce")
    else:
        text = series.astype(str).str.strip().str.lower()
        mapping = {
            "0": 0, "1": 1, "no": 0, "yes": 1, "false": 0, "true": 1,
            "alive": 0, "dead": 1,
        }
        result = text.map(mapping)
    if result.isna().any() or not set(result.unique()).issubset({0, 1}):
        raise ValueError("Could not normalize hospdead to complete binary 0/1 values")
    return result.astype(int)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/support2"))
    parser.add_argument("--local-file", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    canonical = out / "support2_analysis_v1.csv"
    manifest_path = out / "support2_data_manifest_v1.json"
    raw_path = out / "support2_source_archive_v1.zip"

    if (canonical.exists() or manifest_path.exists()) and not args.force:
        raise SystemExit(
            "Prepared SUPPORT2 files already exist. Use --force only before the "
            "scientific lock, never to replace data after results are seen."
        )

    raw = None
    if args.local_file:
        frame, source, raw = load_local(args.local_file.expanduser().resolve())
    else:
        try:
            frame, source, raw = download_hbiostat()
        except Exception as first_error:
            print(f"HBiostat retrieval failed: {type(first_error).__name__}: {first_error}")
            frame, source, raw = fetch_uci()

    frame.columns = [str(c).strip().lower() for c in frame.columns]
    drop = [c for c in frame.columns if c.startswith("unnamed:")]
    if drop:
        frame = frame.drop(columns=drop)

    missing = sorted(set(REQUIRED).difference(frame.columns))
    if missing:
        raise ValueError(f"SUPPORT2 source missing required columns: {missing}")
    if len(frame) != 9105:
        raise ValueError(f"Expected 9105 SUPPORT2 rows, found {len(frame)}")

    analysis = frame[REQUIRED].copy()
    analysis.insert(0, "support2_row_id", np.arange(len(analysis), dtype=int))
    analysis["hospdead"] = normalize_outcome(analysis["hospdead"])

    # Stable, explicit conversion: numeric columns numeric; categoricals textual.
    categorical = ["sex", "dzgroup", "ca", "diabetes", "dementia"]
    for column in REQUIRED:
        if column == "hospdead":
            continue
        if column in categorical:
            analysis[column] = analysis[column].where(analysis[column].notna(), np.nan)
        else:
            analysis[column] = pd.to_numeric(analysis[column], errors="coerce")

    analysis.to_csv(canonical, index=False, na_rep="", float_format="%.17g")
    if raw is not None:
        raw_path.write_bytes(raw)

    missing_counts = {c: int(analysis[c].isna().sum()) for c in analysis.columns}
    manifest = {
        "dataset": "SUPPORT2",
        "source": source,
        "source_url": PRIMARY_URL,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "canonical_path": str(canonical),
        "canonical_sha256": sha256(canonical),
        "canonical_size_bytes": canonical.stat().st_size,
        "rows": int(len(analysis)),
        "columns": analysis.columns.tolist(),
        "outcome": "hospdead",
        "outcome_events": int(analysis["hospdead"].sum()),
        "outcome_prevalence": float(analysis["hospdead"].mean()),
        "missing_counts": missing_counts,
        "raw_archive_sha256": sha256(raw_path) if raw_path.exists() else None,
        "acknowledgment": "Data obtained from http://hbiostat.org/data courtesy of the Vanderbilt University Department of Biostatistics.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("SUPPORT2 preparation complete")
    print(f"Source: {source}")
    print(f"Rows: {manifest['rows']}")
    print(f"Outcome events: {manifest['outcome_events']} ({manifest['outcome_prevalence']:.4f})")
    print(f"Canonical SHA-256: {manifest['canonical_sha256']}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
