#!/usr/bin/env python3
"""Paired cross-library confirmatory policy effects."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


POLICY_EFFECTS = (
    "promising_tess_minus_matched_random",
    "rescue_tess_minus_matched_random",
    "cov_activation_increment",
)


def tess(pi: float, alpha: float) -> float:
    return math.log1p(-pi) / math.log1p(-alpha)


def load_bank(path: Path) -> pd.DataFrame:
    bank = pd.read_csv(path)
    pivot = bank.pivot(
        index="replication",
        columns="policy",
        values="naive_empirical_p_value",
    )
    activation = (
        bank[bank["policy"] == "promising_triggered"]
        .drop_duplicates("replication")
        .set_index("replication")["expanded"]
        .astype(bool)
        .reindex(pivot.index)
    )
    pivot["activation"] = activation
    return pivot.sort_index()


def effects(frame: pd.DataFrame, alpha: float) -> dict[str, float]:
    p_base = frame["fixed_base"].to_numpy(float)
    p_full = frame["fixed_full"].to_numpy(float)
    p_prom = frame["promising_triggered"].to_numpy(float)
    p_rescue = frame["rescue_triggered"].to_numpy(float)
    a = frame["activation"].to_numpy(bool).astype(float)

    r0 = (p_base < alpha).astype(float)
    r1 = (p_full < alpha).astype(float)
    d = r1 - r0
    r = float(a.mean())

    pi_base = float(r0.mean())
    e_d = float(d.mean())
    pi_prom = float(np.mean(p_prom < alpha))
    pi_rescue = float(np.mean(p_rescue < alpha))
    pi_rand_prom = pi_base + r * e_d
    pi_rand_rescue = pi_base + (1.0 - r) * e_d

    return {
        "promising_tess_minus_matched_random": (
            tess(pi_prom, alpha) - tess(pi_rand_prom, alpha)
        ),
        "rescue_tess_minus_matched_random": (
            tess(pi_rescue, alpha) - tess(pi_rand_rescue, alpha)
        ),
        "cov_activation_increment": float(np.mean(a * d) - r * e_d),
        "promising_activation_rate": r,
        "incremental_gain_rate": float(np.mean(d == 1)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--high-bank", type=Path, required=True)
    parser.add_argument("--mixed-bank", type=Path, required=True)
    parser.add_argument(
        "--alphas",
        default="0.20,0.10,0.05,0.025,0.01,0.005",
    )
    parser.add_argument("--bootstrap-repetitions", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    alphas = tuple(float(x) for x in args.alphas.split(",") if x.strip())
    high = load_bank(args.high_bank)
    mixed = load_bank(args.mixed_bank)

    shared = high.index.intersection(mixed.index)
    if len(shared) != len(high) or len(shared) != len(mixed):
        raise ValueError("Libraries do not share the same replication IDs.")
    high = high.loc[shared]
    mixed = mixed.loc[shared]

    point = {
        ("high_dependency_linear_20", alpha): effects(high, alpha)
        for alpha in alphas
    }
    point.update({
        ("mixed_realistic_20", alpha): effects(mixed, alpha)
        for alpha in alphas
    })

    rng = np.random.default_rng(args.seed)
    n = len(shared)
    boot = {
        (library, alpha, metric): np.empty(args.bootstrap_repetitions)
        for library in ("high_dependency_linear_20", "mixed_realistic_20")
        for alpha in alphas
        for metric in POLICY_EFFECTS
    }
    boot.update({
        ("mixed_minus_high", alpha, metric): np.empty(args.bootstrap_repetitions)
        for alpha in alphas
        for metric in POLICY_EFFECTS
    })

    for b in range(args.bootstrap_repetitions):
        idx = rng.integers(0, n, size=n)
        h = high.iloc[idx]
        m = mixed.iloc[idx]
        for alpha in alphas:
            he = effects(h, alpha)
            me = effects(m, alpha)
            for metric in POLICY_EFFECTS:
                boot[("high_dependency_linear_20", alpha, metric)][b] = he[metric]
                boot[("mixed_realistic_20", alpha, metric)][b] = me[metric]
                boot[("mixed_minus_high", alpha, metric)][b] = (
                    me[metric] - he[metric]
                )

    rows = []
    for library in (
        "high_dependency_linear_20",
        "mixed_realistic_20",
        "mixed_minus_high",
    ):
        for alpha in alphas:
            for metric in POLICY_EFFECTS:
                if library == "mixed_minus_high":
                    estimate = (
                        point[("mixed_realistic_20", alpha)][metric]
                        - point[("high_dependency_linear_20", alpha)][metric]
                    )
                else:
                    estimate = point[(library, alpha)][metric]
                values = boot[(library, alpha, metric)]
                rows.append({
                    "library_or_contrast": library,
                    "local_alpha": alpha,
                    "metric": metric,
                    "estimate": estimate,
                    "bootstrap_mean": float(values.mean()),
                    "bootstrap_se": float(values.std(ddof=1)),
                    "ci_low_95": float(np.quantile(values, 0.025)),
                    "ci_high_95": float(np.quantile(values, 0.975)),
                    "bootstrap_probability_gt_zero": float(np.mean(values > 0)),
                    "bootstrap_probability_lt_zero": float(np.mean(values < 0)),
                    "bootstrap_repetitions": args.bootstrap_repetitions,
                    "pairing": "same replication IDs across libraries",
                })

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Wrote: {output}")


if __name__ == "__main__":
    main()
