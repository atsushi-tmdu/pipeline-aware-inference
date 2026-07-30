#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG="${1:-$ROOT/configs/phase3c/phase3c_full.json}"
N_JOBS="${N_JOBS:-6}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$ROOT/results_phase3c/full}"
SUMMARY_ROOT="${SUMMARY_ROOT:-$ROOT/results_phase3c/full_summary}"

cd "$ROOT"
mkdir -p "$OUTPUT_ROOT" "$SUMMARY_ROOT"

for library in high_dependency_linear_20 mixed_realistic_20; do
  echo "============================================================"
  echo "Phase 3C full: $library"
  echo "============================================================"
  python simulations/phase3c/pipeline_candidate_count_phase3c.py \
    --config "$CONFIG" \
    --library "$library" \
    --n-jobs "$N_JOBS" \
    --output-root "$OUTPUT_ROOT"
done

python simulations/phase3c/summarize_phase3c.py \
  --results-root "$OUTPUT_ROOT" \
  --output-root "$SUMMARY_ROOT" \
  --bootstrap-repetitions 50000 \
  --go-threshold 0.05
