#!/usr/bin/env bash
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

D5="theory/policy_search_size/work_package_d5"
PYTHON="${PYTHON:-${PY:-python3}}"

if [[ ! -f "$D5/verify_d5_lock_manifest.py" ]]; then
  echo "FAIL: D5 lock verifier is absent. Lock D5 before a scientific run."
  exit 1
fi

"$PYTHON" "$D5/verify_d5_lock_manifest.py" --require-tag
PYTHON="$PYTHON" bash "$D5/run_d5_tests.sh"

"$PYTHON" "$D5/d5_validate.py" \
  --scientific \
  --config "$D5/D5_NUMERICAL_CONFIG.json"
