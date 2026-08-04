#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$SCRIPT_DIR"
"$PYTHON_BIN" -m unittest discover -s tests -p 'test_*.py' -v
