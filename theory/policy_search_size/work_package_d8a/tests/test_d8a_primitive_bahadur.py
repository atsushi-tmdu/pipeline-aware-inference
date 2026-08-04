from __future__ import annotations

import unittest
import numpy as np

from d8a_core import (
    empirical_quantile_leading_term,
    fixed_dimension_bahadur_l2_closure,
    joint_scaled_l2_remainder_bound,
    quantile_local_tail_bound,
    scaled_lattice_negligibility,
    uniform_integrability_tail_bound,
)


class D8APrimitiveBahadurTests(unittest.TestCase):
    def test_local_tail_bound_is_at_most_one(self) -> None:
        observed = quantile_local_tail_bound(
            reference_size=1000,
            deviation=0.01,
            density_lower_bound=0.5,
        )
        self.assertGreaterEqual(observed, 0.0)
        self.assertLessEqual(observed, 1.0)

    def test_local_tail_bound_decreases_with_deviation(self) -> None:
        small = quantile_local_tail_bound(1000, 0.01, 1.0)
        large = quantile_local_tail_bound(1000, 0.05, 1.0)
        self.assertLess(large, small)

    def test_uniform_integrability_bound_decreases(self) -> None:
        first = uniform_integrability_tail_bound(
            12.0,
            cutoff=2.0,
            moment_order=4.0,
        )
        second = uniform_integrability_tail_bound(
            12.0,
            cutoff=4.0,
            moment_order=4.0,
        )
        self.assertLess(second, first)

    def test_joint_l2_bound_is_component_sum(self) -> None:
        observed = joint_scaled_l2_remainder_bound(
            np.array([0.01, 0.02, 0.03])
        )
        self.assertAlmostEqual(observed, 0.06)

    def test_leading_term_sign(self) -> None:
        observed = empirical_quantile_leading_term(
            empirical_cdf_at_quantile=0.52,
            probability=0.50,
            density_at_quantile=2.0,
        )
        self.assertAlmostEqual(observed, -0.01)

    def test_lattice_negligibility_is_bounded_by_inverse_sqrt_b(self) -> None:
        probability = 0.371234
        for reference_size in (101, 1001, 10001):
            observed = scaled_lattice_negligibility(
                reference_size,
                probability,
            )
            upper_bound = reference_size ** -0.5
            self.assertLessEqual(
                observed,
                upper_bound + 1e-15,
            )
        self.assertLessEqual(
            scaled_lattice_negligibility(
                10001,
                probability,
            ),
            10001 ** -0.5 + 1e-15,
        )

    def test_fixed_dimension_closure_at_zero(self) -> None:
        observed = fixed_dimension_bahadur_l2_closure(
            np.zeros(4)
        )
        self.assertEqual(
            observed["joint_scaled_l2_bound"],
            0.0,
        )
        self.assertTrue(
            observed["joint_l2_remainder_vanishes"]
        )

    def test_fixed_dimension_closure_positive_bound(self) -> None:
        observed = fixed_dimension_bahadur_l2_closure(
            np.array([0.01, 0.02])
        )
        self.assertAlmostEqual(
            observed["joint_scaled_l2_bound"],
            0.03,
        )
        self.assertFalse(
            observed["joint_l2_remainder_vanishes"]
        )


if __name__ == "__main__":
    unittest.main()
