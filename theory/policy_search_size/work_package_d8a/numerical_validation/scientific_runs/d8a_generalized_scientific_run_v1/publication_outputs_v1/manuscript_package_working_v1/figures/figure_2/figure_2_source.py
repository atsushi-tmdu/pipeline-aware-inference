#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


EXPECTED_BRANCH = "tess-top-tier-theory"
RESULT_TAG = "d8a-generalized-scientific-validation-v1"
FIGURE_ID = "TESS_D8A_PUBLICATION_FIGURE_2_REFERENCE_VALIDATION_FINAL_V3"
SCALE_BIAS = 1e5


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


def read_actual_data(
    csv_path: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                {
                    "class_id": str(row["class_id"]),
                    "reference_B": int(row["reference_B"]),
                    "population_delta": float(row["population_delta"]),
                    "observed_mean": float(row["observed_mean"]),
                    "observed_bias": float(row["observed_bias"]),
                    "mcse": float(row["mcse"]),
                    "generalized_coefficient": float(
                        row["generalized_coefficient"]
                    ),
                    "generalized_prediction": float(
                        row["generalized_prediction"]
                    ),
                    "raw_residual": float(row["raw_residual"]),
                    "raw_normalized_residual": float(
                        row["raw_normalized_residual"]
                    ),
                    "mcse_adjusted_normalized_residual": float(
                        row["mcse_adjusted_normalized_residual"]
                    ),
                }
            )
    return records


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
        raise SystemExit(f"FAIL: repository not found: {repo}")

    branch = git_output(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise SystemExit(
            f"FAIL: expected branch {EXPECTED_BRANCH}, observed {branch}"
        )

    result_commit = git_output(
        repo,
        "rev-parse",
        f"{RESULT_TAG}^{{commit}}",
    )
    head = git_output(repo, "rev-parse", "HEAD")
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
    source_dir = (
        run_root
        / "publication_outputs_v1"
        / "figure_2_reference_validation_actual"
    )
    data_csv_path = (
        source_dir
        / "figure_2_reference_validation_data.csv"
    )
    source_provenance_path = (
        source_dir
        / "figure_2_provenance.json"
    )
    diagnostic_path = (
        run_root
        / "formal_adjudication"
        / "diagnostics"
        / "D8A_POSTHOC_MCSE_FLOOR_AND_BASELINE_DIAGNOSTIC.json"
    )
    formal_path = (
        run_root
        / "formal_adjudication"
        / "D8A_FORMAL_SCIENTIFIC_ADJUDICATION.json"
    )

    required = [
        data_csv_path,
        source_provenance_path,
        diagnostic_path,
        formal_path,
    ]
    missing = [
        path for path in required
        if not path.is_file()
    ]
    if missing:
        raise SystemExit(
            "FAIL: required actual-data files are missing:\n"
            + "\n".join(str(path) for path in missing)
        )

    records = read_actual_data(data_csv_path)
    source_provenance = load_json(source_provenance_path)
    diagnostic = load_json(diagnostic_path)
    formal = load_json(formal_path)

    if len(records) != 85:
        raise SystemExit(
            f"FAIL: expected 85 actual-data records, observed {len(records)}"
        )
    if formal["formal_acceptance"]["formal_status"] != "PASS":
        raise SystemExit("FAIL: formal status is not PASS")
    if not source_provenance["generation_policy"][
        "locked_summary_files_only"
    ]:
        raise SystemExit(
            "FAIL: source figure was not generated from locked summaries"
        )

    reference_sizes = sorted(
        {
            int(record["reference_B"])
            for record in records
        }
    )
    class_ids = sorted(
        {
            str(record["class_id"])
            for record in records
        }
    )
    if reference_sizes != [
        250,
        500,
        1000,
        3000,
        10000,
    ]:
        raise SystemExit(
            f"FAIL: unexpected reference sizes: {reference_sizes}"
        )
    if len(class_ids) != 17:
        raise SystemExit(
            f"FAIL: expected 17 primary classes, observed {len(class_ids)}"
        )

    by_class: dict[
        str,
        dict[int, dict[str, float]],
    ] = defaultdict(dict)
    for record in records:
        by_class[
            str(record["class_id"])
        ][
            int(record["reference_B"])
        ] = record

    medians: list[float] = []
    p90s: list[float] = []
    all_raw_values: list[float] = []

    for reference_size in reference_sizes:
        values = [
            float(
                by_class[class_id][reference_size][
                    "raw_normalized_residual"
                ]
            )
            for class_id in class_ids
        ]
        all_raw_values.extend(values)
        medians.append(quantile(values, 0.5))
        p90s.append(quantile(values, 0.9))

    locked_reference = diagnostic[
        "component_summaries"
    ]["reference_B10000"]["raw_normalized"]
    assert_close(
        medians[-1],
        float(locked_reference["median"]),
        label="B=10000 raw median",
    )
    assert_close(
        p90s[-1],
        float(locked_reference["p90"]),
        label="B=10000 raw p90",
    )

    baseline = diagnostic[
        "baseline_improvement_diagnostics"
    ]
    improvement_counts = [
        int(
            baseline[
                "generalized_better_than_no_correction_count"
            ]
        ),
        int(
            baseline[
                "generalized_better_than_gradient_only_count"
            ]
        ),
        int(
            baseline[
                "generalized_better_than_smooth_only_count"
            ]
        ),
    ]
    if improvement_counts != [15, 14, 9]:
        raise SystemExit(
            "FAIL: improvement counts mismatch: "
            f"{improvement_counts}"
        )

    largest_B = reference_sizes[-1]
    largest_records = [
        by_class[class_id][largest_B]
        for class_id in class_ids
    ]
    predictions_scaled = np.asarray(
        [
            float(record["generalized_prediction"])
            * SCALE_BIAS
            for record in largest_records
        ],
        dtype=float,
    )
    biases_scaled = np.asarray(
        [
            float(record["observed_bias"])
            * SCALE_BIAS
            for record in largest_records
        ],
        dtype=float,
    )

    output_dir = (
        run_root
        / "publication_outputs_v1"
        / "figure_2_reference_validation_final"
    )
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    svg_path = (
        output_dir
        / "figure_2_reference_validation.svg"
    )
    pdf_path = (
        output_dir
        / "figure_2_reference_validation.pdf"
    )
    png_path = (
        output_dir
        / "figure_2_reference_validation.png"
    )
    caption_path = (
        output_dir / "figure_2_caption.md"
    )
    provenance_path = (
        output_dir
        / "figure_2_refinement_provenance.json"
    )
    source_copy_path = (
        output_dir / "figure_2_source.py"
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

    # Use the active Matplotlib theme rather than fixed color codes.
    theme = plt.rcParams[
        "axes.prop_cycle"
    ].by_key()["color"]
    main_color = theme[0]
    second_color = theme[1]
    third_color = theme[2]

    fig = plt.figure(
        figsize=(14.7, 4.8),
        constrained_layout=False,
    )
    ax_a = fig.add_axes(
        [0.050, 0.17, 0.355, 0.74]
    )
    ax_b = fig.add_axes(
        [0.445, 0.17, 0.245, 0.74]
    )
    ax_c = fig.add_axes(
        [0.755, 0.17, 0.225, 0.74]
    )

    # Panel A: actual trajectories, with the y-axis fitted to the data.
    for class_id in class_ids:
        class_values = [
            float(
                by_class[class_id][reference_size][
                    "raw_normalized_residual"
                ]
            )
            for reference_size in reference_sizes
        ]
        ax_a.plot(
            reference_sizes,
            class_values,
            linewidth=0.65,
            alpha=0.10,
            marker="o",
            markersize=1.6,
            color=main_color,
        )

    ax_a.plot(
        reference_sizes,
        medians,
        linewidth=2.3,
        marker="o",
        markersize=4.0,
        color=main_color,
        label="Median",
    )
    ax_a.plot(
        reference_sizes,
        p90s,
        linewidth=1.9,
        linestyle="--",
        marker="s",
        markersize=3.7,
        color=second_color,
        label="90th percentile",
    )

    y_max = max(all_raw_values) * 1.14
    ax_a.set_ylim(0.0, y_max)
    ax_a.set_xscale("log")
    ax_a.set_xticks(reference_sizes)
    ax_a.set_xticklabels(
        [
            "250",
            "500",
            "1,000",
            "3,000",
            "10,000",
        ]
    )
    ax_a.set_xlabel(
        r"Reference-bank size $B$"
    )
    ax_a.set_ylabel(
        "Raw normalized residual"
    )
    ax_a.set_title(
        "A. Reference-size dependence",
        loc="left",
    )
    ax_a.grid(
        axis="y",
        alpha=0.18,
    )
    ax_a.legend(
        frameon=False,
        loc="upper left",
        fontsize=8,
    )
    ax_a.text(
        0.98,
        0.97,
        "At $B=10{,}000$:\n"
        f"median {medians[-1]:.4f} (criterion 0.15)\n"
        f"90th percentile {p90s[-1]:.4f} (criterion 0.40)",
        transform=ax_a.transAxes,
        ha="right",
        va="top",
        fontsize=8,
    )

    # Panel B: actual data, explicitly displayed in units of 1e-5.
    abs_limit = max(
        float(
            np.max(
                np.abs(predictions_scaled)
            )
        ),
        float(
            np.max(
                np.abs(biases_scaled)
            )
        ),
        1e-6,
    )
    limit = abs_limit * 1.14
    identity = np.linspace(
        -limit,
        limit,
        100,
    )

    ax_b.plot(
        identity,
        identity,
        linewidth=1.0,
        color="0.48",
    )
    ax_b.scatter(
        predictions_scaled,
        biases_scaled,
        s=31,
        color=main_color,
        zorder=3,
    )
    ax_b.axhline(
        0.0,
        linewidth=0.8,
        linestyle=":",
        color="0.68",
    )
    ax_b.axvline(
        0.0,
        linewidth=0.8,
        linestyle=":",
        color="0.68",
    )
    ax_b.set_xlim(-limit, limit)
    ax_b.set_ylim(-limit, limit)
    ax_b.set_aspect(
        "equal",
        adjustable="box",
    )
    ax_b.set_xlabel(
        "Generalized prediction\n"
        r"$(\times 10^{-5})$"
    )
    ax_b.set_ylabel(
        "Observed bias\n"
        r"$(\times 10^{-5})$"
    )
    ax_b.set_title(
        "B. Observed bias vs generalized prediction",
        loc="left",
    )
    ax_b.text(
        0.04,
        0.96,
        "17 primary classes\n"
        "$B=10{,}000$",
        transform=ax_b.transAxes,
        ha="left",
        va="top",
        fontsize=8,
    )
    ax_b.text(
        0.63,
        0.67,
        "identity",
        transform=ax_b.transAxes,
        ha="center",
        va="center",
        fontsize=8,
        rotation=45,
        color="0.48",
    )

    # Panel C: compact counts; the nonfatal note is moved to a footnote.
    bar_labels = [
        "No correction",
        "Gradient-only",
        "Smooth-only*",
    ]
    y_positions = np.arange(
        len(bar_labels)
    )
    bars = ax_c.barh(
        y_positions,
        improvement_counts,
        height=0.52,
        color=main_color,
    )
    ax_c.set_yticks(y_positions)
    ax_c.set_yticklabels(bar_labels)
    ax_c.invert_yaxis()
    ax_c.set_xlim(0, 17.8)
    ax_c.set_xticks(
        [0, 5, 10, 15, 17]
    )
    ax_c.set_xlabel(
        "Improved primary classes"
    )
    ax_c.set_title(
        "C. Improvement over alternative baselines",
        loc="left",
    )
    ax_c.text(
        0.0,
        0.98,
        "Generalized correction performed better than:",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        fontstyle="italic",
    )
    ax_c.grid(
        axis="x",
        alpha=0.18,
    )

    for bar, count in zip(
        bars,
        improvement_counts,
    ):
        ax_c.text(
            count + 0.20,
            (
                bar.get_y()
                + bar.get_height() / 2
            ),
            f"{count}/17",
            va="center",
            ha="left",
            fontsize=9,
        )

    ax_c.text(
        0.0,
        -0.18,
        "* Descriptive, nonfatal comparison.",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=7.8,
        fontstyle="italic",
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

    caption = rf"""# Figure 2. Reference-only numerical validation

**Caption.**  
(A) Class-specific raw normalized residuals across the five prospectively specified reference-bank sizes. Thin lines represent the 17 primary equivalence classes; the solid and dashed summary lines show the median and 90th percentile, respectively. The vertical range is fitted to the observed values so their size dependence remains visible. The inset text compares the largest-\(B\) summaries with the prospectively specified criteria; the criterion levels are not drawn as horizontal lines because doing so would compress the observed trajectories.  
(B) Class-specific observed reference bias versus the generalized prediction \(C_{{\Delta,B}}^{{\mathrm{{gen}}}}/B\) at \(B=10{{,}}000\). Both axes are displayed in units of \(10^{{-5}}\); the diagonal denotes equality.  
(C) Numbers of primary classes for which the generalized correction reduced absolute bias error relative to no correction, the gradient-only correction, and the smooth-only correction. The smooth-only comparison was descriptive and nonfatal.

All plotted points and trajectories come from the locked `JOB_SUMMARY.json`-derived data table. The raw Monte Carlo batches were not reanalysed. The formal status remained PASS; the raw \(B=500\)-to-\(10{{,}}000\) median diagnostic did not demonstrate monotone improvement.
"""
    caption_path.write_text(
        caption,
        encoding="utf-8",
    )

    provenance = {
        "schema_version": "3.0",
        "figure_id": FIGURE_ID,
        "scientific_validation_tag": RESULT_TAG,
        "scientific_validation_commit": result_commit,
        "source_actual_data_csv": str(
            data_csv_path.relative_to(repo)
        ),
        "source_actual_data_provenance": str(
            source_provenance_path.relative_to(
                repo
            )
        ),
        "source_diagnostic": str(
            diagnostic_path.relative_to(repo)
        ),
        "primary_class_count": len(class_ids),
        "actual_record_count": len(records),
        "reference_sizes": reference_sizes,
        "largest_B_cross_check": {
            "median": medians[-1],
            "p90": p90s[-1],
            "locked_median": float(
                locked_reference["median"]
            ),
            "locked_p90": float(
                locked_reference["p90"]
            ),
            "passed": True,
        },
        "improvement_counts": improvement_counts,
        "refinements": [
            (
                "Panel A y-axis fitted to actual residuals; "
                "locked criteria shown in an explicit numeric annotation."
            ),
            (
                "Class-specific trajectories made visually subordinate "
                "to the median and 90th-percentile summaries."
            ),
            (
                "Panel B axes explicitly scaled to units of 1e-5; "
                "identity and zero references rendered neutrally."
            ),
            (
                "Panel C labels shortened and the nonfatal explanation "
                "retained as a footnote."
            ),
            (
                "Overall run-status footer removed from the figure."
            ),
        ],
        "generation_policy": {
            "actual_locked_data_only": True,
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
        "D8-A actual-data Figure 2 finalized"
    )
    print("=" * 88)
    print(
        f"Figure ID: {FIGURE_ID}"
    )
    print(
        "Actual records used: 85 "
        "(17 classes x 5 reference sizes)"
    )
    print(
        f"B=10000 median / p90: "
        f"{medians[-1]:.12g} / "
        f"{p90s[-1]:.12g}"
    )
    print(
        "Locked-diagnostic cross-check: PASS"
    )
    print(
        "Panel A final annotation and line hierarchy: YES"
    )
    print(
        "Panel B explicit 1e-5 scaling and neutral references: YES"
    )
    print(
        "Panel C final labels and footnote: YES"
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
        f"Caption: {caption_path}"
    )
    print(
        f"Provenance: {provenance_path}"
    )
    print(
        f"Source copy: {source_copy_path}"
    )


if __name__ == "__main__":
    main()
