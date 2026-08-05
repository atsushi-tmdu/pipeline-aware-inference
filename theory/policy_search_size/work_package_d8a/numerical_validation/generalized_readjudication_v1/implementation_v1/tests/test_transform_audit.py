from __future__ import annotations

import unittest

import numpy as np

from d8a_policy_engine import (
    reference_thresholds,
    transform_scores,
)
from d8a_transform_audit import (
    audit_transform_invariance,
)


class TransformAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        rng = np.random.default_rng(44)
        self.reference = rng.normal(
            size=(128, 3)
        )
        self.evaluation = rng.normal(
            size=(96, 3)
        )

    def test_identity_transform(self) -> None:
        np.testing.assert_array_equal(
            transform_scores(
                self.reference,
                "identity",
            ),
            self.reference,
        )

    def test_exponential_is_strictly_monotone(self) -> None:
        values = np.array(
            [-2.0, -0.5, 0.0, 1.0]
        )
        transformed = transform_scores(
            values,
            "exp_0_35",
        )
        self.assertTrue(
            np.all(
                np.diff(transformed) > 0.0
            )
        )

    def test_sinh_is_strictly_monotone(self) -> None:
        values = np.array(
            [-2.0, -0.5, 0.0, 1.0]
        )
        transformed = transform_scores(
            values,
            "sinh_0_5",
        )
        self.assertTrue(
            np.all(
                np.diff(transformed) > 0.0
            )
        )

    def test_exponential_threshold_transforms(self) -> None:
        latent_thresholds = reference_thresholds(
            self.reference,
            0.95,
            0.70,
        )
        transformed_thresholds = reference_thresholds(
            transform_scores(
                self.reference,
                "exp_0_35",
            ),
            0.95,
            0.70,
        )
        np.testing.assert_allclose(
            transformed_thresholds,
            transform_scores(
                latent_thresholds,
                "exp_0_35",
            ),
        )

    def test_full_invariance_audit_passes(self) -> None:
        audit = audit_transform_invariance(
            self.reference,
            self.evaluation,
            0.95,
            0.70,
        )
        self.assertTrue(
            audit["passed"]
        )


if __name__ == "__main__":
    unittest.main()
