#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

CONFIG="configs/ess/confirmatory_policy_v1_smoke.json"
ROOT="/tmp/tess_confirmatory_policy_v1_smoke"
N_JOBS="${ESS_N_JOBS:-8}"

rm -rf "$ROOT"
mkdir -p "$ROOT"

for library in high_dependency_linear_20 mixed_realistic_20; do
  python3 simulations/phase3c/pipeline_candidate_count_phase3c.py \
    --config "$CONFIG" \
    --library "$library" \
    --output-root "$ROOT/results" \
    --n-jobs "$N_JOBS"
done

HIGH_DIR="$(find "$ROOT/results/high_dependency_linear_20" -maxdepth 1 \
  -type d -name 'pipeline_phase3_*' | sort | tail -n 1)"
MIXED_DIR="$(find "$ROOT/results/mixed_realistic_20" -maxdepth 1 \
  -type d -name 'pipeline_phase3_*' | sort | tail -n 1)"

python3 -m simulations.ess.phase3c_adaptive_ml_policy \
  --repo-root . \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --target-expansion-probability 0.5 \
  --bootstrap-repetitions 200 \
  --random-seed 2026081901 \
  --output-dir "$ROOT/analysis/adaptive_policy"

python3 -m simulations.ess.budget_standardized_policy_audit \
  --repo-root . \
  --policy-root "$ROOT/analysis/adaptive_policy" \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --bootstrap-repetitions 200 \
  --seed 2026082301 \
  --output-dir "$ROOT/analysis/audit"

echo
echo "SMOKE TEST COMPLETE — NOT SCIENTIFIC EVIDENCE"
echo "Temporary output: $ROOT"
