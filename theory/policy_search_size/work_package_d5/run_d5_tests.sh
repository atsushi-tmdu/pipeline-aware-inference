#!/usr/bin/env bash
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

PYTHON="${PYTHON:-${PY:-python3}}"

"$PYTHON" -m unittest discover \
  -s theory/policy_search_size/work_package_d5/tests \
  -p 'test_*.py' \
  -v

git diff --check -- theory/policy_search_size/work_package_d5
