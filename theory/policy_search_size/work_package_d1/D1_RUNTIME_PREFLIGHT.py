from __future__ import annotations

import argparse
import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np

from d1_core import estimate_policy, independent_normal_benchmark


def bootstrap_estimates(
    rng: np.random.Generator,
    reference: np.ndarray,
    evaluation: np.ndarray,
    *,
    alpha: float,
    activation_rate: float,
    repetitions: int,
) -> np.ndarray:
    b = reference.shape[0]
    n = evaluation.shape[0]
    out = np.empty((repetitions, 2), dtype=float)
    for j in range(repetitions):
        ref_index = rng.integers(0, b, size=b)
        eval_index = rng.integers(0, n, size=n)
        out[j, :2] = estimate_policy(
            reference[ref_index],
            evaluation[eval_index],
            alpha=alpha,
            activation_rate=activation_rate,
        )[:2]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runtime-only preflight for D1 two-bank inference. NOT SCIENTIFIC EVIDENCE."
    )
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "preflight_output")
    parser.add_argument("--B", type=int, default=1000)
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--outer", type=int, default=30)
    parser.add_argument("--bootstrap", type=int, default=100)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--activation-rate", type=float, default=0.50)
    parser.add_argument("--seed", type=int, default=20260911)
    args = parser.parse_args()

    if min(args.B, args.n) < 100:
        raise ValueError("B and n must each be at least 100")
    if args.outer < 2 or args.bootstrap < 2:
        raise ValueError("outer and bootstrap counts must each be at least 2")

    outdir = args.outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    benchmark = independent_normal_benchmark(
        alpha=args.alpha,
        activation_rate=args.activation_rate,
        lambda_ratio=args.n / args.B,
    )

    start = time.perf_counter()
    outer_rows = []
    bootstrap_seconds = 0.0
    for rep in range(args.outer):
        reference = rng.normal(size=(args.B, 3))
        evaluation = rng.normal(size=(args.n, 3))
        pi_hat, s_hat, q0_hat, q1_hat = estimate_policy(
            reference,
            evaluation,
            alpha=args.alpha,
            activation_rate=args.activation_rate,
        )
        boot_start = time.perf_counter()
        boot = bootstrap_estimates(
            rng,
            reference,
            evaluation,
            alpha=args.alpha,
            activation_rate=args.activation_rate,
            repetitions=args.bootstrap,
        )
        bootstrap_seconds += time.perf_counter() - boot_start
        outer_rows.append(
            {
                "replication": rep,
                "pi_hat": pi_hat,
                "tess_hat": s_hat,
                "q0_hat": q0_hat,
                "q1_hat": q1_hat,
                "bootstrap_sd_pi": float(np.std(boot[:, 0], ddof=1)),
                "bootstrap_sd_tess": float(np.std(boot[:, 1], ddof=1)),
            }
        )

    elapsed = time.perf_counter() - start
    values_pi = np.array([row["pi_hat"] for row in outer_rows])
    values_s = np.array([row["tess_hat"] for row in outer_rows])

    if not np.all(np.isfinite(values_pi)) or not np.all(np.isfinite(values_s)):
        raise RuntimeError("nonfinite preflight output")

    # Runtime-only output. These debug statistics must not be used to tune scientific settings.
    raw_ru_maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        peak_resident_memory_mib = raw_ru_maxrss / (1024.0 * 1024.0)
        ru_maxrss_unit = "bytes"
    else:
        peak_resident_memory_mib = raw_ru_maxrss / 1024.0
        ru_maxrss_unit = "KiB"

    summary = {
        "label": "RUNTIME-ONLY PREFLIGHT — NOT SCIENTIFIC EVIDENCE",
        "status": "PASS",
        "B": args.B,
        "n": args.n,
        "outer_repetitions": args.outer,
        "bootstrap_repetitions_per_outer": args.bootstrap,
        "alpha": args.alpha,
        "activation_rate": args.activation_rate,
        "seed": args.seed,
        "elapsed_seconds": elapsed,
        "seconds_per_outer_dataset": elapsed / args.outer,
        "seconds_per_bootstrap_replicate": bootstrap_seconds / (args.outer * args.bootstrap),
        "peak_resident_memory_mib": peak_resident_memory_mib,
        "ru_maxrss_raw": raw_ru_maxrss,
        "ru_maxrss_platform_unit": ru_maxrss_unit,
        "exact_benchmark": {
            "pi": benchmark.rejection_probability,
            "tess": benchmark.tess,
            "sqrt_n_variance_pi": benchmark.total_variance_sqrt_n,
            "sqrt_n_variance_tess": benchmark.tess_variance_sqrt_n,
        },
        "debug_only_aggregate": {
            "mean_pi_hat": float(np.mean(values_pi)),
            "mean_tess_hat": float(np.mean(values_s)),
            "empirical_variance_pi_hat": float(np.var(values_pi, ddof=1)),
            "empirical_variance_tess_hat": float(np.var(values_s, ddof=1)),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }

    (outdir / "D1_PREFLIGHT_RUNTIME.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    try:
        import pandas as pd
        pd.DataFrame(outer_rows).to_csv(outdir / "D1_PREFLIGHT_DEBUG_REPLICATIONS.csv", index=False)
    except Exception:
        pass

    print("D1 runtime-only preflight complete")
    print("Status: PASS")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Seconds per outer dataset: {elapsed / args.outer:.6f}")
    print(
        "Seconds per bootstrap replicate: "
        f"{bootstrap_seconds / (args.outer * args.bootstrap):.8f}"
    )
    print(f"Peak resident memory (MiB, platform-aware): {summary['peak_resident_memory_mib']:.1f}")
    print(f"Output: {outdir / 'D1_PREFLIGHT_RUNTIME.json'}")
    print("RUNTIME-ONLY PREFLIGHT — NOT SCIENTIFIC EVIDENCE")


if __name__ == "__main__":
    main()
