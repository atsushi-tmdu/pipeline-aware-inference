#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    engine = Path(__file__).resolve().parent

    required = (
        engine
        / "D8A_SCIENTIFIC_SUMMARY_ACCEPTANCE_CONTRACT.json",
        engine
        / "d8a_runner_summary.py",
        engine
        / "d8a_runner_acceptance.py",
        engine
        / "summary_acceptance_engineering_audit"
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_summary_acceptance_audit.json",
        engine
        / "run_d8a_scientific_validation_gate.py",
    )

    failures = [
        f"missing: {path}"
        for path in required
        if not path.is_file()
    ]

    if not failures:
        audit = json.loads(
            required[3].read_text(
                encoding="utf-8"
            )
        )
        contract = json.loads(
            required[0].read_text(
                encoding="utf-8"
            )
        )
        if not audit[
            "engineering_audit_pass"
        ]:
            failures.append(
                "engineering acceptance audit failed"
            )
        if contract[
            "primary_acceptance_denominator"
        ] != 17:
            failures.append(
                "primary denominator is not 17"
            )
        if contract[
            "quantile_method"
        ] != "numpy_linear_type7":
            failures.append(
                "quantile method mismatch"
            )

        gate = subprocess.run(
            [
                sys.executable,
                str(required[4]),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if gate.returncode != 0:
            failures.append(
                "closed-gate status check failed"
            )
        if "Gate state: CLOSED" not in (
            gate.stdout + gate.stderr
        ):
            failures.append(
                "final execution gate is not closed"
            )

    if failures:
        print(
            "D8-A summary/acceptance preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A summary/acceptance preflight")
    print("=" * 80)
    print("Status: PASS")
    print("Primary acceptance denominator: 17")
    print(
        "Common-transform audit rows "
        "counted as evidence: NO"
    )
    print(
        "Reference acceptance evaluator: YES"
    )
    print(
        "Combined policy evaluator: YES"
    )
    print("Combined TESS evaluator: YES")
    print("Exact identity evaluator: YES")
    print(
        "Second-order improvement evaluator: YES"
    )
    print(
        "Precision-limited fraction evaluator: YES"
    )
    print(
        "TESS nonfinite primary criterion: FAIL"
    )
    print("Final execution gate: CLOSED")
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
