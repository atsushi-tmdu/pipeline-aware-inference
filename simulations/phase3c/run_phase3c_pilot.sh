#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
CONFIG="${1:-$ROOT/configs/phase3c/phase3c_pilot.json}"
N_JOBS="${N_JOBS:-18}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$ROOT/results_phase3c/pilot}"

for LIBRARY in high_dependency_linear_20 mixed_realistic_20
do
  "$PYTHON_BIN" "$ROOT/simulations/phase3c/pipeline_candidate_count_phase3c.py" \
    --config "$CONFIG" \
    --library "$LIBRARY" \
    --n-jobs "$N_JOBS" \
    --output-root "$OUTPUT_ROOT"
done

"$PYTHON_BIN" "$ROOT/simulations/phase3c/summarize_phase3c.py" \
  --results-root "$OUTPUT_ROOT" \
  --output-root "$ROOT/results_phase3c/pilot_summary" \
  --bootstrap-repetitions 10000 \
  --go-threshold 0.05
