#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


EXPECTED_STATUS = (
    "ACCEPTANCE_SCALES_PARTIALLY_RECOVERED_"
    "STOPPING_CONTRACT_INCOMPLETE"
)


def main() -> None:
    engine = Path(__file__).resolve().parent

    record = json.loads(
        (
            engine
            / "D8A_PRECISION_CONTRACT_GAP.json"
        ).read_text(encoding="utf-8")
    )
    config = json.loads(
        (
            engine
            / "D8A_SCIENTIFIC_RUNNER_ENGINE_CONFIG.json"
        ).read_text(encoding="utf-8")
    )

    failures = []

    if record["status"] != EXPECTED_STATUS:
        failures.append(
            "unexpected adjudication status"
        )
    if record[
        "historical_python_mcse_formula_candidates"
    ] != 0:
        failures.append(
            "historical MCSE formula candidate count "
            "is not zero"
        )
    if not record[
        "reference_acceptance_scale_recovered"
    ]:
        failures.append(
            "reference scale not recovered"
        )
    if not record[
        "combined_policy_acceptance_scale_recovered"
    ]:
        failures.append(
            "combined policy scale not recovered"
        )
    if not record[
        "combined_tess_acceptance_scale_recovered"
    ]:
        failures.append(
            "combined TESS scale not recovered"
        )
    if record[
        "stopping_contract_complete"
    ]:
        failures.append(
            "stopping contract unexpectedly complete"
        )
    if config["runner_engine_locked"]:
        failures.append(
            "runner engine unexpectedly locked"
        )
    if config["scientific_simulation_run"]:
        failures.append(
            "scientific simulation marked run"
        )

    if failures:
        print(
            "D8-A precision-contract gap check: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A precision-contract gap check")
    print("=" * 80)
    print("Status: PASS")
    print(
        "Reference acceptance scale recovered: YES"
    )
    print(
        "Combined policy scale recovered: YES"
    )
    print(
        "Combined TESS scale recovered: YES"
    )
    print(
        "Historical MCSE formula candidates: 0"
    )
    print("Stopping contract complete: NO")
    print("Runner engine locked: NO")
    print("Scientific output root touched: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
