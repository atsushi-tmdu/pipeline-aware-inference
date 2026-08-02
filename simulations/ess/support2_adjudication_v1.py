#!/usr/bin/env python3
"""Write the locked SUPPORT2 supplementary-validation adjudication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--bank-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    bank_audit = json.loads(args.bank_audit.read_text(encoding="utf-8"))
    failed = int(bank_audit["reference"]["failed_fit_count"]) + int(bank_audit["evaluation"]["failed_fit_count"])
    identity_ok = max(abs(summary["identity_error_promising"]), abs(summary["identity_error_rescue"])) < 1e-12

    if args.smoke:
        status = "SMOKE TEST COMPLETE — NOT SCIENTIFIC EVIDENCE"
    elif not identity_ok:
        status = "TECHNICALLY INCOMPLETE — DECOMPOSITION IDENTITY FAILURE"
    elif summary["supportive_rule_met"]:
        status = "SUPPORTIVE"
    else:
        status = "NOT SUPPORTIVE"

    adjudication = {
        "study_id": config["study_id"],
        "status": status,
        "role": config["role_in_manuscript"],
        "primary": {
            "estimate": summary["primary_estimate"],
            "ci_low_95": summary["primary_ci_low_95"],
            "ci_high_95": summary["primary_ci_high_95"],
            "supportive_rule_met": summary["supportive_rule_met"],
        },
        "mechanism": {
            "covariance": summary["cov_activation_increment"],
            "cov_ci_low_95": summary["cov_ci_low_95"],
            "cov_ci_high_95": summary["cov_ci_high_95"],
            "activation_rate": summary["promising_activation_rate"],
            "gain_capture_fraction": summary["promising_gain_capture_fraction"],
            "incremental_gain_count": summary["incremental_gain_count"],
        },
        "rescue_tess_effect": summary["rescue_tess_effect"],
        "failed_fit_count": failed,
        "technical_warning": failed > 0,
        "identity_ok": identity_ok,
        "interpretation_guardrail": "This supplementary validation does not modify the adjudication of the primary locked confirmatory simulation.",
    }

    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "support2_validation_adjudication.json").write_text(json.dumps(adjudication, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# SUPPORT2-Anchored TESS Supplementary Validation: Adjudication",
        "",
        f"**Status: {status}**",
        "",
        "## Locked supplementary estimand",
        "",
        f"- TESS promising minus budget-matched random: **{summary['primary_estimate']:.6f}**",
        f"- Paired-bootstrap 95% CI: **{summary['primary_ci_low_95']:.6f} to {summary['primary_ci_high_95']:.6f}**",
        f"- Supportive rule met: **{summary['supportive_rule_met']}**",
        "",
        "## Mechanism",
        "",
        f"- Promising activation rate: {summary['promising_activation_rate']:.4f}",
        f"- Incremental gain count: {summary['incremental_gain_count']}",
        f"- Gain capture fraction: {summary['promising_gain_capture_fraction']}",
        f"- Cov(A,D): {summary['cov_activation_increment']:.6f}",
        f"- Covariance 95% CI: {summary['cov_ci_low_95']:.6f} to {summary['cov_ci_high_95']:.6f}",
        "",
        "## Technical audit",
        "",
        f"- Failed fits retained as AUC 0.5: {failed}",
        f"- Decomposition identities within tolerance: {identity_ok}",
        "",
        "## Interpretation guardrail",
        "",
        "This is a real-data-anchored global-null supplementary validation. It is not an ordinary SUPPORT2 prognostic-model application, is not external clinical validation, and does not change the already confirmed primary simulation result.",
    ]
    (out / "SUPPORT2_VALIDATION_ADJUDICATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(status)
    print(f"Adjudication: {out / 'SUPPORT2_VALIDATION_ADJUDICATION.md'}")


if __name__ == "__main__":
    main()
