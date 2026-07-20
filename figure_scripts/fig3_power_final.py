#%%
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (
    extracted_master,
    setup_matplotlib,
    save_figure,
    panel_label,
    legend_handles,
    errorbar_interval,
)


METHODS = ["pipeline_empirical", "bonferroni_empirical"]
COLORS = {
    "pipeline_empirical": "C0",
    "bonferroni_empirical": "C1",
}


def main():
    setup_matplotlib()

    with extracted_master() as root:
        raw = pd.read_csv(root / "figure_data" / "figure3_power.csv")

    data = raw[
        raw["method"].isin(METHODS)
        & raw["target_auc"].isin([0.60, 0.70])
    ].copy()

    panel_defs = [
        ("none", 20, "A"),
        ("none", 100, "B"),
        ("lasso", 20, "C"),
        ("lasso", 100, "D"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 11), sharex=True, sharey=True)

    for ax, (feature_selection, event_count, panel) in zip(axes.ravel(), panel_defs):
        subset = data[
            (data["feature_selection"] == feature_selection)
            & (data["selection_event_count"] == event_count)
        ].copy()

        for method in METHODS:
            group = subset[subset["method"] == method].sort_values("target_auc")
            x = group["target_auc"].to_numpy(float)
            y = group["rejection_rate"].to_numpy(float)
            low, high = errorbar_interval(group)

            style = {
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
                linewidth=2.0,
                markersize=8,
                capsize=4,
            )

        panel_label(ax, panel)
        ax.set_xlim(0.585, 0.715)
        ax.set_xticks([0.60, 0.70])
        ax.set_ylim(0, 1.03)
        ax.grid(axis="y", linewidth=0.45, alpha=0.35)

    for ax in axes[1, :]:
        ax.set_xlabel("Population AUROC of the true predictor")
    for ax in axes[:, 0]:
        ax.set_ylabel("Rejection rate (power)")
    """
    fig.text(
        0.5,
        0.095,
        "Panels: A, no feature selection with 20 events; "
        "B, no feature selection with 100 events; "
        "C, LASSO feature selection with 20 events; "
        "D, LASSO feature selection with 100 events.",
        ha="center",
        va="center",
        fontsize=11,
    )
    """

    """
    fig.text(
        0.5,
        0.060,
        "Naive inference is omitted because its type I error was not controlled.",
        ha="center",
        va="center",
        fontsize=11,
    )
    """
    handles = legend_handles(METHODS)
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.07),
        fontsize=12,
    )

    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save_figure(fig, "Figure3_power_final")


if __name__ == "__main__":
    main()

# %%
