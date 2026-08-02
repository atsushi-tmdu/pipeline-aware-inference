#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

"$PYTHON" "$HERE/build_d1_results_freeze.py"
"$PYTHON" "$HERE/verify_d1_results_freeze.py"

echo
echo "D1 results freeze completed successfully."
