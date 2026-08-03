#!/usr/bin/env python3
"""Numerical validator for Work Package D5."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import numpy as np
import pandas as pd


D5 = Path(__file__).resolve().parent
D4 = D5.parent / "work_package_d4"
REPO = D5.parents[2]

sys.path.insert(0, str(D5))
sys.path.insert(0, str(D4))

from d5_core import boundary_info, estimate_bridge
from d4_validation_core import sample_dgp


ESTIMATE_FIELDS = [
    "q0_hat",
    "q1_hat",
    "c_hat",
    "e0_hat",
    "activation_rate_hat",
    "mu_hat",
    "nu_hat",
    "pi_adaptive_hat",
    "pi_comparator_hat",
    "delta_pi_hat",
    "tess_adaptive_hat",
    "tess_comparator_hat",
    "delta_tess_hat",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(config: dict[str, Any], scientific: bool) -> None:
    required = [
        "study_id",
        "status",
        "d4_master_seed",
        "outer_repetitions",
        "activation_rate",
        "alphas",
        "designs",
        "data_generating_laws",
        "n_jobs",
        "chunk_size",
        "expected_d4_results_commit",
        "expected_d4_results_tag",
        "reproduction_tolerance",
        "output_subdirectory",
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"missing config fields: {missing}")

    allowed_status = (
        {"locked_before_run"}
        if scientific
        else {"smoke_not_scientific", "runtime_only_smoke"}
    )
    if config["status"] not in allowed_status:
        raise ValueError(
            f"invalid status for this run: {config['status']}; "
            f"expected one of {sorted(allowed_status)}"
        )

    if scientific:
        if int(config["outer_repetitions"]) != 3000:
            raise ValueError("scientific outer repetitions must equal 3000")
        if config["alphas"] != [0.01, 0.05, 0.1]:
            raise ValueError("scientific alpha grid differs from D4")
        if config["designs"] != [
            {"B": 500, "n": 500},
            {"B": 1000, "n": 1000},
            {"B": 3000, "n": 3000},
            {"B": 3000, "n": 5000},
        ]:
            raise ValueError("scientific B/n grid differs from D4")


def verify_parent(config: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    expected_tag = str(config["expected_d4_results_tag"])
    expected_commit = str(config["expected_d4_results_commit"])
    observed_commit = subprocess.check_output(
        ["git", "rev-parse", f"{expected_tag}^{{commit}}"],
        cwd=REPO,
        text=True,
    ).strip()
    checks.append(
        {
            "check": "d4_tag_commit",
            "passed": observed_commit == expected_commit,
            "observed": observed_commit,
            "expected": expected_commit,
        }
    )

    lock_manifest_path = D4 / "D4_LOCK_MANIFEST.json"
    lock_manifest = load_json(lock_manifest_path)
    lock_failures: list[str] = []
    for record in lock_manifest["files"]:
        path = D4 / record["file"]
        if not path.is_file():
            lock_failures.append(f"missing:{record['file']}")
            continue
        observed = sha256_file(path)
        if observed != record["sha256"]:
            lock_failures.append(f"hash:{record['file']}")
    checks.append(
        {
            "check": "d4_lock_manifest_files",
            "passed": not lock_failures,
            "failures": lock_failures,
        }
    )

    outputs = D4 / "outputs" / "full_v1"
    frozen_manifest = (
        D4 / "results_freeze" / "full_v1" / "D4_OUTPUTS_SHA256.txt"
    )
    output_failures: list[str] = []
    for line in frozen_manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        path = outputs / relative.strip().removeprefix("./")
        if not path.is_file():
            output_failures.append(f"missing:{path.name}")
            continue
        if sha256_file(path) != digest:
            output_failures.append(f"hash:{path.name}")
    checks.append(
        {
            "check": "d4_frozen_raw_outputs",
            "passed": not output_failures,
            "failures": output_failures,
        }
    )

    if not all(bool(item["passed"]) for item in checks):
        raise RuntimeError(f"D4 parent integrity failed: {checks}")
    return checks


def canonical_d4_cell_index(
    dgp_name: str,
    B: int,
    n: int,
    alpha: float,
) -> tuple[int, int]:
    dgp_order = [
        "independent_normal",
        "gaussian_factor",
        "nonlinear_smooth",
    ]
    design_order = [
        (500, 500),
        (1000, 1000),
        (3000, 3000),
        (3000, 5000),
    ]
    alpha_order = [0.01, 0.05, 0.10]

    if dgp_name not in dgp_order:
        raise ValueError(f"unknown D4 DGP: {dgp_name}")
    if (B, n) not in design_order:
        raise ValueError(f"unknown D4 design: {(B, n)}")

    alpha_matches = [
        index
        for index, candidate in enumerate(alpha_order)
        if math.isclose(float(alpha), candidate, rel_tol=0.0, abs_tol=1e-15)
    ]
    if len(alpha_matches) != 1:
        raise ValueError(f"unknown D4 alpha: {alpha}")

    dgp_index = dgp_order.index(dgp_name)
    design_index = design_order.index((B, n))
    alpha_index = alpha_matches[0]
    cell_index = (
        dgp_index * len(design_order) * len(alpha_order)
        + design_index * len(alpha_order)
        + alpha_index
    )
    return dgp_index, cell_index


def build_cells(config: dict[str, Any]) -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for dgp in config["data_generating_laws"]:
        dgp_name = str(dgp["name"])
        for design in config["designs"]:
            B = int(design["B"])
            n = int(design["n"])
            for alpha in config["alphas"]:
                dgp_index, cell_index = canonical_d4_cell_index(
                    dgp_name,
                    B,
                    n,
                    float(alpha),
                )
                cells.append(
                    {
                        "dgp_index": dgp_index,
                        "cell_index": cell_index,
                        "dgp": dgp_name,
                        "B": B,
                        "n": n,
                        "alpha": float(alpha),
                        "activation_rate_target": float(
                            config["activation_rate"]
                        ),
                    }
                )
    return sorted(cells, key=lambda item: int(item["cell_index"]))


def build_tasks(
    config: dict[str, Any],
    cells: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    outer = int(config["outer_repetitions"])
    chunk = int(config["chunk_size"])
    tasks: list[dict[str, Any]] = []
    for cell in cells:
        for start in range(0, outer, chunk):
            tasks.append(
                {
                    **cell,
                    "start": start,
                    "stop": min(start + chunk, outer),
                    "master_seed": int(config["d4_master_seed"]),
                }
            )
    return tasks


def worker(task: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    B = int(task["B"])
    n = int(task["n"])
    alpha = float(task["alpha"])
    activation_rate = float(task["activation_rate_target"])

    for outer_index in range(int(task["start"]), int(task["stop"])):
        rng = np.random.default_rng(
            np.random.SeedSequence(
                [
                    int(task["master_seed"]),
                    int(task["dgp_index"]),
                    int(task["cell_index"]),
                    outer_index,
                ]
            )
        )
        reference = sample_dgp(rng, str(task["dgp"]), B)
        evaluation = sample_dgp(rng, str(task["dgp"]), n)
        bridge = estimate_bridge(
            reference,
            evaluation,
            alpha,
            activation_rate,
        )
        row = {
            "dgp_index": int(task["dgp_index"]),
            "cell_index": int(task["cell_index"]),
            "outer_index": outer_index,
            "dgp": str(task["dgp"]),
            "B": B,
            "n": n,
            "alpha": alpha,
            "activation_rate_target": activation_rate,
            **bridge.to_dict(),
        }
        row["sqrt_n_delta_pi_bridge"] = math.sqrt(n) * float(
            row["delta_pi_bridge"]
        )
        row["sqrt_B_delta_pi_bridge"] = math.sqrt(B) * float(
            row["delta_pi_bridge"]
        )
        row["B_delta_pi_bridge"] = B * float(row["delta_pi_bridge"])
        row["sqrt_n_delta_tess_bridge"] = math.sqrt(n) * float(
            row["delta_tess_bridge"]
        )
        row["sqrt_B_delta_tess_bridge"] = math.sqrt(B) * float(
            row["delta_tess_bridge"]
        )
        row["B_delta_tess_bridge"] = B * float(
            row["delta_tess_bridge"]
        )
        rows.append(row)
    return rows


def run_tasks(
    config: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    n_jobs = int(config["n_jobs"])

    if n_jobs == 1:
        for index, task in enumerate(tasks, start=1):
            rows.extend(worker(task))
            if index % max(1, len(tasks) // 20) == 0:
                print(f"Completed task {index}/{len(tasks)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = [executor.submit(worker, task) for task in tasks]
            completed = 0
            for future in as_completed(futures):
                rows.extend(future.result())
                completed += 1
                if completed % max(1, len(tasks) // 20) == 0:
                    print(
                        f"Completed task {completed}/{len(tasks)}",
                        flush=True,
                    )

    frame = pd.DataFrame(rows)
    return frame.sort_values(
        ["cell_index", "outer_index"]
    ).reset_index(drop=True)


def load_frozen_d4() -> pd.DataFrame:
    path = (
        D4
        / "outputs"
        / "full_v1"
        / "D4_VALIDATION_REPLICATIONS.csv.gz"
    )
    columns = [
        "dgp_index",
        "cell_index",
        "outer_index",
        "dgp",
        "B",
        "n",
        "alpha",
        "activation_rate_target",
        *ESTIMATE_FIELDS,
    ]
    return pd.read_csv(path, usecols=columns)


def reproduce_d4(
    frame: pd.DataFrame,
    frozen: pd.DataFrame,
    tolerance: float,
) -> dict[str, Any]:
    keys = ["dgp_index", "cell_index", "outer_index"]
    selected = frozen.merge(
        frame[keys].drop_duplicates(),
        on=keys,
        how="inner",
        validate="one_to_one",
    ).rename(
        columns={
            name: f"{name}_frozen"
            for name in ESTIMATE_FIELDS
        }
    )
    merged = frame.merge(
        selected,
        on=keys,
        how="left",
        validate="one_to_one",
        suffixes=("", "_frozen"),
    )

    if len(merged) != len(frame):
        raise RuntimeError("D4 reproduction merge lost rows")
    if merged[[f"{name}_frozen" for name in ESTIMATE_FIELDS]].isna().any().any():
        raise RuntimeError("one or more D5 identities are absent from D4")

    metadata_failures: list[str] = []
    for name in ("dgp", "B", "n", "alpha", "activation_rate_target"):
        left = merged[name]
        right = merged[f"{name}_frozen"]
        if name == "dgp":
            bad = left.astype(str) != right.astype(str)
        else:
            bad = ~np.isclose(
                left.astype(float),
                right.astype(float),
                atol=0.0,
                rtol=0.0,
            )
        if bool(np.any(bad)):
            metadata_failures.append(name)

    errors: dict[str, float] = {}
    for name in ESTIMATE_FIELDS:
        observed = merged[f"quantile_{name}"].astype(float)
        expected = merged[f"{name}_frozen"].astype(float)
        errors[name] = float(np.max(np.abs(observed - expected)))

    maximum = max(errors.values())
    return {
        "passed": (
            not metadata_failures
            and maximum <= tolerance
            and len(merged) == len(frame)
        ),
        "rows_checked": int(len(merged)),
        "maximum_absolute_error": maximum,
        "field_maximum_errors": errors,
        "metadata_failures": metadata_failures,
        "tolerance": tolerance,
    }


def mcse_rms(values: np.ndarray) -> float:
    squared = np.square(values)
    rms = float(np.sqrt(np.mean(squared)))
    if rms == 0.0 or values.size < 2:
        return 0.0
    return float(
        np.std(squared, ddof=1)
        / (math.sqrt(values.size) * 2.0 * rms)
    )


def frequency_mcse(value: float, count: int) -> float:
    return float(math.sqrt(value * (1.0 - value) / count))


def label_ratio(ratio: float) -> str:
    if not math.isfinite(ratio):
        return "undefined"
    if ratio < 0.10:
        return "negligible"
    if ratio < 0.25:
        return "small"
    return "material"


def summarize_metric(
    group: pd.DataFrame,
    metric: str,
    prefix: str,
) -> dict[str, Any]:
    values = group[metric].to_numpy(dtype=float)
    count = values.size
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    rms = float(np.sqrt(np.mean(np.square(values))))
    output = {
        f"{prefix}_mean": mean,
        f"{prefix}_mean_mcse": sd / math.sqrt(count),
        f"{prefix}_median": float(np.median(values)),
        f"{prefix}_sd": sd,
        f"{prefix}_rms": rms,
        f"{prefix}_rms_mcse": mcse_rms(values),
        f"{prefix}_mean_abs": float(np.mean(np.abs(values))),
        f"{prefix}_maximum_abs": float(np.max(np.abs(values))),
    }
    for quantile in (0.01, 0.05, 0.25, 0.75, 0.95, 0.99):
        key = str(quantile).replace(".", "p")
        output[f"{prefix}_q{key}"] = float(np.quantile(values, quantile))
    return output


def summarize_cells(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = frame.groupby(
        ["cell_index", "dgp", "B", "n", "alpha"],
        sort=True,
    )
    for identity, group in grouped:
        cell_index, dgp, B, n, alpha = identity
        row: dict[str, Any] = {
            "cell_index": int(cell_index),
            "dgp": str(dgp),
            "B": int(B),
            "n": int(n),
            "alpha": float(alpha),
            "outer_repetitions": int(len(group)),
        }
        row.update(
            summarize_metric(
                group,
                "delta_pi_bridge",
                "delta_pi_bridge",
            )
        )
        row.update(
            summarize_metric(
                group,
                "delta_tess_bridge",
                "delta_tess_bridge",
            )
        )

        for scale in ("sqrt_n", "sqrt_B", "B"):
            row.update(
                summarize_metric(
                    group,
                    f"{scale}_delta_pi_bridge",
                    f"{scale}_delta_pi_bridge",
                )
            )
            row.update(
                summarize_metric(
                    group,
                    f"{scale}_delta_tess_bridge",
                    f"{scale}_delta_tess_bridge",
                )
            )

        for metric, prefix in (
            ("delta_pi_bridge", "delta_pi"),
            ("delta_tess_bridge", "delta_tess"),
        ):
            equality = float(np.mean(group[metric].to_numpy() == 0.0))
            strict = float(
                np.mean(
                    group[f"{prefix}_strict_sign_reversal"].to_numpy(
                        dtype=bool
                    )
                )
            )
            zero_change = float(
                np.mean(
                    group[f"{prefix}_zero_status_change"].to_numpy(
                        dtype=bool
                    )
                )
            )
            count = len(group)
            row[f"{prefix}_exact_equality_frequency"] = equality
            row[f"{prefix}_exact_equality_mcse"] = frequency_mcse(
                equality,
                count,
            )
            row[f"{prefix}_strict_sign_reversal_frequency"] = strict
            row[f"{prefix}_strict_sign_reversal_mcse"] = frequency_mcse(
                strict,
                count,
            )
            row[f"{prefix}_zero_status_change_frequency"] = zero_change
            row[f"{prefix}_zero_status_change_mcse"] = frequency_mcse(
                zero_change,
                count,
            )

        quantile_pi_sd = float(
            np.std(group["quantile_delta_pi_hat"], ddof=1)
        )
        quantile_tess_sd = float(
            np.std(group["quantile_delta_tess_hat"], ddof=1)
        )
        row["quantile_delta_pi_empirical_sd"] = quantile_pi_sd
        row["quantile_delta_tess_empirical_sd"] = quantile_tess_sd

        pi_rms = float(row["delta_pi_bridge_rms"])
        tess_rms = float(row["delta_tess_bridge_rms"])
        pi_ratio = (
            pi_rms / quantile_pi_sd
            if quantile_pi_sd > 0.0
            else math.nan
        )
        tess_ratio = (
            tess_rms / quantile_tess_sd
            if quantile_tess_sd > 0.0
            else math.nan
        )
        row["delta_pi_bridge_rms_to_d4_sd"] = pi_ratio
        row["delta_tess_bridge_rms_to_d4_sd"] = tess_ratio
        row["delta_pi_bridge_label"] = label_ratio(pi_ratio)
        row["delta_tess_bridge_label"] = label_ratio(tess_ratio)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cell_index").reset_index(drop=True)


def make_boundary_table(config: dict[str, Any]) -> pd.DataFrame:
    rows = []
    seen: set[tuple[int, float]] = set()
    for design in config["designs"]:
        B = int(design["B"])
        for alpha in config["alphas"]:
            key = (B, float(alpha))
            if key in seen:
                continue
            seen.add(key)
            rows.append(boundary_info(*key).to_dict())
    return pd.DataFrame(rows).sort_values(["B", "alpha"]).reset_index(drop=True)


def nonfinite_columns(frame: pd.DataFrame) -> list[str]:
    failures: list[str] = []
    for name in frame.select_dtypes(include=[np.number]).columns:
        if not np.all(np.isfinite(frame[name].to_numpy(dtype=float))):
            failures.append(name)
    return failures


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def dataframe_to_markdown(
    frame: pd.DataFrame,
    columns: list[str] | None = None,
    float_format: str = ".6g",
) -> str:
    # Render a small DataFrame as Markdown without optional dependencies.
    display = frame if columns is None else frame.loc[:, columns]

    def render(value: Any) -> str:
        if pd.isna(value):
            text = ""
        elif isinstance(value, (float, np.floating)):
            text = format(float(value), float_format)
        elif isinstance(value, (bool, np.bool_)):
            text = "true" if bool(value) else "false"
        else:
            text = str(value)
        return text.replace("|", "\\|").replace("\n", "<br>")

    headers = [render(column) for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in display.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(render(value) for value in row) + " |")

    return "\n".join(lines)


def write_adjudication(
    path: Path,
    status: str,
    config: dict[str, Any],
    checks: list[dict[str, Any]],
    cell_summary: pd.DataFrame,
    boundary: pd.DataFrame,
    elapsed: float,
    scientific: bool,
) -> None:
    label = (
        "SCIENTIFIC VALIDATION"
        if scientific
        else "RUNTIME-ONLY SMOKE - NOT SCIENTIFIC EVIDENCE"
    )
    lines = [
        "# D5 Plus-One Bridge: Adjudication",
        "",
        f"**Status: {status}**",
        "",
        f"**Run label: {label}**",
        "",
        "## Design",
        "",
        f"- Cells: {len(cell_summary)}",
        f"- Outer repetitions per cell: {config['outer_repetitions']}",
        f"- Master seed: {config['d4_master_seed']}",
        f"- Elapsed seconds: {elapsed:.3f}",
        "",
        "## Fatal checks",
        "",
    ]
    for item in checks:
        lines.append(
            f"- {'PASS' if item['passed'] else 'FAIL'}: "
            f"{item['check']}"
        )

    lines.extend(
        [
            "",
            "## Exact finite-bank boundaries",
            "",
            dataframe_to_markdown(boundary),
            "",
            "## Bridge summary",
            "",
        ]
    )
    display_columns = [
        "dgp",
        "B",
        "n",
        "alpha",
        "delta_pi_bridge_rms",
        "delta_pi_bridge_rms_to_d4_sd",
        "delta_pi_bridge_label",
        "delta_tess_bridge_rms",
        "delta_tess_bridge_rms_to_d4_sd",
        "delta_tess_bridge_label",
    ]
    lines.append(
        dataframe_to_markdown(
            cell_summary,
            columns=display_columns,
            float_format=".6g",
        )
    )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "PASS concerns implementation integrity and complete reproduction "
            "of the frozen D4 quantile-mode results.",
            "",
            "The negligible/small/material labels are descriptive and do not "
            "determine PASS or FAIL.",
            "",
            "This result concerns the one-candidate-per-branch D4 contrast. "
            "It is not direct evidence for finite multiple-candidate winner "
            "selection.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def create_manifest(
    output_dir: Path,
    config_path: Path,
    elapsed: float,
) -> None:
    records = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name == "D5_VALIDATION_MANIFEST.json":
            continue
        records.append(
            {
                "file": path.name,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "elapsed_seconds": elapsed,
        "files": records,
    }
    write_json(output_dir / "D5_VALIDATION_MANIFEST.json", manifest)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--scientific",
        action="store_true",
        help="require locked scientific configuration",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).expanduser().resolve()
    config = load_json(config_path)
    validate_config(config, scientific=bool(args.scientific))

    start = time.perf_counter()
    parent_checks = verify_parent(config)

    cells = build_cells(config)
    tasks = build_tasks(config, cells)
    print(
        f"D5 tasks: {len(tasks)}; worker processes: {config['n_jobs']}",
        flush=True,
    )
    frame = run_tasks(config, tasks)

    expected_rows = len(cells) * int(config["outer_repetitions"])
    if args.scientific:
        declared_total = int(config["expected_total_outer_datasets"])
        if expected_rows != declared_total:
            raise RuntimeError(
                f"scientific row count mismatch: "
                f"{expected_rows} != {declared_total}"
            )
    frozen = load_frozen_d4()
    reproduction = reproduce_d4(
        frame,
        frozen,
        float(config["reproduction_tolerance"]),
    )

    frame["delta_pi_strict_sign_reversal"] = (
        frame["quantile_delta_pi_hat"]
        * frame["plus_one_delta_pi_hat"]
        < 0.0
    )
    frame["delta_tess_strict_sign_reversal"] = (
        frame["quantile_delta_tess_hat"]
        * frame["plus_one_delta_tess_hat"]
        < 0.0
    )
    frame["delta_pi_zero_status_change"] = (
        (frame["quantile_delta_pi_hat"] == 0.0)
        != (frame["plus_one_delta_pi_hat"] == 0.0)
    )
    frame["delta_tess_zero_status_change"] = (
        (frame["quantile_delta_tess_hat"] == 0.0)
        != (frame["plus_one_delta_tess_hat"] == 0.0)
    )

    numeric_nonfinite = nonfinite_columns(frame)
    duplicate_count = int(
        frame.duplicated(
            ["dgp_index", "cell_index", "outer_index"]
        ).sum()
    )
    activation_threshold_error = float(
        np.max(
            np.abs(
                frame["quantile_c_hat"]
                - frame["plus_one_c_hat"]
            )
        )
    )
    activation_rate_error = float(
        np.max(
            np.abs(
                frame["quantile_activation_rate_hat"]
                - frame["plus_one_activation_rate_hat"]
            )
        )
    )

    boundary = make_boundary_table(config)
    cell_summary = summarize_cells(frame)
    summary_nonfinite = nonfinite_columns(
        cell_summary.drop(
            columns=[
                "delta_pi_bridge_label",
                "delta_tess_bridge_label",
                "dgp",
            ],
            errors="ignore",
        )
    )

    checks = [
        *parent_checks,
        {
            "check": "expected_cell_count",
            "passed": len(cells) == int(config["expected_cell_count"]),
            "observed": len(cells),
            "expected": int(config["expected_cell_count"]),
        },
        {
            "check": "expected_replication_count",
            "passed": len(frame) == expected_rows,
            "observed": len(frame),
            "expected": expected_rows,
        },
        {
            "check": "unique_replication_identity",
            "passed": duplicate_count == 0,
            "duplicate_count": duplicate_count,
        },
        {
            "check": "all_quantile_mode_d4_reproduction",
            **reproduction,
        },
        {
            "check": "common_activation_threshold",
            "passed": activation_threshold_error == 0.0,
            "maximum_absolute_error": activation_threshold_error,
        },
        {
            "check": "common_activation_realization",
            "passed": activation_rate_error == 0.0,
            "maximum_absolute_error": activation_rate_error,
        },
        {
            "check": "finite_replication_outputs",
            "passed": not numeric_nonfinite,
            "nonfinite_columns": numeric_nonfinite,
        },
        {
            "check": "finite_cell_summary",
            "passed": not summary_nonfinite,
            "nonfinite_columns": summary_nonfinite,
        },
        {
            "check": "d4_grid_index_gap_one",
            "passed": bool(
                np.all(boundary["index_gap"].to_numpy(dtype=float) == 1.0)
            ),
        },
    ]

    status = (
        "PASS"
        if all(bool(item["passed"]) for item in checks)
        else "FAIL"
    )

    output_dir = D5 / str(config["output_subdirectory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    frame.to_csv(
        output_dir / "D5_BRIDGE_REPLICATIONS.csv.gz",
        index=False,
        compression={
            "method": "gzip",
            "compresslevel": 9,
            "mtime": 0,
        },
    )
    cell_summary.to_csv(
        output_dir / "D5_BRIDGE_CELL_SUMMARY.csv",
        index=False,
    )
    boundary.to_csv(
        output_dir / "D5_BOUNDARY_TABLE.csv",
        index=False,
    )
    write_json(
        output_dir / "D5_VALIDATION_CHECKS.json",
        checks,
    )

    elapsed = time.perf_counter() - start
    summary = {
        "study_id": config["study_id"],
        "status": status,
        "scientific": bool(args.scientific),
        "cell_count": len(cells),
        "replication_count": len(frame),
        "elapsed_seconds": elapsed,
        "maximum_d4_reproduction_error": reproduction[
            "maximum_absolute_error"
        ],
        "maximum_delta_pi_bridge_ratio": float(
            np.nanmax(
                cell_summary[
                    "delta_pi_bridge_rms_to_d4_sd"
                ].to_numpy(dtype=float)
            )
        ),
        "maximum_delta_tess_bridge_ratio": float(
            np.nanmax(
                cell_summary[
                    "delta_tess_bridge_rms_to_d4_sd"
                ].to_numpy(dtype=float)
            )
        ),
    }
    write_json(
        output_dir / "D5_VALIDATION_SUMMARY.json",
        summary,
    )
    write_adjudication(
        output_dir / "D5_VALIDATION_ADJUDICATION.md",
        status,
        config,
        checks,
        cell_summary,
        boundary,
        elapsed,
        bool(args.scientific),
    )
    create_manifest(output_dir, config_path, elapsed)

    print("D5 validation complete")
    print(f"Status: {status}")
    print(f"Cells: {len(cells)}")
    print(f"Replications: {len(frame)}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Output directory: {output_dir}")

    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
