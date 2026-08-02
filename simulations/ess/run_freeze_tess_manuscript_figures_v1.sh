#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 -m unittest \
  simulations.ess.tests.test_make_tess_manuscript_assets_v1_4_8

python3 simulations/ess/freeze_tess_manuscript_figures_v1.py \
  --repo-root "$REPO_ROOT" \
  --source-version v1_4_8 \
  --final-version final_v1

echo
echo "Open:"
echo "  open manuscript_tess/final_v1/figures"
echo "  open manuscript_tess/final_v1/supplementary_figures"
echo "  open manuscript_tess/final_v1/FIGURE_LEGENDS.md"
