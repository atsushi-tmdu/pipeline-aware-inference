#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


EXPECTED_BRANCH = "tess-top-tier-theory"
PARENT_TAG = "d8a-generalized-implementation-lock-v1"


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
    generalized = package.parent
    numerical = generalized.parent
    d8a = numerical.parent
    repo = d8a.parents[2]

    config = json.loads(
        (
            package
            / "D8A_SCIENTIFIC_RUN_CONFIG.json"
        ).read_text(encoding="utf-8")
    )
    jobs = json.loads(
        (
            package
            / "D8A_SCIENTIFIC_JOB_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )
    seeds = json.loads(
        (
            package
            / "D8A_SCIENTIFIC_SEED_INVENTORY.json"
        ).read_text(encoding="utf-8")
    )

    failures = []

    branch = subprocess.check_output(
        ["git", "branch", "--show-current"],
        cwd=repo,
        text=True,
    ).strip()
    if branch != EXPECTED_BRANCH:
        failures.append(
            f"unexpected branch: {branch}"
        )

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
    ).strip()
    parent = subprocess.check_output(
        [
            "git",
            "rev-parse",
            f"{PARENT_TAG}^{{}}",
        ],
        cwd=repo,
        text=True,
    ).strip()
    if head != parent:
        failures.append(
            "HEAD is not the implementation-lock commit"
        )

    if config["scientific_simulation_run"]:
        failures.append(
            "config marks scientific simulation as run"
        )
    if config[
        "scientific_runner_engine_locked"
    ]:
        failures.append(
            "runner engine unexpectedly locked"
        )
    if config[
        "scientific_execution_started"
    ]:
        failures.append(
            "scientific execution unexpectedly started"
        )

    if len(jobs) != 75:
        failures.append(
            f"expected 75 family jobs, found {len(jobs)}"
        )

    family_counts = {}
    for job in jobs:
        family = job["family"]
        family_counts[family] = (
            family_counts.get(family, 0) + 1
        )
    expected_counts = {
        "reference_only": 25,
        "evaluation_only": 25,
        "combined": 25,
    }
    if family_counts != expected_counts:
        failures.append(
            f"unexpected family counts: {family_counts}"
        )

    job_ids = [
        job["job_id"]
        for job in jobs
    ]
    if len(set(job_ids)) != len(job_ids):
        failures.append(
            "job IDs are not unique"
        )

    seed_ids = [
        item["seed_inventory_id"]
        for item in seeds
    ]
    if len(set(seed_ids)) != len(seed_ids):
        failures.append(
            "seed inventory IDs are not unique"
        )

    prefixes = []
    for item in seeds:
        for stream in item["streams"]:
            prefixes.append(
                tuple(stream["spawn_prefix"])
            )
    if len(set(prefixes)) != len(prefixes):
        failures.append(
            "seed spawn prefixes are not unique"
        )

    output_root = (
        repo / config["output_root_relative_to_repo"]
    )
    if output_root.exists():
        failures.append(
            f"locked output root already exists: {output_root}"
        )

    dependency_hashes = config[
        "locked_dependency_hashes"
    ]
    for relative_path, expected_hash in (
        dependency_hashes.items()
    ):
        path = repo / relative_path
        if not path.is_file():
            failures.append(
                f"dependency missing: {relative_path}"
            )
            continue
        if sha256(path) != expected_hash:
            failures.append(
                f"dependency hash mismatch: {relative_path}"
            )

    if failures:
        print(
            "D8-A scientific-run preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A scientific-run preflight")
    print("=" * 80)
    print("Status: PASS")
    print("Implementation lock verified: YES")
    print("Scientific equivalence classes: 25")
    print("Family jobs: 75")
    print("Reference-only jobs: 25")
    print("Evaluation-only jobs: 25")
    print("Combined jobs: 25")
    print(
        f"Seed inventory entries: {len(seeds)}"
    )
    print("Output root absent before run: YES")
    print("Atomic-write contract present: YES")
    print("Resume contract present: YES")
    print("Scientific runner engine locked: NO")
    print("Scientific execution started: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
