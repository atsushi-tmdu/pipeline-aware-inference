from __future__ import annotations

import math
import unittest

from d8a_runner_precision import (
    evaluate_job_precision,
    scalar_mean_precision,
    tess_contrast_precision,
)
from d8a_runner_precision_scales import (
    natural_scale,
)


TARGET = 0.03


class NaturalScalePrecisionTests(
    unittest.TestCase
):
    def test_natural_scale_zero(self) -> None:
        self.assertEqual(
            natural_scale(0.0),
            1.0,
        )

    def test_natural_scale_negative(self) -> None:
        self.assertEqual(
            natural_scale(-2.0),
            3.0,
        )

    def test_ddof_one_mcse(self) -> None:
        result = scalar_mean_precision(
            [0.0, 2.0],
            scale_denominator=1.0,
            target=TARGET,
        )
        self.assertAlmostEqual(
            result.sample_sd,
            math.sqrt(2.0),
        )
        self.assertAlmostEqual(
            result.mcse,
            1.0,
        )

    def test_zero_variance_passes(self) -> None:
        result = scalar_mean_precision(
            [2.0] * 10,
            scale_denominator=3.0,
            target=TARGET,
        )
        self.assertTrue(
            result.precision_pass
        )
        self.assertEqual(
            result.scaled_mcse,
            0.0,
        )

    def test_scale_changes_precision(self) -> None:
        small = scalar_mean_precision(
            range(20),
            scale_denominator=1.0,
            target=TARGET,
        )
        large = scalar_mean_precision(
            range(20),
            scale_denominator=100.0,
            target=TARGET,
        )
        self.assertFalse(
            small.precision_pass
        )
        self.assertTrue(
            large.precision_pass
        )

    def test_tess_status_scale_is_one(
        self,
    ) -> None:
        records = [
            {
                "status": "finite",
                "value": float(index),
            }
            for index in range(20)
        ]
        result = tess_contrast_precision(
            records,
            finite_scale_denominator=2.0,
            target=TARGET,
        )
        self.assertEqual(
            result["status_precision"][
                "finite"
            ]["scale_denominator"],
            1.0,
        )

    def test_tess_no_finite_not_applicable(
        self,
    ) -> None:
        result = tess_contrast_precision(
            [
                {
                    "status": (
                        "positive_infinity"
                    ),
                    "value": None,
                }
                for _ in range(20)
            ],
            finite_scale_denominator=2.0,
            target=TARGET,
        )
        self.assertEqual(
            result[
                "finite_value_precision"
            ]["status"],
            (
                "not_applicable_"
                "no_finite_values"
            ),
        )

    def test_tess_single_finite_fails(
        self,
    ) -> None:
        records = [
            {
                "status": (
                    "positive_infinity"
                ),
                "value": None,
            }
            for _ in range(19)
        ]
        records.append(
            {
                "status": "finite",
                "value": 1.0,
            }
        )
        result = tess_contrast_precision(
            records,
            finite_scale_denominator=2.0,
            target=TARGET,
        )
        self.assertFalse(
            result["precision_pass"]
        )

    def test_job_uses_maximum(self) -> None:
        rows = []
        for index in range(20):
            rows.append(
                {
                    "job_id": "job",
                    "family": (
                        "evaluation_only"
                    ),
                    "replicate_index": index,
                    "points": [
                        {
                            "adaptive_estimate": (
                                float(index)
                            ),
                            "comparator_estimate": (
                                float(index + 1)
                            ),
                            "delta_hat": -1.0,
                            "tess_contrasts": {
                                "alpha_0.05": {
                                    "status": "finite",
                                    "value": (
                                        float(index)
                                    ),
                                }
                            },
                        }
                    ],
                }
            )

        scale_spec = {
            "job_id": "job",
            "family": "evaluation_only",
            "points": [
                {
                    "scalar_denominators": {
                        "adaptive_estimate": 1.0,
                        "comparator_estimate": 2.0,
                        "delta_hat": 3.0,
                    },
                    "tess_denominators": {
                        "alpha_0.05": 4.0,
                    },
                }
            ],
        }
        result = evaluate_job_precision(
            rows,
            scale_spec,
            target=TARGET,
        )
        self.assertFalse(
            result["precision_pass"]
        )
        self.assertGreater(
            result[
                "maximum_scaled_mcse"
            ],
            0.0,
        )

    def test_scale_spec_mismatch_rejected(
        self,
    ) -> None:
        rows = [
            {
                "job_id": "job",
                "family": "reference_only",
                "points": [
                    {
                        "adaptive_probability": 0.1,
                        "comparator_probability": 0.1,
                        "delta_pi": 0.0,
                        "tess_contrasts": {},
                    }
                ],
            }
            for _ in range(2)
        ]
        with self.assertRaises(
            ValueError
        ):
            evaluate_job_precision(
                rows,
                {
                    "job_id": "other",
                    "family": "reference_only",
                    "points": [],
                },
                target=TARGET,
            )

    def test_nonpositive_denominator_rejected(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            scalar_mean_precision(
                [1.0, 2.0],
                scale_denominator=0.0,
                target=TARGET,
            )

    def test_precision_not_equal_inverse_sqrt_r(
        self,
    ) -> None:
        result = scalar_mean_precision(
            range(20),
            scale_denominator=2.0,
            target=TARGET,
        )
        self.assertNotAlmostEqual(
            result.scaled_mcse,
            1.0 / math.sqrt(20),
        )

    def test_target_must_be_positive(self) -> None:
        with self.assertRaises(
            ValueError
        ):
            scalar_mean_precision(
                [1.0, 2.0],
                scale_denominator=1.0,
                target=0.0,
            )


if __name__ == "__main__":
    unittest.main()
