#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"

cd "$SCRIPT_DIR"
"$PYTHON_BIN" d6_validate.py \
  --config D6_NUMERICAL_CONFIG_SMOKE.json \
  --output-dir outputs/smoke_v1
