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
FIGURE_ID = "TESS_D8A_PUBLICATION_FIGURE_3_TESS_FINITE_SAMPLE_FINAL_3PANEL_V4"
ALPHAS = (0.01, 0.05)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_output(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo,
        text=True,
    ).strip()


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


def alpha_key(alpha: float) -> str:
    return f"alpha_{alpha:.2f}"


def alpha_label(alpha: float) -> str:
    return rf"$\alpha={alpha:.2f}$"


def symmetric_limit(
    x_values: np.ndarray,
    y_values: np.ndarray,
) -> float:
    maximum = max(
        float(np.max(np.abs(x_values))),
        float(np.max(np.abs(y_values))),
        1e-12,
    )
    return 1.16 * maximum


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    fieldnames = [
        "class_id",
        "alpha",
        "observed_bias",
        "predicted_bias",
        "raw_residual",
        "scale",
        "raw_normalized_residual",
        "mcse",
        "z_star",
        "normalized_mcse_band",
        "raw_to_mcse_allowance_ratio",
        "adjusted_normalized_residual",
        "nonfinite_record_count",
    ]
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
    if evidence["tess_finite_sample_evidence"] != (
        "FORMAL_PASS_BUT_MCSE_RESOLUTION_LIMITED"
    ):
        raise SystemExit(
            "FAIL: unexpected TESS evidential classification"
        )

    class_details = list(
        formal["class_details"]
    )
    if len(class_details) != 17:
        raise SystemExit(
            "FAIL: expected 17 primary class details, "
            f"observed {len(class_details)}"
        )

    formal_tess_records = list(
        formal["combined_tess_records"]
    )
    if len(formal_tess_records) != 34:
        raise SystemExit(
            "FAIL: expected 34 formal TESS records, "
            f"observed {len(formal_tess_records)}"
        )

    components = diagnostic[
        "component_summaries"
    ]
    component_by_alpha = {
        0.01: components[
            "combined_tess_alpha_0.01"
        ],
        0.05: components[
            "combined_tess_alpha_0.05"
        ],
    }

    diagnostic_by_alpha_class: dict[
        tuple[float, str],
        dict[str, Any],
    ] = {}
    for alpha in ALPHAS:
        component = component_by_alpha[alpha]
        records = list(component["records"])
        if len(records) != 17:
            raise SystemExit(
                f"FAIL: alpha={alpha:.2f} diagnostic "
                f"record count is {len(records)}, not 17"
            )
        for record in records:
            key = (
                alpha,
                str(record["class_id"]),
            )
            if key in diagnostic_by_alpha_class:
                raise SystemExit(
                    f"FAIL: duplicate diagnostic record: {key}"
                )
            diagnostic_by_alpha_class[key] = record

    nonfinite_by_alpha_class = {
        (
            float(record["alpha"]),
            str(record["class_id"]),
        ): int(
            record["nonfinite_record_count"]
        )
        for record in formal_tess_records
    }

    rows: list[dict[str, Any]] = []

    for class_detail in sorted(
        class_details,
        key=lambda item: str(item["class_id"]),
    ):
        class_id = str(
            class_detail["class_id"]
        )
        combined_tess = class_detail[
            "combined_tess"
        ]

        for alpha in ALPHAS:
            key = alpha_key(alpha)
            details = combined_tess[key]
            metric = details["metric"]
            summary = details["summary"]
            finite_summary = summary[
                "finite_summary"
            ]
            diagnostic_record = (
                diagnostic_by_alpha_class[
                    (alpha, class_id)
                ]
            )

            observed_bias = float(
                metric["observed_bias"]
            )
            predicted_bias = float(
                metric["predicted_bias"]
            )
            raw_residual = float(
                metric["raw_residual"]
            )
            scale = float(
                metric["scale"]
            )
            adjusted = float(
                metric["normalized_residual"]
            )
            mcse = float(
                finite_summary["mcse"]
            )
            z_star = float(
                diagnostic_record["z_star"]
            )
            raw_normalized = abs(
                raw_residual
            ) / scale
            normalized_mcse_band = (
                z_star * mcse / scale
            )
            raw_to_mcse_allowance_ratio = (
                raw_normalized
                / normalized_mcse_band
                if normalized_mcse_band > 0.0
                else (
                    0.0
                    if raw_normalized == 0.0
                    else float("inf")
                )
            )

            assert_close(
                raw_residual,
                observed_bias - predicted_bias,
                label=(
                    f"{class_id}, alpha={alpha:.2f}: "
                    "bias residual identity"
                ),
                tolerance=1e-12,
            )
            assert_close(
                raw_residual,
                float(
                    diagnostic_record[
                        "raw_residual"
                    ]
                ),
                label=(
                    f"{class_id}, alpha={alpha:.2f}: "
                    "diagnostic raw residual"
                ),
            )
            assert_close(
                raw_normalized,
                float(
                    diagnostic_record[
                        "raw_normalized_residual"
                    ]
                ),
                label=(
                    f"{class_id}, alpha={alpha:.2f}: "
                    "diagnostic raw normalized residual"
                ),
            )
            assert_close(
                adjusted,
                float(
                    diagnostic_record[
                        "adjusted_normalized_residual"
                    ]
                ),
                label=(
                    f"{class_id}, alpha={alpha:.2f}: "
                    "diagnostic adjusted residual"
                ),
            )
            assert_close(
                normalized_mcse_band,
                float(
                    diagnostic_record[
                        "mcse_band"
                    ]
                )
                / float(
                    diagnostic_record[
                        "scale"
                    ]
                ),
                label=(
                    f"{class_id}, alpha={alpha:.2f}: "
                    "normalized MCSE band"
                ),
            )

            rows.append(
                {
                    "class_id": class_id,
                    "alpha": alpha,
                    "observed_bias": observed_bias,
                    "predicted_bias": predicted_bias,
                    "raw_residual": raw_residual,
                    "scale": scale,
                    "raw_normalized_residual": (
                        raw_normalized
                    ),
                    "mcse": mcse,
                    "z_star": z_star,
                    "normalized_mcse_band": (
                        normalized_mcse_band
                    ),
                    "raw_to_mcse_allowance_ratio": (
                        raw_to_mcse_allowance_ratio
                    ),
                    "adjusted_normalized_residual": (
                        adjusted
                    ),
                    "nonfinite_record_count": (
                        nonfinite_by_alpha_class[
                            (alpha, class_id)
                        ]
                    ),
                }
            )

    if len(rows) != 34:
        raise SystemExit(
            f"FAIL: expected 34 plot rows, observed {len(rows)}"
        )

    rows_by_alpha = {
        alpha: [
            row
            for row in rows
            if math.isclose(
                float(row["alpha"]),
                alpha,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ]
        for alpha in ALPHAS
    }

    for alpha in ALPHAS:
        component = component_by_alpha[alpha]
        raw_values = [
            float(
                row["raw_normalized_residual"]
            )
            for row in rows_by_alpha[alpha]
        ]
        adjusted_values = [
            float(
                row[
                    "adjusted_normalized_residual"
                ]
            )
            for row in rows_by_alpha[alpha]
        ]
        assert_close(
            float(
                np.quantile(
                    raw_values,
                    0.5,
                    method="linear",
                )
            ),
            float(
                component[
                    "raw_normalized"
                ]["median"]
            ),
            label=(
                f"alpha={alpha:.2f}: raw median"
            ),
        )
        assert_close(
            float(
                np.quantile(
                    raw_values,
                    0.9,
                    method="linear",
                )
            ),
            float(
                component[
                    "raw_normalized"
                ]["p90"]
            ),
            label=(
                f"alpha={alpha:.2f}: raw p90"
            ),
        )
        assert_close(
            float(
                np.quantile(
                    adjusted_values,
                    0.5,
                    method="linear",
                )
            ),
            float(
                component[
                    "adjusted_normalized"
                ]["median"]
            ),
            label=(
                f"alpha={alpha:.2f}: adjusted median"
            ),
        )
        assert_close(
            float(
                np.quantile(
                    adjusted_values,
                    0.9,
                    method="linear",
                )
            ),
            float(
                component[
                    "adjusted_normalized"
                ]["p90"]
            ),
            label=(
                f"alpha={alpha:.2f}: adjusted p90"
            ),
        )

    output_dir = (
        run_root
        / "publication_outputs_v1"
        / "figure_3_tess_finite_sample_final_3panel"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        output_dir
        / "figure_3_tess_finite_sample_data.csv"
    )
    svg_path = (
        output_dir
        / "figure_3_tess_finite_sample.svg"
    )
    pdf_path = (
        output_dir
        / "figure_3_tess_finite_sample.pdf"
    )
    png_path = (
        output_dir
        / "figure_3_tess_finite_sample.png"
    )
    caption_path = (
        output_dir
        / "figure_3_caption.md"
    )
    provenance_path = (
        output_dir
        / "figure_3_provenance.json"
    )
    source_copy_path = (
        output_dir
        / "figure_3_source.py"
    )

    write_csv(
        csv_path,
        rows,
    )

    plt.rcParams.update(
        {
            "font.size": 9,
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
    alpha_colors = {
        0.01: theme[0],
        0.05: theme[1],
    }
    alpha_markers = {
        0.01: "o",
        0.05: "^",
    }

    zero_counts = {
        alpha: int(
            component_by_alpha[alpha][
                "adjusted_zero_count"
            ]
        )
        for alpha in ALPHAS
    }
    nonfinite_counts = {
        alpha: sum(
            int(
                row[
                    "nonfinite_record_count"
                ]
            )
            for row in rows_by_alpha[alpha]
        )
        for alpha in ALPHAS
    }

    fig = plt.figure(
        figsize=(15.2, 4.75),
        constrained_layout=False,
    )
    ax_a = fig.add_axes(
        [0.055, 0.18, 0.255, 0.73]
    )
    ax_b = fig.add_axes(
        [0.365, 0.18, 0.255, 0.73]
    )
    ax_c = fig.add_axes(
        [0.690, 0.18, 0.285, 0.73]
    )

    bias_display_scale = 1e3

    # Panels A and B: alpha-specific observed-versus-predicted TESS bias.
    for axis, alpha, panel_letter in (
        (ax_a, 0.01, "A"),
        (ax_b, 0.05, "B"),
    ):
        alpha_rows = sorted(
            rows_by_alpha[alpha],
            key=lambda row: str(
                row["class_id"]
            ),
        )
        predicted = np.asarray(
            [
                float(row["predicted_bias"])
                * bias_display_scale
                for row in alpha_rows
            ],
            dtype=float,
        )
        observed = np.asarray(
            [
                float(row["observed_bias"])
                * bias_display_scale
                for row in alpha_rows
            ],
            dtype=float,
        )
        limit = symmetric_limit(
            predicted,
            observed,
        )
        step = 1.0 if limit > 3.0 else 0.25
        limit = float(
            math.ceil(limit / step) * step
        )
        identity = np.linspace(
            -limit,
            limit,
            200,
        )

        axis.plot(
            identity,
            identity,
            linewidth=1.0,
            color="0.46",
            zorder=1,
        )
        axis.axhline(
            0.0,
            linestyle=":",
            linewidth=0.8,
            color="0.70",
            zorder=0,
        )
        axis.axvline(
            0.0,
            linestyle=":",
            linewidth=0.8,
            color="0.70",
            zorder=0,
        )
        axis.scatter(
            predicted,
            observed,
            s=34,
            marker=alpha_markers[alpha],
            color=alpha_colors[alpha],
            alpha=0.94,
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
            "Predicted TESS bias\n"
            r"$(\times 10^{-3})$"
        )
        axis.set_ylabel(
            "Observed TESS bias\n"
            r"$(\times 10^{-3})$"
        )
        axis.set_title(
            f"{panel_letter}. Bias agreement, "
            + alpha_label(alpha),
            loc="left",
            pad=8,
        )
        axis.text(
            0.04,
            0.96,
            "$B=n=10{,}000$\n"
            "17 primary classes",
            transform=axis.transAxes,
            ha="left",
            va="top",
            fontsize=8,
        )
        axis.annotate(
            "identity",
            xy=(
                0.68 * limit,
                0.68 * limit,
            ),
            xytext=(-2, 2),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=8,
            rotation=45,
            color="0.46",
            fontstyle="italic",
        )

    # Panel C: exact MCSE-floor diagnostic.
    axis = ax_c
    category_positions = {
        0.01: 0.0,
        0.05: 1.0,
    }
    all_ratios: list[float] = []

    for alpha in ALPHAS:
        alpha_rows = sorted(
            rows_by_alpha[alpha],
            key=lambda row: str(
                row["class_id"]
            ),
        )
        ratios = np.asarray(
            [
                float(
                    row[
                        "raw_to_mcse_allowance_ratio"
                    ]
                )
                for row in alpha_rows
            ],
            dtype=float,
        )
        all_ratios.extend(
            ratios.tolist()
        )

        offsets = np.linspace(
            -0.105,
            0.105,
            len(ratios),
        )
        x_values = (
            category_positions[alpha]
            + offsets
        )

        axis.scatter(
            x_values,
            ratios,
            s=34,
            marker=alpha_markers[alpha],
            color=alpha_colors[alpha],
            alpha=0.94,
            linewidths=0.55,
            edgecolors="white",
            zorder=3,
        )

        median_ratio = float(
            np.median(ratios)
        )
        axis.plot(
            [
                category_positions[alpha]
                - 0.18,
                category_positions[alpha]
                + 0.18,
            ],
            [
                median_ratio,
                median_ratio,
            ],
            linewidth=2.4,
            color="0.18",
            solid_capstyle="butt",
            zorder=4,
        )

    if max(all_ratios) >= 1.0:
        raise SystemExit(
            "FAIL: an MCSE-floor ratio is not below 1"
        )

    axis.axhline(
        1.0,
        linewidth=1.05,
        linestyle="--",
        color="0.45",
    )
    axis.text(
        1.43,
        1.015,
        "MCSE floor boundary",
        ha="right",
        va="bottom",
        fontsize=8.2,
        fontstyle="italic",
        color="0.45",
    )
    axis.set_xlim(
        -0.43,
        1.50,
    )
    axis.set_ylim(
        0.0,
        1.18,
    )
    axis.set_xticks(
        [0.0, 1.0]
    )
    axis.set_xticklabels(
        [
            r"$\alpha=0.01$",
            r"$\alpha=0.05$",
        ]
    )
    axis.set_xlabel(
        r"$\alpha$ level"
    )
    axis.set_ylabel(
        r"$|\mathrm{raw\ residual}|"
        r"/(z^\ast\mathrm{MCSE})$"
    )
    axis.set_title(
        "C. Monte Carlo resolution",
        loc="left",
        pad=8,
    )
    axis.grid(
        axis="y",
        alpha=0.14,
    )

    for alpha in ALPHAS:
        axis.text(
            category_positions[alpha],
            1.145,
            f"{zero_counts[alpha]}/17\n"
            "adjusted to 0",
            ha="center",
            va="top",
            fontsize=8.6,
            color=alpha_colors[alpha],
        )

    axis.text(
        0.0,
        -0.18,
        "Ratio < 1 implies an MCSE-adjusted normalized residual of 0.\n"
        "Nonfinite primary records: 0.",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=7.8,
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

    raw_001 = component_by_alpha[
        0.01
    ]["raw_normalized"]
    raw_005 = component_by_alpha[
        0.05
    ]["raw_normalized"]
    adjusted_001 = component_by_alpha[
        0.01
    ]["adjusted_normalized"]
    adjusted_005 = component_by_alpha[
        0.05
    ]["adjusted_normalized"]

    caption = rf"""# Figure 3. Alpha-specific TESS-bias agreement and Monte Carlo resolution

**Caption.**  
(A–B) Class-specific observed TESS bias versus the generalized finite-sample bias prediction at \(B=n=10{{,}}000\), displayed on the original bias scale separately for \(\alpha=0.01\) and \(\alpha=0.05\). Each marker represents one of the 17 prospectively specified primary equivalence classes; the diagonal denotes equality.  
(C) Class-specific ratios of the absolute raw residual to the simultaneous Monte Carlo allowance \(z^\ast\mathrm{{MCSE}}\). Values below 1 have an MCSE-adjusted normalized residual of zero; horizontal segments indicate medians. All 17 primary classes were below the boundary at both alpha levels, and no nonfinite primary TESS record occurred.

The raw median/90th-percentile normalized-residual diagnostics were {float(raw_001["median"]):.4f}/{float(raw_001["p90"]):.4f} at \(\alpha=0.01\) and {float(raw_005["median"]):.4f}/{float(raw_005["p90"]):.4f} at \(\alpha=0.05\), whereas both corresponding MCSE-adjusted summaries were 0. The result therefore constitutes a formal pass under the prospectively specified metric, while raw finite-sample accuracy remains limited by Monte Carlo resolution.
"""
    caption_path.write_text(
        caption,
        encoding="utf-8",
    )

    provenance = {
        "schema_version": "4.0",
        "figure_id": FIGURE_ID,
        "scientific_validation_tag": RESULT_TAG,
        "scientific_validation_commit": result_commit,
        "primary_class_count": 17,
        "alpha_values": list(ALPHAS),
        "largest_pair": [
            10000,
            10000,
        ],
        "source_files": {
            "formal_adjudication": str(
                formal_path.relative_to(repo)
            ),
            "mcse_floor_diagnostic": str(
                diagnostic_path.relative_to(repo)
            ),
            "evidential_adjudication": str(
                evidence_path.relative_to(repo)
            ),
        },
        "cross_checks": {
            "plot_record_count": len(rows),
            "adjusted_zero_counts": {
                str(alpha): zero_counts[alpha]
                for alpha in ALPHAS
            },
            "nonfinite_record_counts": {
                str(alpha): nonfinite_counts[alpha]
                for alpha in ALPHAS
            },
            "raw_summaries": {
                str(alpha): (
                    component_by_alpha[alpha][
                        "raw_normalized"
                    ]
                )
                for alpha in ALPHAS
            },
            "adjusted_summaries": {
                str(alpha): (
                    component_by_alpha[alpha][
                        "adjusted_normalized"
                    ]
                )
                for alpha in ALPHAS
            },
        },
        "layout_refinements": [
            (
                "Alpha-specific bias panels retain their original bias scales "
                "to avoid visual compression from cross-alpha standardization."
            ),
            (
                "The two agreement panels use identical visual grammar "
                "but alpha-specific axis limits."
            ),
            (
                "The MCSE-resolution panel displays the exact ratio "
                "|raw residual|/(z*MCSE), with the decision boundary at 1."
            ),
            (
                "No plotted scientific quantity or formal criterion was changed."
            ),
        ],
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
        "D8-A actual-data publication Figure 3 finalized (three-panel)"
    )
    print("=" * 88)
    print(
        f"Figure ID: {FIGURE_ID}"
    )
    print(
        "Primary TESS records plotted: "
        "34 (17 classes x 2 alpha levels)"
    )
    print(
        "B=n=10000 raw median / p90, alpha=0.01: "
        f"{float(raw_001['median']):.12g} / "
        f"{float(raw_001['p90']):.12g}"
    )
    print(
        "B=n=10000 raw median / p90, alpha=0.05: "
        f"{float(raw_005['median']):.12g} / "
        f"{float(raw_005['p90']):.12g}"
    )
    print(
        "Adjusted-zero counts, alpha=0.01 / 0.05: "
        f"{zero_counts[0.01]}/17 / "
        f"{zero_counts[0.05]}/17"
    )
    print(
        "Alpha-specific bias scales retained: YES"
    )
    print(
        "Panel C MCSE-floor ratio boundary shown at 1: YES"
    )
    print(
        "Nonfinite records, alpha=0.01 / 0.05: "
        f"{nonfinite_counts[0.01]} / "
        f"{nonfinite_counts[0.05]}"
    )
    print(
        "Formal TESS status: PASS"
    )
    print(
        "Evidential classification: "
        "FORMAL_PASS_BUT_MCSE_RESOLUTION_LIMITED"
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
    print(f"Data CSV: {csv_path}")
    print(f"Caption: {caption_path}")
    print(f"Provenance: {provenance_path}")
    print(f"Source copy: {source_copy_path}")


if __name__ == "__main__":
    main()
