#!/usr/bin/env python3
"""Conditional paired bootstrap for Phase 3C TESS curves.

This analysis resamples the stored *evaluation-bank* replications. It preserves
all within-replication dependencies:

* K=7 and K=20 are resampled together within each candidate library;
* every alpha threshold is evaluated on the same resampled p-values;
* the two libraries are also resampled together when their replication/seed
  keys align exactly (the default ``--cross-library-pairing auto`` behavior).

The resulting intervals are conditional on the frozen empirical null-reference
bank used to construct ``naive_empirical`` p-values. Uncertainty from rebuilding
that reference bank is not included here; that requires a later nested two-bank
bootstrap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

DEFAULT_ALPHAS = (0.20, 0.10, 0.05, 0.025, 0.01, 0.005)
DEFAULT_BOOTSTRAP_REPETITIONS = 20_000
POOL_SIZES = (7, 20)
PRIMARY_METHOD = "naive_empirical"
SENSITIVITY_METHOD = "naive_mannwhitney"
LIBRARIES = ("high_dependency_linear_20", "mixed_realistic_20")


@dataclass(frozen=True)
class LibraryBank:
    """One p-value matrix with paired K=7/K=20 rows."""

    name: str
    input_path: Path
    keys: pd.MultiIndex
    p_values: np.ndarray  # shape: (replications, 2), columns K=7 and K=20

    @property
    def repetitions(self) -> int:
        return int(self.p_values.shape[0])


def parse_alpha_grid(value: str) -> tuple[float, ...]:
    alphas = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    if not alphas:
        raise argparse.ArgumentTypeError("alpha grid must not be empty")
    if len(set(alphas)) != len(alphas):
        raise argparse.ArgumentTypeError("alpha grid must not contain duplicates")
    if any(not 0.0 < alpha < 1.0 for alpha in alphas):
        raise argparse.ArgumentTypeError("every alpha must lie strictly between 0 and 1")
    return alphas


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_p_values(values: np.ndarray, label: str) -> None:
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError(f"{label}: expected an n x 2 p-value matrix; found {values.shape}")
    if values.shape[0] < 20:
        raise ValueError(f"{label}: at least 20 replications are required")
    if not np.isfinite(values).all():
        raise ValueError(f"{label}: p-values contain non-finite values")
    if ((values < 0.0) | (values > 1.0)).any():
        raise ValueError(f"{label}: p-values must lie in [0, 1]")


def load_library_bank(
    path: Path,
    library: str,
    method: str,
    selection_event_count: int,
) -> LibraryBank:
    """Read and pivot one Phase 3C null p-value bank."""
    required = {
        "replication",
        "seed",
        "target_auc",
        "feature_selection",
        "selection_event_count",
        "pool_size",
        "metric",
        "method",
        "p_value",
    }
    df = pd.read_csv(path)
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    subset = df[
        np.isclose(pd.to_numeric(df["target_auc"], errors="raise"), 0.50)
        & (df["feature_selection"] == "none")
        & (pd.to_numeric(df["selection_event_count"], errors="raise") == selection_event_count)
        & (df["metric"] == "roc_auc")
        & (df["method"] == method)
        & pd.to_numeric(df["pool_size"], errors="raise").isin(POOL_SIZES)
    ].copy()
    if subset.empty:
        raise ValueError(
            f"No rows found in {path} for method={method!r}, E={selection_event_count}"
        )

    subset["pool_size"] = pd.to_numeric(subset["pool_size"], errors="raise").astype(int)
    subset["p_value"] = pd.to_numeric(subset["p_value"], errors="raise")
    duplicate_mask = subset.duplicated(["replication", "seed", "pool_size"], keep=False)
    if duplicate_mask.any():
        examples = subset.loc[
            duplicate_mask, ["replication", "seed", "pool_size"]
        ].head().to_dict("records")
        raise ValueError(f"Duplicate p-values in {path}; examples: {examples}")

    pivot = subset.pivot(
        index=["replication", "seed"], columns="pool_size", values="p_value"
    ).sort_index()
    missing_pool_sizes = [pool for pool in POOL_SIZES if pool not in pivot.columns]
    if missing_pool_sizes:
        raise ValueError(f"{path} is missing pool sizes {missing_pool_sizes}")
    pivot = pivot.loc[:, list(POOL_SIZES)]
    if pivot.isna().any().any():
        missing_rows = pivot[pivot.isna().any(axis=1)].head().index.tolist()
        raise ValueError(f"Unpaired K=7/K=20 rows in {path}; examples: {missing_rows}")

    values = pivot.to_numpy(dtype=float)
    validate_p_values(values, str(path))
    return LibraryBank(
        name=library,
        input_path=path,
        keys=pivot.index,
        p_values=values,
    )


def align_cross_library_banks(
    high: LibraryBank,
    mixed: LibraryBank,
    mode: str,
) -> tuple[LibraryBank, LibraryBank, str]:
    """Align library rows and resolve paired versus independent resampling."""
    if mode not in {"auto", "paired", "independent"}:
        raise ValueError(f"Unknown cross-library pairing mode: {mode}")

    same_keys = high.keys.equals(mixed.keys)
    if not same_keys and set(high.keys) == set(mixed.keys):
        lookup = pd.Series(np.arange(mixed.repetitions), index=mixed.keys)
        order = lookup.loc[high.keys].to_numpy(dtype=int)
        mixed = LibraryBank(
            name=mixed.name,
            input_path=mixed.input_path,
            keys=high.keys,
            p_values=mixed.p_values[order],
        )
        same_keys = True

    if mode == "paired" and not same_keys:
        raise ValueError(
            "Cross-library paired bootstrap was requested, but replication/seed keys differ."
        )
    resolved = "paired" if (mode == "paired" or (mode == "auto" and same_keys)) else "independent"
    return high, mixed, resolved


def rejection_probabilities(p_values: np.ndarray, alphas: np.ndarray) -> np.ndarray:
    """Return rejection probabilities, shape (..., K, alpha)."""
    return np.mean(p_values[..., :, None] < alphas, axis=-3)


def tess_from_probabilities(
    probabilities: np.ndarray,
    alphas: np.ndarray,
    repetitions: int,
) -> tuple[np.ndarray, int]:
    """Transform rejection probabilities to TESS with boundary protection.

    The clipping is inactive unless a bootstrap sample contains zero or all
    rejections. It prevents infinite values while recording how often a
    boundary correction was needed.
    """
    boundary = (probabilities <= 0.0) | (probabilities >= 1.0)
    corrected = int(np.count_nonzero(boundary))
    lower = 0.5 / repetitions
    upper = 1.0 - lower
    safe = np.clip(probabilities, lower, upper)
    return np.log1p(-safe) / np.log1p(-alphas), corrected


def original_tess(bank: LibraryBank, alphas: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    probabilities = np.mean(bank.p_values[:, :, None] < alphas, axis=0)
    rejections = np.sum(bank.p_values[:, :, None] < alphas, axis=0)
    tess, _ = tess_from_probabilities(probabilities, alphas, bank.repetitions)
    return probabilities, rejections, tess


def bootstrap_tess(
    high: LibraryBank,
    mixed: LibraryBank,
    alphas: np.ndarray,
    bootstrap_repetitions: int,
    bootstrap_seed: int,
    batch_size: int,
    pairing: str,
) -> tuple[np.ndarray, int]:
    """Return bootstrap TESS array with shape (B, library, K, alpha)."""
    if bootstrap_repetitions < 100:
        raise ValueError("At least 100 bootstrap repetitions are required")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if pairing == "paired" and high.repetitions != mixed.repetitions:
        raise ValueError("Paired cross-library bootstrap requires equal bank sizes")

    rng = np.random.default_rng(bootstrap_seed)
    output = np.empty(
        (bootstrap_repetitions, len(LIBRARIES), len(POOL_SIZES), len(alphas)),
        dtype=float,
    )
    boundary_corrections = 0

    for start in range(0, bootstrap_repetitions, batch_size):
        stop = min(start + batch_size, bootstrap_repetitions)
        batch = stop - start

        if pairing == "paired":
            indices = rng.integers(0, high.repetitions, size=(batch, high.repetitions))
            selected_high = high.p_values[indices]
            selected_mixed = mixed.p_values[indices]
        else:
            high_indices = rng.integers(
                0, high.repetitions, size=(batch, high.repetitions)
            )
            mixed_indices = rng.integers(
                0, mixed.repetitions, size=(batch, mixed.repetitions)
            )
            selected_high = high.p_values[high_indices]
            selected_mixed = mixed.p_values[mixed_indices]

        for library_index, (selected, repetitions) in enumerate(
            ((selected_high, high.repetitions), (selected_mixed, mixed.repetitions))
        ):
            probabilities = np.mean(selected[..., None] < alphas, axis=1)
            transformed, corrected = tess_from_probabilities(
                probabilities, alphas, repetitions
            )
            output[start:stop, library_index, :, :] = transformed
            boundary_corrections += corrected

    return output, boundary_corrections


def percentile_interval(values: np.ndarray, confidence: float = 0.95) -> tuple[np.ndarray, np.ndarray]:
    tail = (1.0 - confidence) / 2.0
    return (
        np.quantile(values, tail, axis=0),
        np.quantile(values, 1.0 - tail, axis=0),
    )


def simultaneous_bands(
    point: np.ndarray,
    bootstrap: np.ndarray,
    confidence: float = 0.95,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Max-|z| simultaneous band across alpha for one curve."""
    if bootstrap.ndim != 2:
        raise ValueError("bootstrap must have shape (B, alpha)")
    standard_error = np.std(bootstrap, axis=0, ddof=1)
    safe_se = np.where(standard_error > 0.0, standard_error, 1.0)
    standardized = np.abs((bootstrap - point) / safe_se)
    standardized[:, standard_error == 0.0] = 0.0
    critical = float(np.quantile(np.max(standardized, axis=1), confidence))
    low = np.maximum(0.0, point - critical * standard_error)
    high = point + critical * standard_error
    return low, high, critical


def scalar_summary(
    name: str,
    estimate: float,
    bootstrap: np.ndarray,
    method: str,
    details: str,
) -> dict[str, object]:
    low, high = percentile_interval(bootstrap)
    return {
        "method": method,
        "contrast": name,
        "details": details,
        "estimate": float(estimate),
        "bootstrap_mean": float(np.mean(bootstrap)),
        "bootstrap_bias": float(np.mean(bootstrap) - estimate),
        "bootstrap_se": float(np.std(bootstrap, ddof=1)),
        "ci_low_95": float(low),
        "ci_high_95": float(high),
        "bootstrap_probability_gt_zero": float(np.mean(bootstrap > 0.0)),
        "bootstrap_probability_lt_zero": float(np.mean(bootstrap < 0.0)),
        "bootstrap_repetitions": int(bootstrap.shape[0]),
        "interval_type": "paired percentile bootstrap",
    }


def alpha_position(alphas: np.ndarray, target: float) -> int | None:
    matches = np.flatnonzero(np.isclose(alphas, target, rtol=0.0, atol=1e-12))
    return int(matches[0]) if len(matches) else None


def summarize_curves(
    method: str,
    alphas: np.ndarray,
    original_probabilities: np.ndarray,
    original_rejections: np.ndarray,
    original: np.ndarray,
    bootstrap: np.ndarray,
    bank_sizes: tuple[int, int],
    pairing: str,
) -> pd.DataFrame:
    point_low, point_high = percentile_interval(bootstrap)
    rows: list[dict[str, object]] = []
    for library_index, library in enumerate(LIBRARIES):
        for pool_index, pool_size in enumerate(POOL_SIZES):
            curve = bootstrap[:, library_index, pool_index, :]
            sim_low, sim_high, critical = simultaneous_bands(
                original[library_index, pool_index, :], curve
            )
            for alpha_index, alpha in enumerate(alphas):
                values = curve[:, alpha_index]
                rows.append(
                    {
                        "method": method,
                        "library": library,
                        "nominal_candidate_count": int(pool_size),
                        "local_alpha": float(alpha),
                        "evaluation_repetitions": int(bank_sizes[library_index]),
                        "naive_rejections": int(
                            original_rejections[library_index, pool_index, alpha_index]
                        ),
                        "naive_rejection_probability": float(
                            original_probabilities[library_index, pool_index, alpha_index]
                        ),
                        "tail_ess": float(original[library_index, pool_index, alpha_index]),
                        "bootstrap_mean": float(np.mean(values)),
                        "bootstrap_bias": float(
                            np.mean(values) - original[library_index, pool_index, alpha_index]
                        ),
                        "bootstrap_se": float(np.std(values, ddof=1)),
                        "pointwise_low_95": float(
                            point_low[library_index, pool_index, alpha_index]
                        ),
                        "pointwise_high_95": float(
                            point_high[library_index, pool_index, alpha_index]
                        ),
                        "simultaneous_low_95": float(sim_low[alpha_index]),
                        "simultaneous_high_95": float(sim_high[alpha_index]),
                        "simultaneous_max_z_critical": critical,
                        "bootstrap_repetitions": int(bootstrap.shape[0]),
                        "cross_library_pairing": pairing,
                        "interval_scope": "simultaneous across alpha within library/K curve",
                        "bootstrap_conditioning": "conditional on frozen null-reference bank",
                    }
                )
    return pd.DataFrame(rows)


def summarize_difference_curve(
    method: str,
    name: str,
    details: str,
    alphas: np.ndarray,
    point: np.ndarray,
    bootstrap: np.ndarray,
    pairing: str,
) -> pd.DataFrame:
    point_low, point_high = percentile_interval(bootstrap)
    sim_low, sim_high, critical = simultaneous_bands(point, bootstrap)
    rows: list[dict[str, object]] = []
    for index, alpha in enumerate(alphas):
        values = bootstrap[:, index]
        rows.append(
            {
                "method": method,
                "curve": name,
                "details": details,
                "local_alpha": float(alpha),
                "estimate": float(point[index]),
                "bootstrap_mean": float(np.mean(values)),
                "bootstrap_bias": float(np.mean(values) - point[index]),
                "bootstrap_se": float(np.std(values, ddof=1)),
                "pointwise_low_95": float(point_low[index]),
                "pointwise_high_95": float(point_high[index]),
                "simultaneous_low_95": float(sim_low[index]),
                "simultaneous_high_95": float(sim_high[index]),
                "simultaneous_max_z_critical": critical,
                "bootstrap_probability_gt_zero": float(np.mean(values > 0.0)),
                "bootstrap_probability_lt_zero": float(np.mean(values < 0.0)),
                "bootstrap_repetitions": int(bootstrap.shape[0]),
                "cross_library_pairing": pairing,
                "bootstrap_conditioning": "conditional on frozen null-reference bank",
            }
        )
    return pd.DataFrame(rows)


def build_primary_contrasts(
    method: str,
    alphas: np.ndarray,
    original: np.ndarray,
    bootstrap: np.ndarray,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    alpha_010 = alpha_position(alphas, 0.10)
    alpha_005 = alpha_position(alphas, 0.05)
    alpha_001 = alpha_position(alphas, 0.01)

    if alpha_010 is not None and alpha_001 is not None:
        for library_index, library in enumerate(LIBRARIES):
            for pool_index, pool_size in enumerate(POOL_SIZES):
                estimate = (
                    original[library_index, pool_index, alpha_001]
                    - original[library_index, pool_index, alpha_010]
                )
                values = (
                    bootstrap[:, library_index, pool_index, alpha_001]
                    - bootstrap[:, library_index, pool_index, alpha_010]
                )
                rows.append(
                    scalar_summary(
                        name=f"tail_change_{library}_K{pool_size}_alpha0.01_minus_0.10",
                        estimate=float(estimate),
                        bootstrap=values,
                        method=method,
                        details="TESS(0.01) - TESS(0.10) within one library and K",
                    )
                )

            k_effect_001 = (
                original[library_index, 1, alpha_001]
                - original[library_index, 0, alpha_001]
            )
            k_effect_010 = (
                original[library_index, 1, alpha_010]
                - original[library_index, 0, alpha_010]
            )
            values = (
                (bootstrap[:, library_index, 1, alpha_001] - bootstrap[:, library_index, 0, alpha_001])
                - (bootstrap[:, library_index, 1, alpha_010] - bootstrap[:, library_index, 0, alpha_010])
            )
            rows.append(
                scalar_summary(
                    name=f"tail_amplification_of_K_effect_{library}_alpha0.01_vs_0.10",
                    estimate=float(k_effect_001 - k_effect_010),
                    bootstrap=values,
                    method=method,
                    details="[TESS_K20-TESS_K7 at 0.01] - [same difference at 0.10]",
                )
            )

    for alpha_index, alpha_label in [
        (alpha_005, "0.05"),
        (alpha_001, "0.01"),
    ]:
        if alpha_index is None:
            continue
        for library_index, library in enumerate(LIBRARIES):
            estimate = (
                original[library_index, 1, alpha_index]
                - original[library_index, 0, alpha_index]
            )
            values = (
                bootstrap[:, library_index, 1, alpha_index]
                - bootstrap[:, library_index, 0, alpha_index]
            )
            rows.append(
                scalar_summary(
                    name=f"K20_minus_K7_{library}_alpha{alpha_label}",
                    estimate=float(estimate),
                    bootstrap=values,
                    method=method,
                    details=f"TESS_K20 - TESS_K7 at alpha={alpha_label}",
                )
            )

        for pool_index, pool_size in enumerate(POOL_SIZES):
            estimate = (
                original[1, pool_index, alpha_index]
                - original[0, pool_index, alpha_index]
            )
            values = (
                bootstrap[:, 1, pool_index, alpha_index]
                - bootstrap[:, 0, pool_index, alpha_index]
            )
            rows.append(
                scalar_summary(
                    name=f"mixed_minus_high_K{pool_size}_alpha{alpha_label}",
                    estimate=float(estimate),
                    bootstrap=values,
                    method=method,
                    details=f"Mixed-realistic minus high-dependency TESS at K={pool_size}",
                )
            )

        estimate = (
            (original[1, 1, alpha_index] - original[1, 0, alpha_index])
            - (original[0, 1, alpha_index] - original[0, 0, alpha_index])
        )
        values = (
            (bootstrap[:, 1, 1, alpha_index] - bootstrap[:, 1, 0, alpha_index])
            - (bootstrap[:, 0, 1, alpha_index] - bootstrap[:, 0, 0, alpha_index])
        )
        rows.append(
            scalar_summary(
                name=f"difference_in_differences_alpha{alpha_label}",
                estimate=float(estimate),
                bootstrap=values,
                method=method,
                details="(Mixed K20-K7) - (High-dependency K20-K7)",
            )
        )

    if alpha_010 is not None and alpha_001 is not None:
        did_001 = (
            (original[1, 1, alpha_001] - original[1, 0, alpha_001])
            - (original[0, 1, alpha_001] - original[0, 0, alpha_001])
        )
        did_010 = (
            (original[1, 1, alpha_010] - original[1, 0, alpha_010])
            - (original[0, 1, alpha_010] - original[0, 0, alpha_010])
        )
        values = (
            (
                (bootstrap[:, 1, 1, alpha_001] - bootstrap[:, 1, 0, alpha_001])
                - (bootstrap[:, 0, 1, alpha_001] - bootstrap[:, 0, 0, alpha_001])
            )
            - (
                (bootstrap[:, 1, 1, alpha_010] - bootstrap[:, 1, 0, alpha_010])
                - (bootstrap[:, 0, 1, alpha_010] - bootstrap[:, 0, 0, alpha_010])
            )
        )
        rows.append(
            scalar_summary(
                name="tail_amplification_of_difference_in_differences_alpha0.01_vs_0.10",
                estimate=float(did_001 - did_010),
                bootstrap=values,
                method=method,
                details="Change in library-by-K interaction from alpha=0.10 to alpha=0.01",
            )
        )

    return pd.DataFrame(rows)


def plot_curves_with_simultaneous_bands(summary: pd.DataFrame, output_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipped figures")
        return

    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    for (library, pool_size), group in summary.groupby(
        ["library", "nominal_candidate_count"], sort=True
    ):
        group = group.sort_values("local_alpha")
        line = ax.plot(
            group["local_alpha"],
            group["tail_ess"],
            marker="o",
            label=f"{library}, K={int(pool_size)}",
        )[0]
        ax.fill_between(
            group["local_alpha"],
            group["simultaneous_low_95"],
            group["simultaneous_high_95"],
            alpha=0.14,
            color=line.get_color(),
        )
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("Local significance level (alpha)")
    ax.set_ylabel("Tail-equivalent search size (TESS)")
    ax.set_title("Phase 3C TESS curves with conditional paired-bootstrap bands")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "phase3c_tess_bootstrap_curves.png", dpi=300)
    fig.savefig(output_dir / "phase3c_tess_bootstrap_curves.svg")
    plt.close(fig)


def plot_difference_curves(differences: pd.DataFrame, output_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    k_curves = differences[differences["curve"].str.startswith("K20_minus_K7")]
    if not k_curves.empty:
        fig, ax = plt.subplots(figsize=(9.0, 5.5))
        for curve_name, group in k_curves.groupby("curve", sort=True):
            group = group.sort_values("local_alpha")
            line = ax.plot(
                group["local_alpha"], group["estimate"], marker="o", label=curve_name
            )[0]
            ax.fill_between(
                group["local_alpha"],
                group["simultaneous_low_95"],
                group["simultaneous_high_95"],
                alpha=0.14,
                color=line.get_color(),
            )
        ax.axhline(0.0, linewidth=1.0)
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_xlabel("Local significance level (alpha)")
        ax.set_ylabel("TESS(K=20) - TESS(K=7)")
        ax.set_title("Candidate-count effect across the tail")
        ax.grid(True, which="both", linewidth=0.5, alpha=0.25)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(output_dir / "phase3c_tess_K20_minus_K7.png", dpi=300)
        fig.savefig(output_dir / "phase3c_tess_K20_minus_K7.svg")
        plt.close(fig)

    did = differences[differences["curve"] == "difference_in_differences"]
    if not did.empty:
        did = did.sort_values("local_alpha")
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.plot(did["local_alpha"], did["estimate"], marker="o")
        ax.fill_between(
            did["local_alpha"],
            did["simultaneous_low_95"],
            did["simultaneous_high_95"],
            alpha=0.14,
        )
        ax.axhline(0.0, linewidth=1.0)
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_xlabel("Local significance level (alpha)")
        ax.set_ylabel("Difference in K effect between libraries")
        ax.set_title("Library-by-candidate-count interaction in TESS")
        ax.grid(True, which="both", linewidth=0.5, alpha=0.25)
        fig.tight_layout()
        fig.savefig(output_dir / "phase3c_tess_difference_in_differences.png", dpi=300)
        fig.savefig(output_dir / "phase3c_tess_difference_in_differences.svg")
        plt.close(fig)


def run_method(
    method: str,
    high_path: Path,
    mixed_path: Path,
    alphas: np.ndarray,
    selection_event_count: int,
    bootstrap_repetitions: int,
    bootstrap_seed: int,
    batch_size: int,
    pairing_mode: str,
    output_dir: Path,
    save_replicates: bool,
) -> dict[str, object]:
    high = load_library_bank(
        high_path, LIBRARIES[0], method=method, selection_event_count=selection_event_count
    )
    mixed = load_library_bank(
        mixed_path, LIBRARIES[1], method=method, selection_event_count=selection_event_count
    )
    high, mixed, resolved_pairing = align_cross_library_banks(
        high, mixed, mode=pairing_mode
    )

    original_probabilities = np.empty((2, 2, len(alphas)), dtype=float)
    original_rejections = np.empty((2, 2, len(alphas)), dtype=int)
    original = np.empty((2, 2, len(alphas)), dtype=float)
    for library_index, bank in enumerate((high, mixed)):
        prob, reject, tess = original_tess(bank, alphas)
        original_probabilities[library_index] = prob
        original_rejections[library_index] = reject
        original[library_index] = tess

    bootstrap, boundary_corrections = bootstrap_tess(
        high=high,
        mixed=mixed,
        alphas=alphas,
        bootstrap_repetitions=bootstrap_repetitions,
        bootstrap_seed=bootstrap_seed,
        batch_size=batch_size,
        pairing=resolved_pairing,
    )

    method_dir = output_dir / method
    method_dir.mkdir(parents=True, exist_ok=True)

    curve_summary = summarize_curves(
        method=method,
        alphas=alphas,
        original_probabilities=original_probabilities,
        original_rejections=original_rejections,
        original=original,
        bootstrap=bootstrap,
        bank_sizes=(high.repetitions, mixed.repetitions),
        pairing=resolved_pairing,
    )
    curve_summary.to_csv(method_dir / "phase3c_tess_bootstrap_curve_summary.csv", index=False)

    difference_frames: list[pd.DataFrame] = []
    for library_index, library in enumerate(LIBRARIES):
        point = original[library_index, 1, :] - original[library_index, 0, :]
        values = bootstrap[:, library_index, 1, :] - bootstrap[:, library_index, 0, :]
        difference_frames.append(
            summarize_difference_curve(
                method=method,
                name=f"K20_minus_K7_{library}",
                details=f"TESS(K=20)-TESS(K=7) within {library}",
                alphas=alphas,
                point=point,
                bootstrap=values,
                pairing=resolved_pairing,
            )
        )

    for pool_index, pool_size in enumerate(POOL_SIZES):
        point = original[1, pool_index, :] - original[0, pool_index, :]
        values = bootstrap[:, 1, pool_index, :] - bootstrap[:, 0, pool_index, :]
        difference_frames.append(
            summarize_difference_curve(
                method=method,
                name=f"mixed_minus_high_K{pool_size}",
                details=f"Mixed-realistic minus high-dependency at K={pool_size}",
                alphas=alphas,
                point=point,
                bootstrap=values,
                pairing=resolved_pairing,
            )
        )

    did_point = (original[1, 1, :] - original[1, 0, :]) - (
        original[0, 1, :] - original[0, 0, :]
    )
    did_values = (bootstrap[:, 1, 1, :] - bootstrap[:, 1, 0, :]) - (
        bootstrap[:, 0, 1, :] - bootstrap[:, 0, 0, :]
    )
    difference_frames.append(
        summarize_difference_curve(
            method=method,
            name="difference_in_differences",
            details="(Mixed K20-K7) - (High-dependency K20-K7)",
            alphas=alphas,
            point=did_point,
            bootstrap=did_values,
            pairing=resolved_pairing,
        )
    )
    differences = pd.concat(difference_frames, ignore_index=True)
    differences.to_csv(method_dir / "phase3c_tess_bootstrap_difference_curves.csv", index=False)

    contrasts = build_primary_contrasts(
        method=method, alphas=alphas, original=original, bootstrap=bootstrap
    )
    contrasts.to_csv(method_dir / "phase3c_tess_bootstrap_primary_contrasts.csv", index=False)

    plot_curves_with_simultaneous_bands(curve_summary, method_dir)
    plot_difference_curves(differences, method_dir)

    if save_replicates:
        np.savez_compressed(
            method_dir / "phase3c_tess_bootstrap_replicates.npz",
            tess=bootstrap,
            original_tess=original,
            alphas=alphas,
            libraries=np.asarray(LIBRARIES),
            pool_sizes=np.asarray(POOL_SIZES),
        )

    print(f"\n=== {method} ===")
    print(f"Cross-library bootstrap: {resolved_pairing}")
    print(f"Bootstrap repetitions:   {bootstrap_repetitions:,}")
    print(f"Boundary corrections:    {boundary_corrections}")
    if not contrasts.empty:
        print()
        print(
            contrasts[
                ["contrast", "estimate", "ci_low_95", "ci_high_95"]
            ].to_string(index=False)
        )

    return {
        "method": method,
        "resolved_cross_library_pairing": resolved_pairing,
        "high_repetitions": high.repetitions,
        "mixed_repetitions": mixed.repetitions,
        "boundary_corrections": boundary_corrections,
        "output_directory": str(method_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Conditional paired bootstrap for Phase 3C TESS curves"
    )
    parser.add_argument("--high-dependency", type=Path, required=True)
    parser.add_argument("--mixed-realistic", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--alphas", type=parse_alpha_grid, default=DEFAULT_ALPHAS
    )
    parser.add_argument("--selection-event-count", type=int, default=100)
    parser.add_argument(
        "--bootstrap-repetitions", type=int, default=DEFAULT_BOOTSTRAP_REPETITIONS
    )
    parser.add_argument("--bootstrap-seed", type=int, default=20260730)
    parser.add_argument("--batch-size", type=int, default=250)
    parser.add_argument(
        "--cross-library-pairing",
        choices=("auto", "paired", "independent"),
        default="auto",
    )
    parser.add_argument("--include-mannwhitney-sensitivity", action="store_true")
    parser.add_argument("--save-bootstrap-replicates", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else repo_root / "simulations" / "ess" / "outputs" / "phase3c_bootstrap"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    high_path = args.high_dependency.expanduser().resolve()
    mixed_path = args.mixed_realistic.expanduser().resolve()
    for path in (high_path, mixed_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    alphas = np.asarray(tuple(args.alphas), dtype=float)
    methods = [PRIMARY_METHOD]
    if args.include_mannwhitney_sensitivity:
        methods.append(SENSITIVITY_METHOD)

    method_metadata = []
    for method_index, method in enumerate(methods):
        method_metadata.append(
            run_method(
                method=method,
                high_path=high_path,
                mixed_path=mixed_path,
                alphas=alphas,
                selection_event_count=args.selection_event_count,
                bootstrap_repetitions=args.bootstrap_repetitions,
                bootstrap_seed=args.bootstrap_seed + method_index * 100_003,
                batch_size=args.batch_size,
                pairing_mode=args.cross_library_pairing,
                output_dir=output_dir,
                save_replicates=args.save_bootstrap_replicates,
            )
        )

    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "analysis": "conditional paired bootstrap of Phase 3C TESS curves",
        "bootstrap_conditioning": "frozen empirical null-reference bank",
        "not_included": "uncertainty from rebuilding the null-reference bank",
        "high_dependency_input": str(high_path),
        "high_dependency_sha256": file_sha256(high_path),
        "mixed_realistic_input": str(mixed_path),
        "mixed_realistic_sha256": file_sha256(mixed_path),
        "alphas": [float(alpha) for alpha in alphas],
        "selection_event_count": int(args.selection_event_count),
        "bootstrap_repetitions": int(args.bootstrap_repetitions),
        "bootstrap_seed": int(args.bootstrap_seed),
        "batch_size": int(args.batch_size),
        "requested_cross_library_pairing": args.cross_library_pairing,
        "methods": method_metadata,
    }
    (output_dir / "phase3c_tess_bootstrap_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"\nWrote bootstrap outputs to {output_dir}")


if __name__ == "__main__":
    main()
