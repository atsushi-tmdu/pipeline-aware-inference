#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

HIGH_DIR="$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/high_dependency_linear_20/pipeline_phase3_quick_20260724_133334"
MIXED_DIR="$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/mixed_realistic_20/pipeline_phase3_quick_20260724_141555"

python3 -m simulations.ess.budget_standardized_policy_audit \
  --repo-root . \
  --high-dependency-run-dir "$HIGH_DIR" \
  --mixed-realistic-run-dir "$MIXED_DIR" \
  --bootstrap-repetitions 20000

echo
echo "Open:"
echo "  open simulations/ess/BUDGET_STANDARDIZED_POLICY_AUDIT_EXPLANATION_JA_V1.1.md"
echo "  open simulations/ess/outputs/budget_standardized_policy_audit/BUDGET_STANDARDIZED_POLICY_AUDIT_SUMMARY.md"
echo "  open simulations/ess/outputs/budget_standardized_policy_audit/mixed_realistic_20/budget_standardized_policy_effects.png"
echo "  open simulations/ess/outputs/budget_standardized_policy_audit/high_dependency_linear_20/fixed_policy_reconstruction_audit.csv"
