#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from simulations.ess.phase3c_tess_bootstrap import (
    LibraryBank,
    align_cross_library_banks,
    bootstrap_tess,
    original_tess,
    simultaneous_bands,
)


class TestPhase3CTESSBootstrap(unittest.TestCase):
    def make_bank(self, name: str, values: np.ndarray) -> LibraryBank:
        keys = pd.MultiIndex.from_arrays(
            [np.arange(len(values)), np.arange(1000, 1000 + len(values))],
            names=["replication", "seed"],
        )
        return LibraryBank(name=name, input_path=None, keys=keys, p_values=values)  # type: ignore[arg-type]

    def test_original_curve_uses_strict_threshold(self) -> None:
        values = np.array(
            [
                [0.01, 0.01],
                [0.05, 0.04],
                [0.20, 0.05],
                [0.80, 0.80],
            ],
            dtype=float,
        )
        bank = self.make_bank("test", values)
        probabilities, rejections, _ = original_tess(bank, np.array([0.05, 0.10]))
        self.assertEqual(int(rejections[0, 0]), 1)
        self.assertEqual(int(rejections[1, 0]), 2)
        self.assertAlmostEqual(float(probabilities[0, 1]), 0.5)

    def test_paired_bootstrap_preserves_identical_K_curves(self) -> None:
        rng = np.random.default_rng(7)
        p = rng.uniform(size=100)
        values = np.column_stack([p, p])
        high = self.make_bank("high", values)
        mixed = self.make_bank("mixed", values)
        bootstrap, corrections = bootstrap_tess(
            high=high,
            mixed=mixed,
            alphas=np.array([0.20, 0.10, 0.05]),
            bootstrap_repetitions=200,
            bootstrap_seed=19,
            batch_size=50,
            pairing="paired",
        )
        np.testing.assert_allclose(bootstrap[:, :, 0, :], bootstrap[:, :, 1, :])
        self.assertEqual(corrections, 0)

    def test_bootstrap_is_reproducible(self) -> None:
        rng = np.random.default_rng(11)
        high = self.make_bank("high", rng.uniform(size=(80, 2)))
        mixed = self.make_bank("mixed", rng.uniform(size=(80, 2)))
        kwargs = dict(
            high=high,
            mixed=mixed,
            alphas=np.array([0.20, 0.10]),
            bootstrap_repetitions=120,
            bootstrap_seed=1234,
            batch_size=40,
            pairing="paired",
        )
        first, _ = bootstrap_tess(**kwargs)
        second, _ = bootstrap_tess(**kwargs)
        np.testing.assert_array_equal(first, second)

    def test_auto_pairing_aligns_reordered_keys(self) -> None:
        rng = np.random.default_rng(21)
        high = self.make_bank("high", rng.uniform(size=(30, 2)))
        order = np.arange(29, -1, -1)
        mixed = LibraryBank(
            name="mixed",
            input_path=None,  # type: ignore[arg-type]
            keys=high.keys[order],
            p_values=high.p_values[order],
        )
        high_aligned, mixed_aligned, mode = align_cross_library_banks(
            high, mixed, mode="auto"
        )
        self.assertEqual(mode, "paired")
        self.assertTrue(high_aligned.keys.equals(mixed_aligned.keys))
        np.testing.assert_array_equal(high_aligned.p_values, mixed_aligned.p_values)

    def test_simultaneous_band_shapes(self) -> None:
        point = np.array([1.0, 1.2, 1.4])
        bootstrap = np.array(
            [
                [0.9, 1.1, 1.3],
                [1.1, 1.3, 1.5],
                [1.0, 1.2, 1.4],
                [0.95, 1.25, 1.35],
            ]
        )
        low, high, critical = simultaneous_bands(point, bootstrap)
        self.assertEqual(low.shape, point.shape)
        self.assertEqual(high.shape, point.shape)
        self.assertGreaterEqual(critical, 0.0)
        self.assertTrue(np.all(low <= point))
        self.assertTrue(np.all(high >= point))


if __name__ == "__main__":
    unittest.main()
