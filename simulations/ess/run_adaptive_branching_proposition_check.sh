#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 -m simulations.ess.adaptive_branching_proposition_check \
  --repo-root .

echo
echo "Open:"
echo "  open simulations/ess/ADAPTIVE_BRANCHING_PROPOSITION_JA_V0.8.md"
echo "  open simulations/ess/ADAPTIVE_BRANCHING_THEORY_DRAFT_EN_V0.8.md"
echo "  open simulations/ess/outputs/adaptive_branching_proposition/adaptive_policy_tess_differences.png"
echo "  open simulations/ess/outputs/adaptive_branching_proposition/adaptive_branching_manuscript_table.csv"
