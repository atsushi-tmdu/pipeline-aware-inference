#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

echo "Using Python: $("$PYTHON" --version 2>&1)"
echo

"$PYTHON" "$ROOT/work_package_a/verify.py"
echo
"$PYTHON" "$ROOT/work_package_b/verify.py"
echo
"$PYTHON" "$ROOT/make_manifest.py"

echo
echo "All policy-search-size theory reproductions passed."
