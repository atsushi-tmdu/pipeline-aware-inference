#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    d7 = Path(__file__).resolve().parent
    manifest_path = (
        d7 / "D7_VALIDATION_IMPLEMENTATION_MANIFEST.json"
    )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    failures = []
    for item in payload["files"]:
        path = d7 / item["relative_path"]
        if not path.is_file():
            failures.append(f"missing: {item['relative_path']}")
            continue
        observed = sha256(path)
        if observed != item["sha256"]:
            failures.append(
                f"hash mismatch: {item['relative_path']} "
                f"expected={item['sha256']} observed={observed}"
            )

    if failures:
        print("D7 validation implementation verification: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("D7 validation implementation verification: PASS")
    print(f"Lock ID: {payload['lock_id']}")
    print(f"Files verified: {len(payload['files'])}")
    print("Scientific full run completed: NO")


if __name__ == "__main__":
    main()
