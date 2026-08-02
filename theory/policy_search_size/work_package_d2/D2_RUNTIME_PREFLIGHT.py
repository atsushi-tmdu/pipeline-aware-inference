from __future__ import annotations

import argparse
import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np

from d2_core import (
    exact_finite_reference_mean,
    exact_independent_normal_benchmark,
    one_outer_d2,
)


def peak_memory_mib() -> float:
    value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform == "darwin":
        return value / (1024.0 * 1024.0)
    return value / 1024.0


def main() -> None:
    parser = argparse.ArgumentParser(description="D2 runtime-only preflight")
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "preflight_output")
    parser.add_argument("--B", type=int, default=1000)
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--activation-rate", type=float, default=0.5)
    parser.add_argument("--outer", type=int, default=30)
    parser.add_argument("--bootstrap", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261003)
    args = parser.parse_args()

    outdir = args.outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    started = time.perf_counter()
    rows = [
        one_outer_d2(
            rng=rng,
            B=args.B,
            n=args.n,
            alpha=args.alpha,
            r=args.activation_rate,
            bootstrap_repetitions=args.bootstrap,
        )
        for _ in range(args.outer)
    ]
    elapsed = time.perf_counter() - started

    pi_values = np.array([row["pi_hat"] for row in rows])
    tess_values = np.array([row["tess_hat"] for row in rows])
    known_values = np.array([row["known_trigger_pi_hat"] for row in rows])
    boot_pi_sd = np.array([row["bootstrap_pi_sd"] for row in rows])
    boot_tess_sd = np.array([row["bootstrap_tess_sd"] for row in rows])

    exact = exact_independent_normal_benchmark(
        alpha=args.alpha,
        r=args.activation_rate,
        lambda_ratio=args.n / args.B,
    )
    finite = exact_finite_reference_mean(
        alpha=args.alpha,
        r=args.activation_rate,
        B=args.B,
        estimated_trigger=True,
    )
    finite_known = exact_finite_reference_mean(
        alpha=args.alpha,
        r=args.activation_rate,
        B=args.B,
        estimated_trigger=False,
    )

    result = {
        "label": "RUNTIME-ONLY PREFLIGHT - NOT SCIENTIFIC EVIDENCE",
        "status": "PASS",
        "B": args.B,
        "n": args.n,
        "alpha": args.alpha,
        "activation_rate": args.activation_rate,
        "outer_repetitions": args.outer,
        "bootstrap_repetitions_per_outer": args.bootstrap,
        "seed": args.seed,
        "elapsed_seconds": elapsed,
        "seconds_per_outer_dataset": elapsed / args.outer,
        "seconds_per_bootstrap_replicate": elapsed / (args.outer * args.bootstrap),
        "peak_resident_memory_mib": peak_memory_mib(),
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "population_benchmark": exact,
        "finite_reference_exact_mean": finite,
        "finite_reference_known_trigger_exact_mean": finite_known,
        "debug_only_aggregate": {
            "mean_pi_hat": float(np.mean(pi_values)),
            "mean_tess_hat": float(np.mean(tess_values)),
            "mean_known_trigger_pi_hat": float(np.mean(known_values)),
            "mean_trigger_estimation_pi_difference": float(np.mean(pi_values - known_values)),
            "empirical_variance_pi_hat": float(np.var(pi_values, ddof=1)),
            "empirical_variance_tess_hat": float(np.var(tess_values, ddof=1)),
            "mean_bootstrap_pi_sd": float(np.mean(boot_pi_sd)),
            "mean_bootstrap_tess_sd": float(np.mean(boot_tess_sd)),
        },
    }

    for value in [
        *pi_values,
        *tess_values,
        *boot_pi_sd,
        *boot_tess_sd,
    ]:
        if not np.isfinite(value):
            result["status"] = "FAIL"
            break

    path = outdir / "D2_PREFLIGHT_RUNTIME.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("D2 runtime-only preflight complete")
    print(f"Status: {result['status']}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output: {path}")

    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
