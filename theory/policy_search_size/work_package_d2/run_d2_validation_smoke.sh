#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
OUT="$ROOT/outputs/smoke_v1"
rm -rf "$OUT"
mkdir -p "$OUT"
cd "$ROOT"
"$PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
"$PYTHON" d2_validate.py --config D2_NUMERICAL_CONFIG_SMOKE.json --outdir "$OUT"
echo
echo "SMOKE TEST COMPLETE - NOT SCIENTIFIC EVIDENCE"
echo "Output: $OUT"
