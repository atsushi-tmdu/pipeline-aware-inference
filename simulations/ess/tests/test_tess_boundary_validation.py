from __future__ import annotations

import math
import unittest

from simulations.ess.ess_estimators import sidak_equivalent_ess
from simulations.ess.tess_boundary_validation import (
    exact_complete_dependence_rejection_probability,
    exact_independent_rejection_probability,
    parse_float_list,
    parse_int_list,
)


class BoundaryValidationTests(unittest.TestCase):
    def test_complete_dependence_recovers_one(self) -> None:
        for alpha in (0.20, 0.05, 0.01, 0.005):
            probability = exact_complete_dependence_rejection_probability(alpha)
            self.assertAlmostEqual(sidak_equivalent_ess(probability, alpha), 1.0, places=12)

    def test_independence_recovers_k(self) -> None:
        for k in (1, 7, 20):
            for alpha in (0.20, 0.05, 0.01, 0.005):
                probability = exact_independent_rejection_probability(alpha, k)
                self.assertAlmostEqual(sidak_equivalent_ess(probability, alpha), float(k), places=11)

    def test_probability_formula(self) -> None:
        self.assertAlmostEqual(exact_independent_rejection_probability(0.05, 2), 0.0975)
        self.assertAlmostEqual(exact_complete_dependence_rejection_probability(0.05), 0.05)

    def test_parsers(self) -> None:
        self.assertEqual(parse_float_list("0.1,0.05"), (0.1, 0.05))
        self.assertEqual(parse_int_list("7,20"), (7, 20))


if __name__ == "__main__":
    unittest.main()
