#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 -m simulations.ess.phase3c_adaptive_policy_mechanism \
  --repo-root . \
  --bootstrap-repetitions 20000

echo
echo "Open:"
echo "  open simulations/ess/ADAPTIVE_POLICY_GENERAL_DECOMPOSITION_JA_V1.0.md"
echo "  open simulations/ess/outputs/phase3c_adaptive_policy_mechanism/ADAPTIVE_POLICY_MECHANISM_SUMMARY.md"
echo "  open simulations/ess/outputs/phase3c_adaptive_policy_mechanism/high_dependency_linear_20/activation_increment_covariance.png"
echo "  open simulations/ess/outputs/phase3c_adaptive_policy_mechanism/mixed_realistic_20/incremental_effect_by_base_score.png"
