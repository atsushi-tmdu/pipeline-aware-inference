from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from d8a_generalized_oracle import (
    all_target_reference_oracle,
    generalized_directional_approximation,
)

LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def main() -> None:
    root = Path(__file__).resolve().parent
    classes = json.loads(
        (root.parents[0] / "D8A_EQUIVALENCE_CLASS_REGISTRY.json").read_text(
            encoding="utf-8"
        )
    )
    directions = (
        np.array([1.0, 0.3, -0.8, 0.2]),
        np.array([-0.7, 1.0, 0.2, -0.2]),
        np.array([0.2, -0.8, 1.0, 0.1]),
        np.array([0.5, 0.5, 0.5, 0.0]),
    )
    rows = []
    maximum_002 = 0.0
    maximum_001 = 0.0
    maximum_kink = 0.0
    maximum_step = 0.0
    all_finite = True

    for class_record in classes:
        oracle = all_target_reference_oracle(class_record, 500, step=0.02)
        repeat = all_target_reference_oracle(class_record, 500, step=0.005)
        class_002 = 0.0
        class_001 = 0.0
        class_kink = 0.0
        class_step = 0.0
        for name, target in oracle["targets"].items():
            class_step = max(
                class_step,
                abs(
                    target["generalized_coefficient"]
                    - repeat["targets"][name]["generalized_coefficient"]
                ),
            )
            class_kink = max(
                class_kink,
                abs(target["kink_correction"] - target["declared_kink_correction"]),
            )
            for direction in directions:
                for radius in (0.002, 0.001):
                    exact, approximation = generalized_directional_approximation(
                        name, class_record, direction, radius, oracle
                    )
                    normalized = abs(exact - approximation) / radius**2
                    if radius == 0.002:
                        class_002 = max(class_002, normalized)
                    else:
                        class_001 = max(class_001, normalized)
        finite = bool(
            np.all(
                np.isfinite(
                    [
                        class_002,
                        class_001,
                        class_kink,
                        class_step,
                        *[
                            target["generalized_coefficient"]
                            for target in oracle["targets"].values()
                        ],
                    ]
                )
            )
        )
        all_finite = all_finite and finite
        maximum_002 = max(maximum_002, class_002)
        maximum_001 = max(maximum_001, class_001)
        maximum_kink = max(maximum_kink, class_kink)
        maximum_step = max(maximum_step, class_step)
        rows.append(
            {
                "label": LABEL,
                "class_id": class_record["class_id"],
                "maximum_directional_error_radius_0.002": class_002,
                "maximum_directional_error_radius_0.001": class_001,
                "maximum_kink_identity_error": class_kink,
                "maximum_step_argument_dependence": class_step,
                "all_values_finite": finite,
            }
        )

    output_dir = root / "analytic_boundary_audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "NON_SCIENTIFIC_ENGINEERING_ONLY_analytic_boundary_audit.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "label": LABEL,
        "classes_audited": len(classes),
        "all_values_finite": all_finite,
        "maximum_directional_error_radius_0.002": maximum_002,
        "maximum_directional_error_radius_0.001": maximum_001,
        "maximum_kink_identity_error": maximum_kink,
        "maximum_step_argument_dependence": maximum_step,
        "analytic_boundary_oracle_implemented": True,
        "implementation_lock_created": False,
        "scientific_execution_authorized": False,
        "scientific_simulation_run": False,
        "results_file": csv_path.name,
    }
    summary_path = output_dir / "NON_SCIENTIFIC_ENGINEERING_ONLY_analytic_boundary_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    failures = []
    if len(classes) != 25:
        failures.append("not all classes audited")
    if not all_finite:
        failures.append("nonfinite value")
    if maximum_002 > 1e-4:
        failures.append("radius 0.002 directional tolerance failure")
    if maximum_kink > 1e-10:
        failures.append("kink identity failure")
    if maximum_step > 1e-13:
        failures.append("analytic oracle depends on step argument")

    print(json.dumps(summary, indent=2, sort_keys=True))
    if failures:
        print("D8-A analytic boundary audit: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)
    print("D8-A analytic boundary audit: PASS")
    print("Implementation lock created: NO")
    print("Scientific execution authorized: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
