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
    root = Path(__file__).resolve().parent
    manifest = json.loads(
        (
            root
            / "D8A_NUMERICAL_DESIGN_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )

    failures = []
    for item in manifest["files"]:
        path = root / item["relative_path"]
        if not path.is_file():
            failures.append(
                f"missing: {item['relative_path']}"
            )
            continue
        observed = sha256(path)
        if observed != item["sha256"]:
            failures.append(
                f"hash mismatch: {item['relative_path']} "
                f"expected={item['sha256']} "
                f"observed={observed}"
            )

    if failures:
        print(
            "D8-A numerical-design verification: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(
        "D8-A numerical-design verification: PASS"
    )
    print(
        f"Lock ID: {manifest['lock_id']}"
    )
    print(
        f"Files verified: {len(manifest['files'])}"
    )
    print(
        f"Registered cells: {manifest['registered_cells']}"
    )
    print(
        f"Primary cells: {manifest['primary_cells']}"
    )
    print(
        f"Diagnostic cells: {manifest['diagnostic_cells']}"
    )
    print("Scientific numerical design locked: YES")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
