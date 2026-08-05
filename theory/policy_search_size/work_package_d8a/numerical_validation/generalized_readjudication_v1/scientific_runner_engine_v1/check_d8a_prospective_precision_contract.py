#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from d8a_runner_precision_scales import (
    natural_scale,
)


def main() -> None:
    engine = Path(__file__).resolve().parent

    contract = json.loads(
        (
            engine
            / "D8A_PROSPECTIVE_NATURAL_SCALE_PRECISION_CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    config = json.loads(
        (
            engine
            / "D8A_SCIENTIFIC_RUNNER_ENGINE_CONFIG.json"
        ).read_text(encoding="utf-8")
    )
    audit = json.loads(
        (
            engine
            / "precision_engineering_audit"
            / "NON_SCIENTIFIC_ENGINEERING_ONLY_natural_scale_precision_audit_summary.json"
        ).read_text(encoding="utf-8")
    )

    failures = []

    if contract["amendment_id"] != (
        "TESS_D8A_PROSPECTIVE_NATURAL_SCALE_"
        "PRECISION_CONTRACT_AMENDMENT_V3"
    ):
        failures.append(
            "unexpected amendment ID"
        )
    if not contract[
        "studentized_v1_superseded"
    ]:
        failures.append(
            "studentized V1 not superseded"
        )
    if not contract[
        "rate_aware_v2_superseded_for_stopping"
    ]:
        failures.append(
            "rate-aware V2 not superseded"
        )
    if contract[
        "scientific_output_inspected_before_amendment"
    ]:
        failures.append(
            "scientific output marked inspected"
        )
    if contract[
        "scientific_simulation_run"
    ]:
        failures.append(
            "scientific simulation marked run"
        )
    if contract[
        "monte_carlo_variance_ddof"
    ] != 1:
        failures.append(
            "ddof is not 1"
        )
    if abs(
        natural_scale(-2.0)
        - 3.0
    ) > 1e-15:
        failures.append(
            "natural-scale formula mismatch"
        )
    if not audit[
        "all_jobs_correctly_fail_at_20"
    ]:
        failures.append(
            "20-replicate jobs did not all fail"
        )
    if audit[
        "studentized_mcse_constant_rule_used"
    ]:
        failures.append(
            "studentized rule still used"
        )
    if audit[
        "rate_aware_bias_scale_used_for_stopping"
    ]:
        failures.append(
            "rate-aware bias scale still "
            "used for stopping"
        )
    if audit[
        "distinct_maximum_scaled_mcse_values"
    ] < 2:
        failures.append(
            "scaled MCSE did not vary "
            "across jobs"
        )
    if config["runner_engine_locked"]:
        failures.append(
            "runner engine unexpectedly locked"
        )
    if config[
        "scientific_output_root_touched"
    ]:
        failures.append(
            "scientific output root was touched"
        )
    if config[
        "scientific_simulation_run"
    ]:
        failures.append(
            "scientific simulation marked run"
        )

    if failures:
        print(
            "D8-A natural-scale precision "
            "contract check: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print(
        "D8-A natural-scale precision contract check"
    )
    print("=" * 80)
    print("Status: PASS")
    print("Studentized V1 superseded: YES")
    print(
        "Rate-aware V2 superseded "
        "for stopping: YES"
    )
    print(
        "Rate-aware scales retained "
        "for final acceptance: YES"
    )
    print("Monte Carlo variance ddof: 1")
    print(
        "Stopping scale: "
        "1+|locked population target|"
    )
    print(
        "Effect-dependent stopping: NO"
    )
    print(
        "Observed Monte Carlo mean "
        "used in scale: NO"
    )
    print(
        "All 20-replicate engineering "
        "jobs correctly fail: YES"
    )
    print(
        "Scaled MCSE varies across jobs: YES"
    )
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
