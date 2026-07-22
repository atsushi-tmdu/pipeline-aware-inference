from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import (
    extracted_master,
    setup_matplotlib,
    save_figure,
    panel_label,
    MODEL_LABELS,
)


def main():
    setup_matplotlib()

    with extracted_master() as root:
        candidate = pd.read_csv(root / "figure_data" / "figure5a_support2_candidate_models.csv")
        null_df = pd.read_csv(root / "figure_data" / "figure5b_support2_pipeline_null.csv")
        table3 = pd.read_csv(root / "table_data" / "table3_support2_performance.csv")

    candidate = candidate.sort_values("roc_auc", ascending=False).copy()
    null_auc = null_df[null_df["metric"] == "roc_auc"].copy()
    observed_auc = float(candidate["roc_auc"].max())

    # p-value
    p_df = table3[
        (table3["model_version"] == "selection_winner")
        & (table3["metric"] == "roc_auc")
    ]
    pipeline_p = float(p_df["pipeline_empirical"].iloc[0]) if not p_df.empty else 1.0 / 5001.0

    auc_rows = table3[table3["metric"] == "roc_auc"].copy()
    version_order = {
        "selection_winner": 0,
        "locked_training_only": 1,
        "final_refit_train_plus_selection": 2,
    }
    version_labels = {
        "selection_winner": "Model-selection\nset",
        "locked_training_only": "Untouched test\nlocked model",
        "final_refit_train_plus_selection": "Untouched test\nfinal refit",
    }
    auc_rows["order"] = auc_rows["model_version"].map(version_order)
    auc_rows = auc_rows.sort_values("order")

    fig, axes = plt.subplots(1, 3, figsize=(20.5, 8))

    # Panel A
    ax = axes[0]
    panel_label(ax, "A")
    x = np.arange(len(candidate))
    bars = ax.bar(
        x,
        candidate["roc_auc"],
        color="C0",
        edgecolor="black",
        linewidth=0.8,
    )

    for i, (bar, model, value) in enumerate(zip(bars, candidate["model"], candidate["roc_auc"])):
        if model == "random_forest":
            bar.set_hatch("//")
            bar.set_linewidth(2.0)
            ax.text(i, value + 0.004, "Selected", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("Model-selection AUROC")
    ax.set_ylim(0.50, 0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [MODEL_LABELS.get(m, m) for m in candidate["model"]],
        rotation=0,
        ha="center",
        fontsize=8.5,
    )
    ax.grid(axis="y", linewidth=0.45, alpha=0.35)

    # Panel B
    ax = axes[1]
    panel_label(ax, "B")
    ax.hist(
        null_auc["null_maximum"],
        bins=40,
        color="C0",
        edgecolor="black",
        linewidth=0.45,
    )
    ax.axvline(observed_auc, linestyle="--", linewidth=3, color="C0")
    ax.text(0.62, ax.get_ylim()[1] * 0.88, f"Pipeline-aware p = {pipeline_p:.5f}", fontsize=12)
    ax.text(0.61, ax.get_ylim()[1] * 0.07, f"Observed maximum\nAUROC = {observed_auc:.3f}", fontsize=12)
    ax.set_xlim(0.48, 0.85)
    ax.set_xlabel("Maximum AUROC under the pipeline null")
    ax.set_ylabel("Null replications")

    # Panel C
    ax = axes[2]
    panel_label(ax, "C")
    colors = ["C0", "C1", "C2"]

    for i, (_, row) in enumerate(auc_rows.iterrows()):
        est = float(row["estimate"])
        ax.plot(i, est, "o", color=colors[i], markersize=12)
        if pd.notna(row["ci95_low"]) and pd.notna(row["ci95_high"]):
            low = est - float(row["ci95_low"])
            high = float(row["ci95_high"]) - est
            ax.errorbar(i, est, yerr=np.array([[low], [high]]), fmt="none", color=colors[i], capsize=6, linewidth=2)
        #ax.text(i, est + 0.008, f"{est:.3f}", ha="center", va="bottom", fontsize=12)
        if pd.notna(row["ci95_high"]):
            label_y = float(row["ci95_high"]) + 0.006
        else:
            label_y = est + 0.006

        ax.text(
                i,
                label_y,
                f"{est:.3f}",
                ha="center",
                va="bottom",
                fontsize=12,
        )
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([version_labels[v] for v in auc_rows["model_version"]], fontsize=10)
    ax.set_ylabel("AUROC")
    ax.set_ylim(0.50, 0.87)
    ax.grid(axis="y", linewidth=0.45, alpha=0.35)
    """
    fig.text(
        0.5,
        0.05,
        "Panels: A, prespecified candidate library; "
        "B, pipeline-specific null distribution; "
        "C, generalization to the untouched test set.",
        ha="center",
        va="center",
        fontsize=12,
    )
    """

    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save_figure(fig, "Figure5_SUPPORT2_final")


if __name__ == "__main__":
    main()
