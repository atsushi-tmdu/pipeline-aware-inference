#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

cd "$HERE"
"$PYTHON" -m unittest discover -s tests -v
"$PYTHON" D4_RUNTIME_PREFLIGHT.py
