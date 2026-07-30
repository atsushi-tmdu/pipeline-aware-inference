#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
cd "$REPO_ROOT"

python3 simulations/ess/tess_boundary_validation.py \
  --output-dir simulations/ess/outputs/boundary_validation \
  --repetitions "${TESS_BOUNDARY_REPETITIONS:-1000000}" \
  --chunk-size "${TESS_BOUNDARY_CHUNK_SIZE:-50000}" \
  --seed "${TESS_BOUNDARY_SEED:-20260730}"
