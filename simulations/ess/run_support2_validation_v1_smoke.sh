#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

CONFIG="configs/ess/support2_validation_v1_smoke.json"
ROOT="/tmp/tess_support2_validation_v1_smoke"
RUN_DIR="$ROOT/raw/support2_real_structure_20"
ANALYSIS_ROOT="$ROOT/analysis"
N_JOBS="${ESS_N_JOBS:-4}"

rm -rf "$ROOT"
mkdir -p "$ROOT/raw"

python3 -m simulations.ess.support2_generate_model_banks_v1 \
  --config "$CONFIG" \
  --data data/support2/support2_analysis_v1.csv \
  --data-manifest data/support2/support2_data_manifest_v1.json \
  --output-dir "$RUN_DIR" \
  --n-jobs "$N_JOBS"

python3 -m simulations.ess.support2_analyze_policy_v1 \
  --config "$CONFIG" \
  --run-dir "$RUN_DIR" \
  --output-dir "$ANALYSIS_ROOT"

python3 -m simulations.ess.support2_adjudication_v1 \
  --config "$CONFIG" \
  --summary "$ANALYSIS_ROOT/support2_validation_summary.json" \
  --bank-audit "$RUN_DIR/model_bank_audit.json" \
  --output-dir "$ANALYSIS_ROOT" \
  --smoke

echo
echo "SMOKE TEST COMPLETE — NOT SCIENTIFIC EVIDENCE"
echo "Output: $ROOT"
