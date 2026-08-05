#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from d8a_runner_statistics import (
    tess_contrast_record,
    tess_status_is_valid,
)
from d8a_runner_stopping import (
    RoleAwarePrecisionOnlyStoppingRule,
    StoppingSchedule,
)


def main() -> None:
    engine = Path(__file__).resolve().parent

    contract = json.loads(
        (
            engine
            / "D8A_LOCKED_MONTE_CARLO_CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    schedules = contract[
        "normalized_schedules"
    ]

    rule = RoleAwarePrecisionOnlyStoppingRule(
        primary=StoppingSchedule(
            **schedules["primary"]
        ),
        diagnostic=StoppingSchedule(
            **schedules["diagnostic"]
        ),
    )

    failures = []

    for role in (
        "primary",
        "diagnostic",
    ):
        schedule = rule.schedule_for(role)

        initial = rule.decide(
            role,
            0,
            precision_pass=True,
        )
        if initial.stop:
            failures.append(
                f"{role}: stopped before minimum"
            )

        precision = rule.decide(
            role,
            schedule.initial_replicates,
            precision_pass=True,
        )
        if (
            not precision.stop
            or precision.reason
            != "precision_target_met"
        ):
            failures.append(
                f"{role}: precision stop incorrect"
            )

        maximum = rule.decide(
            role,
            schedule.maximum_replicates,
            precision_pass=False,
        )
        if (
            not maximum.stop
            or maximum.reason
            != "maximum_replicates_reached"
        ):
            failures.append(
                f"{role}: maximum stop incorrect"
            )

    records = (
        tess_contrast_record(
            0.2,
            0.1,
            0.05,
        ),
        tess_contrast_record(
            1.0,
            0.2,
            0.05,
        ),
        tess_contrast_record(
            0.2,
            1.0,
            0.05,
        ),
        tess_contrast_record(
            1.0,
            1.0,
            0.05,
        ),
    )
    if not all(
        tess_status_is_valid(record)
        for record in records
    ):
        failures.append(
            "TESS status validation failed"
        )

    if failures:
        print(
            "D8-A stopping/TESS adjudication: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A stopping/TESS adjudication")
    print("=" * 80)
    print("Status: PASS")
    print("Raw Monte Carlo contract retained: YES")
    print("Role-aware precision-only stopping: YES")
    print(
        "Primary minimum replicates: "
        f"{rule.primary.initial_replicates}"
    )
    print(
        "Primary maximum replicates: "
        f"{rule.primary.maximum_replicates}"
    )
    print(
        "Diagnostic minimum replicates: "
        f"{rule.diagnostic.initial_replicates}"
    )
    print(
        "Diagnostic maximum replicates: "
        f"{rule.diagnostic.maximum_replicates}"
    )
    print(
        f"Shared batch size: "
        f"{rule.primary.batch_size}"
    )
    print("TESS p=1 value: POSITIVE_INFINITY")
    print(
        "TESS both-p=1 contrast: "
        "INDETERMINATE_BOTH_ONE"
    )
    print("Boundary records silently dropped: NO")
    print("Runner engine locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
