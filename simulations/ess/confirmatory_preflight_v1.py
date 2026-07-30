#!/usr/bin/env python3
"""Locked preflight for the TESS confirmatory policy study."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_SHA256 = "ae58b6080bc4ae27a6e89e2545ebf7a0c8b9e12d96f3bc99012f3df03ccac1e8"
EXPECTED_STUDY_ID = "TESS_CONFIRMATORY_POLICY_V1"


def command_output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/ess/confirmatory_policy_v1.json"),
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = repo / config_path

    raw = config_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(
            "LOCK FAILURE: confirmatory config hash changed.\n"
            f"Expected: {EXPECTED_SHA256}\nObserved: {digest}"
        )

    config = json.loads(raw)
    if config.get("study_id") != EXPECTED_STUDY_ID:
        raise SystemExit("LOCK FAILURE: unexpected study_id.")

    branch = command_output("git", "-C", str(repo), "branch", "--show-current")
    if branch != "ess-study":
        raise SystemExit(f"Expected branch ess-study, found {branch}")

    status = command_output("git", "-C", str(repo), "status", "--porcelain")
    if status and not args.allow_dirty:
        raise SystemExit(
            "Working tree is not clean. Commit the locked protocol/code before "
            "running the confirmatory study.\n" + status
        )

    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = repo / manifest_path
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "study_id": EXPECTED_STUDY_ID,
        "config_path": str(config_path),
        "config_sha256": digest,
        "git_commit": command_output("git", "-C", str(repo), "rev-parse", "HEAD"),
        "git_branch": branch,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": command_output("python3", "--version"),
        "config": config,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Confirmatory lock preflight passed")
    print(f"Config SHA-256: {digest}")
    print(f"Git commit: {manifest['git_commit']}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
