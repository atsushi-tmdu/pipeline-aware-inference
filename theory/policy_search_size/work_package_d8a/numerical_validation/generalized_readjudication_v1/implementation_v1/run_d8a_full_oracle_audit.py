from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from d8a_generalized_oracle import (
    all_target_reference_oracle,
    evaluation_variances,
    generalized_directional_approximation,
    tess_first_derivative,
    tess_second_derivative,
    theta_from_class,
)
from d8a_policy_engine import (
    policy_population_probabilities,
)
from d8a_seed_contract import make_rng
from d8a_transform_audit import (
    audit_transform_invariance,
)


LABEL = "NON_SCIENTIFIC_ENGINEERING_ONLY"


def run_full_oracle_audit(
    classes: list[dict[str, object]],
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    rows: list[dict[str, object]] = []
    directions = (
        np.array([1.0, 0.3, -0.8, 0.2]),
        np.array([-0.7, 1.0, 0.2, -0.2]),
        np.array([0.2, -0.8, 1.0, 0.1]),
        np.array([0.5, 0.5, 0.5, 0.0]),
    )

    maximum_covariance_negative = 0.0
    maximum_kink_identity_error = 0.0
    maximum_directional_error = 0.0
    maximum_step_discrepancy = 0.0
    all_transform_pass = True
    all_finite = True

    for class_record in classes:
        oracle = all_target_reference_oracle(
            class_record,
            reference_size=500,
            step=0.01,
        )
        oracle_audit = all_target_reference_oracle(
            class_record,
            reference_size=500,
            step=0.008,
        )
        covariance = oracle[
            "moments"
        ]["covariance"]
        minimum_eigenvalue = float(
            np.min(
                np.linalg.eigvalsh(
                    covariance
                )
            )
        )
        maximum_covariance_negative = max(
            maximum_covariance_negative,
            max(-minimum_eigenvalue, 0.0),
        )

        correlation = np.asarray(
            class_record["correlation_matrix"],
            dtype=float,
        )
        population = (
            policy_population_probabilities(
                theta_from_class(
                    class_record
                ),
                correlation,
            )
        )
        evaluation = evaluation_variances(
            class_record
        )

        class_max_directional = 0.0
        class_max_kink_identity = 0.0
        class_max_step = 0.0

        for target_name, target in oracle[
            "targets"
        ].items():
            audit_target = oracle_audit[
                "targets"
            ][target_name]
            kink_identity_error = abs(
                target["kink_correction"]
                - target[
                    "declared_kink_correction"
                ]
            )
            class_max_kink_identity = max(
                class_max_kink_identity,
                kink_identity_error,
            )
            denominator = max(
                1.0,
                abs(
                    target[
                        "generalized_coefficient"
                    ]
                ),
                abs(
                    audit_target[
                        "generalized_coefficient"
                    ]
                ),
            )
            step_discrepancy = abs(
                target[
                    "generalized_coefficient"
                ]
                - audit_target[
                    "generalized_coefficient"
                ]
            ) / denominator
            class_max_step = max(
                class_max_step,
                step_discrepancy,
            )

            for direction in directions:
                exact, approximation = (
                    generalized_directional_approximation(
                        target_name,
                        class_record,
                        direction,
                        radius=0.001,
                        oracle=oracle,
                    )
                )
                normalized = abs(
                    exact - approximation
                ) / 0.001**2
                class_max_directional = max(
                    class_max_directional,
                    normalized,
                )

        reference_rng = make_rng(
            class_record,
            "full_oracle_audit_reference",
            0,
        )
        evaluation_rng = make_rng(
            class_record,
            "full_oracle_audit_evaluation",
            0,
        )
        latent_reference = (
            reference_rng.multivariate_normal(
                np.zeros(3),
                correlation,
                size=64,
            )
        )
        latent_evaluation = (
            evaluation_rng.multivariate_normal(
                np.zeros(3),
                correlation,
                size=64,
            )
        )
        transform_audit = (
            audit_transform_invariance(
                latent_reference,
                latent_evaluation,
                float(
                    class_record[
                        "candidate_probability"
                    ]
                ),
                float(
                    class_record[
                        "trigger_probability"
                    ]
                ),
            )
        )
        all_transform_pass = (
            all_transform_pass
            and bool(
                transform_audit["passed"]
            )
        )

        adaptive = oracle["targets"][
            "adaptive_probability"
        ]
        comparator = oracle["targets"][
            "comparator_probability"
        ]
        adaptive_probability = float(
            population[
                "adaptive_probability"
            ]
        )
        comparator_probability = float(
            population[
                "comparator_probability"
            ]
        )

        tess_values: dict[str, float] = {}
        for alpha in (0.01, 0.05):
            tess_reference = float(
                tess_first_derivative(
                    adaptive_probability,
                    alpha,
                )
                * adaptive[
                    "generalized_coefficient"
                ]
                + 0.5
                * tess_second_derivative(
                    adaptive_probability,
                    alpha,
                )
                * (
                    adaptive["gradient"]
                    @ covariance
                    @ adaptive["gradient"]
                )
                - tess_first_derivative(
                    comparator_probability,
                    alpha,
                )
                * comparator[
                    "generalized_coefficient"
                ]
                - 0.5
                * tess_second_derivative(
                    comparator_probability,
                    alpha,
                )
                * (
                    comparator["gradient"]
                    @ covariance
                    @ comparator["gradient"]
                )
            )
            tess_evaluation = float(
                0.5
                * tess_second_derivative(
                    adaptive_probability,
                    alpha,
                )
                * evaluation[
                    "adaptive_variance"
                ]
                - tess_first_derivative(
                    comparator_probability,
                    alpha,
                )
                * population["delta_pi"]
                - 0.5
                * tess_second_derivative(
                    comparator_probability,
                    alpha,
                )
                * evaluation[
                    "comparator_variance"
                ]
            )
            tess_values[
                f"tess_reference_alpha_{alpha:.2f}"
            ] = tess_reference
            tess_values[
                f"tess_evaluation_alpha_{alpha:.2f}"
            ] = tess_evaluation

        finite_values = [
            population["delta_pi"],
            evaluation["adaptive_variance"],
            evaluation["comparator_variance"],
            minimum_eigenvalue,
            class_max_kink_identity,
            class_max_step,
            class_max_directional,
            *tess_values.values(),
            *[
                target[
                    "generalized_coefficient"
                ]
                for target in oracle[
                    "targets"
                ].values()
            ],
        ]
        class_finite = bool(
            np.all(
                np.isfinite(finite_values)
            )
        )
        all_finite = (
            all_finite
            and class_finite
        )

        maximum_kink_identity_error = max(
            maximum_kink_identity_error,
            class_max_kink_identity,
        )
        maximum_step_discrepancy = max(
            maximum_step_discrepancy,
            class_max_step,
        )
        maximum_directional_error = max(
            maximum_directional_error,
            class_max_directional,
        )

        rows.append(
            {
                "label": LABEL,
                "class_id": class_record["class_id"],
                "class_role": class_record["class_role"],
                "dependence": class_record["dependence"],
                "candidate_probability": (
                    class_record[
                        "candidate_probability"
                    ]
                ),
                "trigger_probability": (
                    class_record[
                        "trigger_probability"
                    ]
                ),
                "minimum_covariance_eigenvalue": (
                    minimum_eigenvalue
                ),
                "maximum_kink_identity_error": (
                    class_max_kink_identity
                ),
                "maximum_step_discrepancy": (
                    class_max_step
                ),
                "maximum_directional_normalized_error": (
                    class_max_directional
                ),
                "transform_invariance_pass": (
                    transform_audit["passed"]
                ),
                "all_values_finite": class_finite,
                "delta_generalized_coefficient": (
                    oracle["targets"][
                        "delta_pi"
                    ][
                        "generalized_coefficient"
                    ]
                ),
                **tess_values,
            }
        )

    csv_path = (
        output_dir
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_full_oracle_audit.csv"
    )
    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(
                rows[0].keys()
            ),
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "label": LABEL,
        "scientific_simulation_run": False,
        "classes_audited": len(classes),
        "all_values_finite": all_finite,
        "all_transform_invariance_pass": (
            all_transform_pass
        ),
        "maximum_covariance_negative_part": (
            maximum_covariance_negative
        ),
        "maximum_kink_identity_error": (
            maximum_kink_identity_error
        ),
        "maximum_step_discrepancy": (
            maximum_step_discrepancy
        ),
        "maximum_directional_normalized_error": (
            maximum_directional_error
        ),
        "implementation_lock_created": False,
        "scientific_execution_authorized": False,
        "results_file": csv_path.name,
    }
    (
        output_dir
        / "NON_SCIENTIFIC_ENGINEERING_ONLY_full_oracle_audit_summary.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    root = Path(__file__).resolve().parent
    classes = json.loads(
        (
            root.parents[0]
            / "D8A_EQUIVALENCE_CLASS_REGISTRY.json"
        ).read_text(encoding="utf-8")
    )
    summary = run_full_oracle_audit(
        classes,
        root / "full_oracle_audit",
    )
    print(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
    )

    fatal = []
    if summary["classes_audited"] != 25:
        fatal.append(
            "not all 25 classes were audited"
        )
    if not summary["all_values_finite"]:
        fatal.append(
            "nonfinite oracle value"
        )
    if not summary[
        "all_transform_invariance_pass"
    ]:
        fatal.append(
            "transform invariance failure"
        )
    if summary[
        "maximum_covariance_negative_part"
    ] > 1e-7:
        fatal.append(
            "quantile covariance PSD failure"
        )
    if summary[
        "maximum_kink_identity_error"
    ] > 1e-10:
        fatal.append(
            "kink identity failure"
        )

    if fatal:
        print(
            "D8-A full oracle audit: FAIL"
        )
        for failure in fatal:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(
        "D8-A full oracle audit: PASS"
    )
    print(
        "Scientific interpretation performed: NO"
    )
    print(
        "Implementation lock created: NO"
    )
    print(
        "Scientific execution authorized: NO"
    )
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
