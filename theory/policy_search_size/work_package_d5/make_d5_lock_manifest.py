#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


D5 = Path(__file__).resolve().parent
LOCK_TAG = "tess-theory-work-package-d5-v1-lock-20260803"
STUDY_ID = "TESS_THEORY_D5_PLUS_ONE_BRIDGE_V1"

LOCKED_FILES = [
    ".gitignore",
    "D5_PROTOCOL.md",
    "D5_PROTOCOL_CONFIG.json",
    "D5_THEORY_MEMO.md",
    "D5_NUMERICAL_PROTOCOL.md",
    "D5_NUMERICAL_CONFIG.json",
    "D5_NUMERICAL_CONFIG_SMOKE.json",
    "README.md",
    "d5_core.py",
    "d5_validate.py",
    "make_d5_lock_manifest.py",
    "verify_d5_lock_manifest.py",
    "run_d5_tests.sh",
    "run_d5_validation_smoke.sh",
    "run_d5_validation_full.sh",
    "tests/__init__.py",
    "tests/test_d5_core.py",
    "tests/test_d5_parent_reproduction.py",
    "tests/test_d5_validation.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    records = []
    for relative in LOCKED_FILES:
        path = D5 / relative
        if not path.is_file():
            raise SystemExit(f"FAIL: missing locked file: {relative}")
        records.append(
            {
                "file": relative,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )

    manifest = {
        "study_id": STUDY_ID,
        "status": "locked_before_run",
        "required_lock_tag": LOCK_TAG,
        "preceding_results_tag": "d4-validation-full-v1",
        "expected_d4_results_commit": (
            "9b0a2530bfb5e363f59bd7b290d1c064c82b5eaa"
        ),
        "files": records,
    }

    output = D5 / "D5_LOCK_MANIFEST.json"
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"D5 lock manifest written: {output}")
    print(f"Locked files: {len(records)}")


if __name__ == "__main__":
    main()
