from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "D1_LOCK_MANIFEST.json"
TRACKED = [
    "D1_THEORY_MEMO.md",
    "d1_core.py",
    "D1_RUNTIME_PREFLIGHT.py",
    "D1_NUMERICAL_PROTOCOL.md",
    "D1_NUMERICAL_CONFIG.json",
    "D1_NUMERICAL_CONFIG_SMOKE.json",
    "d1_validate.py",
    "run_preflight.sh",
    "run_d1_validation_smoke.sh",
    "run_d1_validation_full.sh",
    "make_d1_lock_manifest.py",
    "verify_d1_lock_manifest.py",
    "references.bib",
    "README.md",
    "README_NUMERICAL.md",
    ".gitignore",
    "tests/test_d1_core.py",
    "tests/test_d1_numerical.py",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    records = []
    for rel in TRACKED:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"Required D1 lock file not found: {rel}")
        records.append(
            {
                "file": rel,
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "study_id": "TESS_THEORY_D1_NUMERICAL_VALIDATION_V1",
        "status": "locked_before_run",
        "required_lock_tag": "tess-theory-work-package-d1-v1-lock-20260802",
        "files": records,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"D1 lock manifest written: {OUTPUT}")
    print(f"Files hashed: {len(records)}")


if __name__ == "__main__":
    main()
