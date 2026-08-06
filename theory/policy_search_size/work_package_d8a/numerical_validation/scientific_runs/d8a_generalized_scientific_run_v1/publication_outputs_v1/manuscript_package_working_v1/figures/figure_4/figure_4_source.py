#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


EXPECTED_BRANCH = "tess-top-tier-theory"
RESULT_TAG = "d8a-generalized-scientific-validation-v1"
FIGURE_ID = "TESS_D8A_PUBLICATION_FIGURE_4_COMBINED_AND_EXACT_IDENTITY_V1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo,
        text=True,
    ).strip()


def quantile(values: list[float], probability: float) -> float:
    return float(
        np.quantile(
            np.asarray(values, dtype=float),
            probability,
            method="linear",
        )
    )


def assert_close(
    observed: float,
    expected: float,
    *,
    label: str,
    tolerance: float = 1e-10,
) -> None:
    if not math.isclose(
        float(observed),
        float(expected),
        rel_tol=tolerance,
        abs_tol=tolerance,
    ):
        raise ValueError(
            f"{label} mismatch: observed={observed}, expected={expected}"
        )


def display_exponent(values: list[float]) -> int:
    maximum = max(
        [abs(float(value)) for value in values]
        + [1e-300]
    )
    if maximum == 0.0:
        return 0
    return int(math.floor(math.log10(maximum)))


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str],
) -> None:
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    repo = Path(
        os.environ.get(
            "REPO",
            "/Users/sendaatsushi/Documents/"
            "pipeline-aware/"
            "pipeline-aware-inference-clean-20260803",
        )
    ).expanduser().resolve()

    if not (repo / ".git").exists():
        raise SystemExit(
            f"FAIL: repository not found: {repo}"
        )

    branch = git_output(
        repo,
        "branch",
        "--show-current",
    )
    if branch != EXPECTED_BRANCH:
        raise SystemExit(
            f"FAIL: expected branch {EXPECTED_BRANCH}, observed {branch}"
        )

    result_commit = git_output(
        repo,
        "rev-parse",
        f"{RESULT_TAG}^{{commit}}",
    )
    head = git_output(
        repo,
        "rev-parse",
        "HEAD",
    )
    if head != result_commit:
        raise SystemExit(
            "FAIL: HEAD is not the locked scientific-validation result commit"
        )

    run_root = (
        repo
        / "theory"
        / "policy_search_size"
        / "work_package_d8a"
        / "numerical_validation"
        / "scientific_runs"
        / "d8a_generalized_scientific_run_v1"
    )
    formal_path = (
        run_root
        / "formal_adjudication"
        / "D8A_FORMAL_SCIENTIFIC_ADJUDICATION.json"
    )
    diagnostic_path = (
        run_root
        / "formal_adjudication"
        / "diagnostics"
        / "D8A_POSTHOC_MCSE_FLOOR_AND_BASELINE_DIAGNOSTIC.json"
    )
    evidence_path = (
        run_root
        / "formal_adjudication"
        / "D8A_EVIDENTIAL_STRENGTH_ADJUDICATION.json"
    )

    required = [
        formal_path,
        diagnostic_path,
        evidence_path,
    ]
    missing = [
        path for path in required
        if not path.is_file()
    ]
    if missing:
        raise SystemExit(
            "FAIL: required locked-result files are missing:\n"
            + "\n".join(
                str(path)
                for path in missing
            )
        )

    formal = load_json(formal_path)
    diagnostic = load_json(diagnostic_path)
    evidence = load_json(evidence_path)

    if formal["formal_acceptance"]["formal_status"] != "PASS":
        raise SystemExit(
            "FAIL: formal scientific status is not PASS"
        )
    if evidence["policy_expansion_evidence"] != "STRONG_SUPPORT":
        raise SystemExit(
            "FAIL: policy expansion evidence is not STRONG_SUPPORT"
        )

    contract = formal["contract"]
    combined_pair = tuple(
        int(value)
        for value in contract[
            "combined_policy_acceptance"
        ]["largest_pair"]
    )
    if combined_pair != (10000, 10000):
        raise SystemExit(
            f"FAIL: unexpected combined pair: {combined_pair}"
        )

    exact_contract = contract[
        "exact_evaluation_identity"
    ]
    exact_z_star = float(
        exact_contract["z_star"]
    )
    expected_comparisons = int(
        exact_contract["comparison_count"]
    )
    if expected_comparisons != 85:
        raise SystemExit(
            "FAIL: expected exact-comparison count is not 85"
        )

    # ------------------------------------------------------------------
    # Panel A data: combined-policy bias agreement.
    # ------------------------------------------------------------------
    class_details = sorted(
        list(formal["class_details"]),
        key=lambda item: str(item["class_id"]),
    )
    if len(class_details) != 17:
        raise SystemExit(
            "FAIL: expected 17 primary class details, "
            f"observed {len(class_details)}"
        )

    combined_rows: list[dict[str, Any]] = []

    for class_detail in class_details:
        class_id = str(class_detail["class_id"])
        combined = class_detail["combined_policy"]
        point = combined["point"]
        metric = combined["metric"]

        B = int(point["reference_B"])
        n = int(point["evaluation_n"])
        if (B, n) != combined_pair:
            raise SystemExit(
                f"FAIL: unexpected combined point for {class_id}: {(B, n)}"
            )

        observed_bias = float(metric["observed_bias"])
        predicted_bias = float(metric["predicted_bias"])
        raw_residual = float(metric["raw_residual"])
        scale = float(metric["scale"])
        adjusted_normalized = float(
            metric["normalized_residual"]
        )
        raw_normalized = abs(raw_residual) / scale

        assert_close(
            raw_residual,
            observed_bias - predicted_bias,
            label=f"{class_id}: combined bias identity",
            tolerance=1e-12,
        )

        combined_rows.append(
            {
                "class_id": class_id,
                "reference_B": B,
                "evaluation_n": n,
                "observed_bias": observed_bias,
                "predicted_bias": predicted_bias,
                "raw_residual": raw_residual,
                "scale": scale,
                "raw_normalized_residual": raw_normalized,
                "adjusted_normalized_residual": adjusted_normalized,
            }
        )

    combined_component = diagnostic[
        "component_summaries"
    ]["combined_policy"]
    combined_raw_values = [
        float(row["raw_normalized_residual"])
        for row in combined_rows
    ]
    combined_adjusted_values = [
        float(row["adjusted_normalized_residual"])
        for row in combined_rows
    ]

    combined_raw_median = quantile(
        combined_raw_values,
        0.5,
    )
    combined_raw_p90 = quantile(
        combined_raw_values,
        0.9,
    )
    combined_adjusted_median = quantile(
        combined_adjusted_values,
        0.5,
    )
    combined_adjusted_p90 = quantile(
        combined_adjusted_values,
        0.9,
    )

    assert_close(
        combined_raw_median,
        float(
            combined_component[
                "raw_normalized"
            ]["median"]
        ),
        label="combined raw median",
    )
    assert_close(
        combined_raw_p90,
        float(
            combined_component[
                "raw_normalized"
            ]["p90"]
        ),
        label="combined raw p90",
    )
    assert_close(
        combined_adjusted_median,
        float(
            combined_component[
                "adjusted_normalized"
            ]["median"]
        ),
        label="combined adjusted median",
    )
    assert_close(
        combined_adjusted_p90,
        float(
            combined_component[
                "adjusted_normalized"
            ]["p90"]
        ),
        label="combined adjusted p90",
    )

    # ------------------------------------------------------------------
    # Panel B data: exact finite-n identity.
    # ------------------------------------------------------------------
    exact_records = list(
        formal["exact_identity_records"]
    )
    if len(exact_records) != expected_comparisons:
        raise SystemExit(
            "FAIL: exact identity record count mismatch: "
            f"{len(exact_records)}"
        )

    exact_rows: list[dict[str, Any]] = []
    for record in exact_records:
        class_id = str(record["class_id"])
        n = int(record["evaluation_n"])
        observed_mean = float(
            record["observed_mean"]
        )
        target = float(
            record["identity_target"]
        )
        mcse = float(record["mcse"])
        difference = observed_mean - target

        if mcse == 0.0:
            if abs(difference) > 1e-15:
                raise SystemExit(
                    f"FAIL: nonzero discrepancy with zero MCSE: {class_id}, n={n}"
                )
            signed_z = 0.0
        else:
            signed_z = difference / mcse

        absolute_z = abs(signed_z)
        passed = bool(record["passed"])

        assert_close(
            abs(difference),
            float(record["absolute_difference"]),
            label=f"{class_id}, n={n}: absolute difference",
            tolerance=1e-12,
        )
        assert_close(
            exact_z_star * mcse,
            float(record["simultaneous_tolerance"]),
            label=f"{class_id}, n={n}: simultaneous tolerance",
            tolerance=1e-12,
        )
        if passed != bool(
            absolute_z <= exact_z_star + 1e-12
        ):
            raise SystemExit(
                f"FAIL: pass flag mismatch: {class_id}, n={n}"
            )

        exact_rows.append(
            {
                "class_id": class_id,
                "evaluation_n": n,
                "observed_mean": observed_mean,
                "identity_target": target,
                "mcse": mcse,
                "signed_standardized_discrepancy": signed_z,
                "absolute_standardized_discrepancy": absolute_z,
                "passed": passed,
            }
        )

    evaluation_sizes = sorted(
        {
            int(row["evaluation_n"])
            for row in exact_rows
        }
    )
    if evaluation_sizes != [
        250,
        500,
        1000,
        3000,
        10000,
    ]:
        raise SystemExit(
            f"FAIL: unexpected evaluation-size grid: {evaluation_sizes}"
        )

    count_by_n = {
        n: sum(
            int(row["evaluation_n"] == n)
            for row in exact_rows
        )
        for n in evaluation_sizes
    }
    if any(
        count != 17
        for count in count_by_n.values()
    ):
        raise SystemExit(
            f"FAIL: exact identity counts by n are not all 17: {count_by_n}"
        )

    passed_count = sum(
        bool(row["passed"])
        for row in exact_rows
    )
    if passed_count != expected_comparisons:
        raise SystemExit(
            f"FAIL: only {passed_count}/{expected_comparisons} exact checks passed"
        )

    absolute_z_values = [
        float(
            row[
                "absolute_standardized_discrepancy"
            ]
        )
        for row in exact_rows
    ]
    exact_median = quantile(
        absolute_z_values,
        0.5,
    )
    exact_p90 = quantile(
        absolute_z_values,
        0.9,
    )
    exact_maximum = max(
        absolute_z_values
    )

    exact_diagnostic = diagnostic[
        "exact_identity_standardized"
    ]
    assert_close(
        exact_median,
        float(exact_diagnostic["median"]),
        label="exact standardized median",
    )
    assert_close(
        exact_p90,
        float(exact_diagnostic["p90"]),
        label="exact standardized p90",
    )
    assert_close(
        exact_maximum,
        float(exact_diagnostic["maximum"]),
        label="exact standardized maximum",
    )
    assert_close(
        exact_z_star,
        float(
            exact_diagnostic[
                "locked_z_star"
            ]
        ),
        label="exact locked z star",
    )

    output_dir = (
        run_root
        / "publication_outputs_v1"
        / "figure_4_combined_and_exact_identity_actual"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_csv_path = (
        output_dir
        / "figure_4_combined_policy_data.csv"
    )
    exact_csv_path = (
        output_dir
        / "figure_4_exact_identity_data.csv"
    )
    svg_path = (
        output_dir
        / "figure_4_combined_and_exact_identity.svg"
    )
    pdf_path = (
        output_dir
        / "figure_4_combined_and_exact_identity.pdf"
    )
    png_path = (
        output_dir
        / "figure_4_combined_and_exact_identity.png"
    )
    caption_path = (
        output_dir
        / "figure_4_caption.md"
    )
    provenance_path = (
        output_dir
        / "figure_4_provenance.json"
    )
    source_copy_path = (
        output_dir
        / "figure_4_source.py"
    )

    write_csv(
        combined_csv_path,
        combined_rows,
        [
            "class_id",
            "reference_B",
            "evaluation_n",
            "observed_bias",
            "predicted_bias",
            "raw_residual",
            "scale",
            "raw_normalized_residual",
            "adjusted_normalized_residual",
        ],
    )
    write_csv(
        exact_csv_path,
        exact_rows,
        [
            "class_id",
            "evaluation_n",
            "observed_mean",
            "identity_target",
            "mcse",
            "signed_standardized_discrepancy",
            "absolute_standardized_discrepancy",
            "passed",
        ],
    )

    plt.rcParams.update(
        {
            "font.size": 9.5,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    theme = plt.rcParams[
        "axes.prop_cycle"
    ].by_key()["color"]
    main_color = theme[0]
    highlight_color = theme[1]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12.9, 5.15),
        gridspec_kw={
            "width_ratios": [
                1.0,
                1.18,
            ]
        },
        constrained_layout=False,
    )
    fig.subplots_adjust(
        left=0.075,
        right=0.985,
        bottom=0.16,
        top=0.90,
        wspace=0.30,
    )

    # Panel A: combined-policy agreement.
    axis = axes[0]
    predicted = np.asarray(
        [
            float(row["predicted_bias"])
            for row in combined_rows
        ],
        dtype=float,
    )
    observed = np.asarray(
        [
            float(row["observed_bias"])
            for row in combined_rows
        ],
        dtype=float,
    )
    exponent = display_exponent(
        predicted.tolist()
        + observed.tolist()
    )
    display_factor = 10.0 ** (-exponent)
    predicted_display = predicted * display_factor
    observed_display = observed * display_factor

    limit = 1.14 * max(
        float(
            np.max(
                np.abs(
                    predicted_display
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    observed_display
                )
            )
        ),
        1e-12,
    )
    identity = np.linspace(
        -limit,
        limit,
        200,
    )

    axis.plot(
        identity,
        identity,
        linewidth=1.05,
        color="0.46",
        zorder=1,
    )
    axis.axhline(
        0.0,
        linestyle=":",
        linewidth=0.85,
        color="0.70",
        zorder=0,
    )
    axis.axvline(
        0.0,
        linestyle=":",
        linewidth=0.85,
        color="0.70",
        zorder=0,
    )
    axis.scatter(
        predicted_display,
        observed_display,
        s=38,
        color=main_color,
        linewidths=0.55,
        edgecolors="white",
        zorder=3,
    )
    axis.set_xlim(
        -limit,
        limit,
    )
    axis.set_ylim(
        -limit,
        limit,
    )
    axis.set_aspect(
        "equal",
        adjustable="box",
    )
    axis.set_xlabel(
        "Predicted combined-policy bias\n"
        rf"$(\times 10^{{{exponent}}})$"
    )
    axis.set_ylabel(
        "Observed combined-policy bias\n"
        rf"$(\times 10^{{{exponent}}})$"
    )
    axis.set_title(
        "A. Combined-policy bias agreement",
        loc="left",
        pad=9,
    )
    axis.text(
        0.04,
        0.96,
        "$B=n=10{,}000$\n"
        "17 primary classes",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=8.2,
    )
    axis.annotate(
        "identity",
        xy=(
            0.67 * limit,
            0.67 * limit,
        ),
        xytext=(-2, 2),
        textcoords="offset points",
        ha="center",
        va="center",
        fontsize=8.2,
        rotation=45,
        color="0.46",
        fontstyle="italic",
    )
    axis.text(
        0.96,
        0.05,
        "Raw normalized residual\n"
        f"median {combined_raw_median:.4f}\n"
        f"90th percentile {combined_raw_p90:.4f}",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.2,
    )

    # Panel B: exact finite-n identity.
    axis = axes[1]
    x_positions = {
        n: float(index)
        for index, n in enumerate(
            evaluation_sizes
        )
    }

    plotted_records: list[
        tuple[dict[str, Any], float]
    ] = []
    for n in evaluation_sizes:
        n_rows = sorted(
            [
                row
                for row in exact_rows
                if int(row["evaluation_n"]) == n
            ],
            key=lambda row: str(
                row["class_id"]
            ),
        )
        offsets = np.linspace(
            -0.16,
            0.16,
            len(n_rows),
        )
        for row, offset in zip(
            n_rows,
            offsets,
        ):
            x_value = (
                x_positions[n]
                + float(offset)
            )
            plotted_records.append(
                (row, x_value)
            )

    max_index = int(
        np.argmax(
            [
                float(
                    row[
                        "absolute_standardized_discrepancy"
                    ]
                )
                for row, _ in plotted_records
            ]
        )
    )

    for index, (row, x_value) in enumerate(
        plotted_records
    ):
        is_maximum = index == max_index
        axis.scatter(
            [x_value],
            [
                float(
                    row[
                        "signed_standardized_discrepancy"
                    ]
                )
            ],
            s=42 if is_maximum else 27,
            color=(
                highlight_color
                if is_maximum
                else main_color
            ),
            linewidths=0.55,
            edgecolors="white",
            zorder=4 if is_maximum else 3,
        )

    axis.axhline(
        0.0,
        linewidth=0.8,
        color="0.62",
    )
    axis.axhline(
        exact_z_star,
        linewidth=1.05,
        linestyle="--",
        color="0.45",
    )
    axis.axhline(
        -exact_z_star,
        linewidth=1.05,
        linestyle="--",
        color="0.45",
    )
    y_limit = 1.13 * exact_z_star
    axis.set_ylim(
        -y_limit,
        y_limit,
    )
    axis.set_xlim(
        -0.45,
        len(evaluation_sizes) - 0.55,
    )
    axis.set_xticks(
        [
            x_positions[n]
            for n in evaluation_sizes
        ]
    )
    axis.set_xticklabels(
        [
            f"{n:,}"
            for n in evaluation_sizes
        ]
    )
    axis.set_xlabel(
        r"Evaluation-sample size $n$"
    )
    axis.set_ylabel(
        "Signed discrepancy / MCSE"
    )
    axis.set_title(
        "B. Exact finite-$n$ evaluation identity",
        loc="left",
        pad=9,
    )
    axis.grid(
        axis="y",
        alpha=0.14,
    )
    axis.text(
        0.02,
        0.88,
        f"{passed_count}/{expected_comparisons} passed\n"
        f"maximum $|Z|$ = {exact_maximum:.3f}",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
    )
    axis.text(
        0.98,
        0.88,
        r"Target: $(1-1/n)\Delta_\pi$",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=8.2,
    )
    axis.text(
        0.98,
        0.10,
        rf"simultaneous bounds: $\pm {exact_z_star:.3f}$",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.2,
        color="0.45",
    )

    fig.savefig(
        svg_path,
        format="svg",
        bbox_inches="tight",
    )
    fig.savefig(
        pdf_path,
        format="pdf",
        bbox_inches="tight",
    )
    fig.savefig(
        png_path,
        format="png",
        dpi=320,
        bbox_inches="tight",
    )
    plt.close(fig)

    caption = rf"""# Figure 4. Combined-policy approximation and exact finite-\(n\) evaluation identity

**Caption.**  
(A) Class-specific observed combined-policy bias versus the generalized joint reference/evaluation prediction at \(B=n=10{{,}}000\). Each point represents one of the 17 primary equivalence classes; the diagonal denotes equality. The raw normalized-residual median and 90th percentile were {combined_raw_median:.4f} and {combined_raw_p90:.4f}, respectively, compared with the prospectively specified criteria of 0.15 and 0.40.  
(B) Signed standardized discrepancies for the exact finite-\(n\) identity \(E(\widehat{{\Delta}}_n)=(1-1/n)\Delta_\pi\) across 17 primary classes and five evaluation-sample sizes. Dashed horizontal lines denote the simultaneous two-sided Bonferroni boundaries \(\pm {exact_z_star:.5f}\). All {passed_count} of {expected_comparisons} comparisons passed; the maximum absolute standardized discrepancy was {exact_maximum:.5f}. The highlighted point is the comparison with the largest absolute discrepancy.

All displayed values come from the locked formal-adjudication and diagnostic files. The raw Monte Carlo batches were not reanalysed.
"""
    caption_path.write_text(
        caption,
        encoding="utf-8",
    )

    provenance = {
        "schema_version": "1.0",
        "figure_id": FIGURE_ID,
        "scientific_validation_tag": RESULT_TAG,
        "scientific_validation_commit": result_commit,
        "source_files": {
            "formal_adjudication": str(
                formal_path.relative_to(repo)
            ),
            "mcse_floor_and_baseline_diagnostic": str(
                diagnostic_path.relative_to(repo)
            ),
            "evidential_adjudication": str(
                evidence_path.relative_to(repo)
            ),
        },
        "combined_policy": {
            "primary_class_count": len(
                combined_rows
            ),
            "reference_B": combined_pair[0],
            "evaluation_n": combined_pair[1],
            "raw_normalized_median": (
                combined_raw_median
            ),
            "raw_normalized_p90": (
                combined_raw_p90
            ),
            "adjusted_normalized_median": (
                combined_adjusted_median
            ),
            "adjusted_normalized_p90": (
                combined_adjusted_p90
            ),
        },
        "exact_identity": {
            "comparison_count": len(
                exact_rows
            ),
            "passed_count": passed_count,
            "evaluation_sizes": (
                evaluation_sizes
            ),
            "comparisons_per_size": (
                count_by_n
            ),
            "locked_z_star": exact_z_star,
            "absolute_standardized_median": (
                exact_median
            ),
            "absolute_standardized_p90": (
                exact_p90
            ),
            "absolute_standardized_maximum": (
                exact_maximum
            ),
        },
        "generation_policy": {
            "locked_summary_files_only": True,
            "raw_batch_reanalysis": False,
            "prospective_criteria_changed": False,
            "scientific_simulation_rerun": False,
            "files_staged_or_committed": False,
        },
    }
    provenance_path.write_text(
        json.dumps(
            provenance,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    shutil.copy2(
        Path(__file__).resolve(),
        source_copy_path,
    )

    print("=" * 88)
    print(
        "D8-A actual-data publication Figure 4 generated"
    )
    print("=" * 88)
    print(
        f"Figure ID: {FIGURE_ID}"
    )
    print(
        "Combined-policy primary classes: "
        f"{len(combined_rows)}"
    )
    print(
        "Combined raw median / p90: "
        f"{combined_raw_median:.12g} / "
        f"{combined_raw_p90:.12g}"
    )
    print(
        "Combined locked-diagnostic cross-check: PASS"
    )
    print(
        "Exact identity comparisons passed: "
        f"{passed_count}/{expected_comparisons}"
    )
    print(
        "Exact |difference|/MCSE median / p90 / maximum: "
        f"{exact_median:.12g} / "
        f"{exact_p90:.12g} / "
        f"{exact_maximum:.12g}"
    )
    print(
        "Exact locked-diagnostic cross-check: PASS"
    )
    print(
        f"Exact simultaneous boundary: +/- {exact_z_star:.12g}"
    )
    print(
        "Raw Monte Carlo batches reanalysed: NO"
    )
    print(
        "Prospective criteria changed: NO"
    )
    print(
        "Scientific simulation rerun: NO"
    )
    print(
        "Files staged or committed: NO"
    )
    print(f"SVG: {svg_path}")
    print(f"PDF: {pdf_path}")
    print(f"PNG: {png_path}")
    print(
        f"Combined data CSV: {combined_csv_path}"
    )
    print(
        f"Exact identity data CSV: {exact_csv_path}"
    )
    print(f"Caption: {caption_path}")
    print(f"Provenance: {provenance_path}")
    print(f"Source copy: {source_copy_path}")


if __name__ == "__main__":
    main()
