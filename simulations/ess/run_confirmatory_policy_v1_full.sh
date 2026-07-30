#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

CONFIG="configs/ess/confirmatory_policy_v1.json"
OUTPUT_ROOT="results_ess_confirmatory/policy_v1_seed20260817"
ANALYSIS_ROOT="simulations/ess/outputs/confirmatory_policy_v1"
N_JOBS="${ESS_N_JOBS:-30}"

if [[ -e "$OUTPUT_ROOT" ]]; then
  echo "ERROR: locked confirmatory output already exists:"
  echo "  $OUTPUT_ROOT"
  echo "Rename it only if the prior run failed before producing scientific results."
  exit 1
fi

python3 -m simulations.ess.confirmatory_preflight_v1 \
  --repo-root . \
  --config "$CONFIG" \
  --manifest "$OUTPUT_ROOT/confirmatory_run_manifest.json"

for library in high_dependency_linear_20 mixed_realistic_20; do
  python3 simulations/phase3c/pipeline_candidate_count_phase3c.py \
    --config "$CONFIG" \
    --library "$library" \
    --output-root "$OUTPUT_ROOT" \
    --n-jobs "$N_JOBS"
done

HIGH_DIR="$(find "$OUTPUT_ROOT/high_dependency_linear_20" -maxdepth 1 \
  -type d -name 'pipeline_phase3_*' | sort | tail -n 1)"
MIXED_DIR="$(find "$OUTPUT_ROOT/mixed_realistic_20" -maxdepth 1 \
  -type d -name 'pipeline_phase3_*' | sort | tail -n 1)"

if [[ -z "$HIGH_DIR" || -z "$MIXED_DIR" ]]; then
  echo "ERROR: confirmatory Phase 3C run directories were not found."
  exit 1
fi

POLICY_ROOT="$ANALYSIS_ROOT/adaptive_policy"
MECHANISM_ROOT="$ANALYSIS_ROOT/mechanism"
AUDIT_ROOT="$ANALYSIS_ROOT/budget_standardized_audit"

python3 -m simulations.ess.phase3c_adaptive_ml_policy \
  --repo-root . \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --target-expansion-probability 0.5 \
  --bootstrap-repetitions 20000 \
  --random-seed 20260819 \
  --output-dir "$POLICY_ROOT"

python3 -m simulations.ess.phase3c_adaptive_policy_mechanism \
  --repo-root . \
  --input-root "$POLICY_ROOT" \
  --bootstrap-repetitions 20000 \
  --seed 20260823 \
  --output-dir "$MECHANISM_ROOT"

python3 -m simulations.ess.budget_standardized_policy_audit \
  --repo-root . \
  --policy-root "$POLICY_ROOT" \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --bootstrap-repetitions 20000 \
  --seed 20260823 \
  --output-dir "$AUDIT_ROOT"

python3 -m simulations.ess.confirmatory_policy_interaction_v1 \
  --high-bank "$POLICY_ROOT/high_dependency_linear_20/adaptive_ml_policy_replication_bank.csv" \
  --mixed-bank "$POLICY_ROOT/mixed_realistic_20/adaptive_ml_policy_replication_bank.csv" \
  --bootstrap-repetitions 20000 \
  --seed 20260823 \
  --output "$ANALYSIS_ROOT/confirmatory_policy_interaction.csv"

python3 -m simulations.ess.confirmatory_adjudication_v1 \
  --interaction "$ANALYSIS_ROOT/confirmatory_policy_interaction.csv" \
  --audit "$AUDIT_ROOT/fixed_policy_reconstruction_audit_all_libraries.csv" \
  --output-dir "$ANALYSIS_ROOT"

echo
echo "Confirmatory study complete."
echo "Primary adjudication:"
echo "  $ANALYSIS_ROOT/CONFIRMATORY_ADJUDICATION.md"
