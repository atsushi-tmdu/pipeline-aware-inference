#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 simulations/ess/tail_dependence_tess_comparison.py --repo-root .

echo
echo "Open:"
echo "  open simulations/ess/NOVELTY_POSITIONING_JA_V0.6.md"
echo "  open simulations/ess/ASYMPTOTIC_DEPENDENCE_EXPLANATION_JA_V0.6.md"
echo "  open simulations/ess/outputs/tail_dependence_comparison/tess_tail_class_comparison_K20.png"
echo "  open simulations/ess/outputs/tail_dependence_comparison/TAIL_CLASS_COMPARISON_SUMMARY.md"
