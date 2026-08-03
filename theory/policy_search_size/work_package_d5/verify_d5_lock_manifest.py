#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


D5 = Path(__file__).resolve().parent
REPO = D5.parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-tag",
        action="store_true",
        help="also require the declared annotated lock tag at current HEAD",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = D5 / "D5_LOCK_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit(f"FAIL: missing manifest: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []

    config_path = D5 / "D5_NUMERICAL_CONFIG.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    if manifest.get("status") != "locked_before_run":
        failures.append("manifest status is not locked_before_run")
    if config.get("status") != "locked_before_run":
        failures.append("scientific config status is not locked_before_run")
    if (
        config.get("required_lock_tag")
        != manifest.get("required_lock_tag")
    ):
        failures.append("config and manifest lock tags differ")

    for record in manifest.get("files", []):
        relative = record["file"]
        path = D5 / relative
        if not path.is_file():
            failures.append(f"missing:{relative}")
            continue
        if path.stat().st_size != int(record["size_bytes"]):
            failures.append(f"size:{relative}")
        if sha256_file(path) != record["sha256"]:
            failures.append(f"hash:{relative}")

    if args.require_tag:
        tag = str(manifest["required_lock_tag"])
        try:
            tagged_commit = subprocess.check_output(
                ["git", "rev-parse", f"{tag}^{{commit}}"],
                cwd=REPO,
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
            head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO,
                text=True,
            ).strip()
        except subprocess.CalledProcessError as exc:
            failures.append(
                "lock tag unavailable: "
                + exc.output.strip().replace("\n", " ")
            )
        else:
            if tagged_commit != head:
                failures.append(
                    f"lock tag does not point to HEAD: "
                    f"{tagged_commit} != {head}"
                )

    if failures:
        print("D5 lock manifest verification FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(
        "D5 lock manifest verification PASS: "
        f"{len(manifest['files'])} files"
    )
    if args.require_tag:
        print(
            "D5 annotated lock tag verification PASS: "
            f"{manifest['required_lock_tag']}"
        )


if __name__ == "__main__":
    main()
