#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

"$PYTHON" "$HERE/build_d2_results_freeze.py"
"$PYTHON" "$HERE/verify_d2_results_freeze.py"

echo
echo "D2 results freeze completed successfully."
