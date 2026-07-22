#%%
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (
    extracted_master,
    setup_matplotlib,
    save_figure,
    weighted_rate_summary,
    legend_handles,
    panel_label,
)


METHODS = ["naive_empirical", "pipeline_empirical", "bonferroni_empirical"]
COLORS = {
    "naive_empirical": "C0",
    "pipeline_empirical": "C1",
    "bonferroni_empirical": "C2",
}


def main():
    setup_matplotlib()

    with extracted_master() as root:
        raw = pd.read_csv(root / "figure_data" / "figure2_type1_error.csv")

    data = raw[raw["method"].isin(METHODS)].copy()

    summary = weighted_rate_summary(
        data,
        ["metric", "pool_size", "method"],
    )

    metrics = ["roc_auc", "average_precision", "pauc_fpr_0_10"]
    panel_letters = ["A", "B", "C"]

    fig, axes = plt.subplots(1, 3, figsize=(20.5, 7.2), sharey=True)

    for i, (metric, ax) in enumerate(zip(metrics, axes)):
        subset = summary[summary["metric"] == metric].copy()

        for method in METHODS:
            group = subset[subset["method"] == method].sort_values("pool_size")
            x = group["pool_size"].to_numpy(float)
            y = group["rejection_rate"].to_numpy(float)
            low = y - group["mc95_low"].to_numpy(float)
            high = group["mc95_high"].to_numpy(float) - y

            style = {
                "naive_empirical": ("o", "-", "C0"),
                "pipeline_empirical": ("s", "-.", "C1"),
                "bonferroni_empirical": ("^", "--", "C2"),
            }[method]

            ax.errorbar(
                x,
                y,
                yerr=np.vstack([low, high]),
                fmt=style[0],
                linestyle=style[1],
                color=style[2],
                linewidth=2.2,
                markersize=9,
                capsize=4,
            )

        ax.axhline(0.05, linestyle=":", color="C0", linewidth=2.0)
        ax.text(6.8, 0.054, r"Nominal $\alpha=0.05$", ha="right", va="bottom", fontsize=10)

        panel_label(ax, panel_letters[i])

        ax.set_xticks([1, 3, 7])
        ax.set_xlabel("Number of candidate algorithms")
        ax.set_ylim(0, 0.26)
        ax.grid(axis="y", linewidth=0.45, alpha=0.35)

    axes[0].set_ylabel("Empirical type I error")
    """
    fig.text(
        0.5,
        0.10,
        "Panels: A, AUROC; B, Average precision; C, Partial AUROC (FPR ≤ 0.10).",
        ha="center",
        va="center",
        fontsize=12,
    )
    """
    handles = legend_handles(METHODS)
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.05),
        fontsize=12,
    )

    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save_figure(fig, "Figure2_type1_error_final")


if __name__ == "__main__":
    main()

# %%
