#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 -m unittest simulations.ess.tests.test_reference_bank_uncertainty_v1

ARCHIVE_DEFAULT="$HOME/Documents/pipeline-aware-confirmatory-archives/tess_confirmatory_policy_v1_seed20260817.tar.gz"
ARCHIVE="${TESS_CONFIRMATORY_ARCHIVE:-$ARCHIVE_DEFAULT}"
EXTRACT_ROOT="${TESS_CONFIRMATORY_EXTRACT_ROOT:-$HOME/Documents/pipeline-aware-confirmatory-archives/tess_confirmatory_policy_v1_seed20260817_extracted}"

resolve_run_dir() {
  if [[ -n "${TESS_CONFIRMATORY_MIXED_RUN_DIR:-}" ]]; then
    printf '%s\n' "$TESS_CONFIRMATORY_MIXED_RUN_DIR"
    return
  fi
  local existing
  existing="$(find \
    "$REPO_ROOT/results_ess_confirmatory/policy_v1_seed20260817/mixed_realistic_20" \
    -maxdepth 2 -type f -name candidate_library_manifest.csv 2>/dev/null \
    | sort | tail -n 1 || true)"
  if [[ -n "$existing" ]]; then
    dirname "$existing"
    return
  fi
  if [[ ! -f "$ARCHIVE" ]]; then
    echo "ERROR: no raw run or archive found." >&2
    exit 1
  fi
  mkdir -p "$EXTRACT_ROOT"
  if ! find "$EXTRACT_ROOT" -type f -name candidate_library_manifest.csv \
      -path '*mixed_realistic_20*' -print -quit | grep -q .; then
    tar -xzf "$ARCHIVE" -C "$EXTRACT_ROOT"
  fi
  local extracted
  extracted="$(find "$EXTRACT_ROOT" -type f -name candidate_library_manifest.csv \
    -path '*mixed_realistic_20*' | sort | tail -n 1 || true)"
  [[ -n "$extracted" ]] || { echo "ERROR: mixed run not found." >&2; exit 1; }
  dirname "$extracted"
}

RUN_DIR="$(resolve_run_dir)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tess_reference_bank_uncertainty_smoke.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

python3 -m simulations.ess.reference_bank_uncertainty_v1 \
  --repo-root . \
  --run-dir "$RUN_DIR" \
  --config configs/ess/reference_bank_uncertainty_v1_smoke.json \
  --output-dir "$TMP_DIR" \
  --no-checkpoint

python3 - "$TMP_DIR" <<'PY'
import json
import sys
from pathlib import Path
import pandas as pd

root = Path(sys.argv[1])
summary = json.loads((root / "reference_bank_uncertainty_summary.json").read_text())
replicates = pd.read_csv(root / "reference_bank_uncertainty_bootstrap_replicates.csv")
assert len(replicates) == 100
assert abs(summary["point_estimate_recomputed"] - 0.7949499185) <= 1e-8
assert summary["primary_adjudication_unchanged"] is True
print("Real-bank smoke verification: OK")
PY

echo "Reference-bank uncertainty smoke test: PASS"
