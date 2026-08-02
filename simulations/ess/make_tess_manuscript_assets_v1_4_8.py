#!/usr/bin/env python3
"""Create integrated frozen TESS manuscript assets v1.4.8.

The primary confirmatory simulation and the SUPPORT2-anchored supplementary
validation remain distinct evidence tiers. This script reads frozen processed
results only; it does not rerun any simulation or alter adjudications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np
import pandas as pd


POLICY_ORDER = (
    "fixed_base",
    "rescue_triggered",
    "random_expansion",
    "promising_triggered",
    "fixed_full",
)

POLICY_SHORT = {
    "fixed_base": "Fixed base",
    "fixed_full": "Fixed full",
    "random_expansion": "Random",
    "promising_triggered": "Promising",
    "rescue_triggered": "Rescue",
}

CONFIRMATORY_LABELS = {
    "high_dependency_linear_20": "High-dependency",
    "mixed_realistic_20": "Mixed-realistic",
}

SUPPORT2_LIBRARY = "support2_real_structure_20"
SUPPORT2_LABEL = "SUPPORT2-anchored"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required frozen input not found: {path}")
    return path


def save_figure(fig, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".png"), dpi=600, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def set_publication_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out")
    ax.grid(axis="y", alpha=0.18)


def make_figure1(output_dir: Path) -> None:
    """Draw the workflow with continuous connectors and visible arrowheads.

    Box coordinates are exact: rounded rectangles use zero padding so the
    border location is unambiguous. Connector lines meet the border exactly.
    Arrowheads are drawn last, above the boxes, with their tips on the
    destination border and their bases outside the destination box.
    """
    fig, ax = plt.subplots(figsize=(8.0, 10.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    line_width = 1.25
    arrow_half_width = 0.0070
    arrow_height = 0.0110

    def connector(xs, ys, *, zorder=2.2):
        ax.plot(
            xs,
            ys,
            color="black",
            linewidth=line_width,
            solid_capstyle="butt",
            solid_joinstyle="miter",
            zorder=zorder,
            clip_on=False,
        )

    def arrowhead_down(x: float, y_tip: float):
        """Draw a downward triangle with its tip exactly at y_tip."""
        y_base = y_tip + arrow_height
        triangle = Polygon(
            [
                (x, y_tip),
                (x - arrow_half_width, y_base),
                (x + arrow_half_width, y_base),
            ],
            closed=True,
            facecolor="black",
            edgecolor="black",
            linewidth=0.4,
            zorder=5,
            clip_on=False,
        )
        ax.add_patch(triangle)

    def down_arrow(x: float, y_start: float, y_tip: float):
        """Draw a vertical line ending in a visible arrowhead at y_tip."""
        y_base = y_tip + arrow_height
        connector([x, x], [y_start, y_base])
        arrowhead_down(x, y_tip)

    def box(x: float, y: float, w: float, h: float, *, linewidth: float = 1.35):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.0,rounding_size=0.012",
            facecolor="white",
            edgecolor="black",
            linewidth=linewidth,
            zorder=3,
        )
        ax.add_patch(patch)

    # Exact visible box boundaries: (x, y, width, height).
    base = (0.31, 0.865, 0.38, 0.078)
    evidence = (0.31, 0.735, 0.38, 0.078)
    left = (0.10, 0.565, 0.34, 0.090)
    right = (0.58, 0.565, 0.24, 0.090)
    winner = (0.33, 0.405, 0.34, 0.092)
    rejection = (0.20, 0.235, 0.60, 0.115)
    tess = (0.20, 0.070, 0.60, 0.125)

    # Draw boxes first. Lines are then placed only outside the boxes, and
    # arrowheads are drawn above the box layer so they cannot disappear.
    for geometry in (base, evidence, left, right, winner, rejection, tess):
        box(*geometry)

    # Main vertical flow.
    down_arrow(0.50, base[1], evidence[1] + evidence[3])

    # Evidence -> branch boxes. The connector starts exactly at the evidence
    # bottom border; no line exists inside the evidence box.
    branch_y = 0.690
    connector([0.50, 0.50], [evidence[1], branch_y])
    connector([0.27, 0.70], [branch_y, branch_y])
    down_arrow(0.27, branch_y, left[1] + left[3])
    down_arrow(0.70, branch_y, right[1] + right[3])

    # Branch boxes -> winner. Elbows share exact coordinates, eliminating gaps.
    merge_y = 0.530
    connector([0.27, 0.27, 0.43], [left[1], merge_y, merge_y])
    connector([0.70, 0.70, 0.57], [right[1], merge_y, merge_y])
    down_arrow(0.43, merge_y, winner[1] + winner[3])
    down_arrow(0.57, merge_y, winner[1] + winner[3])

    down_arrow(0.50, winner[1], rejection[1] + rejection[3])
    down_arrow(0.50, rejection[1], tess[1] + tess[3])

    # Title and labels.
    ax.text(
        0.5,
        0.982,
        "Adaptive development policy and inferential search size",
        ha="center",
        va="top",
        fontsize=15.5,
        fontweight="bold",
        zorder=6,
    )

    ax.text(0.50, 0.915, "Base candidate family", ha="center", va="center", fontsize=12.4, zorder=6)
    ax.text(0.50, 0.885, r"$K=7$", ha="center", va="center", fontsize=15.0, zorder=6)
    ax.text(0.50, 0.774, "Base-stage evidence", ha="center", va="center", fontsize=12.4, zorder=6)

    ax.text(0.27, 0.622, "Optional candidate family", ha="center", va="center", fontsize=11.5, zorder=6)
    ax.text(0.27, 0.590, r"$K=13$", ha="center", va="center", fontsize=14.7, zorder=6)
    ax.text(0.70, 0.610, "No expansion", ha="center", va="center", fontsize=12.1, zorder=6)
    ax.text(0.19, 0.681, "activate", ha="center", va="bottom", fontsize=9.8, zorder=6)
    ax.text(0.79, 0.681, "do not activate", ha="center", va="bottom", fontsize=9.8, zorder=6)

    ax.text(0.50, 0.463, "Final winner", ha="center", va="center", fontsize=12.3, zorder=6)
    ax.text(0.50, 0.430, "and naive p-value", ha="center", va="center", fontsize=12.3, zorder=6)

    ax.text(0.50, 0.315, "Policy rejection curve", ha="center", va="center", fontsize=11.8, zorder=6)
    ax.text(
        0.50,
        0.274,
        r"$\pi_{\mathcal{A}}(\alpha)=P_{0}\,\left(P_{\mathcal{A}}<\alpha\right)$",
        ha="center",
        va="center",
        fontsize=17.0,
        zorder=6,
    )

    ax.text(0.50, 0.160, "TESS standardization", ha="center", va="center", fontsize=11.8, zorder=6)
    ax.text(
        0.50,
        0.111,
        r"$\mathrm{TESS}_{\mathcal{A}}(\alpha)"
        r"=\dfrac{\log\{1-\pi_{\mathcal{A}}(\alpha)\}}{\log(1-\alpha)}$",
        ha="center",
        va="center",
        fontsize=16.2,
        zorder=6,
    )

    ax.text(
        0.50,
        0.025,
        r"Matched-budget mechanism: "
        r"$\pi_{A}-\pi_{\mathrm{random},r}="
        r"\operatorname{Cov}(A,R_{\mathrm{full}}-R_{\mathrm{base}})$",
        ha="center",
        va="center",
        fontsize=9.3,
        zorder=6,
    )

    save_figure(fig, output_dir / "Figure1_policy_framework")


def load_curve_data(results_root: Path, library: str) -> pd.DataFrame:
    path = require(
        results_root
        / "adaptive_policy"
        / library
        / "adaptive_ml_policy_tess_bootstrap_curves.csv"
    )
    frame = pd.read_csv(path)
    required = {
        "policy",
        "local_alpha",
        "tess",
        "pointwise_low_95",
        "pointwise_high_95",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    return frame


def make_tess_curve(frame: pd.DataFrame, title: str, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 5.3))
    for policy in POLICY_ORDER:
        subset = frame[frame["policy"] == policy].copy()
        if subset.empty:
            continue
        subset = subset.sort_values("local_alpha", ascending=False)
        lower = subset["tess"] - subset["pointwise_low_95"]
        upper = subset["pointwise_high_95"] - subset["tess"]
        ax.errorbar(
            subset["local_alpha"],
            subset["tess"],
            yerr=np.vstack([lower, upper]),
            marker="o",
            linewidth=1.45,
            capsize=3,
            label=POLICY_SHORT[policy],
        )
    ax.axvline(0.05, linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Tail-equivalent search size")
    ax.set_title(title)
    set_publication_axes(ax)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    save_figure(fig, output_path)


def make_policy_curve_small_multiples(
    frame: pd.DataFrame,
    title: str,
    output_path: Path,
) -> None:
    """Render one aligned panel per policy to eliminate interval overlap.

    All panels share the same x and y limits. The point estimates remain
    connected across alpha and the frozen pointwise 95% intervals are shown as
    capped vertical error bars. Separating policies makes every interval
    visible without changing any estimate or confidence limit.
    """
    available = [policy for policy in POLICY_ORDER if not frame[frame["policy"] == policy].empty]
    if not available:
        raise ValueError("No policy rows available for supplementary curve figure")

    fig, axes = plt.subplots(
        len(available),
        1,
        figsize=(8.0, 9.3),
        sharex=True,
        sharey=True,
    )
    if len(available) == 1:
        axes = np.asarray([axes])

    selected = frame[frame["policy"].isin(available)].copy()
    ymin = float(selected["pointwise_low_95"].min())
    ymax = float(selected["pointwise_high_95"].max())
    pad = max((ymax - ymin) * 0.08, 0.12)

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    alpha_ticks = np.array([0.20, 0.10, 0.05, 0.025, 0.010, 0.005])

    for index, (ax, policy) in enumerate(zip(axes, available)):
        subset = frame[frame["policy"] == policy].copy().sort_values("local_alpha", ascending=False)
        x = subset["local_alpha"].to_numpy(dtype=float)
        y = subset["tess"].to_numpy(dtype=float)
        low = subset["pointwise_low_95"].to_numpy(dtype=float)
        high = subset["pointwise_high_95"].to_numpy(dtype=float)
        yerr = np.vstack([y - low, high - y])
        color = colors[index % len(colors)]

        ax.errorbar(
            x,
            y,
            yerr=yerr,
            color=color,
            marker="o",
            markersize=4.8,
            linewidth=1.45,
            elinewidth=1.05,
            capsize=3.0,
            capthick=1.0,
            zorder=3,
        )
        ax.axvline(0.05, linestyle="--", linewidth=0.9, color="0.45", zorder=1)
        ax.set_xscale("log")
        ax.set_ylim(max(0.0, ymin - pad), ymax + pad)
        ax.grid(axis="y", alpha=0.14)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.text(
            0.015,
            0.84,
            POLICY_SHORT[policy],
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=10.0,
            fontweight="bold",
        )

    axes[-1].set_xlim(0.22, 0.0045)
    axes[-1].set_xticks(alpha_ticks)
    axes[-1].set_xticklabels(["0.20", "0.10", "0.05", "0.025", "0.010", "0.005"])
    axes[-1].set_xlabel("Local alpha (smaller = deeper tail)")
    fig.supylabel("Tail-equivalent search size")
    fig.suptitle(title, fontsize=13.2, fontweight="bold", y=0.995)
    fig.tight_layout(rect=(0.05, 0.03, 1.0, 0.98), h_pad=0.45)
    save_figure(fig, output_path)


def make_fixed_search_comparison_figure(
    confirmatory_root: Path,
    output_path: Path,
) -> None:
    """Plot fixed K=7 and K=20 TESS curves from frozen confirmatory CSVs.

    This is a deterministic data visualization. It reads the fixed-base and
    fixed-full rows from the frozen paired-bootstrap curve files; no values are
    typed into the plotting code.
    """
    structures = [
        ("high_dependency_linear_20", "High-dependency library"),
        ("mixed_realistic_20", "Mixed-realistic library"),
    ]
    policy_to_label = {
        "fixed_base": "K = 7",
        "fixed_full": "K = 20",
    }
    alpha_ticks = np.array([0.20, 0.10, 0.05, 0.025, 0.010, 0.005])

    fig, axes = plt.subplots(2, 1, figsize=(9.0, 7.2), sharex=True)
    for ax, (library, title) in zip(axes, structures):
        frame = load_curve_data(confirmatory_root, library)
        for policy in ("fixed_base", "fixed_full"):
            subset = frame[frame["policy"] == policy].copy()
            if subset.empty:
                raise ValueError(f"No frozen curve rows found for {library}/{policy}")
            subset = subset.sort_values("local_alpha", ascending=False)
            x = subset["local_alpha"].to_numpy(dtype=float)
            y = subset["tess"].to_numpy(dtype=float)
            low = subset["pointwise_low_95"].to_numpy(dtype=float)
            high = subset["pointwise_high_95"].to_numpy(dtype=float)
            line, = ax.plot(
                x,
                y,
                marker="o",
                markersize=5.5,
                linewidth=1.75,
                label=policy_to_label[policy],
                zorder=3,
            )
            ax.fill_between(
                x,
                low,
                high,
                color=line.get_color(),
                alpha=0.12,
                linewidth=0,
                zorder=1,
            )

        ax.set_xscale("log")
        ax.set_title(title, fontsize=13.0, fontweight="bold", pad=7)
        ax.set_ylabel("Tail-equivalent search size (TESS)")
        ax.grid(axis="y", alpha=0.15)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, loc="upper left", fontsize=9.5)

        # Data-dependent y-limits retain the true uncertainty range while
        # avoiding unused vertical space.
        selected = frame[frame["policy"].isin(["fixed_base", "fixed_full"])]
        ymin = float(selected["pointwise_low_95"].min())
        ymax = float(selected["pointwise_high_95"].max())
        pad = max((ymax - ymin) * 0.10, 0.15)
        ax.set_ylim(max(0.0, ymin - pad), ymax + pad)

    # Set the shared x-direction once. Calling invert_xaxis() inside both
    # shared panels would toggle the direction twice.
    axes[-1].set_xlim(0.22, 0.0045)
    axes[-1].set_xticks(alpha_ticks)
    axes[-1].set_xticklabels(["0.20", "0.10", "0.05", "0.025", "0.010", "0.005"])
    axes[-1].set_xlabel("Local significance level (alpha)")
    fig.tight_layout(h_pad=1.5)
    save_figure(fig, output_path)


def load_confirmatory_rows(confirmatory_root: Path, include_interaction: bool) -> pd.DataFrame:
    interaction = pd.read_csv(require(confirmatory_root / "confirmatory_policy_interaction.csv"))
    mapping = [
        ("high_dependency_linear_20", "promising_tess_minus_matched_random", "High-dependency", "Promising − matched random"),
        ("high_dependency_linear_20", "rescue_tess_minus_matched_random", "High-dependency", "Rescue − matched random"),
        ("mixed_realistic_20", "promising_tess_minus_matched_random", "Mixed-realistic", "Promising − matched random"),
        ("mixed_realistic_20", "rescue_tess_minus_matched_random", "Mixed-realistic", "Rescue − matched random"),
    ]
    if include_interaction:
        mapping.append(
            ("mixed_minus_high", "promising_tess_minus_matched_random", "Mixed − high", "Promising policy interaction")
        )

    rows = []
    for structure, metric, display, contrast in mapping:
        selected = interaction[
            (interaction["library_or_contrast"] == structure)
            & np.isclose(interaction["local_alpha"], 0.05)
            & (interaction["metric"] == metric)
        ]
        if len(selected) != 1:
            raise ValueError(f"Expected one confirmatory row for {structure}/{metric}")
        row = selected.iloc[0]
        rows.append(
            {
                "evidence_tier": "Locked confirmatory",
                "structure": display,
                "contrast": contrast,
                "estimate": float(row["estimate"]),
                "low": float(row["ci_low_95"]),
                "high": float(row["ci_high_95"]),
                "locked_primary": structure == "mixed_realistic_20" and metric.startswith("promising"),
                "supportive": False,
                "source": "Locked paired confirmatory bootstrap",
            }
        )
    return pd.DataFrame(rows)


def load_support2_rows(support2_root: Path) -> pd.DataFrame:
    adjudication = json.loads(
        require(support2_root / "support2_validation_adjudication.json").read_text(encoding="utf-8")
    )
    point = pd.read_csv(
        require(support2_root / "budget_standardized_audit" / "budget_standardized_policy_effects.csv")
    )
    boot = pd.read_csv(
        require(support2_root / "budget_standardized_audit" / "budget_standardized_policy_effects_bootstrap.csv")
    )
    point_row = point[np.isclose(point["local_alpha"], 0.05)]
    if len(point_row) != 1:
        raise ValueError("Expected one SUPPORT2 point-estimate row at alpha 0.05")
    point_row = point_row.iloc[0]
    rescue_boot = boot[
        np.isclose(boot["local_alpha"], 0.05)
        & (boot["metric"] == "tess_rescue_minus_matched_random")
    ]
    if len(rescue_boot) != 1:
        raise ValueError("Expected one SUPPORT2 rescue bootstrap row at alpha 0.05")
    rescue_boot = rescue_boot.iloc[0]

    primary = adjudication["primary"]
    return pd.DataFrame(
        [
            {
                "evidence_tier": "Supplementary validation",
                "structure": SUPPORT2_LABEL,
                "contrast": "Promising − matched random",
                "estimate": float(primary["estimate"]),
                "low": float(primary["ci_low_95"]),
                "high": float(primary["ci_high_95"]),
                "locked_primary": False,
                "supportive": bool(primary["supportive_rule_met"]),
                "source": "Locked SUPPORT2 paired bootstrap",
            },
            {
                "evidence_tier": "Supplementary validation",
                "structure": SUPPORT2_LABEL,
                "contrast": "Rescue − matched random",
                "estimate": float(point_row["tess_rescue_minus_matched_random"]),
                "low": float(rescue_boot["ci_low_95"]),
                "high": float(rescue_boot["ci_high_95"]),
                "locked_primary": False,
                "supportive": False,
                "source": "Locked SUPPORT2 paired bootstrap",
            },
        ]
    )


def make_forest_plot(rows: pd.DataFrame, output_path: Path) -> None:
    order = [
        ("High-dependency", "Promising − matched random"),
        ("High-dependency", "Rescue − matched random"),
        ("Mixed-realistic", "Promising − matched random"),
        ("Mixed-realistic", "Rescue − matched random"),
        (SUPPORT2_LABEL, "Promising − matched random"),
        (SUPPORT2_LABEL, "Rescue − matched random"),
    ]
    ordered_rows = []
    for structure, contrast in order:
        selected = rows[(rows["structure"] == structure) & (rows["contrast"] == contrast)]
        if len(selected) != 1:
            raise ValueError(f"Expected one forest row for {structure}/{contrast}")
        ordered_rows.append(selected.iloc[0])
    ordered = pd.DataFrame(ordered_rows)

    y = np.array([5.5, 4.7, 3.4, 2.6, 1.3, 0.5])
    labels = [
        "High-dependency: promising",
        "High-dependency: rescue",
        "Mixed-realistic: promising",
        "Mixed-realistic: rescue",
        "SUPPORT2-anchored: promising",
        "SUPPORT2-anchored: rescue",
    ]

    fig, ax = plt.subplots(figsize=(9.1, 6.0))
    for yy, (_, row) in zip(y, ordered.iterrows()):
        if row["locked_primary"]:
            marker = "s"
            markersize = 7.5
        elif row["evidence_tier"] == "Supplementary validation":
            marker = "D"
            markersize = 7.0
        else:
            marker = "o"
            markersize = 6.5
        ax.errorbar(
            row["estimate"],
            yy,
            xerr=np.array([[row["estimate"] - row["low"]], [row["high"] - row["estimate"]]]),
            marker=marker,
            markersize=markersize,
            capsize=4,
            linewidth=1.45,
        )

    ax.axvline(0.0, linewidth=1)
    ax.axhline(4.05, linewidth=0.8, alpha=0.35)
    ax.axhline(1.95, linewidth=0.8, alpha=0.35)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Budget-standardized TESS difference at alpha = 0.05")
    ax.set_title("Adaptive-policy effects across simulated and clinical-data structures")
    set_publication_axes(ax)
    ax.grid(axis="x", alpha=0.18)
    ax.grid(axis="y", visible=False)
    ax.set_ylim(0.0, 6.0)
    fig.text(
        0.5,
        0.012,
        "Square: locked primary confirmatory comparison; diamonds: supplementary SUPPORT2-anchored null validation.",
        ha="center",
        fontsize=8.5,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    save_figure(fig, output_path)


def load_confirmatory_mechanism(confirmatory_root: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        require(confirmatory_root / "mechanism" / "phase3c_policy_mechanism_all_libraries.csv")
    )
    return frame[np.isclose(frame["local_alpha"], 0.05)].copy()


def load_support2_summary(support2_root: Path) -> dict:
    return json.loads(
        require(support2_root / "support2_validation_summary.json").read_text(encoding="utf-8")
    )


def make_gain_capture_plot(confirmatory_root: Path, support2_root: Path, output_path: Path) -> None:
    """Draw a minimal grouped bar chart from frozen mechanism summaries."""
    mechanism = load_confirmatory_mechanism(confirmatory_root)
    support2 = load_support2_summary(support2_root)

    labels = ["High-dependency", "Mixed-realistic", "SUPPORT2"]
    activation: list[float] = []
    capture: list[float] = []

    for library in ("high_dependency_linear_20", "mixed_realistic_20"):
        row = mechanism[mechanism["library"] == library]
        if len(row) != 1:
            raise ValueError(f"Expected one mechanism row for {library}")
        row = row.iloc[0]
        activation.append(100.0 * float(row["promising_activation_rate"]))
        total = int(row["gain_count_promising"]) + int(row["gain_count_rescue"])
        capture.append(100.0 * int(row["gain_count_promising"]) / total if total else np.nan)

    activation.append(100.0 * float(support2["promising_activation_rate"]))
    capture.append(100.0 * float(support2["promising_gain_capture_fraction"]))

    x = np.arange(len(labels), dtype=float)
    width = 0.30
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    bars_activation = ax.bar(
        x - width / 2,
        activation,
        width,
        label="Activated",
        edgecolor="none",
        zorder=3,
    )
    bars_capture = ax.bar(
        x + width / 2,
        capture,
        width,
        label="Incremental gains captured",
        edgecolor="none",
        zorder=3,
    )

    for bars in (bars_activation, bars_capture):
        for bar in bars:
            value = float(bar.get_height())
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 1.5,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10.0,
            )

    ax.axhline(50.0, color="0.35", linewidth=0.9, zorder=2)
    ax.text(
        len(labels) - 0.02,
        50.0,
        "50% activation\nbaseline",
        ha="left",
        va="center",
        fontsize=8.8,
        color="0.35",
    )
    ax.set_xlim(-0.55, len(labels) - 0.20)
    ax.set_ylim(0, 110)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percent (%)")
    ax.set_title(
        "Promising activation captures disproportionate incremental gains",
        fontsize=13.0,
        fontweight="bold",
        pad=10,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.15, zorder=0)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    save_figure(fig, output_path)


def make_covariance_plot(confirmatory_root: Path, support2_root: Path, output_path: Path) -> None:
    interaction = pd.read_csv(require(confirmatory_root / "confirmatory_policy_interaction.csv"))
    confirmatory = interaction[
        interaction["library_or_contrast"].isin(
            ["high_dependency_linear_20", "mixed_realistic_20"]
        )
        & (interaction["metric"] == "cov_activation_increment")
    ].copy()
    support2 = pd.read_csv(
        require(
            support2_root
            / "mechanism"
            / SUPPORT2_LIBRARY
            / "activation_increment_covariance_bootstrap.csv"
        )
    )

    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    for library in ("high_dependency_linear_20", "mixed_realistic_20"):
        group = confirmatory[confirmatory["library_or_contrast"] == library].sort_values(
            "local_alpha", ascending=False
        )
        ax.errorbar(
            group["local_alpha"],
            group["estimate"],
            yerr=np.vstack(
                [group["estimate"] - group["ci_low_95"], group["ci_high_95"] - group["estimate"]]
            ),
            marker="o",
            linewidth=1.45,
            capsize=3,
            label=CONFIRMATORY_LABELS[library],
        )

    estimate_col = "cov_activation_increment" if "cov_activation_increment" in support2.columns else "estimate"
    support2 = support2.sort_values("local_alpha", ascending=False)
    ax.errorbar(
        support2["local_alpha"],
        support2[estimate_col],
        yerr=np.vstack(
            [support2[estimate_col] - support2["ci_low_95"], support2["ci_high_95"] - support2[estimate_col]]
        ),
        marker="D",
        linewidth=1.45,
        capsize=3,
        label=SUPPORT2_LABEL,
    )
    ax.axhline(0.0, linewidth=1)
    ax.axvline(0.05, linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local alpha (smaller = deeper tail)")
    ax.set_ylabel("Cov(activation, incremental rejection effect)")
    ax.set_title("Policy allocation mechanism across inferential thresholds")
    set_publication_axes(ax)
    ax.legend(frameon=False)
    fig.tight_layout()
    save_figure(fig, output_path)


def make_decile_plot(results_root: Path, library: str, title: str, output_path: Path) -> None:
    frame = pd.read_csv(
        require(results_root / "mechanism" / library / "incremental_effect_by_base_score.csv")
    ).sort_values("score_mean")
    fig, ax = plt.subplots(figsize=(7.3, 5.2))
    ax.plot(frame["score_mean"], frame["incremental_gain_rate"], marker="o", label="Base nonreject → full reject")
    ax.plot(frame["score_mean"], frame["incremental_loss_rate"], marker="s", label="Base reject → full nonreject")
    ax.plot(frame["score_mean"], frame["mean_incremental_effect"], marker="^", label="Net incremental effect")
    # Neutral zero-reference line: keep it visually distinct from data series.
    ax.axhline(
        0.0,
        color="0.55",
        linestyle="--",
        linewidth=0.9,
        zorder=0,
    )
    ax.set_xlabel("Mean base-stage maximum ROC AUC within decile")
    ax.set_ylabel("Conditional probability / mean effect")
    ax.set_title(title)
    set_publication_axes(ax)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    save_figure(fig, output_path)


def make_table1(confirmatory_config: Path, support2_config: Path, output_path: Path) -> pd.DataFrame:
    c = json.loads(confirmatory_config.read_text(encoding="utf-8"))
    s = json.loads(support2_config.read_text(encoding="utf-8"))
    rows = [
        ("Locked confirmatory simulation", "Role", "Primary confirmatory evidence"),
        ("Locked confirmatory simulation", "Structures", "; ".join(c["libraries"])),
        ("Locked confirmatory simulation", "Candidate split", "Base 7; optional extra 13"),
        ("Locked confirmatory simulation", "Reference replications", f"{c['null_repetitions']:,} per structure"),
        ("Locked confirmatory simulation", "Evaluation replications", f"{c['evaluation_repetitions']:,} per structure"),
        ("Locked confirmatory simulation", "Primary alpha", c["primary_alpha"]),
        ("Locked confirmatory simulation", "Primary estimand", c["primary_estimand"]),
        ("Locked confirmatory simulation", "Success rule", c["primary_success_rule"]),
        ("SUPPORT2-anchored validation", "Role", s["role_in_manuscript"]),
        ("SUPPORT2-anchored validation", "Observed rows", s["data"]["expected_rows"]),
        ("SUPPORT2-anchored validation", "Fixed train / selection", f"{s['design']['n_train']} / {s['design']['n_selection']}"),
        ("SUPPORT2-anchored validation", "Reference / evaluation", f"{s['design']['reference_repetitions']:,} / {s['design']['evaluation_repetitions']:,}"),
        ("SUPPORT2-anchored validation", "Candidate split", f"Base {s['adaptive_policy']['base_candidate_count']}; optional extra {s['adaptive_policy']['full_candidate_count'] - s['adaptive_policy']['base_candidate_count']}"),
        ("SUPPORT2-anchored validation", "Null construction", s["design"]["permutation_scheme"]),
        ("SUPPORT2-anchored validation", "Supportive alpha", s["inference"]["primary_alpha"]),
        ("SUPPORT2-anchored validation", "Supportive rule", s["inference"]["supportive_rule"]),
    ]
    table = pd.DataFrame(rows, columns=["Study component", "Element", "Prespecified value"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    return table


def confirmatory_covariance_rows(confirmatory_root: Path) -> list[dict]:
    interaction = pd.read_csv(require(confirmatory_root / "confirmatory_policy_interaction.csv"))
    rows = []
    for structure, display in (
        ("high_dependency_linear_20", "High-dependency"),
        ("mixed_realistic_20", "Mixed-realistic"),
    ):
        selected = interaction[
            (interaction["library_or_contrast"] == structure)
            & np.isclose(interaction["local_alpha"], 0.05)
            & (interaction["metric"] == "cov_activation_increment")
        ]
        if len(selected) != 1:
            raise ValueError(f"Expected one covariance row for {structure}")
        row = selected.iloc[0]
        rows.append(
            {
                "Evidence tier": "Locked confirmatory",
                "Structure": display,
                "Contrast": "Cov(A,D)",
                "Alpha": 0.05,
                "Estimate": float(row["estimate"]),
                "CI low": float(row["ci_low_95"]),
                "CI high": float(row["ci_high_95"]),
                "Interpretation": "Allocation mechanism",
                "Source": "Locked paired confirmatory bootstrap",
            }
        )
    return rows


def make_table2(confirmatory_root: Path, support2_root: Path, output_path: Path) -> pd.DataFrame:
    confirmatory = load_confirmatory_rows(confirmatory_root, include_interaction=True)
    support2 = load_support2_rows(support2_root)
    rows = []
    for _, row in confirmatory.iterrows():
        if row["structure"] == "Mixed − high":
            interpretation = "Cross-structure interaction"
        elif row["locked_primary"]:
            interpretation = "Locked primary; confirmed"
        elif "Rescue" in row["contrast"]:
            interpretation = "Opposite allocation effect"
        else:
            interpretation = "Confirmatory secondary"
        rows.append(
            {
                "Evidence tier": row["evidence_tier"],
                "Structure": row["structure"],
                "Contrast": row["contrast"],
                "Alpha": 0.05,
                "Estimate": row["estimate"],
                "CI low": row["low"],
                "CI high": row["high"],
                "Interpretation": interpretation,
                "Source": row["source"],
            }
        )
    rows.extend(confirmatory_covariance_rows(confirmatory_root))

    support2_adj = json.loads(
        require(support2_root / "support2_validation_adjudication.json").read_text(encoding="utf-8")
    )
    for _, row in support2.iterrows():
        rows.append(
            {
                "Evidence tier": row["evidence_tier"],
                "Structure": row["structure"],
                "Contrast": row["contrast"],
                "Alpha": 0.05,
                "Estimate": row["estimate"],
                "CI low": row["low"],
                "CI high": row["high"],
                "Interpretation": "Supportive supplementary validation" if row["supportive"] else "Opposite allocation effect",
                "Source": row["source"],
            }
        )
    mech = support2_adj["mechanism"]
    rows.append(
        {
            "Evidence tier": "Supplementary validation",
            "Structure": SUPPORT2_LABEL,
            "Contrast": "Cov(A,D)",
            "Alpha": 0.05,
            "Estimate": float(mech["covariance"]),
            "CI low": float(mech["cov_ci_low_95"]),
            "CI high": float(mech["cov_ci_high_95"]),
            "Interpretation": "Allocation mechanism",
            "Source": "Locked SUPPORT2 paired bootstrap",
        }
    )
    table = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    return table


def make_support2_candidate_table(config_path: Path, output_path: Path) -> pd.DataFrame:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    rows = []
    for candidate in config["candidate_library"]:
        rows.append(
            {
                "Order": candidate["order"],
                "Candidate": candidate["name"],
                "Family": candidate["family"],
                "Base candidate": candidate["base"],
                "Parameters": json.dumps(candidate["params"], sort_keys=True),
            }
        )
    table = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    return table


def make_support2_audit_table(support2_root: Path, data_manifest_path: Path, support2_config: Path, output_path: Path) -> pd.DataFrame:
    adjudication = json.loads(
        require(support2_root / "support2_validation_adjudication.json").read_text(encoding="utf-8")
    )
    data_manifest = json.loads(require(data_manifest_path).read_text(encoding="utf-8"))
    config = json.loads(require(support2_config).read_text(encoding="utf-8"))
    row = {
        "Status": adjudication["status"],
        "Role": adjudication["role"],
        "Observed rows": data_manifest["rows"],
        "Outcome events": data_manifest["outcome_events"],
        "Outcome prevalence": data_manifest["outcome_prevalence"],
        "Reference replications": config["design"]["reference_repetitions"],
        "Evaluation replications": config["design"]["evaluation_repetitions"],
        "Failed fits": adjudication["failed_fit_count"],
        "Identity check passed": adjudication["identity_ok"],
        "Data SHA-256": data_manifest["canonical_sha256"],
    }
    table = pd.DataFrame([row])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_path, index=False)
    return table


def make_results_numbers(confirmatory_root: Path, support2_root: Path, table2: pd.DataFrame, output_path: Path) -> None:
    confirmatory = json.loads(
        require(confirmatory_root / "confirmatory_adjudication.json").read_text(encoding="utf-8")
    )
    support2 = json.loads(
        require(support2_root / "support2_validation_adjudication.json").read_text(encoding="utf-8")
    )
    primary = confirmatory["primary"]
    supp_primary = support2["primary"]
    supp_mech = support2["mechanism"]
    text = f"""# Frozen TESS manuscript numbers — integrated v1.4

## Evidence hierarchy

1. Locked primary confirmatory simulation.
2. Locked confirmatory secondary analyses.
3. SUPPORT2-anchored supplementary global-null validation.

The SUPPORT2 analysis supports generalizability to an observed clinical
covariate and missingness structure but does not modify the primary
confirmatory adjudication.

## Locked primary confirmatory result

- TESS promising minus budget-matched random: **{primary['estimate']:.6f}**
- Paired-bootstrap 95% CI: **{primary['ci_low_95']:.6f} to {primary['ci_high_95']:.6f}**
- Status: **CONFIRMED**

## SUPPORT2-anchored supplementary validation

- TESS promising minus budget-matched random: **{supp_primary['estimate']:.6f}**
- Paired-bootstrap 95% CI: **{supp_primary['ci_low_95']:.6f} to {supp_primary['ci_high_95']:.6f}**
- Status: **{support2['status']}**
- Promising activation rate: **{supp_mech['activation_rate']:.4f}**
- Incremental gain capture fraction: **{supp_mech['gain_capture_fraction']:.4f}**
- Incremental gain count: **{supp_mech['incremental_gain_count']}**
- Cov(A,D): **{supp_mech['covariance']:.6f}**
- Covariance 95% CI: **{supp_mech['cov_ci_low_95']:.6f} to {supp_mech['cov_ci_high_95']:.6f}**
- Rescue TESS effect: **{support2['rescue_tess_effect']:.6f}**
- Failed fits retained under the locked rule: **{support2['failed_fit_count']}**

## Recommended main-text sentence

> In a prespecified SUPPORT2-anchored global-null validation preserving the
> observed clinical covariate and missingness structure, promising-stage
> expansion increased TESS by {supp_primary['estimate']:.3f} relative to
> budget-matched random expansion (95% CI, {supp_primary['ci_low_95']:.3f}–{supp_primary['ci_high_95']:.3f}),
> while rescue expansion produced an effect in the opposite direction.

## Recommended abstract addition

> A supplementary validation preserving the covariate and missingness
> structure of the SUPPORT2 cohort yielded a similar promising-policy effect
> (TESS difference, {supp_primary['estimate']:.3f}; 95% CI, {supp_primary['ci_low_95']:.3f}–{supp_primary['ci_high_95']:.3f}).

## Table 2 rows

```text
{table2.to_string(index=False)}
```
"""
    output_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--confirmatory-results-root",
        type=Path,
        default=Path("simulations/ess/outputs/confirmatory_policy_v1"),
    )
    parser.add_argument(
        "--support2-results-root",
        type=Path,
        default=Path("simulations/ess/outputs/support2_validation_v1"),
    )
    parser.add_argument(
        "--confirmatory-config",
        type=Path,
        default=Path("configs/ess/confirmatory_policy_v1.json"),
    )
    parser.add_argument(
        "--support2-config",
        type=Path,
        default=Path("configs/ess/support2_validation_v1.json"),
    )
    parser.add_argument(
        "--support2-data-manifest",
        type=Path,
        default=Path("data/support2/support2_data_manifest_v1.json"),
    )
    parser.add_argument("--output-root", type=Path, default=Path("manuscript_tess"))
    args = parser.parse_args()

    repo = args.repo_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else repo / path

    confirmatory_root = resolve(args.confirmatory_results_root)
    support2_root = resolve(args.support2_results_root)
    confirmatory_config = resolve(args.confirmatory_config)
    support2_config = resolve(args.support2_config)
    support2_data_manifest = resolve(args.support2_data_manifest)
    output_root = resolve(args.output_root)

    figure_dir = output_root / "figures" / "v1_4_8"
    supplementary_figure_dir = output_root / "supplementary_figures" / "v1_4_8"
    table_dir = output_root / "tables" / "v1_4_8"
    supplementary_table_dir = output_root / "supplementary_tables" / "v1_4_8"
    for path in (figure_dir, supplementary_figure_dir, table_dir, supplementary_table_dir):
        path.mkdir(parents=True, exist_ok=True)

    make_figure1(figure_dir)

    make_fixed_search_comparison_figure(
        confirmatory_root,
        figure_dir / "Figure2A_fixed_search_TESS_curves",
    )

    # Preserve the full five-policy curves as supplementary evidence rather
    # than crowding the main two-panel fixed-search comparison.
    make_policy_curve_small_multiples(
        load_curve_data(confirmatory_root, "high_dependency_linear_20"),
        "High-dependency adaptive-policy TESS curves",
        supplementary_figure_dir / "FigureS3A_high_dependency_adaptive_policy_TESS_curves",
    )
    make_policy_curve_small_multiples(
        load_curve_data(confirmatory_root, "mixed_realistic_20"),
        "Mixed-realistic adaptive-policy TESS curves",
        supplementary_figure_dir / "FigureS3B_mixed_realistic_adaptive_policy_TESS_curves",
    )

    forest_rows = pd.concat(
        [load_confirmatory_rows(confirmatory_root, include_interaction=False), load_support2_rows(support2_root)],
        ignore_index=True,
    )
    make_forest_plot(forest_rows, figure_dir / "Figure3_policy_effects_with_SUPPORT2")
    make_gain_capture_plot(confirmatory_root, support2_root, figure_dir / "Figure4A_activation_and_gain_capture")
    make_covariance_plot(confirmatory_root, support2_root, figure_dir / "Figure4B_activation_increment_covariance")

    make_tess_curve(
        load_curve_data(support2_root, SUPPORT2_LIBRARY),
        "SUPPORT2-anchored supplementary validation",
        supplementary_figure_dir / "FigureS1_SUPPORT2_TESS_curves",
    )
    make_decile_plot(
        confirmatory_root,
        "high_dependency_linear_20",
        "High-dependency confirmatory structure",
        supplementary_figure_dir / "FigureS2A_high_dependency_score_deciles",
    )
    make_decile_plot(
        confirmatory_root,
        "mixed_realistic_20",
        "Mixed-realistic confirmatory structure",
        supplementary_figure_dir / "FigureS2B_mixed_realistic_score_deciles",
    )
    make_decile_plot(
        support2_root,
        SUPPORT2_LIBRARY,
        "SUPPORT2-anchored validation",
        supplementary_figure_dir / "FigureS2C_SUPPORT2_score_deciles",
    )

    make_table1(confirmatory_config, support2_config, table_dir / "Table1_integrated_study_design.csv")
    table2 = make_table2(confirmatory_root, support2_root, table_dir / "Table2_integrated_confirmatory_and_SUPPORT2_results.csv")
    make_support2_candidate_table(support2_config, supplementary_table_dir / "TableS1_SUPPORT2_candidate_library.csv")
    make_support2_audit_table(
        support2_root,
        support2_data_manifest,
        support2_config,
        supplementary_table_dir / "TableS2_SUPPORT2_technical_audit.csv",
    )

    legend_source = Path(__file__).resolve().parent / "MANUSCRIPT_FIGURE_LEGENDS_V1_4_3.md"
    if legend_source.exists():
        (output_root / "FIGURE_LEGENDS_V1_4_3.md").write_text(
            legend_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
    structure_source = Path(__file__).resolve().parent / "MANUSCRIPT_STRUCTURE_UPDATE_V1_4_3.md"
    if structure_source.exists():
        (output_root / "MANUSCRIPT_STRUCTURE_UPDATE_V1_4_3.md").write_text(
            structure_source.read_text(encoding="utf-8"), encoding="utf-8"
        )

    make_results_numbers(
        confirmatory_root,
        support2_root,
        table2,
        output_root / "RESULTS_NUMBERS_V1_4_3.md",
    )

    input_paths = [
        confirmatory_config,
        support2_config,
        support2_data_manifest,
        confirmatory_root / "confirmatory_adjudication.json",
        confirmatory_root / "confirmatory_policy_interaction.csv",
        confirmatory_root / "mechanism" / "phase3c_policy_mechanism_all_libraries.csv",
        confirmatory_root / "adaptive_policy" / "high_dependency_linear_20" / "adaptive_ml_policy_tess_bootstrap_curves.csv",
        confirmatory_root / "adaptive_policy" / "mixed_realistic_20" / "adaptive_ml_policy_tess_bootstrap_curves.csv",
        support2_root / "support2_validation_adjudication.json",
        support2_root / "support2_validation_summary.json",
        support2_root / "budget_standardized_audit" / "budget_standardized_policy_effects.csv",
        support2_root / "budget_standardized_audit" / "budget_standardized_policy_effects_bootstrap.csv",
        support2_root / "adaptive_policy" / SUPPORT2_LIBRARY / "adaptive_ml_policy_tess_bootstrap_curves.csv",
        support2_root / "mechanism" / SUPPORT2_LIBRARY / "activation_increment_covariance_bootstrap.csv",
        support2_root / "mechanism" / SUPPORT2_LIBRARY / "incremental_effect_by_base_score.csv",
    ]
    input_paths = [require(path) for path in input_paths]

    manifest = {
        "asset_version": "v1.4.8",
        "source_tags": [
            "tess-confirmatory-policy-v1-final-20260802",
            "tess-support2-validation-v1-final-20260802",
        ],
        "evidence_hierarchy": [
            "locked primary confirmatory simulation",
            "locked confirmatory secondary analyses",
            "SUPPORT2-anchored supplementary global-null validation",
        ],
        "source_inputs": [
            {
                "path": str(path.relative_to(repo)),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in input_paths
        ],
        "generated_main_figures": sorted(
            str(path.relative_to(repo)) for path in figure_dir.glob("*") if path.is_file()
        ),
        "generated_supplementary_figures": sorted(
            str(path.relative_to(repo)) for path in supplementary_figure_dir.glob("*") if path.is_file()
        ),
        "generated_main_tables": sorted(
            str(path.relative_to(repo)) for path in table_dir.glob("*") if path.is_file()
        ),
        "generated_supplementary_tables": sorted(
            str(path.relative_to(repo)) for path in supplementary_table_dir.glob("*") if path.is_file()
        ),
    }
    (output_root / "MANUSCRIPT_ASSET_MANIFEST_V1_4_3.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    confirmatory = json.loads((confirmatory_root / "confirmatory_adjudication.json").read_text(encoding="utf-8"))
    support2 = json.loads((support2_root / "support2_validation_adjudication.json").read_text(encoding="utf-8"))
    print("TESS integrated manuscript assets v1.4.8 generated")
    print(f"Output root: {output_root}")
    print(f"Main figure files: {len(manifest['generated_main_figures'])}")
    print(f"Supplementary figure files: {len(manifest['generated_supplementary_figures'])}")
    print(f"Main tables: {len(manifest['generated_main_tables'])}")
    print(f"Supplementary tables: {len(manifest['generated_supplementary_tables'])}")
    print("\nLocked primary confirmatory result:")
    print(
        f"  estimate={confirmatory['primary']['estimate']:.6f}, "
        f"95% CI {confirmatory['primary']['ci_low_95']:.6f} to {confirmatory['primary']['ci_high_95']:.6f}"
    )
    print("SUPPORT2 supplementary validation:")
    print(
        f"  estimate={support2['primary']['estimate']:.6f}, "
        f"95% CI {support2['primary']['ci_low_95']:.6f} to {support2['primary']['ci_high_95']:.6f}, "
        f"status={support2['status']}"
    )


if __name__ == "__main__":
    main()
