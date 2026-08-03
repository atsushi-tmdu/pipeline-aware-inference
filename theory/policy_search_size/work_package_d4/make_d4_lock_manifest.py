from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "D4_LOCK_MANIFEST.json"
TRACKED = [
    "D4_THEORY_MEMO.md",
    "d4_core.py",
    "D4_RUNTIME_PREFLIGHT.py",
    "D4_PREFLIGHT_CONFIG.json",
    "D4_NUMERICAL_PROTOCOL.md",
    "D4_NUMERICAL_CONFIG.json",
    "D4_NUMERICAL_CONFIG_SMOKE.json",
    "d4_validation_core.py",
    "d4_validate.py",
    "run_preflight.sh",
    "run_d4_validation_smoke.sh",
    "run_d4_validation_full.sh",
    "make_d4_lock_manifest.py",
    "verify_d4_lock_manifest.py",
    "references.bib",
    "README.md",
    "README_NUMERICAL.md",
    ".gitignore",
    "tests/test_d4_core.py",
    "tests/test_d4_numerical.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    records = []
    for rel in TRACKED:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"Required D4 lock file not found: {rel}")
        records.append(
            {
                "file": rel,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "study_id": "TESS_THEORY_D4_NUMERICAL_VALIDATION_V1",
        "status": "locked_before_run",
        "required_lock_tag": "tess-theory-work-package-d4-v1-lock-20260802",
        "files": records,
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"D4 lock manifest written: {OUTPUT}")
    print(f"Files hashed: {len(records)}")


if __name__ == "__main__":
    main()
