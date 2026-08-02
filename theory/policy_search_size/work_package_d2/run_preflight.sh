#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

cd "$HERE"
"$PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
"$PYTHON" D2_RUNTIME_PREFLIGHT.py
