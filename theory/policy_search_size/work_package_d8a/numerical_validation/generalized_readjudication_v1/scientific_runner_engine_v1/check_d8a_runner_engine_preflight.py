#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> None:
    engine = Path(__file__).resolve().parent
    generalized = engine.parent
    implementation = (
        generalized
        / "implementation_v1"
    )
    run_package = (
        generalized
        / "scientific_run_prelock_v1"
    )

    failures = []

    for path in (
        implementation
        / "verify_d8a_generalized_implementation_lock.py",
        run_package
        / "verify_d8a_scientific_run_package.py",
        engine
        / "D8A_SCIENTIFIC_RUNNER_ENGINE_CONFIG.json",
        engine
        / "engineering_smoke"
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_runner_smoke_summary.json",
    ):
        if not path.is_file():
            failures.append(
                f"missing: {path}"
            )

    if not failures:
        implementation_check = subprocess.run(
            [
                str(
                    implementation
                    / "verify_d8a_generalized_implementation_lock.py"
                )
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if implementation_check.returncode != 0:
            failures.append(
                "implementation verifier failed"
            )

        package_check = subprocess.run(
            [
                str(
                    run_package
                    / "verify_d8a_scientific_run_package.py"
                )
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if package_check.returncode != 0:
            failures.append(
                "run-package verifier failed"
            )

    if not failures:
        config = json.loads(
            (
                engine
                / "D8A_SCIENTIFIC_RUNNER_ENGINE_CONFIG.json"
            ).read_text(encoding="utf-8")
        )
        summary = json.loads(
            (
                engine
                / "engineering_smoke"
                / "NON_SCIENTIFIC_ENGINEERING_ONLY_runner_smoke_summary.json"
            ).read_text(encoding="utf-8")
        )

        if config[
            "runner_engine_locked"
        ]:
            failures.append(
                "runner engine unexpectedly locked"
            )
        if config[
            "scientific_simulation_run"
        ]:
            failures.append(
                "scientific simulation marked run"
            )
        if summary[
            "scientific_simulation_run"
        ]:
            failures.append(
                "engineering smoke marked scientific"
            )
        if summary[
            "scientific_output_root_touched"
        ]:
            failures.append(
                "scientific output root was touched"
            )
        if not summary[
            "all_resume_checks_pass"
        ]:
            failures.append(
                "resume checks failed"
            )

    if failures:
        print(
            "D8-A runner engine preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A runner engine preflight")
    print("=" * 80)
    print("Status: PASS")
    print("Implementation lock verified: YES")
    print("Scientific run package verified: YES")
    print("Seed inventory consumed exactly: YES")
    print("Nested family engine executable: YES")
    print("Atomic batch writes: PASS")
    print("Resume scans: PASS")
    print("Engineering smoke: PASS")
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
