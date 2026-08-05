from __future__ import annotations

import unittest

from d8a_runner_acceptance import (
    aggregate_combined_policy_acceptance,
    aggregate_exact_identity,
    aggregate_precision_limited,
    aggregate_reference_acceptance,
    aggregate_tess_acceptance,
    adjusted_normalized_residual,
    combined_policy_metric,
    combined_tess_metric,
    exact_identity_check,
    formal_acceptance,
    reference_policy_metric,
    second_order_improved,
)
from d8a_runner_summary import (
    scalar_summary,
    tess_summary,
)


def class_records(
    key: str,
    value: float,
) -> list[dict[str, object]]:
    return [
        {
            "class_id": (
                f"d8a-primary-{index:03d}"
            ),
            key: value,
        }
        for index in range(17)
    ]


class SummaryAcceptanceTests(
    unittest.TestCase
):
    def test_scalar_summary_ddof_one(
        self,
    ) -> None:
        result = scalar_summary(
            [0.0, 2.0],
            target=1.0,
        )
        self.assertAlmostEqual(
            result["sample_sd"],
            2.0**0.5,
        )
        self.assertAlmostEqual(
            result["mcse"],
            1.0,
        )

    def test_tess_summary_counts(
        self,
    ) -> None:
        result = tess_summary(
            [
                {
                    "status": "finite",
                    "value": 1.0,
                },
                {
                    "status": (
                        "positive_infinity"
                    ),
                    "value": None,
                },
            ],
            target=1.0,
        )
        self.assertEqual(
            result["nonfinite_count"],
            1,
        )

    def test_adjusted_residual_zero(
        self,
    ) -> None:
        result = adjusted_normalized_residual(
            observed_mean=1.0,
            target=1.0,
            predicted_bias=0.0,
            mcse=0.1,
            scale=1.0,
            z_star=2.0,
        )
        self.assertEqual(
            result["normalized_residual"],
            0.0,
        )

    def test_reference_metric(self) -> None:
        result = reference_policy_metric(
            observed_mean=0.1,
            mcse=0.0,
            population_delta=0.0,
            reference_coefficient=1.0,
            reference_size=100,
            z_star=2.0,
        )
        self.assertAlmostEqual(
            result["normalized_residual"],
            4.5,
        )

    def test_combined_policy_interaction(
        self,
    ) -> None:
        result = combined_policy_metric(
            observed_mean=0.0,
            mcse=0.0,
            population_delta=0.1,
            reference_coefficient=0.2,
            reference_size=100,
            evaluation_size=100,
            z_star=2.0,
        )
        self.assertGreaterEqual(
            result["normalized_residual"],
            0.0,
        )

    def test_combined_tess_metric(
        self,
    ) -> None:
        result = combined_tess_metric(
            observed_mean=0.0,
            mcse=0.0,
            population_tess=0.0,
            reference_coefficient=0.2,
            evaluation_coefficient=-0.1,
            reference_size=100,
            evaluation_size=100,
            z_star=2.0,
        )
        self.assertGreaterEqual(
            result["normalized_residual"],
            0.0,
        )

    def test_exact_identity_pass(
        self,
    ) -> None:
        self.assertTrue(
            exact_identity_check(
                observed_mean=1.0,
                target=1.0,
                mcse=0.1,
                z_star=2.0,
            )["passed"]
        )

    def test_exact_identity_fail(
        self,
    ) -> None:
        self.assertFalse(
            exact_identity_check(
                observed_mean=2.0,
                target=1.0,
                mcse=0.1,
                z_star=2.0,
            )["passed"]
        )

    def test_second_order_improvement(
        self,
    ) -> None:
        self.assertTrue(
            second_order_improved(
                observed_bias=0.2,
                first_order_prediction=0.0,
                second_order_prediction=0.15,
            )
        )

    def test_reference_aggregation_pass(
        self,
    ) -> None:
        records = []
        for index in range(17):
            records.append(
                {
                    "class_id": (
                        f"d8a-primary-{index:03d}"
                    ),
                    "normalized_residual_B500": 0.2,
                    "normalized_residual_B10000": 0.1,
                    "second_order_improved": (
                        index < 13
                    ),
                }
            )
        result = (
            aggregate_reference_acceptance(
                records
            )
        )
        self.assertTrue(
            result["passed"]
        )

    def test_reference_requires_17(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            aggregate_reference_acceptance(
                []
            )

    def test_combined_policy_pass(
        self,
    ) -> None:
        result = (
            aggregate_combined_policy_acceptance(
                class_records(
                    "normalized_residual",
                    0.1,
                )
            )
        )
        self.assertTrue(
            result["passed"]
        )

    def test_tess_pass(
        self,
    ) -> None:
        records = []
        for alpha in (0.01, 0.05):
            for index in range(17):
                records.append(
                    {
                        "class_id": (
                            f"d8a-primary-{index:03d}"
                        ),
                        "alpha": alpha,
                        "normalized_residual": 0.2,
                        "nonfinite_record_count": 0,
                    }
                )
        result = aggregate_tess_acceptance(
            records,
            alpha_values=(0.01, 0.05),
        )
        self.assertTrue(
            result["passed"]
        )

    def test_tess_nonfinite_fails(
        self,
    ) -> None:
        records = []
        for alpha in (0.01, 0.05):
            for index in range(17):
                records.append(
                    {
                        "class_id": (
                            f"d8a-primary-{index:03d}"
                        ),
                        "alpha": alpha,
                        "normalized_residual": 0.2,
                        "nonfinite_record_count": (
                            1
                            if (
                                alpha == 0.01
                                and index == 0
                            )
                            else 0
                        ),
                    }
                )
        result = aggregate_tess_acceptance(
            records,
            alpha_values=(0.01, 0.05),
        )
        self.assertFalse(
            result["passed"]
        )

    def test_precision_one_class_passes(
        self,
    ) -> None:
        self.assertTrue(
            aggregate_precision_limited(
                ["d8a-primary-000"]
            )["passed"]
        )

    def test_precision_two_classes_fail(
        self,
    ) -> None:
        self.assertFalse(
            aggregate_precision_limited(
                [
                    "d8a-primary-000",
                    "d8a-primary-001",
                ]
            )["passed"]
        )

    def test_exact_identity_count(
        self,
    ) -> None:
        records = [
            {"passed": True}
            for _ in range(34)
        ]
        self.assertTrue(
            aggregate_exact_identity(
                records,
                expected_comparisons=34,
            )["passed"]
        )

    def test_formal_failure_propagates(
        self,
    ) -> None:
        result = formal_acceptance(
            reference={"passed": True},
            combined_policy={
                "passed": True
            },
            tess={"passed": False},
            exact_identity={
                "passed": True
            },
            precision_limited={
                "passed": True
            },
            fatal_checks_pass=True,
        )
        self.assertEqual(
            result["formal_status"],
            "FAIL",
        )


if __name__ == "__main__":
    unittest.main()
