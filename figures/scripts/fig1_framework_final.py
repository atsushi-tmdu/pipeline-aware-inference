#%%
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from common import setup_matplotlib, save_figure


def add_box(ax, x, y, w, h, text, fontsize=11):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.8,
        facecolor="white",
        edgecolor="black",
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize)


def add_arrow(ax, start, end):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=24,
        linewidth=1.8,
        shrinkA=18,
        shrinkB=18,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arrow)


def main():
    setup_matplotlib()

    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Panel A label only
    ax.text(0.025, 0.92, "A", fontsize=14, fontweight="bold", ha="left", va="center")

    add_box(ax, 0.04, 0.66, 0.15, 0.14, "Observed\nclinical data", fontsize=18)
    add_box(
        ax,
        0.25,
        0.62,
        0.30,
        0.22,
        "Complete prespecified\nanalytical pipeline\n\n"
        "Preprocessing\n"
        "Feature selection\n"
        "Candidate algorithms\n"
        "Tuning and model search",
        fontsize=16,
    )
    add_box(ax, 0.61, 0.66, 0.16, 0.14, "Select model with\nmaximum performance", fontsize=17)
    add_box(ax, 0.83, 0.66, 0.13, 0.14, "Selected maximum\nperformance\n$T_{\\mathrm{obs}}$", fontsize=17)

    add_arrow(ax, (0.19, 0.73), (0.25, 0.73))
    add_arrow(ax, (0.55, 0.73), (0.61, 0.73))
    add_arrow(ax, (0.77, 0.73), (0.83, 0.73))

    # Panel B label only
    ax.text(0.025, 0.49, "B", fontsize=14, fontweight="bold", ha="left", va="center")

    add_box(ax, 0.04, 0.25, 0.15, 0.14, "Generate $B$ null datasets\nby outcome permutation", fontsize=14)
    add_box(
        ax,
        0.25,
        0.21,
        0.30,
        0.22,
        "Repeat the identical pipeline\nfor every null dataset\n\n"
        "No outcome-dependent step\nis omitted",
        fontsize=16,
    )
    add_box(ax, 0.61, 0.25, 0.16, 0.14, "Retain the selected\nnull maximum\n$T_{0b}$", fontsize=17)
    add_box(
        ax,
        0.83,
        0.22,
        0.13,
        0.20,
        "Pipeline-aware p-value\n\n"
        "$p=\\frac{1+\\sum_b\\,  I(T_{0b}\\geq T_{\\mathrm{obs}})}{B+1}$",
        fontsize=14,
    )

    add_arrow(ax, (0.19, 0.32), (0.25, 0.32))
    add_arrow(ax, (0.55, 0.32), (0.61, 0.32))
    add_arrow(ax, (0.77, 0.32), (0.83, 0.32))
    """
    ax.text(
        0.5,
        0.08,
        "Panel A, observed analytical pipeline.  "
        "Panel B, independent pipeline-specific null reference bank.",
        ha="center",
        va="center",
        fontsize=15,
    )

    ax.text(
        0.5,
        0.045,
        "The inferential target is the selected maximum, not a candidate model treated as prespecified.",
        ha="center",
        va="center",
        fontsize=15,
    )
    """
    save_figure(fig, "Figure1_framework_final")


if __name__ == "__main__":
    main()

# %%
