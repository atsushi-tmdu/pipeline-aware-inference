from __future__ import annotations

import math
import unittest

from d8a_runner_statistics import (
    finite_n_delta_target,
    tess_contrast,
    tess_value,
)


class StatisticsTests(unittest.TestCase):
    def test_tess_at_alpha_equals_one(self) -> None:
        self.assertAlmostEqual(
            tess_value(0.05, 0.05),
            1.0,
        )

    def test_tess_zero(self) -> None:
        self.assertEqual(
            tess_value(0.0, 0.05),
            0.0,
        )

    def test_tess_one_is_undefined(self) -> None:
        self.assertIsNone(
            tess_value(1.0, 0.05)
        )

    def test_tess_matches_log_formula(self) -> None:
        self.assertAlmostEqual(
            tess_value(0.2, 0.05),
            math.log1p(-0.2)
            / math.log1p(-0.05),
        )

    def test_tess_contrast_identity(self) -> None:
        self.assertAlmostEqual(
            tess_contrast(
                0.2,
                0.1,
                0.05,
            ),
            tess_value(0.2, 0.05)
            - tess_value(0.1, 0.05),
        )

    def test_finite_n_target(self) -> None:
        self.assertAlmostEqual(
            finite_n_delta_target(
                0.04,
                100,
            ),
            0.0396,
        )


if __name__ == "__main__":
    unittest.main()
