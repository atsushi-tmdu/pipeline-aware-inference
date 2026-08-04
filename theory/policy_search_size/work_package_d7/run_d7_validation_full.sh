#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
OUTPUT_DIR="$SCRIPT_DIR/outputs/full_v1"

"$PYTHON_BIN" "$SCRIPT_DIR/verify_d7_theory_checkpoint.py"
"$PYTHON_BIN" "$SCRIPT_DIR/verify_d7_numerical_lock.py"

if [[ -e "$OUTPUT_DIR" ]]; then
  echo "FAIL: full output directory already exists: $OUTPUT_DIR" >&2
  exit 1
fi
mkdir -p "$OUTPUT_DIR"

cd "$SCRIPT_DIR"
"$PYTHON_BIN" d7_validation.py \
  --mode full \
  --output-dir "$OUTPUT_DIR"
