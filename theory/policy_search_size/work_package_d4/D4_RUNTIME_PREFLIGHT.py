from __future__ import annotations

import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np
import scipy

from d4_core import (
    estimate_d4,
    finite_difference_gradient_gaussian,
    gaussian_d4_benchmark,
    paired_two_bank_bootstrap,
)


HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "D4_PREFLIGHT_CONFIG.json"
OUTPUT_DIR = HERE / "preflight_output"
OUTPUT_PATH = OUTPUT_DIR / "D4_PREFLIGHT_RUNTIME.json"


def peak_resident_memory_mib() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes; Linux reports KiB.
    if sys.platform == "darwin":
        return float(usage / (1024**2))
    return float(usage / 1024.0)


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    alpha = float(config["alpha"])
    activation_rate = float(config["target_activation_rate"])
    B = int(config["B"])
    n = int(config["n"])
    outer = int(config["outer_repetitions"])
    bootstrap_repetitions = int(config["bootstrap_repetitions_per_outer"])
    seed = int(config["seed"])
    correlation = np.asarray(config["correlation"], dtype=float)

    benchmark = gaussian_d4_benchmark(alpha, activation_rate, correlation)
    finite_difference = finite_difference_gradient_gaussian(
        alpha,
        activation_rate,
        correlation,
        step=2e-4,
    )
    analytic_gradient = np.asarray(benchmark["gradient_delta_tess"], dtype=float)
    gradient_max_abs_error = float(np.max(np.abs(finite_difference - analytic_gradient)))

    seed_sequence = np.random.SeedSequence(seed)
    outer_seeds = seed_sequence.spawn(outer)

    delta_pi = np.empty(outer, dtype=float)
    delta_tess = np.empty(outer, dtype=float)
    adaptive_pi = np.empty(outer, dtype=float)
    comparator_pi = np.empty(outer, dtype=float)
    bootstrap_delta_pi_sd = np.empty(outer, dtype=float)
    bootstrap_delta_tess_sd = np.empty(outer, dtype=float)

    start = time.perf_counter()
    for index, outer_seed in enumerate(outer_seeds):
        rng = np.random.default_rng(outer_seed)
        reference = rng.multivariate_normal(np.zeros(3), correlation, size=B)
        evaluation = rng.multivariate_normal(np.zeros(3), correlation, size=n)
        estimate = estimate_d4(reference, evaluation, alpha, activation_rate)
        bootstrap = paired_two_bank_bootstrap(
            reference,
            evaluation,
            alpha,
            activation_rate,
            repetitions=bootstrap_repetitions,
            seed=int(rng.integers(0, np.iinfo(np.int32).max)),
        )
        delta_pi[index] = estimate.delta_pi_hat
        delta_tess[index] = estimate.delta_tess_hat
        adaptive_pi[index] = estimate.pi_adaptive_hat
        comparator_pi[index] = estimate.pi_comparator_hat
        bootstrap_delta_pi_sd[index] = float(np.std(bootstrap["delta_pi"], ddof=1))
        bootstrap_delta_tess_sd[index] = float(np.std(bootstrap["delta_tess"], ddof=1))
    elapsed = time.perf_counter() - start

    expected_delta_tess_sd = float(
        np.sqrt(benchmark["sigma_total2_sqrt_n"] / n)
    )

    arrays = [
        delta_pi,
        delta_tess,
        adaptive_pi,
        comparator_pi,
        bootstrap_delta_pi_sd,
        bootstrap_delta_tess_sd,
    ]
    finite = all(np.all(np.isfinite(array)) for array in arrays)
    status = "PASS" if finite and gradient_max_abs_error < 5e-3 else "FAIL"

    output = {
        "label": config["label"],
        "status": status,
        "alpha": alpha,
        "target_activation_rate": activation_rate,
        "B": B,
        "n": n,
        "outer_repetitions": outer,
        "bootstrap_repetitions_per_outer": bootstrap_repetitions,
        "seed": seed,
        "correlation": correlation.tolist(),
        "elapsed_seconds": elapsed,
        "seconds_per_outer_dataset": elapsed / outer,
        "seconds_per_bootstrap_replicate": elapsed / (outer * bootstrap_repetitions),
        "peak_resident_memory_mib": peak_resident_memory_mib(),
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
        },
        "population_benchmark": benchmark,
        "derivative_check": {
            "analytic_gradient": analytic_gradient.tolist(),
            "finite_difference_gradient": finite_difference.tolist(),
            "maximum_absolute_error": gradient_max_abs_error,
        },
        "debug_only_aggregate": {
            "mean_pi_adaptive_hat": float(np.mean(adaptive_pi)),
            "mean_pi_comparator_hat": float(np.mean(comparator_pi)),
            "mean_delta_pi_hat": float(np.mean(delta_pi)),
            "mean_delta_tess_hat": float(np.mean(delta_tess)),
            "empirical_variance_delta_pi_hat": float(np.var(delta_pi, ddof=1)),
            "empirical_variance_delta_tess_hat": float(np.var(delta_tess, ddof=1)),
            "mean_bootstrap_delta_pi_sd": float(np.mean(bootstrap_delta_pi_sd)),
            "mean_bootstrap_delta_tess_sd": float(np.mean(bootstrap_delta_tess_sd)),
            "asymptotic_delta_tess_sd_at_design": expected_delta_tess_sd,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
