from __future__ import annotations

from contextlib import contextmanager
import tempfile
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]

MASTER_ZIP = (
    REPO_ROOT
    / "figures"
    / "frozen_results"
    / "phase5a_master_results.zip"
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


METHOD_LABELS = {
    "naive_empirical": "Naive",
    "pipeline_empirical": "Pipeline-aware",
    "bonferroni_empirical": "Bonferroni",
}

METHOD_STYLES = {
    "naive_empirical": {
        "marker": "o",
        "linestyle": "-",
    },
    "pipeline_empirical": {
        "marker": "s",
        "linestyle": "-.",
    },
    "bonferroni_empirical": {
        "marker": "^",
        "linestyle": "--",
    },
}

METRIC_PANEL_TEXT = {
    "roc_auc": "A, AUROC",
    "average_precision": "B, Average precision",
    "pauc_fpr_0_10": "C, Partial AUROC (FPR ≤ 0.10)",
}

MODEL_LABELS = {
    "random_forest": "Random\nforest",
    "hist_gradient_boosting": "Histogram\ngradient boosting",
    "linear_svm": "Linear\nSVM",
    "logistic_regression": "Logistic\nregression",
    "rbf_svm": "RBF\nSVM",
    "decision_tree": "Decision\ntree",
    "gaussian_nb": "Gaussian\nNB",
}

LIBRARY_LABELS = {
    "similar_linear_7": "Similar linear",
    "heterogeneous_core_7": "Heterogeneous core",
    "extended_sklearn_7": "Expanded nonlinear",
}


def setup_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 10,
            "axes.titlesize": 10,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    png = OUTPUT_DIR / f"{stem}.png"
    pdf = OUTPUT_DIR / f"{stem}.pdf"
    svg = OUTPUT_DIR / f"{stem}.svg"

    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.04,
        1.03,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=14,
        fontweight="bold",
    )


@contextmanager
def extracted_master():
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        with zipfile.ZipFile(MASTER_ZIP, "r") as zf:
            zf.extractall(tmpdir)

        candidates = list(tmpdir.rglob("figure_data/figure2_type1_error.csv"))
        if len(candidates) != 1:
            raise RuntimeError("Could not identify extracted master-result directory.")
        root = candidates[0].parent.parent
        yield root


def weighted_rate_summary(
    data: pd.DataFrame,
    grouping: list[str],
) -> pd.DataFrame:
    rows = []

    for keys, group in data.groupby(grouping, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)

        weights = pd.to_numeric(group["n"], errors="coerce").fillna(0).to_numpy(float)
        values = pd.to_numeric(group["rejection_rate"], errors="coerce").to_numpy(float)

        valid = np.isfinite(weights) & np.isfinite(values) & (weights > 0)
        if not np.any(valid):
            continue

        total_n = int(weights[valid].sum())
        rate = float(np.average(values[valid], weights=weights[valid]))
        se = np.sqrt(rate * (1.0 - rate) / total_n)

        row = dict(zip(grouping, keys))
        row["n"] = total_n
        row["rejection_rate"] = rate
        row["mc95_low"] = max(0.0, rate - 1.96 * se)
        row["mc95_high"] = min(1.0, rate + 1.96 * se)
        rows.append(row)

    return pd.DataFrame(rows)


def legend_handles(methods: list[str]) -> list[Line2D]:
    handles = []
    for method in methods:
        style = METHOD_STYLES[method]
        handles.append(
            Line2D(
                [0],
                [0],
                color="C0" if method == "naive_empirical" else ("C1" if method == "pipeline_empirical" else "C2"),
                marker=style["marker"],
                linestyle=style["linestyle"],
                linewidth=2,
                markersize=7,
                label=METHOD_LABELS[method],
            )
        )
    return handles


def errorbar_interval(group: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    y = pd.to_numeric(group["rejection_rate"], errors="coerce").to_numpy(float)

    if {"rejection_rate_mc95_low", "rejection_rate_mc95_high"}.issubset(group.columns):
        low = pd.to_numeric(group["rejection_rate_mc95_low"], errors="coerce").to_numpy(float)
        high = pd.to_numeric(group["rejection_rate_mc95_high"], errors="coerce").to_numpy(float)
    else:
        n = pd.to_numeric(group["n"], errors="coerce").to_numpy(float)
        se = np.sqrt(np.maximum(y * (1.0 - y), 0.0) / n)
        low = np.maximum(0.0, y - 1.96 * se)
        high = np.minimum(1.0, y + 1.96 * se)

    return y - low, high - y
