from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from d6_validation_core import (
    build_dgps,
    compute_population_benchmark,
    run_bootstrap_outer_dataset,
    run_outer_replication,
    validate_dgp,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run D6 fixed-finite-candidate unique-winner numerical validation."
        )
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    fieldnames = list(rows[0].keys())
    for row in rows:
        if list(row.keys()) != fieldnames:
            raise ValueError(f"inconsistent CSV fields for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _cell_key(
    dgp: str,
    alpha: float,
    reference: int,
    evaluation: int,
) -> str:
    return f"{dgp}|{alpha:.2f}|{reference}|{evaluation}"


def _benchmark_key(dgp: str, alpha: float) -> str:
    return f"{dgp}|{alpha:.2f}"


def _declared_count(
    section: dict[str, Any],
    final_key: str,
    draft_key: str,
) -> int:
    if final_key in section:
        value = int(section[final_key])
    elif draft_key in section:
        value = int(section[draft_key])
    else:
        raise KeyError(
            f"missing declared count: {final_key} or {draft_key}"
        )
    if value <= 0:
        raise ValueError(f"{final_key} must be positive")
    return value


def _is_scientific(config: dict[str, Any]) -> bool:
    status = str(config.get("status", "")).lower()
    role = str(config.get("role", "")).lower()
    return (
        "smoke" not in status
        and "runtime" not in status
        and "smoke" not in role
        and "debug" not in role
    )


def _main_regime(alpha: float, reference: int, evaluation: int) -> bool:
    if math.isclose(alpha, 0.01):
        return reference >= 3000 and evaluation >= 3000
    return reference >= 1000 and evaluation >= 1000


def _summarize_full_grid(
    frame: pd.DataFrame,
    benchmarks: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grouping = ["dgp", "alpha", "reference_size", "evaluation_size"]
    for keys, group in frame.groupby(grouping, sort=False):
        dgp, alpha, reference, evaluation = keys
        alpha = float(alpha)
        reference = int(reference)
        evaluation = int(evaluation)
        benchmark = benchmarks[_benchmark_key(str(dgp), alpha)]
        population = benchmark["population"]
        influence = benchmark["influence"]

        exact_var_delta = (
            float(influence["var_phi_eval_delta"]) / evaluation
            + float(influence["var_phi_ref_delta"]) / reference
        )
        exact_var_s = (
            float(influence["var_phi_eval_s"]) / evaluation
            + float(influence["var_phi_ref_s"]) / reference
        )
        empirical_var_delta = float(
            group["delta_pi_regular"].var(ddof=1)
        )
        empirical_var_s = float(group["delta_s_regular"].var(ddof=1))
        bias_delta = float(
            group["delta_pi_regular"].mean()
            - float(population["delta_pi"])
        )
        bias_s = float(
            group["delta_s_regular"].mean()
            - float(population["delta_s"])
        )
        exact_sd_delta = math.sqrt(max(0.0, exact_var_delta))
        exact_sd_s = math.sqrt(max(0.0, exact_var_s))
        bridge_delta = group["bridge_delta_pi"].to_numpy(float)
        bridge_s = group["bridge_delta_s"].to_numpy(float)

        rows.append(
            {
                "dgp": dgp,
                "alpha": alpha,
                "reference_size": reference,
                "evaluation_size": evaluation,
                "replications": int(group.shape[0]),
                "main_regime": int(
                    _main_regime(alpha, reference, evaluation)
                ),
                "true_delta_pi": float(population["delta_pi"]),
                "mean_delta_pi": float(group["delta_pi_regular"].mean()),
                "bias_delta_pi": bias_delta,
                "standardized_bias_delta_pi": (
                    bias_delta / exact_sd_delta
                    if exact_sd_delta > 0
                    else float("nan")
                ),
                "empirical_var_delta_pi": empirical_var_delta,
                "exact_if_var_delta_pi": exact_var_delta,
                "empirical_exact_var_ratio_delta_pi": (
                    empirical_var_delta / exact_var_delta
                    if exact_var_delta > 0
                    else float("nan")
                ),
                "mean_estimated_var_delta_pi": float(
                    group["var_total_delta_hat"].mean()
                ),
                "estimated_exact_var_ratio_delta_pi": (
                    float(group["var_total_delta_hat"].mean())
                    / exact_var_delta
                    if exact_var_delta > 0
                    else float("nan")
                ),
                "normal_coverage_delta_pi": float(
                    group["cover_normal_delta"].mean()
                ),
                "evaluation_only_coverage_delta_pi": float(
                    group["cover_eval_only_delta"].mean()
                ),
                "reference_variance_share_delta_pi": (
                    (float(influence["var_phi_ref_delta"]) / reference)
                    / exact_var_delta
                    if exact_var_delta > 0
                    else float("nan")
                ),
                "true_delta_s": float(population["delta_s"]),
                "mean_delta_s": float(group["delta_s_regular"].mean()),
                "bias_delta_s": bias_s,
                "standardized_bias_delta_s": (
                    bias_s / exact_sd_s
                    if exact_sd_s > 0
                    else float("nan")
                ),
                "empirical_var_delta_s": empirical_var_s,
                "exact_if_var_delta_s": exact_var_s,
                "empirical_exact_var_ratio_delta_s": (
                    empirical_var_s / exact_var_s
                    if exact_var_s > 0
                    else float("nan")
                ),
                "mean_estimated_var_delta_s": float(
                    group["var_total_s_hat"].mean()
                ),
                "estimated_exact_var_ratio_delta_s": (
                    float(group["var_total_s_hat"].mean()) / exact_var_s
                    if exact_var_s > 0
                    else float("nan")
                ),
                "normal_coverage_delta_s": float(
                    group["cover_normal_s"].mean()
                ),
                "evaluation_only_coverage_delta_s": float(
                    group["cover_eval_only_s"].mean()
                ),
                "reference_variance_share_delta_s": (
                    (float(influence["var_phi_ref_s"]) / reference)
                    / exact_var_s
                    if exact_var_s > 0
                    else float("nan")
                ),
                "mean_bridge_delta_pi": float(np.mean(bridge_delta)),
                "rms_bridge_delta_pi": float(
                    np.sqrt(np.mean(bridge_delta**2))
                ),
                "standardized_rms_bridge_delta_pi": (
                    float(np.sqrt(np.mean(bridge_delta**2)))
                    / exact_sd_delta
                    if exact_sd_delta > 0
                    else float("nan")
                ),
                "mean_bridge_delta_s": float(np.mean(bridge_s)),
                "rms_bridge_delta_s": float(
                    np.sqrt(np.mean(bridge_s**2))
                ),
                "standardized_rms_bridge_delta_s": (
                    float(np.sqrt(np.mean(bridge_s**2))) / exact_sd_s
                    if exact_sd_s > 0
                    else float("nan")
                ),
                "mean_pathwise_disagreement_probability": float(
                    group["pathwise_disagreement_probability"].mean()
                ),
                "mean_interval_union_probability": float(
                    group["interval_union_probability"].mean()
                ),
                "support_violation_count": int(
                    group["support_violation_count"].sum()
                ),
                "maximum_covariance_identity_error": float(
                    group["covariance_identity_error"].max()
                ),
                "maximum_candidate_threshold_gap": float(
                    group["maximum_candidate_threshold_gap"].max()
                ),
                "monte_carlo_se_coverage": float(
                    math.sqrt(
                        max(
                            0.0,
                            float(group["cover_normal_delta"].mean())
                            * (
                                1.0
                                - float(
                                    group["cover_normal_delta"].mean()
                                )
                            )
                            / group.shape[0],
                        )
                    )
                ),
            }
        )
    return rows


def _summarize_bootstrap(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    grouping = ["dgp", "alpha", "reference_size", "evaluation_size"]
    for keys, group in frame.groupby(grouping, sort=False):
        dgp, alpha, reference, evaluation = keys
        empirical_sd_delta = float(group["delta_pi"].std(ddof=1))
        empirical_sd_s = float(group["delta_s"].std(ddof=1))
        mean_boot_delta = float(group["delta_bootstrap_sd"].mean())
        mean_boot_s = float(group["s_bootstrap_sd"].mean())
        rows.append(
            {
                "dgp": dgp,
                "alpha": float(alpha),
                "reference_size": int(reference),
                "evaluation_size": int(evaluation),
                "outer_datasets": int(group.shape[0]),
                "empirical_sd_delta_pi": empirical_sd_delta,
                "mean_bootstrap_sd_delta_pi": mean_boot_delta,
                "bootstrap_empirical_sd_ratio_delta_pi": (
                    mean_boot_delta / empirical_sd_delta
                    if empirical_sd_delta > 0
                    else float("nan")
                ),
                "bootstrap_normal_coverage_delta_pi": float(
                    group["delta_cover_bootstrap_normal"].mean()
                ),
                "percentile_coverage_delta_pi": float(
                    group["delta_cover_percentile"].mean()
                ),
                "basic_coverage_delta_pi": float(
                    group["delta_cover_basic"].mean()
                ),
                "empirical_sd_delta_s": empirical_sd_s,
                "mean_bootstrap_sd_delta_s": mean_boot_s,
                "bootstrap_empirical_sd_ratio_delta_s": (
                    mean_boot_s / empirical_sd_s
                    if empirical_sd_s > 0
                    else float("nan")
                ),
                "bootstrap_normal_coverage_delta_s": float(
                    group["s_cover_bootstrap_normal"].mean()
                ),
                "percentile_coverage_delta_s": float(
                    group["s_cover_percentile"].mean()
                ),
                "basic_coverage_delta_s": float(
                    group["s_cover_basic"].mean()
                ),
                "bootstrap_failures": int(
                    group["bootstrap_failures"].sum()
                ),
                "minimum_finite_bootstrap_replicates": int(
                    group["bootstrap_replicates_finite"].min()
                ),
            }
        )
    return rows


def _bridge_sequence_diagnostics(
    cell_summary: pd.DataFrame,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (dgp, alpha), group in cell_summary.groupby(
        ["dgp", "alpha"],
        sort=False,
    ):
        smallest = group.loc[
            group["reference_size"].idxmin()
        ]
        largest_candidates = group[
            group["reference_size"] == group["reference_size"].max()
        ]
        largest = largest_candidates.sort_values(
            ["evaluation_size"],
            ascending=False,
        ).iloc[0]
        initial = float(
            smallest["standardized_rms_bridge_delta_pi"]
        )
        final = float(largest["standardized_rms_bridge_delta_pi"])
        rows.append(
            {
                "dgp": dgp,
                "alpha": float(alpha),
                "initial_reference_size": int(
                    smallest["reference_size"]
                ),
                "largest_reference_size": int(
                    largest["reference_size"]
                ),
                "initial_standardized_rms": initial,
                "largest_standardized_rms": final,
                "relative_change": (
                    (final - initial) / initial
                    if initial > 0
                    else float("nan")
                ),
                "decreased": int(final < initial),
                "not_increased_over_25_percent": int(
                    initial <= 0 or final <= 1.25 * initial
                ),
            }
        )
    return rows


def _scientific_adjudication(
    config: dict[str, Any],
    cell_summary: pd.DataFrame,
    bootstrap_summary: pd.DataFrame,
    bridge_summary: pd.DataFrame,
) -> dict[str, Any]:
    criteria = config["success_criteria"]
    main = cell_summary[cell_summary["main_regime"] == 1].copy()

    checks: dict[str, bool] = {}
    for suffix in ["delta_pi", "delta_s"]:
        standardized_bias = main[
            f"standardized_bias_{suffix}"
        ].abs()
        variance_ratio = main[
            f"empirical_exact_var_ratio_{suffix}"
        ]
        coverage = main[f"normal_coverage_{suffix}"]
        checks[f"{suffix}_bias_per_cell"] = bool(
            (standardized_bias
             <= criteria["standardized_bias_per_main_cell_max"]).all()
        )
        checks[f"{suffix}_median_bias"] = bool(
            standardized_bias.median()
            <= criteria["median_standardized_bias_max"]
        )
        low, high = criteria["variance_ratio_per_main_cell"]
        checks[f"{suffix}_variance_ratio_per_cell"] = bool(
            ((variance_ratio >= low) & (variance_ratio <= high)).all()
        )
        low, high = criteria["median_variance_ratio"]
        checks[f"{suffix}_median_variance_ratio"] = bool(
            low <= variance_ratio.median() <= high
        )
        low, high = criteria["normal_coverage_per_main_cell"]
        checks[f"{suffix}_coverage_per_cell"] = bool(
            ((coverage >= low) & (coverage <= high)).all()
        )
        low, high = criteria["mean_normal_coverage"]
        checks[f"{suffix}_mean_coverage"] = bool(
            low <= coverage.mean() <= high
        )

    for suffix in ["delta_pi", "delta_s"]:
        ratios = bootstrap_summary[
            f"bootstrap_empirical_sd_ratio_{suffix}"
        ]
        low, high = criteria["bootstrap_sd_ratio_per_cell"]
        checks[f"{suffix}_bootstrap_sd_cells"] = bool(
            int(((ratios >= low) & (ratios <= high)).sum())
            >= criteria["bootstrap_sd_ratio_required_cells"]
        )
        low, high = criteria["median_bootstrap_sd_ratio"]
        checks[f"{suffix}_bootstrap_sd_median"] = bool(
            low <= ratios.median() <= high
        )
        coverage = bootstrap_summary[
            f"bootstrap_normal_coverage_{suffix}"
        ]
        low, high = criteria["bootstrap_coverage_per_cell"]
        checks[f"{suffix}_bootstrap_coverage_cells"] = bool(
            ((coverage >= low) & (coverage <= high)).all()
        )
        low, high = criteria["mean_bootstrap_coverage"]
        checks[f"{suffix}_bootstrap_coverage_mean"] = bool(
            low <= coverage.mean() <= high
        )

    checks["plus_one_sequences"] = bool(
        int(
            bridge_summary[
                "not_increased_over_25_percent"
            ].sum()
        )
        >= criteria["plus_one_nonincrease_sequences_required"]
    )
    return {
        "checks": checks,
        "pass": bool(all(checks.values())),
    }


def _render_adjudication(
    status: str,
    scientific: bool,
    elapsed_seconds: float,
    full_rows: int,
    bootstrap_rows: int,
    fatal_checks: dict[str, bool],
    scientific_result: dict[str, Any] | None,
) -> str:
    lines = [
        "# D6 Numerical Validation Adjudication",
        "",
        f"**Status: {status}**",
        "",
    ]
    if scientific:
        lines.append(
            "This is the locked scientific numerical validation adjudication."
        )
    else:
        lines.extend(
            [
                "This is runtime-only smoke and implementation debugging.",
                "It is not scientific evidence and does not lock the D6 design.",
            ]
        )
    lines.extend(
        [
            "",
            "## Execution",
            "",
            f"- Full-grid replication rows: {full_rows}",
            f"- Bootstrap outer-dataset rows: {bootstrap_rows}",
            f"- Elapsed seconds: {elapsed_seconds:.3f}",
            "",
            "## Fatal implementation checks",
            "",
        ]
    )
    for key, value in fatal_checks.items():
        lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    if scientific_result is not None:
        lines.extend(["", "## Scientific checks", ""])
        for key, value in scientific_result["checks"].items():
            lines.append(f"- {key}: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This validation concerns fixed finite candidate pools, continuous unique winners, candidate-specific calibration, and a separate scalar activation trigger.",
            "",
            "It is not direct evidence for maximum-score activation, deterministic tie rules, failed-fit fallback, growing candidate dimension, or simultaneous alpha-process inference.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_manifest(output_dir: Path) -> None:
    candidates = sorted(
        path
        for path in output_dir.iterdir()
        if path.is_file() and path.name != "D6_OUTPUTS_SHA256.txt"
    )
    lines = [f"{_sha256(path)}  {path.name}" for path in candidates]
    (output_dir / "D6_OUTPUTS_SHA256.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    scientific = _is_scientific(config)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config_copy = args.output_dir / "D6_CONFIG_USED.json"
    config_copy.write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    dgps = build_dgps(config)
    alphas = [float(value) for value in config["alphas"]]
    activation_rate = float(config["activation_rate"])
    benchmark_seed = int(config["benchmark"]["seed"])
    benchmarks: dict[str, dict[str, Any]] = {}

    print("=" * 72)
    print("D6 fixed-finite-candidate numerical validation")
    print("=" * 72)
    print(f"Mode: {'SCIENTIFIC' if scientific else 'RUNTIME-ONLY SMOKE'}")
    print(f"DGPs: {len(dgps)}")
    print(f"Full cells: {len(dgps) * len(alphas) * len(config['bank_designs'])}")
    print(f"Bootstrap cells: {len(config['bootstrap']['cells'])}")

    for dgp_index, dgp in enumerate(dgps):
        for alpha_index, alpha in enumerate(alphas):
            print(f"Benchmark: {dgp.name}, alpha={alpha:.2f}")
            benchmark = compute_population_benchmark(
                dgp,
                alpha,
                activation_rate,
                config["benchmark"],
                benchmark_seed,
                dgp_index,
                alpha_index,
            )
            benchmarks[_benchmark_key(dgp.name, alpha)] = benchmark

    benchmark_path = args.output_dir / "D6_POPULATION_BENCHMARKS.json"
    benchmark_path.write_text(
        json.dumps(benchmarks, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    full_rows: list[dict[str, Any]] = []
    outer_repetitions = _declared_count(
        config["full_grid"],
        "outer_repetitions_per_cell",
        "outer_repetitions_per_cell_draft",
    )
    full_seed_root = int(config["full_grid"]["seed_root"])
    for dgp_index, dgp in enumerate(dgps):
        for alpha_index, alpha in enumerate(alphas):
            benchmark = benchmarks[_benchmark_key(dgp.name, alpha)]
            for design_index, design in enumerate(config["bank_designs"]):
                reference = int(design["reference"])
                evaluation = int(design["evaluation"])
                print(
                    f"Full cell: {dgp.name}, alpha={alpha:.2f}, "
                    f"B={reference}, n={evaluation}, R={outer_repetitions}"
                )
                for replication in range(outer_repetitions):
                    result = run_outer_replication(
                        dgp,
                        alpha,
                        activation_rate,
                        reference,
                        evaluation,
                        (
                            full_seed_root,
                            dgp_index,
                            alpha_index,
                            design_index,
                            replication,
                        ),
                        benchmark,
                    )
                    full_rows.append(
                        {
                            "dgp": dgp.name,
                            "dgp_index": dgp_index,
                            "alpha": alpha,
                            "alpha_index": alpha_index,
                            "reference_size": reference,
                            "evaluation_size": evaluation,
                            "design_index": design_index,
                            "replication": replication,
                            **result,
                        }
                    )

    full_path = args.output_dir / "D6_FULL_GRID_REPLICATIONS.csv"
    _write_csv(full_path, full_rows)
    full_frame = pd.DataFrame(full_rows)
    cell_rows = _summarize_full_grid(full_frame, benchmarks)
    cell_path = args.output_dir / "D6_FULL_GRID_CELL_SUMMARY.csv"
    _write_csv(cell_path, cell_rows)
    cell_frame = pd.DataFrame(cell_rows)

    bridge_rows = _bridge_sequence_diagnostics(cell_frame)
    bridge_path = args.output_dir / "D6_PLUS_ONE_SEQUENCE_SUMMARY.csv"
    _write_csv(bridge_path, bridge_rows)
    bridge_frame = pd.DataFrame(bridge_rows)

    dgp_by_name = {dgp.name: dgp for dgp in dgps}
    dgp_index_by_name = {
        dgp.name: index for index, dgp in enumerate(dgps)
    }
    alpha_index_by_value = {
        alpha: index for index, alpha in enumerate(alphas)
    }
    bootstrap_rows: list[dict[str, Any]] = []
    bootstrap_outer = _declared_count(
        config["bootstrap"],
        "outer_datasets_per_cell",
        "outer_datasets_per_cell_draft",
    )
    resamples = _declared_count(
        config["bootstrap"],
        "resamples_per_dataset",
        "resamples_per_dataset_draft",
    )
    bootstrap_outer_seed = int(config["bootstrap"]["outer_seed_root"])
    bootstrap_resample_seed = int(
        config["bootstrap"]["resample_seed_root"]
    )
    for cell_index, cell in enumerate(config["bootstrap"]["cells"]):
        dgp = dgp_by_name[str(cell["dgp"])]
        dgp_index = dgp_index_by_name[dgp.name]
        alpha = float(cell["alpha"])
        alpha_index = alpha_index_by_value[alpha]
        reference = int(cell["reference"])
        evaluation = int(cell["evaluation"])
        benchmark = benchmarks[_benchmark_key(dgp.name, alpha)]
        print(
            f"Bootstrap cell: {dgp.name}, alpha={alpha:.2f}, "
            f"B={reference}, n={evaluation}, outer={bootstrap_outer}, "
            f"M={resamples}"
        )
        for outer in range(bootstrap_outer):
            result = run_bootstrap_outer_dataset(
                dgp,
                alpha,
                activation_rate,
                reference,
                evaluation,
                resamples,
                (
                    bootstrap_outer_seed,
                    cell_index,
                    outer,
                    0,
                ),
                (
                    bootstrap_resample_seed,
                    cell_index,
                    outer,
                    0,
                ),
                benchmark,
            )
            bootstrap_rows.append(
                {
                    "dgp": dgp.name,
                    "dgp_index": dgp_index,
                    "alpha": alpha,
                    "alpha_index": alpha_index,
                    "reference_size": reference,
                    "evaluation_size": evaluation,
                    "bootstrap_cell_index": cell_index,
                    "outer_dataset": outer,
                    **result,
                }
            )

    bootstrap_path = args.output_dir / "D6_BOOTSTRAP_OUTER_RESULTS.csv"
    _write_csv(bootstrap_path, bootstrap_rows)
    bootstrap_frame = pd.DataFrame(bootstrap_rows)
    bootstrap_summary_rows = _summarize_bootstrap(bootstrap_frame)
    bootstrap_summary_path = (
        args.output_dir / "D6_BOOTSTRAP_CELL_SUMMARY.csv"
    )
    _write_csv(bootstrap_summary_path, bootstrap_summary_rows)
    bootstrap_summary_frame = pd.DataFrame(bootstrap_summary_rows)

    tolerance = float(config.get("fatal_tolerance", 1e-12))
    fatal_checks = {
        "all_dgp_covariances_positive_definite": all(
            validate_dgp(dgp)["minimum_covariance_eigenvalue"] > 0
            for dgp in dgps
        ),
        "full_grid_row_count": (
            len(full_rows)
            == len(dgps)
            * len(alphas)
            * len(config["bank_designs"])
            * outer_repetitions
        ),
        "bootstrap_row_count": (
            len(bootstrap_rows)
            == len(config["bootstrap"]["cells"]) * bootstrap_outer
        ),
        "covariance_identity": bool(
            (
                full_frame["covariance_identity_error"]
                <= tolerance
            ).all()
        ),
        "plus_one_support": bool(
            (full_frame["support_violation_count"] == 0).all()
        ),
        "plus_one_index_gap": bool(
            (
                (
                    full_frame["plus_one_index"]
                    - full_frame["regular_quantile_index"]
                ).isin([0, 1])
            ).all()
        ),
        "finite_full_grid": bool(
            np.isfinite(
                full_frame.select_dtypes(include=[np.number]).to_numpy()
            ).all()
        ),
        "finite_bootstrap": bool(
            np.isfinite(
                bootstrap_frame.select_dtypes(
                    include=[np.number]
                ).to_numpy()
            ).all()
        ),
        "zero_bootstrap_failures": bool(
            (bootstrap_frame["bootstrap_failures"] == 0).all()
        ),
        "nonempty_required_outputs": all(
            path.is_file() and path.stat().st_size > 0
            for path in [
                config_copy,
                benchmark_path,
                full_path,
                cell_path,
                bridge_path,
                bootstrap_path,
                bootstrap_summary_path,
            ]
        ),
    }
    fatal_pass = all(fatal_checks.values())

    scientific_result: dict[str, Any] | None = None
    scientific_pass = True
    if scientific and fatal_pass:
        scientific_result = _scientific_adjudication(
            config,
            cell_frame,
            bootstrap_summary_frame,
            bridge_frame,
        )
        scientific_pass = bool(scientific_result["pass"])

    status = "PASS" if fatal_pass and scientific_pass else "FAIL"
    elapsed = time.perf_counter() - started
    checks_payload = {
        "status": status,
        "scientific_mode": scientific,
        "fatal_checks": fatal_checks,
        "scientific_checks": (
            scientific_result["checks"]
            if scientific_result is not None
            else None
        ),
    }
    checks_path = args.output_dir / "D6_VALIDATION_CHECKS.json"
    checks_path.write_text(
        json.dumps(checks_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary_payload = {
        "status": status,
        "scientific_mode": scientific,
        "dgp_count": len(dgps),
        "full_cell_count": (
            len(dgps) * len(alphas) * len(config["bank_designs"])
        ),
        "full_replication_rows": len(full_rows),
        "bootstrap_cell_count": len(config["bootstrap"]["cells"]),
        "bootstrap_outer_rows": len(bootstrap_rows),
        "elapsed_seconds": elapsed,
        "output_directory": str(args.output_dir.resolve()),
    }
    summary_path = args.output_dir / "D6_VALIDATION_SUMMARY.json"
    summary_path.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    adjudication_path = (
        args.output_dir / "D6_VALIDATION_ADJUDICATION.md"
    )
    adjudication_path.write_text(
        _render_adjudication(
            status,
            scientific,
            elapsed,
            len(full_rows),
            len(bootstrap_rows),
            fatal_checks,
            scientific_result,
        ),
        encoding="utf-8",
    )

    _write_manifest(args.output_dir)

    print("=" * 72)
    print(f"Status: {status}")
    print(f"Full replication rows: {len(full_rows)}")
    print(f"Bootstrap outer rows: {len(bootstrap_rows)}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output directory: {args.output_dir.resolve()}")
    print(
        "Scientific evidence: "
        + ("YES" if scientific else "NO (runtime-only smoke)")
    )

    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
