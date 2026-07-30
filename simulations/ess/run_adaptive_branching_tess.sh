#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 simulations/ess/adaptive_branching_tess.py --repo-root .

echo
echo "Open:"
echo "  open simulations/ess/ADAPTIVE_BRANCHING_EXPLANATION_JA_V0.7.md"
echo "  open simulations/ess/outputs/adaptive_branching/adaptive_rules_same_expected_K.png"
echo "  open simulations/ess/outputs/adaptive_branching/ADAPTIVE_BRANCHING_SUMMARY.md"
