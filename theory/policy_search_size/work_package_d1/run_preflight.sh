#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

cd "$ROOT"
"$PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
"$PYTHON" D1_RUNTIME_PREFLIGHT.py "$@"
