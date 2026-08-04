#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
OUTPUT_DIR="$SCRIPT_DIR/outputs/smoke_v1"

"$PYTHON_BIN" "$SCRIPT_DIR/verify_d7_theory_checkpoint.py"
"$PYTHON_BIN" "$SCRIPT_DIR/verify_d7_numerical_lock.py"

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

cd "$SCRIPT_DIR"
"$PYTHON_BIN" d7_validation.py \
  --mode smoke \
  --output-dir "$OUTPUT_DIR"
