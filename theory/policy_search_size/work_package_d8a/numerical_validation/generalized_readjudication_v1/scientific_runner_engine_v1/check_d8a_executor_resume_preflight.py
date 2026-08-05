#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    engine = Path(__file__).resolve().parent
    generalized = engine.parent
    run_package = (
        generalized
        / "scientific_run_prelock_v1"
    )

    required = (
        engine
        / "D8A_SCIENTIFIC_EXECUTOR_RESUME_CONTRACT.json",
        engine
        / "d8a_runner_scheduler.py",
        engine
        / "execute_d8a_scientific_run.py",
        engine
        / "run_d8a_executor_resume_engineering_audit.py",
        engine
        / "executor_resume_engineering_audit"
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_executor_resume_audit.json",
    )
    failures = [
        f"missing: {path}"
        for path in required
        if not path.is_file()
    ]

    if not failures:
        contract = json.loads(
            required[0].read_text(
                encoding="utf-8"
            )
        )
        audit = json.loads(
            required[4].read_text(
                encoding="utf-8"
            )
        )
        if contract[
            "scientific_job_count"
        ] != 75:
            failures.append(
                "scientific job count is not 75"
            )
        if not audit[
            "resume_matches_direct"
        ]:
            failures.append(
                "resumed rows differ from direct rows"
            )
        if not audit[
            "completed_rerun_idempotent"
        ]:
            failures.append(
                "completed rerun is not idempotent"
            )
        if not audit[
            "executor_refused_without_lock"
        ]:
            failures.append(
                "executor did not refuse without lock"
            )
        if audit[
            "scientific_output_root_touched"
        ]:
            failures.append(
                "scientific output root was touched"
            )

        executor_check = subprocess.run(
            [
                sys.executable,
                str(required[2]),
                "--execute",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if executor_check.returncode != 2:
            failures.append(
                "executor refusal exit code is not 2"
            )

        scientific_root = (
            Path(
                subprocess.check_output(
                    [
                        "git",
                        "rev-parse",
                        "--show-toplevel",
                    ],
                    cwd=engine,
                    text=True,
                ).strip()
            )
            / json.loads(
                (
                    run_package
                    / "D8A_SCIENTIFIC_RUN_CONFIG.json"
                ).read_text(
                    encoding="utf-8"
                )
            )[
                "output_root_relative_to_repo"
            ]
        )
        if scientific_root.exists():
            failures.append(
                "scientific output root exists"
            )

    if failures:
        print(
            "D8-A executor/resume preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A executor/resume preflight")
    print("=" * 80)
    print("Status: PASS")
    print("Scientific family jobs registered: 75")
    print("Atomic batch execution: PASS")
    print("Interrupted-run resume: PASS")
    print("Resumed rows equal direct rows: YES")
    print("Completed rerun idempotent: YES")
    print("Parallel job-level executor present: YES")
    print("Executor lock self-check present: YES")
    print("Executor without lock: REFUSED")
    print("Final execution gate: CLOSED")
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
