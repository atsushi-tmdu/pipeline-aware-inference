from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from simulations.ess.make_tess_manuscript_assets_v1_4_8 import (
    POLICY_ORDER,
    make_decile_plot,
    make_figure1,
    make_policy_curve_small_multiples,
)


class FigurePolishV148Tests(unittest.TestCase):
    def test_figure1_writes_all_formats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            make_figure1(out)
            for suffix in (".png", ".svg", ".pdf"):
                self.assertTrue((out / "Figure1_policy_framework").with_suffix(suffix).exists())

    def test_supplementary_figure2_zero_line_is_neutral_dashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = "test_library"
            csv_dir = root / "mechanism" / library
            csv_dir.mkdir(parents=True)
            pd.DataFrame(
                {
                    "score_mean": [0.48, 0.50, 0.52],
                    "incremental_gain_rate": [0.01, 0.03, 0.06],
                    "incremental_loss_rate": [0.00, 0.01, 0.01],
                    "mean_incremental_effect": [0.01, 0.02, 0.05],
                }
            ).to_csv(csv_dir / "incremental_effect_by_base_score.csv", index=False)

            stem = root / "s2"
            make_decile_plot(root, library, "Test", stem)
            svg = stem.with_suffix(".svg").read_text(encoding="utf-8").lower()
            self.assertIn("#8c8c8c", svg)
            self.assertIn("stroke-dasharray", svg)
            for suffix in (".png", ".svg", ".pdf"):
                self.assertTrue(stem.with_suffix(suffix).exists())

    def test_policy_small_multiples_still_writes_all_formats(self) -> None:
        rows = []
        for p_index, policy in enumerate(POLICY_ORDER):
            for alpha in (0.20, 0.10, 0.05):
                point = 1.0 + p_index * 0.2 + (0.20 - alpha)
                rows.append(
                    {
                        "policy": policy,
                        "local_alpha": alpha,
                        "tess": point,
                        "pointwise_low_95": point - 0.1,
                        "pointwise_high_95": point + 0.1,
                    }
                )
        frame = pd.DataFrame(rows)
        with tempfile.TemporaryDirectory() as tmp:
            stem = Path(tmp) / "s3"
            make_policy_curve_small_multiples(frame, "Test", stem)
            for suffix in (".png", ".svg", ".pdf"):
                self.assertTrue(stem.with_suffix(suffix).exists())


if __name__ == "__main__":
    unittest.main()
