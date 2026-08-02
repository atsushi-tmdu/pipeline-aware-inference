#!/usr/bin/env python3
"""Locked preflight for the SUPPORT2 supplementary validation."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_CONFIG_SHA256 = "eb89a6b42b0ea080c689aae37c3476ac9338f9bd5f923d41bb9ca8e9e552f2da"
EXPECTED_STUDY_ID = "TESS_SUPPORT2_VALIDATION_V1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=Path("configs/ess/support2_validation_v1.json"))
    parser.add_argument("--data", type=Path, default=Path("data/support2/support2_analysis_v1.csv"))
    parser.add_argument("--data-manifest", type=Path, default=Path("data/support2/support2_data_manifest_v1.json"))
    parser.add_argument("--run-manifest", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    config_path = repo / args.config if not args.config.is_absolute() else args.config
    data_path = repo / args.data if not args.data.is_absolute() else args.data
    data_manifest_path = repo / args.data_manifest if not args.data_manifest.is_absolute() else args.data_manifest

    config_raw = config_path.read_bytes()
    config_hash = hashlib.sha256(config_raw).hexdigest()
    if config_hash != EXPECTED_CONFIG_SHA256:
        raise SystemExit(f"CONFIG LOCK FAILURE\nExpected: {EXPECTED_CONFIG_SHA256}\nObserved: {config_hash}")
    config = json.loads(config_raw)
    if config.get("study_id") != EXPECTED_STUDY_ID:
        raise SystemExit("CONFIG LOCK FAILURE: unexpected study_id")

    if not data_path.exists() or not data_manifest_path.exists():
        raise SystemExit("DATA LOCK FAILURE: prepare SUPPORT2 data and commit its manifest first")
    data_manifest = json.loads(data_manifest_path.read_text(encoding="utf-8"))
    observed_data_hash = sha256(data_path)
    if observed_data_hash != data_manifest.get("canonical_sha256"):
        raise SystemExit("DATA LOCK FAILURE: canonical file differs from committed manifest")
    if int(data_manifest.get("rows", -1)) != 9105:
        raise SystemExit("DATA LOCK FAILURE: unexpected row count")

    branch = command("git", "-C", str(repo), "branch", "--show-current")
    if branch != "ess-study":
        raise SystemExit(f"Expected branch ess-study, found {branch}")
    status = command("git", "-C", str(repo), "status", "--porcelain")
    if status:
        raise SystemExit("Working tree must be clean before the scientific run.\n" + status)
    tracked = command("git", "-C", str(repo), "ls-files", str(data_manifest_path.relative_to(repo)))
    if not tracked:
        raise SystemExit("DATA LOCK FAILURE: data manifest is not tracked by Git")

    manifest_path = repo / args.run_manifest if not args.run_manifest.is_absolute() else args.run_manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "study_id": EXPECTED_STUDY_ID,
        "config_sha256": config_hash,
        "data_sha256": observed_data_hash,
        "data_manifest": data_manifest,
        "git_commit": command("git", "-C", str(repo), "rev-parse", "HEAD"),
        "git_branch": branch,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": command("python3", "--version"),
        "config": config,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("SUPPORT2 validation lock preflight passed")
    print(f"Config SHA-256: {config_hash}")
    print(f"Data SHA-256: {observed_data_hash}")
    print(f"Git commit: {manifest['git_commit']}")


if __name__ == "__main__":
    main()
