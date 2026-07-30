#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-$HOME/Developer/pipeline-aware-inference-clean-20260730}"
HIGH="${HIGH:-$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/high_dependency_linear_20/pipeline_phase3_quick_20260724_133334/independent_inference_results.csv}"
MIXED="${MIXED:-$HOME/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/full/mixed_realistic_20/pipeline_phase3_quick_20260724_141555/independent_inference_results.csv}"
BOOTSTRAP_REPETITIONS="${BOOTSTRAP_REPETITIONS:-20000}"
BOOTSTRAP_SEED="${BOOTSTRAP_SEED:-20260730}"

for path in "$REPO" "$HIGH" "$MIXED"; do
  if [[ ! -e "$path" ]]; then
    echo "ERROR: required path not found: $path" >&2
    exit 1
  fi
done

cd "$REPO"

python3 simulations/ess/phase3c_tess_bootstrap.py \
  --repo-root . \
  --high-dependency "$HIGH" \
  --mixed-realistic "$MIXED" \
  --bootstrap-repetitions "$BOOTSTRAP_REPETITIONS" \
  --bootstrap-seed "$BOOTSTRAP_SEED" \
  --cross-library-pairing auto \
  --include-mannwhitney-sensitivity \
  --save-bootstrap-replicates

echo
echo "Primary outputs:"
echo "$REPO/simulations/ess/outputs/phase3c_bootstrap/naive_empirical/"
