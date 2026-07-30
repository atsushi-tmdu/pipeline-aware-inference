#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

MC_CSV="simulations/ess/outputs/boundary_validation/tess_boundary_validation.csv"

python3 simulations/ess/gaussian_copula_tess_exact.py \
  --repo-root . \
  --monte-carlo-boundary-csv "$MC_CSV"

echo
echo "Open the theory note and outputs with:"
echo "  open simulations/ess/TESS_THEORY_NOTE_JA_V0.5.md"
echo "  open simulations/ess/outputs/gaussian_copula_exact/gaussian_copula_tess_exact_curves_K20.png"
echo "  open simulations/ess/outputs/gaussian_copula_exact/gaussian_copula_tess_convergence.png"
echo "  open simulations/ess/outputs/gaussian_copula_exact/GAUSSIAN_COPULA_EXACT_SUMMARY.md"
