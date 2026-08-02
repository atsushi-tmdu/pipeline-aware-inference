#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

CONFIG="configs/ess/support2_validation_v1.json"
RAW_ROOT="results_ess_support2/validation_v1_seed20260903"
RUN_DIR="$RAW_ROOT/support2_real_structure_20"
ANALYSIS_ROOT="simulations/ess/outputs/support2_validation_v1"
N_JOBS="${ESS_N_JOBS:-28}"

if [[ -e "$RAW_ROOT" || -e "$ANALYSIS_ROOT" ]]; then
  echo "ERROR: SUPPORT2 scientific output already exists."
  echo "Do not delete or rerun it without first diagnosing the existing run."
  exit 1
fi

python3 -m simulations.ess.support2_preflight_v1 \
  --repo-root . \
  --config "$CONFIG" \
  --run-manifest "$RAW_ROOT/support2_run_manifest.json"

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
  --output-dir "$ANALYSIS_ROOT"

cp "$RAW_ROOT/support2_run_manifest.json" "$ANALYSIS_ROOT/support2_run_manifest.json"
cp data/support2/support2_data_manifest_v1.json "$ANALYSIS_ROOT/support2_data_manifest_v1.json"

echo
echo "SUPPORT2 supplementary validation complete."
echo "Adjudication:"
echo "  $ANALYSIS_ROOT/SUPPORT2_VALIDATION_ADJUDICATION.md"
