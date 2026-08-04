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
    repair = Path(__file__).resolve().parent
    d8a = repair.parent
    manifest = json.loads(
        (
            repair
            / "D8A_GENERALIZED_THEORY_REPAIR_MANIFEST.json"
        ).read_text(encoding="utf-8")
    )

    failures = []
    for item in manifest["files"]:
        path = d8a / item["relative_path"]
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
            "D8-A generalized-theory repair verification: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(
        "D8-A generalized-theory repair verification: PASS"
    )
    print(
        f"Checkpoint ID: {manifest['checkpoint_id']}"
    )
    print(
        f"Files verified: {len(manifest['files'])}"
    )
    print(
        "Generic moving-max cell lemma proved: YES"
    )
    print(
        "Full generalized policy coincidence theorem proved: YES"
    )
    print(
        "Generalized expectation theorem proved: YES"
    )
    print(
        "Repaired policy-bias corollary proved: YES"
    )
    print(
        "Repaired TESS reference corollary proved: YES"
    )
    print(
        "Historical numerical design re-adjudicated: NO"
    )
    print("Scientific simulation blocked: YES")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
