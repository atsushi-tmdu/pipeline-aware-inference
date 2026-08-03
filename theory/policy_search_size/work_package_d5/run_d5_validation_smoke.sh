#!/usr/bin/env bash
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

D5="theory/policy_search_size/work_package_d5"
PYTHON="${PYTHON:-${PY:-python3}}"

PYTHON="$PYTHON" bash "$D5/run_d5_tests.sh"

"$PYTHON" "$D5/d5_validate.py" \
  --config "$D5/D5_NUMERICAL_CONFIG_SMOKE.json"

echo
echo "D5 smoke complete."
echo "Review: $D5/outputs/smoke_v1/D5_VALIDATION_ADJUDICATION.md"
