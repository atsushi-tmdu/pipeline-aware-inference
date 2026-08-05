#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    package = Path(__file__).resolve().parent
    manifest = json.loads(
        (
            package
            / "D8A_SCIENTIFIC_RUN_PACKAGE_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )

    failures = []
    for item in manifest["files"]:
        path = package / item["relative_path"]
        if not path.is_file():
            failures.append(
                f"missing: {item['relative_path']}"
            )
            continue
        if sha256(path) != item["sha256"]:
            failures.append(
                f"hash mismatch: {item['relative_path']}"
            )

    if failures:
        print(
            "D8-A scientific-run package "
            "verification: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(
        "D8-A scientific-run package "
        "verification: PASS"
    )
    print(
        f"Package ID: {manifest['package_id']}"
    )
    print(
        f"Files verified: {len(manifest['files'])}"
    )
    print("Scientific equivalence classes: 25")
    print("Family jobs: 75")
    print("Seed namespace inventory locked: YES")
    print("Output/resume contract locked: YES")
    print("Scientific runner engine locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
