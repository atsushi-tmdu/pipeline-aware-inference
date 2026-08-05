from __future__ import annotations

import unittest

from d8a_runner_statistics import (
    tess_contrast_record,
    tess_status_is_valid,
    tess_value_record,
)


class TessBoundaryPolicyTests(
    unittest.TestCase
):
    def test_finite_value(self) -> None:
        record = tess_value_record(
            0.2,
            0.05,
        )
        self.assertEqual(
            record["status"],
            "finite",
        )
        self.assertIsInstance(
            record["value"],
            float,
        )

    def test_probability_one_is_infinite(
        self,
    ) -> None:
        record = tess_value_record(
            1.0,
            0.05,
        )
        self.assertEqual(
            record["status"],
            "positive_infinity",
        )
        self.assertIsNone(
            record["value"]
        )

    def test_positive_infinite_contrast(
        self,
    ) -> None:
        record = tess_contrast_record(
            1.0,
            0.2,
            0.05,
        )
        self.assertEqual(
            record["status"],
            "positive_infinity",
        )

    def test_negative_infinite_contrast(
        self,
    ) -> None:
        record = tess_contrast_record(
            0.2,
            1.0,
            0.05,
        )
        self.assertEqual(
            record["status"],
            "negative_infinity",
        )

    def test_both_one_is_indeterminate(
        self,
    ) -> None:
        record = tess_contrast_record(
            1.0,
            1.0,
            0.05,
        )
        self.assertEqual(
            record["status"],
            "indeterminate_both_one",
        )

    def test_all_statuses_validate(self) -> None:
        for adaptive, comparator in (
            (0.2, 0.1),
            (1.0, 0.2),
            (0.2, 1.0),
            (1.0, 1.0),
        ):
            self.assertTrue(
                tess_status_is_valid(
                    tess_contrast_record(
                        adaptive,
                        comparator,
                        0.05,
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
