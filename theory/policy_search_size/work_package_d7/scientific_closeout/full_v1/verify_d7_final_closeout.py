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
    closeout = Path(__file__).resolve().parent
    manifest = json.loads(
        (closeout / "D7_FINAL_CLOSEOUT_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )

    failures = []
    for item in manifest["package_files"]:
        path = closeout / item["relative_path"]
        if not path.is_file():
            failures.append(f"missing package file: {item['relative_path']}")
            continue
        observed = sha256(path)
        if observed != item["sha256"]:
            failures.append(
                f"package hash mismatch: {item['relative_path']} "
                f"expected={item['sha256']} observed={observed}"
            )

    d7 = closeout.parents[1]
    source_output = d7 / "outputs" / "full_v1"
    source_present = source_output.is_dir()
    source_verified = 0
    if source_present:
        for item in manifest["source_output_inventory"]:
            path = source_output / item["filename"]
            if not path.is_file():
                failures.append(
                    f"missing source output: {item['filename']}"
                )
                continue
            observed = sha256(path)
            if observed != item["sha256"]:
                failures.append(
                    f"source hash mismatch: {item['filename']} "
                    f"expected={item['sha256']} observed={observed}"
                )
            else:
                source_verified += 1

    if failures:
        print("D7 final closeout verification: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("D7 final closeout verification: PASS")
    print(f"Closeout ID: {manifest['closeout_id']}")
    print(f"Package files verified: {len(manifest['package_files'])}")
    print(f"Formal status: {manifest['formal_status']}")
    print("Scientific simulation repeated: NO")
    if source_present:
        print(
            "Source full outputs verified: "
            f"{source_verified}/{len(manifest['source_output_inventory'])}"
        )
    else:
        print("Source full outputs: not present; package verification only")


if __name__ == "__main__":
    main()
