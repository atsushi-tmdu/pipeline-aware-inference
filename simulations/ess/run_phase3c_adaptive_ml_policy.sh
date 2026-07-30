#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

HIGH_DIR="$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/high_dependency_linear_20/pipeline_phase3_quick_20260724_133334"
MIXED_DIR="$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/mixed_realistic_20/pipeline_phase3_quick_20260724_141555"

for path in "$HIGH_DIR" "$MIXED_DIR"; do
  if [[ ! -d "$path" ]]; then
    echo "ERROR: Phase 3C run directory not found:"
    echo "  $path"
    exit 1
  fi
done

python3 -m simulations.ess.phase3c_adaptive_ml_policy \
  --repo-root . \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --bootstrap-repetitions 20000

echo
echo "Open:"
echo "  open simulations/ess/PHASE3C_ADAPTIVE_ML_POLICY_EXPLANATION_JA_V0.9.md"
echo "  open simulations/ess/outputs/phase3c_adaptive_ml_policy/PHASE3C_ADAPTIVE_ML_POLICY_SUMMARY.md"
echo "  open simulations/ess/outputs/phase3c_adaptive_ml_policy/high_dependency_linear_20/adaptive_ml_policy_tess_curves.png"
echo "  open simulations/ess/outputs/phase3c_adaptive_ml_policy/mixed_realistic_20/adaptive_ml_policy_tess_curves.png"
