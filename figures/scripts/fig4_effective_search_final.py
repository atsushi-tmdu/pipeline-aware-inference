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
    LIBRARY_LABELS,
)


METHODS = ["naive_empirical", "pipeline_empirical", "bonferroni_empirical"]


def main():
    setup_matplotlib()

    with extracted_master() as root:
        data = pd.read_csv(root / "figure_data" / "figure4_effective_search.csv")

    order = ["similar_linear_7", "heterogeneous_core_7", "extended_sklearn_7"]
    data["order"] = data["library"].map({k: i for i, k in enumerate(order)})
    data = data.sort_values("order").copy()

    fig, axes = plt.subplots(1, 2, figsize=(23.48, 7.50))

    # Panel A
    ax = axes[0]
    panel_label(ax, "A")
    ax.set_title("Candidate dependence and effective search size", fontweight="bold", pad=14)

    ax.scatter(
        data["mean_pairwise_correlation"],
        data["effective_model_count"],
        s=220,
        color="C0",
    )

    for _, row in data.iterrows():
        if row["library"] == "similar_linear_7":
            ax.annotate(
                LIBRARY_LABELS[row["library"]],
                (row["mean_pairwise_correlation"], row["effective_model_count"]),
                xytext=(-80, 12),
                textcoords="offset points",
                fontsize=11,
            )
        else:
            ax.annotate(
                LIBRARY_LABELS[row["library"]],
                (row["mean_pairwise_correlation"], row["effective_model_count"]),
                xytext=(10, 12),
                textcoords="offset points",
                fontsize=11,
            )
    """
    ax.text(
        0.98,
        0.04,
        "All libraries: nominal K = 7",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=11,
    )
    """
    ax.set_xlabel("Mean pairwise correlation of null performance")
    ax.set_ylabel("Effective number of candidate models")
    ax.grid(linewidth=0.45, alpha=0.35)
    ax.set_ylim(top=3.8)


    # Panel B
    ax = axes[1]
    panel_label(ax, "B")
    ax.set_title("AUROC type I error across candidate libraries", fontweight="bold", pad=14)

    x = np.arange(len(data))
    style_map = {
        "naive_empirical": ("o", "-", "C0"),
        "pipeline_empirical": ("s", "-.", "C1"),
        "bonferroni_empirical": ("^", "--", "C2"),
    }

    for method in METHODS:
        marker, linestyle, color = style_map[method]
        ax.plot(
            x,
            data[method].to_numpy(float),
            marker=marker,
            linestyle=linestyle,
            color=color,
            linewidth=2.3,
            markersize=9,
        )

    ax.axhline(0.05, linestyle=":", color="C0", linewidth=2.0)
    ax.text(2.0, 0.054, r"Nominal $\alpha=0.05$", ha="right", va="bottom", fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(["Similar\nlinear", "Heterogeneous\ncore", "Expanded\nnonlinear"])

    ax.set_ylabel("Empirical type I error")
    ax.set_ylim(0, 0.26)
    ax.grid(axis="y", linewidth=0.45, alpha=0.35)

    handles = legend_handles(METHODS)
    ax.legend(handles=handles, frameon=False, loc="upper right", fontsize=11)
    """
    fig.text(
        0.5,
        0.06,
        "Panels: A, dependence and effective search size; "
        "B, calibration across model libraries.",
        ha="center",
        va="center",
        fontsize=12,
    )
    """
   
    save_figure(fig, "Figure4_effective_search_final")
    #fig.tight_layout(rect=(0, 0.08, 1, 1))
    #save_figure(fig, "Figure4_effective_search_final")


if __name__ == "__main__":
    main()

# %%
