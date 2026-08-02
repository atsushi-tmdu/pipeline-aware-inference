from __future__ import annotations

import json
import unittest
from pathlib import Path
import tempfile

import numpy as np

from simulations.ess.support2_generate_model_banks_v1 import candidate_seed, permuted_labels, validate_bank


class Support2ValidationTests(unittest.TestCase):
    def setUp(self):
        config_path = Path("configs/ess/support2_validation_v1.json")
        self.config = json.loads(config_path.read_text(encoding="utf-8"))

    def test_locked_candidate_counts(self):
        candidates = self.config["candidate_library"]
        self.assertEqual(len(candidates), 20)
        self.assertEqual(sum(bool(c["base"]) for c in candidates), 7)
        self.assertEqual([c["order"] for c in candidates], list(range(1, 21)))
        self.assertEqual(len({c["name"] for c in candidates}), 20)

    def test_permutation_preserves_counts_and_is_deterministic(self):
        y = np.array([0, 1, 0, 1, 1, 0, 0, 1])
        a = permuted_labels(y, 123)
        b = permuted_labels(y, 123)
        self.assertTrue(np.array_equal(a, b))
        self.assertEqual(int(a.sum()), int(y.sum()))

    def test_candidate_seed_is_stable_and_candidate_specific(self):
        self.assertEqual(candidate_seed(10, 2, 3), candidate_seed(10, 2, 3))
        self.assertNotEqual(candidate_seed(10, 2, 3), candidate_seed(10, 2, 4))


if __name__ == "__main__":
    unittest.main()
