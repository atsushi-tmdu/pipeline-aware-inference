#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
PYTHON="${PYTHON:-python3}"
LOCK_TAG="tess-theory-work-package-d1-v1-lock-20260802"
OUT="$ROOT/outputs/full_v1"

cd "$REPO"

if ! git rev-parse -q --verify "refs/tags/$LOCK_TAG" >/dev/null; then
  echo "Required lock tag not found: $LOCK_TAG" >&2
  exit 1
fi

LOCK_COMMIT="$(git rev-list -n 1 "$LOCK_TAG")"
if ! git merge-base --is-ancestor "$LOCK_COMMIT" HEAD; then
  echo "Lock tag is not an ancestor of HEAD: $LOCK_TAG" >&2
  exit 1
fi

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "Tracked working tree is not clean. Commit the locked D1 protocol before the full run." >&2
  git status --short
  exit 1
fi

"$PYTHON" "$ROOT/verify_d1_lock_manifest.py"
rm -rf "$OUT"
mkdir -p "$OUT"

export D1_SOURCE_GIT_COMMIT="$(git rev-parse HEAD)"

cd "$ROOT"
"$PYTHON" -m unittest discover -s tests -p 'test_*.py' -v
"$PYTHON" d1_validate.py \
  --config D1_NUMERICAL_CONFIG.json \
  --outdir "$OUT"

echo
echo "D1 full numerical validation complete."
echo "Review: $OUT/D1_VALIDATION_ADJUDICATION.md"
