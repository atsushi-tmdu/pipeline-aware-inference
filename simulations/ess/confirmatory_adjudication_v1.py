#!/usr/bin/env python3
"""Apply the locked confirmatory success rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def one_row(frame, library, alpha, metric):
    result = frame[
        (frame["library_or_contrast"] == library)
        & np.isclose(frame["local_alpha"], alpha)
        & (frame["metric"] == metric)
    ]
    if len(result) != 1:
        raise ValueError(
            f"Expected one row for {library}, alpha={alpha}, metric={metric}"
        )
    return result.iloc[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interaction", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    interaction = pd.read_csv(args.interaction)
    audit = pd.read_csv(args.audit)

    primary = one_row(
        interaction,
        "mixed_realistic_20",
        0.05,
        "promising_tess_minus_matched_random",
    )
    covariance = one_row(
        interaction,
        "mixed_realistic_20",
        0.05,
        "cov_activation_increment",
    )
    rescue = one_row(
        interaction,
        "mixed_realistic_20",
        0.05,
        "rescue_tess_minus_matched_random",
    )
    interaction_effect = one_row(
        interaction,
        "mixed_minus_high",
        0.05,
        "promising_tess_minus_matched_random",
    )

    decision_mismatches = int(
        audit["decision_mismatch_count_across_all_alphas"].sum()
    )

    checks = {
        "primary_confirmed": bool(primary["ci_low_95"] > 0),
        "mixed_covariance_positive": bool(covariance["ci_low_95"] > 0),
        "mixed_rescue_effect_negative": bool(rescue["ci_high_95"] < 0),
        "mixed_effect_exceeds_high": bool(interaction_effect["ci_low_95"] > 0),
        "zero_reconstruction_decision_mismatches": decision_mismatches == 0,
    }

    result = {
        "study_id": "TESS_CONFIRMATORY_POLICY_V1",
        "overall_primary_status": (
            "CONFIRMED" if checks["primary_confirmed"] else "NOT CONFIRMED"
        ),
        "checks": checks,
        "primary": primary.to_dict(),
        "mixed_covariance": covariance.to_dict(),
        "mixed_rescue": rescue.to_dict(),
        "mixed_minus_high": interaction_effect.to_dict(),
        "reconstruction_decision_mismatches": decision_mismatches,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmatory_adjudication.json").write_text(
        json.dumps(result, indent=2, default=float) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# TESS Confirmatory Policy Study v1: Adjudication",
        "",
        f"**Primary status: {result['overall_primary_status']}**",
        "",
        "## Locked primary estimand",
        "",
        "Mixed-realistic library, alpha=0.05:",
        "",
        (
            f"- Estimate: {primary['estimate']:.6f}\n"
            f"- Paired-bootstrap 95% CI: "
            f"{primary['ci_low_95']:.6f} to {primary['ci_high_95']:.6f}\n"
            f"- Success rule: lower bound > 0"
        ),
        "",
        "## Prespecified checks",
        "",
    ]
    for name, passed in checks.items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} — {name}")

    lines.extend([
        "",
        "## Key secondary results",
        "",
        (
            f"- Mixed covariance: {covariance['estimate']:.6f} "
            f"({covariance['ci_low_95']:.6f}, "
            f"{covariance['ci_high_95']:.6f})"
        ),
        (
            f"- Mixed rescue TESS effect: {rescue['estimate']:.6f} "
            f"({rescue['ci_low_95']:.6f}, "
            f"{rescue['ci_high_95']:.6f})"
        ),
        (
            f"- Mixed-minus-high promising TESS effect: "
            f"{interaction_effect['estimate']:.6f} "
            f"({interaction_effect['ci_low_95']:.6f}, "
            f"{interaction_effect['ci_high_95']:.6f})"
        ),
        "",
        f"- Reconstruction decision mismatches: {decision_mismatches}",
        "",
        "The primary status is determined only by the locked primary success rule.",
    ])

    (args.output_dir / "CONFIRMATORY_ADJUDICATION.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("\n".join(lines[:8]))
    print(f"\nWrote adjudication to: {args.output_dir}")


if __name__ == "__main__":
    main()
