#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 -m simulations.ess.make_tess_manuscript_assets_v1_4_8 \
  --repo-root . \
  --output-root manuscript_tess

echo
echo "Open corrected assets:"
echo "  open manuscript_tess/figures/v1_4_8"
echo "  open manuscript_tess/supplementary_figures/v1_4_8"
