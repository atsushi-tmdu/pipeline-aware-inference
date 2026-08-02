#!/usr/bin/env python3
"""Locked preflight for the TESS reference-bank uncertainty sensitivity."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_CONFIG_SHA256 = "a8c8d1293675f89187703d52b12aa0a59b99822712814ede5e2f47b8b279c500"
EXPECTED_STUDY_ID = "TESS_REFERENCE_BANK_UNCERTAINTY_V1"
EXPECTED_BRANCH = "ess-study"
SOURCE_TAG = "tess-confirmatory-policy-v1-final-20260802"
REQUIRED_FILES = (
    "candidate_library_manifest.csv",
    "null_reference_model_metrics.csv",
    "evaluation_model_metrics.csv",
)


def command_output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/ess/reference_bank_uncertainty_v1.json"),
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    repo = args.repo_root.expanduser().resolve()
    config_path = args.config
    if not config_path.is_absolute():
        config_path = repo / config_path
    run_dir = args.run_dir.expanduser().resolve()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = repo / manifest_path

    raw = config_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_CONFIG_SHA256:
        raise SystemExit(
            "LOCK FAILURE: reference-bank sensitivity config hash changed.\n"
            f"Expected: {EXPECTED_CONFIG_SHA256}\nObserved: {digest}"
        )
    config = json.loads(raw)
    if config.get("study_id") != EXPECTED_STUDY_ID:
        raise SystemExit("LOCK FAILURE: unexpected study_id.")
    if config.get("primary_adjudication_unchanged") is not True:
        raise SystemExit("LOCK FAILURE: sensitivity must not alter the primary adjudication.")

    branch = command_output("git", "-C", str(repo), "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise SystemExit(f"Expected branch {EXPECTED_BRANCH}, found {branch}")
    status = command_output("git", "-C", str(repo), "status", "--porcelain")
    if status and not args.allow_dirty:
        raise SystemExit(
            "Working tree is not clean. Commit and tag the sensitivity protocol/code before running.\n"
            + status
        )

    try:
        source_tag_commit = command_output(
            "git", "-C", str(repo), "rev-list", "-n", "1", SOURCE_TAG
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Required source tag is absent: {SOURCE_TAG}") from exc

    expected_source_prefix = str(config.get("source_confirmatory_commit", ""))
    if expected_source_prefix and not source_tag_commit.startswith(expected_source_prefix):
        raise SystemExit(
            "LOCK FAILURE: source confirmatory tag does not resolve to the expected commit.\n"
            f"Expected prefix: {expected_source_prefix}\nObserved: {source_tag_commit}"
        )

    missing = [str(run_dir / name) for name in REQUIRED_FILES if not (run_dir / name).is_file()]
    if missing:
        raise SystemExit("Required raw confirmatory files are missing:\n" + "\n".join(missing))

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "study_id": EXPECTED_STUDY_ID,
        "analysis_label": "post hoc sensitivity",
        "primary_adjudication_unchanged": True,
        "config_path": str(config_path),
        "config_sha256": digest,
        "source_tag": SOURCE_TAG,
        "source_tag_commit": source_tag_commit,
        "run_dir": str(run_dir),
        "input_files": [
            {
                "path": str(run_dir / name),
                "size_bytes": (run_dir / name).stat().st_size,
                "sha256": sha256_file(run_dir / name),
            }
            for name in REQUIRED_FILES
        ],
        "git_commit_at_start": command_output("git", "-C", str(repo), "rev-parse", "HEAD"),
        "git_branch": branch,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": command_output("python3", "--version"),
        "config": config,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Reference-bank uncertainty sensitivity preflight passed")
    print(f"Config SHA-256: {digest}")
    print(f"Source tag: {SOURCE_TAG} ({source_tag_commit})")
    print(f"Run directory: {run_dir}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
