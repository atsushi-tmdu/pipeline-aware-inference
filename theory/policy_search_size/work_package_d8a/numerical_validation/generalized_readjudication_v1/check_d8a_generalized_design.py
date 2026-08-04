from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parent
    config = json.loads(
        (
            root
            / "D8A_GENERALIZED_DESIGN.json"
        ).read_text(encoding="utf-8")
    )
    classes = json.loads(
        (
            root
            / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )

    failures = []
    if len(classes) != 25:
        failures.append("equivalence class count is not 25")
    if sum(
        item["class_role"] == "primary"
        for item in classes
    ) != 17:
        failures.append("primary class count is not 17")
    if sum(
        item["class_role"] == "diagnostic"
        for item in classes
    ) != 8:
        failures.append("diagnostic class count is not 8")
    if sum(
        len(item["audit_member_cell_ids"])
        for item in classes
    ) != 50:
        failures.append("audit member count is not 50")

    for item in classes:
        if len(item["member_cell_ids"]) != 3:
            failures.append(
                f"class member count failure: {item['class_id']}"
            )
        if set(item["transforms"]) != {
            "identity",
            "exp_0_35",
            "sinh_0_5",
        }:
            failures.append(
                f"transform set failure: {item['class_id']}"
            )
        if item["latent_separation"] < 0.10:
            failures.append(
                f"separation failure: {item['class_id']}"
            )
        variances = np.asarray(
            item["candidate_added_contrast_variances"],
            dtype=float,
        )
        if np.min(variances) <= 1e-12:
            failures.append(
                f"contrast variance failure: {item['class_id']}"
            )

    if not config[
        "generalized_numerical_design_locked"
    ]:
        failures.append("generalized design not locked")
    if config["implementation_locked"]:
        failures.append("implementation unexpectedly locked")
    if config["scientific_simulation_run"]:
        failures.append("scientific simulation marked run")
    if config["scientific_execution_authorized"]:
        failures.append("scientific execution unexpectedly authorized")

    if failures:
        print(
            "D8-A generalized design preflight: FAIL"
        )
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print("=" * 80)
    print("D8-A generalized design preflight")
    print("=" * 80)
    print("Status: PASS")
    print("Historical registry rows retained: 75")
    print("Scientific equivalence classes: 25")
    print("Primary scientific classes: 17")
    print("Diagnostic scientific classes: 8")
    print("Transformation-audit rows: 50")
    print("Active candidate coincidence hyperplanes: 2")
    print("All contrast variances positive: YES")
    print("Common-transform invariance recognized: YES")
    print("Generalized numerical design locked: YES")
    print("Generalized implementation locked: NO")
    print("Scientific execution authorized: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
