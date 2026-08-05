#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


LOCK_ID = "TESS_D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK_V1"
LOCK_TAG = "d8a-scientific-runner-engine-lock-v1"
EXPECTED_TEST_COUNT = 82

MANIFEST_NAME = "D8A_SCIENTIFIC_RUNNER_ENGINE_MANIFEST.json"
LOCK_NAME = "D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK.json"

EXCLUDED_FROM_MANIFEST = {
    MANIFEST_NAME,
    LOCK_NAME,
    "verify_d8a_scientific_runner_engine_lock.py",
    "D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def run(
    command: list[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def repository_root(engine: Path) -> Path:
    result = run(
        [
            "git",
            "rev-parse",
            "--show-toplevel",
        ],
        cwd=engine,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "cannot resolve repository root"
        )
    return Path(
        result.stdout.strip()
    ).resolve()


def all_manifest_candidates(
    engine: Path,
) -> set[str]:
    result = set()
    for path in engine.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(engine)
        if "__pycache__" in relative.parts:
            continue
        if path.suffix == ".pyc":
            continue
        if relative.name in EXCLUDED_FROM_MANIFEST:
            continue
        result.add(relative.as_posix())
    return result


def verify_manifest(
    engine: Path,
    manifest: dict[str, object],
) -> list[str]:
    failures = []
    records = manifest.get("files")
    if not isinstance(records, list):
        return ["manifest files field is invalid"]

    declared_paths = []
    for record in records:
        if not isinstance(record, dict):
            failures.append(
                "manifest contains a non-object record"
            )
            continue
        relative = str(record.get("path"))
        declared_paths.append(relative)

        if relative in EXCLUDED_FROM_MANIFEST:
            failures.append(
                f"excluded lock file is in manifest: {relative}"
            )
            continue
        if relative.startswith("/") or ".." in Path(relative).parts:
            failures.append(
                f"unsafe manifest path: {relative}"
            )
            continue

        path = engine / relative
        if not path.is_file():
            failures.append(
                f"manifest file is missing: {relative}"
            )
            continue

        if path.stat().st_size != int(
            record.get("size", -1)
        ):
            failures.append(
                f"size mismatch: {relative}"
            )

        if sha256(path) != str(
            record.get("sha256")
        ):
            failures.append(
                f"SHA-256 mismatch: {relative}"
            )

    if len(declared_paths) != len(set(declared_paths)):
        failures.append(
            "manifest contains duplicate paths"
        )

    candidate_paths = all_manifest_candidates(
        engine
    )
    declared_set = set(declared_paths)
    if declared_set != candidate_paths:
        missing = sorted(
            candidate_paths - declared_set
        )
        extra = sorted(
            declared_set - candidate_paths
        )
        if missing:
            failures.append(
                "unmanifested engine files: "
                + ", ".join(missing)
            )
        if extra:
            failures.append(
                "manifest paths not present: "
                + ", ".join(extra)
            )

    if int(
        manifest.get("file_count", -1)
    ) != len(records):
        failures.append(
            "manifest file_count mismatch"
        )

    return failures


def verify_audit_records(
    engine: Path,
) -> list[str]:
    failures = []
    required = {
        "engineering_smoke": (
            engine
            / "engineering_smoke"
            / "NON_SCIENTIFIC_ENGINEERING_ONLY_runner_smoke_summary.json"
        ),
        "natural_precision": (
            engine
            / "precision_engineering_audit"
            / "NON_SCIENTIFIC_ENGINEERING_ONLY_natural_scale_precision_audit_summary.json"
        ),
        "summary_acceptance": (
            engine
            / "summary_acceptance_engineering_audit"
            / "NON_SCIENTIFIC_ENGINEERING_ONLY_summary_acceptance_audit.json"
        ),
        "executor_resume": (
            engine
            / "executor_resume_engineering_audit"
            / "NON_SCIENTIFIC_ENGINEERING_ONLY_executor_resume_audit.json"
        ),
    }

    loaded = {}
    for name, path in required.items():
        if not path.is_file():
            failures.append(
                f"required audit is missing: {name}"
            )
            continue
        loaded[name] = json.loads(
            path.read_text(encoding="utf-8")
        )

    if "engineering_smoke" in loaded:
        value = loaded["engineering_smoke"]
        if value.get("scientific_simulation_run"):
            failures.append(
                "engineering smoke is marked scientific"
            )
        if not value.get("all_resume_checks_pass"):
            failures.append(
                "engineering smoke resume checks failed"
            )

    if "natural_precision" in loaded:
        value = loaded["natural_precision"]
        if value.get(
            "studentized_mcse_constant_rule_used"
        ):
            failures.append(
                "studentized precision rule remains active"
            )
        if value.get(
            "rate_aware_bias_scale_used_for_stopping"
        ):
            failures.append(
                "bias-rate scale remains active for stopping"
            )
        if not value.get(
            "rate_aware_bias_scale_retained_for_acceptance"
        ):
            failures.append(
                "bias-rate acceptance scale is missing"
            )

    if "summary_acceptance" in loaded:
        value = loaded["summary_acceptance"]
        if not value.get("engineering_audit_pass"):
            failures.append(
                "summary/acceptance audit failed"
            )
        passing = value.get(
            "synthetic_passing_acceptance",
            {},
        ).get(
            "formal",
            {},
        ).get("formal_status")
        failing = value.get(
            "synthetic_tess_boundary_failure",
            {},
        ).get(
            "formal",
            {},
        ).get("formal_status")
        if passing != "PASS":
            failures.append(
                "synthetic passing acceptance did not pass"
            )
        if failing != "FAIL":
            failures.append(
                "TESS-boundary failure did not propagate"
            )

    if "executor_resume" in loaded:
        value = loaded["executor_resume"]
        if not value.get("engineering_audit_pass"):
            failures.append(
                "executor/resume audit failed"
            )
        if not value.get("resume_matches_direct"):
            failures.append(
                "resume does not match direct execution"
            )
        if not value.get(
            "completed_rerun_idempotent"
        ):
            failures.append(
                "completed rerun is not idempotent"
            )
        if not value.get(
            "executor_refused_without_lock"
        ):
            failures.append(
                "executor refusal was not audited"
            )

    return failures


def verify_scientific_root(
    repo: Path,
    engine: Path,
    lock: dict[str, object],
    tag_commit: str,
) -> tuple[list[str], bool]:
    failures = []
    run_package = (
        engine.parent
        / "scientific_run_prelock_v1"
    )
    run_config = json.loads(
        (
            run_package
            / "D8A_SCIENTIFIC_RUN_CONFIG.json"
        ).read_text(encoding="utf-8")
    )
    scientific_root = (
        repo
        / run_config[
            "output_root_relative_to_repo"
        ]
    )

    if not scientific_root.exists():
        return failures, False

    metadata_path = (
        scientific_root / "RUN_METADATA.json"
    )
    if not metadata_path.is_file():
        failures.append(
            "scientific output root lacks RUN_METADATA.json"
        )
        return failures, True

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )
    if metadata.get("label") != "SCIENTIFIC":
        failures.append(
            "scientific run metadata label mismatch"
        )
    if metadata.get(
        "runner_engine_lock_id"
    ) != lock["lock_id"]:
        failures.append(
            "scientific run lock ID mismatch"
        )
    if metadata.get(
        "runner_engine_lock_tag"
    ) != lock["lock_tag"]:
        failures.append(
            "scientific run lock tag mismatch"
        )
    if metadata.get(
        "runner_engine_lock_commit"
    ) != tag_commit:
        failures.append(
            "scientific run lock commit mismatch"
        )
    if not metadata.get(
        "scientific_simulation_run",
        False,
    ):
        failures.append(
            "scientific run metadata is not marked scientific"
        )

    return failures, True


def main() -> None:
    engine = Path(__file__).resolve().parent
    repo = repository_root(engine)
    failures = []

    lock_path = engine / LOCK_NAME
    manifest_path = engine / MANIFEST_NAME

    if not lock_path.is_file():
        failures.append(
            "runner-engine lock record is missing"
        )
    if not manifest_path.is_file():
        failures.append(
            "runner-engine manifest is missing"
        )

    if failures:
        print(
            "D8-A scientific runner-engine "
            "verification: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    lock = json.loads(
        lock_path.read_text(encoding="utf-8")
    )
    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    if lock.get("lock_id") != LOCK_ID:
        failures.append(
            "unexpected lock ID"
        )
    if lock.get("lock_tag") != LOCK_TAG:
        failures.append(
            "unexpected lock tag"
        )
    if not lock.get("runner_engine_locked", False):
        failures.append(
            "runner engine is not marked locked"
        )
    if not lock.get(
        "scientific_execution_authorized",
        False,
    ):
        failures.append(
            "scientific execution is not authorized"
        )
    if lock.get("scientific_simulation_run", False):
        failures.append(
            "lock record is marked post-execution"
        )

    if sha256(manifest_path) != lock.get(
        "manifest_sha256"
    ):
        failures.append(
            "manifest SHA-256 does not match lock record"
        )
    if int(
        lock.get("manifest_file_count", -1)
    ) != int(
        manifest.get("file_count", -2)
    ):
        failures.append(
            "manifest count does not match lock record"
        )

    failures.extend(
        verify_manifest(engine, manifest)
    )
    failures.extend(
        verify_audit_records(engine)
    )

    tag_result = run(
        [
            "git",
            "rev-parse",
            "--verify",
            f"{LOCK_TAG}^{{commit}}",
        ],
        cwd=repo,
    )
    tag_commit = ""
    if tag_result.returncode != 0:
        failures.append(
            f"annotated lock tag is absent: {LOCK_TAG}"
        )
    else:
        tag_commit = tag_result.stdout.strip()
        head_result = run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
        )
        if head_result.stdout.strip() != tag_commit:
            failures.append(
                "HEAD does not equal the lock-tag commit"
            )

        tag_type = run(
            ["git", "cat-file", "-t", LOCK_TAG],
            cwd=repo,
        )
        if (
            tag_type.returncode != 0
            or tag_type.stdout.strip() != "tag"
        ):
            failures.append(
                "lock tag is not annotated"
            )

    engine_relative = engine.relative_to(repo)
    status = run(
        [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            str(engine_relative),
        ],
        cwd=repo,
    )
    if status.stdout.strip():
        failures.append(
            "runner-engine working tree is not clean"
        )

    implementation = (
        engine.parent / "implementation_v1"
    )
    implementation_check = run(
        [
            sys.executable,
            str(
                implementation
                / "verify_d8a_generalized_implementation_lock.py"
            ),
        ],
        cwd=repo,
    )
    implementation_output = (
        implementation_check.stdout
        + implementation_check.stderr
    )
    if (
        implementation_check.returncode != 0
        or "verification: PASS"
        not in implementation_output
    ):
        failures.append(
            "generalized implementation verifier failed"
        )

    run_package = (
        engine.parent
        / "scientific_run_prelock_v1"
    )
    package_check = run(
        [
            sys.executable,
            str(
                run_package
                / "verify_d8a_scientific_run_package.py"
            ),
        ],
        cwd=repo,
    )
    package_output = (
        package_check.stdout
        + package_check.stderr
    )
    if (
        package_check.returncode != 0
        or "verification: PASS"
        not in package_output
    ):
        failures.append(
            "scientific-run package verifier failed"
        )

    tests = run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(engine / "tests"),
            "-p",
            "test_*.py",
            "-v",
        ],
        cwd=repo,
    )
    test_output = (
        tests.stdout + tests.stderr
    )
    if (
        tests.returncode != 0
        or f"Ran {EXPECTED_TEST_COUNT} tests"
        not in test_output
        or "OK" not in test_output
    ):
        failures.append(
            "runner-engine tests did not report 82/82 PASS"
        )

    if tag_commit:
        root_failures, root_exists = (
            verify_scientific_root(
                repo,
                engine,
                lock,
                tag_commit,
            )
        )
        failures.extend(root_failures)
    else:
        root_exists = False

    if failures:
        print("=" * 80)
        print(
            "D8-A scientific runner-engine verification"
        )
        print("=" * 80)
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        print(
            "Scientific execution authorized: NO"
        )
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A scientific runner-engine verification"
    )
    print("=" * 80)
    print("Status: PASS")
    print(f"Lock ID: {LOCK_ID}")
    print(f"Lock tag: {LOCK_TAG}")
    print(f"Lock commit: {tag_commit}")
    print(
        f"Manifest files verified: "
        f"{manifest['file_count']}"
    )
    print("Runner-engine tests: 82/82 PASS")
    print(
        "Generalized implementation lock: PASS"
    )
    print(
        "Scientific-run package prelock: PASS"
    )
    print(
        "Engineering evidence records: PASS"
    )
    print("Runner engine locked: YES")
    print(
        "Scientific execution authorized: YES"
    )
    print(
        "Scientific output root present: "
        + ("YES" if root_exists else "NO")
    )
    print(
        "Scientific simulation run: "
        + ("YES" if root_exists else "NO")
    )


if __name__ == "__main__":
    main()
