from __future__ import annotations

import unittest

import numpy as np

from d8a_seed_contract import (
    canonical_class_key,
    make_rng,
    seed_sequence,
)


CLASS = {
    "dependence": "independent",
    "candidate_probability": 0.95,
    "trigger_probability": 0.70,
}


class SeedContractTests(unittest.TestCase):
    def test_canonical_key_is_stable(self) -> None:
        self.assertEqual(
            canonical_class_key(CLASS),
            "independent|0.950000000000|0.700000000000",
        )

    def test_same_stream_reproduces(self) -> None:
        left = make_rng(
            CLASS,
            "reference",
            3,
        ).normal(size=8)
        right = make_rng(
            CLASS,
            "reference",
            3,
        ).normal(size=8)
        np.testing.assert_array_equal(
            left,
            right,
        )

    def test_different_streams_differ(self) -> None:
        left = make_rng(
            CLASS,
            "reference",
            0,
        ).normal(size=8)
        right = make_rng(
            CLASS,
            "evaluation",
            0,
        ).normal(size=8)
        self.assertFalse(
            np.array_equal(left, right)
        )

    def test_different_replicates_differ(self) -> None:
        left = make_rng(
            CLASS,
            "reference",
            0,
        ).normal(size=8)
        right = make_rng(
            CLASS,
            "reference",
            1,
        ).normal(size=8)
        self.assertFalse(
            np.array_equal(left, right)
        )

    def test_seed_sequence_has_five_spawn_words(self) -> None:
        sequence = seed_sequence(
            CLASS,
            "reference",
            4,
        )
        self.assertEqual(
            len(sequence.spawn_key),
            5,
        )


if __name__ == "__main__":
    unittest.main()
