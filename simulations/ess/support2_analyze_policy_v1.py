#!/usr/bin/env python3
"""Analyze one SUPPORT2 real-structure policy bank using frozen TESS utilities."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from simulations.ess.phase3c_adaptive_ml_policy import analyze_library as analyze_policy
from simulations.ess.phase3c_adaptive_policy_mechanism import analyze_library as analyze_mechanism
from simulations.ess.budget_standardized_policy_audit import (
    bootstrap_effects,
    load_policy_bank,
    point_effects,
)

LIBRARY = "support2_real_structure_20"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    inference = config["inference"]
    adaptive = config["adaptive_policy"]
    alphas = tuple(float(x) for x in inference["reported_curve_alphas"])
    boot_n = int(inference["bootstrap_repetitions"])
    policy_seed = int(adaptive["policy_seed"])
    bootstrap_seed = int(inference["bootstrap_seed"])

    out = args.output_dir.expanduser().resolve()
    policy_root = out / "adaptive_policy"
    mechanism_root = out / "mechanism"
    audit_root = out / "budget_standardized_audit"
    for p in (policy_root, mechanism_root, audit_root):
        p.mkdir(parents=True, exist_ok=True)

    policy_result = analyze_policy(
        args.run_dir.expanduser().resolve(),
        LIBRARY,
        policy_root,
        alphas,
        100,
        float(adaptive["target_expansion_probability"]),
        boot_n,
        policy_seed,
    )

    bank_path = policy_root / LIBRARY / "adaptive_ml_policy_replication_bank.csv"
    mechanism_result = analyze_mechanism(
        bank_path,
        LIBRARY,
        mechanism_root,
        alphas,
        float(inference["primary_alpha"]),
        boot_n,
        bootstrap_seed,
    )

    bank, joined = load_policy_bank(bank_path)
    point = point_effects(joined, alphas, LIBRARY)
    boot = bootstrap_effects(joined, alphas, LIBRARY, boot_n, bootstrap_seed)
    point.to_csv(audit_root / "budget_standardized_policy_effects.csv", index=False)
    boot.to_csv(audit_root / "budget_standardized_policy_effects_bootstrap.csv", index=False)

    primary_alpha = float(inference["primary_alpha"])
    primary_point = point[np.isclose(point["local_alpha"], primary_alpha)].iloc[0]
    primary_boot = boot[
        np.isclose(boot["local_alpha"], primary_alpha)
        & (boot["metric"] == "tess_promising_minus_matched_random")
    ].iloc[0]
    covariance = mechanism_result["covariance"][
        np.isclose(mechanism_result["covariance"]["local_alpha"], primary_alpha)
    ].iloc[0]
    mechanism = mechanism_result["mechanism"][
        np.isclose(mechanism_result["mechanism"]["local_alpha"], primary_alpha)
    ].iloc[0]

    summary = {
        "study_id": config["study_id"],
        "library": LIBRARY,
        "primary_alpha": primary_alpha,
        "primary_estimate": float(primary_point["tess_promising_minus_matched_random"]),
        "primary_ci_low_95": float(primary_boot["ci_low_95"]),
        "primary_ci_high_95": float(primary_boot["ci_high_95"]),
        "supportive_rule_met": bool(float(primary_boot["ci_low_95"]) > 0),
        "tess_promising": float(primary_point["tess_promising"]),
        "tess_random_matched": float(primary_point["tess_random_matched_promising_budget"]),
        "promising_activation_rate": float(primary_point["promising_activation_rate"]),
        "promising_gain_capture_fraction": (
            None if pd.isna(primary_point["promising_gain_capture_fraction"])
            else float(primary_point["promising_gain_capture_fraction"])
        ),
        "incremental_gain_count": int(primary_point["incremental_gain_count"]),
        "cov_activation_increment": float(covariance["cov_activation_increment"]),
        "cov_ci_low_95": float(covariance["ci_low_95"]),
        "cov_ci_high_95": float(covariance["ci_high_95"]),
        "rescue_tess_effect": float(primary_point["tess_rescue_minus_matched_random"]),
        "identity_error_promising": float(mechanism["promising_identity_error"]),
        "identity_error_rescue": float(mechanism["rescue_identity_error"]),
        "bootstrap_repetitions": boot_n,
    }
    (out / "support2_validation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("SUPPORT2 policy analysis complete")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
