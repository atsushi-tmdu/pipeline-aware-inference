#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

CONFIG="configs/ess/reference_bank_uncertainty_v1.json"
OUTPUT_DIR="simulations/ess/outputs/reference_bank_uncertainty_v1"
PREFLIGHT_MANIFEST="$OUTPUT_DIR/preflight_manifest.json"
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
    echo "ERROR: confirmatory raw run was not found in the repository and archive is absent:" >&2
    echo "  $ARCHIVE" >&2
    echo "Set TESS_CONFIRMATORY_MIXED_RUN_DIR or TESS_CONFIRMATORY_ARCHIVE." >&2
    exit 1
  fi

  if [[ -f "${ARCHIVE}.sha256" ]]; then
    echo "Verifying confirmatory archive checksum..." >&2
    expected_hash="$(awk 'NR==1 {print $1}' "${ARCHIVE}.sha256")"
    actual_hash="$(shasum -a 256 "$ARCHIVE" | awk '{print $1}')"
    if [[ "$actual_hash" != "$expected_hash" ]]; then
      echo "ERROR: confirmatory archive SHA-256 mismatch." >&2
      exit 1
    fi
    echo "Archive SHA-256: OK" >&2
  fi

  mkdir -p "$EXTRACT_ROOT"
  if ! find "$EXTRACT_ROOT" -type f -name candidate_library_manifest.csv \
      -path '*mixed_realistic_20*' -print -quit | grep -q .; then
    echo "Extracting frozen confirmatory archive outside the Git repository..." >&2
    tar -xzf "$ARCHIVE" -C "$EXTRACT_ROOT"
  fi

  local extracted
  extracted="$(find "$EXTRACT_ROOT" -type f -name candidate_library_manifest.csv \
    -path '*mixed_realistic_20*' | sort | tail -n 1 || true)"
  if [[ -z "$extracted" ]]; then
    echo "ERROR: mixed-realistic confirmatory run not found after extraction." >&2
    exit 1
  fi
  dirname "$extracted"
}

RUN_DIR="$(resolve_run_dir)"
for required in candidate_library_manifest.csv null_reference_model_metrics.csv evaluation_model_metrics.csv; do
  if [[ ! -f "$RUN_DIR/$required" ]]; then
    echo "ERROR: missing $RUN_DIR/$required" >&2
    exit 1
  fi
done

echo "Mixed-realistic confirmatory run:"
echo "  $RUN_DIR"

if [[ -f "$OUTPUT_DIR/REFERENCE_BANK_UNCERTAINTY_SENSITIVITY.md" ]]; then
  echo "ERROR: completed sensitivity output already exists: $OUTPUT_DIR" >&2
  exit 1
fi

# A failure before the first checkpoint can leave only the preflight manifest.
# Remove that non-scientific partial directory so the clean-tree preflight can
# be repeated. Checkpointed runs are never deleted and are resumed below.
if [[ -f "$PREFLIGHT_MANIFEST" && ! -f "$OUTPUT_DIR/.reference_bank_uncertainty_checkpoint.npz" ]]; then
  echo "Removing incomplete pre-checkpoint output: $OUTPUT_DIR"
  rm -rf "$OUTPUT_DIR"
fi

if [[ -f "$OUTPUT_DIR/.reference_bank_uncertainty_checkpoint.npz" ]]; then
  echo "Resuming an interrupted two-bank bootstrap..."
  python3 -m simulations.ess.reference_bank_uncertainty_v1 \
    --repo-root . \
    --run-dir "$RUN_DIR" \
    --config "$CONFIG" \
    --output-dir "$OUTPUT_DIR" \
    --resume
else
  python3 -m simulations.ess.reference_bank_uncertainty_preflight_v1 \
    --repo-root . \
    --config "$CONFIG" \
    --run-dir "$RUN_DIR" \
    --manifest "$PREFLIGHT_MANIFEST"

  python3 -m simulations.ess.reference_bank_uncertainty_v1 \
    --repo-root . \
    --run-dir "$RUN_DIR" \
    --config "$CONFIG" \
    --output-dir "$OUTPUT_DIR"
fi

echo
echo "Reference-bank uncertainty sensitivity complete."
echo "Review:"
echo "  $OUTPUT_DIR/REFERENCE_BANK_UNCERTAINTY_SENSITIVITY.md"
echo
echo "Then stage the processed outputs only:"
echo "  git add $OUTPUT_DIR"
