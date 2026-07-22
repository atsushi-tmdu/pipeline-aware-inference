#!/usr/bin/env bash

set -Eeuo pipefail

WITH_SUPPORT2=0
case "${1:-}" in
  "") ;;
  --with-support2) WITH_SUPPORT2=1 ;;
  -h|--help)
    cat <<'EOF'
Usage: bash tools/run_release_smoke_tests.sh [--with-support2]

Without options, run compile/import checks, regenerate Figures 1–5, and run
smoke presets for Phases 1–3B.

With --with-support2, additionally download public UCI SUPPORT2 data, reconstruct
the frozen split, run a sealed Phase 4C smoke search, verify Phase 4D in dry-run
mode, and run a five-repetition restricted-permutation functional check.

The script never invokes --open-test CONFIRM.
EOF
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    exit 2
    ;;
esac

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd -- "$SCRIPT_DIR/.." && pwd)
N_JOBS=${N_JOBS:-2}

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON=$PYTHON_BIN
elif [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
elif [[ -x "$REPO/.venv/bin/python" ]]; then
  PYTHON="$REPO/.venv/bin/python"
else
  PYTHON=python3
fi

TMP_BASE=${TMPDIR:-/tmp}
WORK=$(mktemp -d "$TMP_BASE/pipeline-aware-release-check.XXXXXX")

cleanup() {
  if [[ "${KEEP_WORK:-0}" == "1" ]]; then
    echo "Preserving test outputs: $WORK"
  else
    rm -rf "$WORK"
  fi
}
trap cleanup EXIT
trap 'echo "RELEASE SMOKE TEST FAILED at line $LINENO" >&2' ERR

cd "$REPO"

echo "=== Repository ==="
echo "Path: $REPO"
git branch --show-current
git log -1 --oneline

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Tracked repository files contain uncommitted changes." >&2
  git status --short >&2
  exit 1
fi

echo
echo "=== Python environment ==="
"$PYTHON" --version
"$PYTHON" - <<'PY'
import importlib
packages = [
    "numpy", "pandas", "scipy", "sklearn", "joblib", "matplotlib"
]
for name in packages:
    module = importlib.import_module(name)
    print(f"{name}={getattr(module, '__version__', 'unknown')}")
PY

echo
echo "=== Compile check ==="
"$PYTHON" -m compileall -q simulations figures support2 tools

echo
echo "=== Portable import checks ==="
# One direct invocation from outside the repository verifies that repository-local
# imports do not depend on the current working directory.
(cd "$WORK" && "$PYTHON" \
  "$REPO/simulations/phase2/pipeline_signal_phase2.py" --help >/dev/null)

# Import every phase module in one interpreter to avoid repeatedly importing the
# scientific Python stack during a smoke test.
"$PYTHON" - "$REPO" <<'PY'
import sys
from pathlib import Path

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo))

from simulations.phase1 import pipeline_null_pilot_v2  # noqa: F401
from simulations.phase2 import pipeline_signal_phase2  # noqa: F401
from simulations.phase2 import pipeline_event_prevalence_phase2b  # noqa: F401
from simulations.phase2 import pipeline_metric_phase2c  # noqa: F401
from simulations.phase2 import pipeline_target_ap_phase2d  # noqa: F401
from simulations.phase3 import pipeline_independent_null_phase3  # noqa: F401
from simulations.phase3b import pipeline_model_library_phase3b  # noqa: F401

print("PORTABLE IMPORT CHECKS: PASS")
PY

echo
echo "=== Figures 1–5 ==="
bash figures/scripts/run_all.sh
for number in 1 2 3 4 5; do
  count=$(find figures/scripts/output -maxdepth 1 -type f \
    -name "Figure${number}_*" | wc -l | tr -d ' ')
  if [[ "$count" -lt 1 ]]; then
    echo "Figure $number was not generated." >&2
    exit 1
  fi
done
echo "FIGURES 1–5: PASS"

mkdir -p \
  "$WORK/phase1" \
  "$WORK/phase2a" \
  "$WORK/phase2b" \
  "$WORK/phase2c" \
  "$WORK/phase2d" \
  "$WORK/phase3" \
  "$WORK/phase3b"

echo
echo "=== Phase 1 ==="
"$PYTHON" simulations/phase1/pipeline_null_pilot_v2.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase1"

echo
echo "=== Phase 2A ==="
"$PYTHON" simulations/phase2/pipeline_signal_phase2.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase2a"

echo
echo "=== Phase 2B ==="
"$PYTHON" simulations/phase2/pipeline_event_prevalence_phase2b.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase2b"

echo
echo "=== Phase 2C ==="
"$PYTHON" simulations/phase2/pipeline_metric_phase2c.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase2c"

echo
echo "=== Phase 2D ==="
"$PYTHON" simulations/phase2/pipeline_target_ap_phase2d.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase2d"

echo
echo "=== Phase 3 ==="
"$PYTHON" simulations/phase3/pipeline_independent_null_phase3.py \
  --preset smoke --n-jobs "$N_JOBS" --output-root "$WORK/phase3"

echo
echo "=== Phase 3B ==="
"$PYTHON" simulations/phase3b/pipeline_model_library_phase3b.py \
  --library similar_linear_7 \
  --signal-structure single_linear \
  --preset smoke \
  --n-jobs "$N_JOBS" \
  --output-root "$WORK/phase3b"

for phase in phase1 phase2a phase2b phase2c phase2d phase3 phase3b; do
  count=$(find "$WORK/$phase" -type f -name '*.zip' | wc -l | tr -d ' ')
  if [[ "$count" -lt 1 ]]; then
    echo "$phase did not generate a result ZIP." >&2
    exit 1
  fi
  echo "$phase: PASS"
done

if [[ "$WITH_SUPPORT2" == "1" ]]; then
  mkdir -p \
    "$WORK/phase4a" \
    "$WORK/phase4b" \
    "$WORK/phase4c" \
    "$WORK/phase4d" \
    "$WORK/restricted"

  echo
  echo "=== Phase 4A: acquire and audit public SUPPORT2 ==="
  "$PYTHON" support2/support2_phase4a_audit.py \
    --output-root "$WORK/phase4a"

  AUDIT_ZIP=$(find "$WORK/phase4a" -type f \
    -name 'support2_phase4a_audit_*.zip' | sort | tail -n 1)
  test -n "$AUDIT_ZIP"
  test -f "$AUDIT_ZIP"

  echo
  echo "=== Phase 4B: reconstruct frozen split ==="
  "$PYTHON" support2/support2_phase4b_freeze.py \
    --audit-zip "$AUDIT_ZIP" \
    --output-root "$WORK/phase4b"

  FROZEN_ZIP=$(find "$WORK/phase4b" -type f \
    -name 'support2_phase4b_frozen_*.zip' | sort | tail -n 1)
  test -n "$FROZEN_ZIP"
  test -f "$FROZEN_ZIP"

  echo
  echo "=== Phase 4C: sealed smoke search ==="
  "$PYTHON" support2/support2_phase4c_locked_search.py \
    --frozen-zip "$FROZEN_ZIP" \
    --preset smoke \
    --n-jobs "$N_JOBS" \
    --parallel-backend threading \
    --output-root "$WORK/phase4c"

  PHASE4C_ZIP=$(find "$WORK/phase4c" -type f \
    -name 'support2_phase4c_*.zip' | sort | tail -n 1)
  test -n "$PHASE4C_ZIP"
  test -f "$PHASE4C_ZIP"

  "$PYTHON" - "$PHASE4C_ZIP" <<'PY'
import json
import sys
import zipfile
from pathlib import Path

path = Path(sys.argv[1])
with zipfile.ZipFile(path) as archive:
    names = archive.namelist()
    status_names = [name for name in names if name.endswith("run_complete.json")]
    if len(status_names) != 1:
        raise RuntimeError(
            f"Expected one run_complete.json; found {len(status_names)}"
        )
    status = json.loads(archive.read(status_names[0]).decode("utf-8"))
    forbidden = [
        name for name in names
        if "untouched_test_predictions" in name
        or "untouched_test_performance" in name
        or name.endswith("test_predictions.csv")
    ]

if status.get("test_set_evaluated") is not False:
    raise RuntimeError("Phase 4C did not preserve the test-set seal.")
if forbidden:
    raise RuntimeError("Unexpected test-result files:\n" + "\n".join(forbidden))
print("PHASE 4C TEST-SET SEAL: PASS")
PY

  echo
  echo "=== Phase 4D: dry-run lock verification ==="
  "$PYTHON" support2/support2_phase4d_open_test.py \
    --frozen-zip "$FROZEN_ZIP" \
    --phase4c-zip "$PHASE4C_ZIP" \
    --dry-run \
    --output-root "$WORK/phase4d"

  echo
  echo "=== Restricted-permutation functional check ==="
  "$PYTHON" support2/restricted_sensitivity/run_restricted_sensitivity.py \
    --frozen-zip "$FROZEN_ZIP" \
    --phase4c-zip "$PHASE4C_ZIP" \
    --n 5 \
    --jobs "$N_JOBS" \
    --parallel-backend threading \
    --output-dir "$WORK/restricted"

  test -s "$WORK/restricted/restricted_sensitivity_summary.csv"

  echo "PHASE 4A–4D DRY-RUN: PASS"
  echo "RESTRICTED SENSITIVITY: PASS"
  echo "TEST SET WAS NOT EVALUATED"
fi

echo
echo "=== Current-tree release audit ==="
"$PYTHON" tools/release_audit.py --current-tree-only

echo
echo "FIGURES 1–5: PASS"
echo "PHASE 1–3B: PASS"
if [[ "$WITH_SUPPORT2" == "1" ]]; then
  echo "PHASE 4A–4D DRY-RUN: PASS"
  echo "RESTRICTED SENSITIVITY: PASS"
  echo "TEST SET WAS NOT EVALUATED"
fi
echo "RELEASE SMOKE TEST: PASS"
