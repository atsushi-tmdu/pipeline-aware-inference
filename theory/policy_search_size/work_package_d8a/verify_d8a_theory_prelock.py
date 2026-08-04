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
    d8a = Path(__file__).resolve().parent
    manifest = json.loads(
        (d8a / "D8A_THEORY_PRELOCK_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )

    failures = []
    for item in manifest["files"]:
        path = d8a / item["relative_path"]
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
        print("D8-A theory prelock verification: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("D8-A theory prelock verification: PASS")
    print(f"Checkpoint ID: {manifest['checkpoint_id']}")
    print(f"Files verified: {len(manifest['files'])}")
    print("Exact evaluation identity established: YES")
    print("D7 IF-gradient consistency established: YES")
    print("General policy-map C2 theorem proved: NO")
    print("Joint second-order quantile lemma proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
