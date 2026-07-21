#!/usr/bin/env python3
"""Post hoc SUPPORT2 restricted-permutation sensitivity analysis.

This script repeats the seven-algorithm model search while permuting the
outcome within diagnostic group, separately in the frozen training and
model-selection splits. Participant-level SUPPORT2 data are not distributed
with the repository; supply the frozen Phase 4B and Phase 4C archives created
by the companion scripts.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

PHASE4C_SCRIPT = Path(__file__).resolve().parents[1] / "support2_phase4c_locked_search.py"


def load_phase4c_module():
    spec = importlib.util.spec_from_file_location("p4c", PHASE4C_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {PHASE4C_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_archive(archive: Path, parent: Path) -> Path:
    target = parent / archive.stem
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target)
    candidates = [p for p in target.iterdir() if p.is_dir()]
    return candidates[0] if len(candidates) == 1 else target


def restricted_permute(y: np.ndarray, groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = np.asarray(y).copy()
    for group in pd.unique(groups):
        idx = np.flatnonzero(groups == group)
        out[idx] = rng.permutation(out[idx])
    return out


def one(rep: int, seed: int, x_train, y_train, group_train, x_selection, y_selection, group_selection, max_fpr: float, p4c):
    rng = np.random.default_rng(seed)
    permuted_train = restricted_permute(y_train, group_train, rng)
    permuted_selection = restricted_permute(y_selection, group_selection, rng)
    rows = p4c.fit_all_models(
        x_train,
        permuted_train,
        x_selection,
        permuted_selection,
        seed,
        max_fpr,
    )
    frame = pd.DataFrame(rows)
    maxima = {"replication": rep, "seed": seed}
    for metric in p4c.METRICS:
        maxima[metric] = float(pd.to_numeric(frame[metric], errors="coerce").max())
    for row in rows:
        row["replication"] = rep
        row["seed"] = seed
    return maxima, rows


def empirical_p(observed: float, reference) -> float:
    ref = np.asarray(reference, dtype=float)
    ref = ref[np.isfinite(ref)]
    return (1 + int(np.sum(ref >= observed))) / (len(ref) + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-zip", type=Path, required=True, help="Frozen Phase 4B archive.")
    parser.add_argument("--phase4c-zip", type=Path, required=True, help="Completed Phase 4C archive containing observed_selection_model_metrics.csv.")
    parser.add_argument("--n", type=int, default=1000, help="Restricted null repetitions.")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--parallel-backend",
        choices=("loky", "threading"),
        default="loky",
        help="Joblib backend; threading is useful for low-memory smoke tests.",
    )
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument("--output-dir", type=Path, default=Path("restricted_sensitivity_output"))
    args = parser.parse_args()

    for path in (args.frozen_zip, args.phase4c_zip):
        if not path.exists():
            parser.error(f"Archive not found: {path}")

    p4c = load_phase4c_module()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="support2_restricted_") as tmp:
        tmp_path = Path(tmp)
        frozen_dir = extract_archive(args.frozen_zip, tmp_path / "frozen")
        phase4c_dir = extract_archive(args.phase4c_zip, tmp_path / "phase4c")
        dataset_path = next(frozen_dir.rglob("analysis_dataset_primary.csv"))
        plan_path = next(frozen_dir.rglob("analysis_plan.json"))
        observed_path = next(phase4c_dir.rglob("observed_selection_model_metrics.csv"))

        data = pd.read_csv(dataset_path)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        p4c.validate_frozen_design(data, plan)
        train = data.query("split == 'train'").copy()
        selection = data.query("split == 'selection'").copy()
        predictors = plan["primary_predictors"]
        preprocessor = p4c.build_preprocessor(plan)
        x_train = np.asarray(preprocessor.fit_transform(train[predictors]))
        x_selection = np.asarray(preprocessor.transform(selection[predictors]))
        y_train = train.hospdead.to_numpy(int)
        y_selection = selection.hospdead.to_numpy(int)
        group_train = train.dzgroup.astype(str).to_numpy()
        group_selection = selection.dzgroup.astype(str).to_numpy()

        sequence = np.random.SeedSequence(args.seed)
        seeds = [int(x.generate_state(1, dtype=np.uint32)[0]) for x in sequence.spawn(args.n)]
        start = time.time()
        results = Parallel(
            n_jobs=args.jobs,
            verbose=10,
            batch_size=1,
            backend=args.parallel_backend,
            max_nbytes=None if args.parallel_backend == "threading" else "10M",
        )(
            delayed(one)(
                i + 1,
                seeds[i],
                x_train,
                y_train,
                group_train,
                x_selection,
                y_selection,
                group_selection,
                0.10,
                p4c,
            )
            for i in range(args.n)
        )

        maxima = pd.DataFrame([result[0] for result in results])
        maxima.to_csv(args.output_dir / "restricted_null_maxima.csv", index=False)
        model_rows = []
        for _, rows in results:
            model_rows.extend(rows)
        pd.DataFrame(model_rows).to_csv(args.output_dir / "restricted_null_model_metrics.csv", index=False)

        observed = pd.read_csv(observed_path)
        labels = {
            "roc_auc": "AUROC",
            "average_precision": "Average precision",
            "pauc_fpr_0_10": "Standardized partial AUROC (FPR <= 0.10)",
        }
        summary = []
        for metric in p4c.METRICS:
            observed_maximum = float(pd.to_numeric(observed[metric], errors="coerce").max())
            reference = maxima[metric].to_numpy(float)
            summary.append(
                {
                    "metric": metric,
                    "metric_label": labels[metric],
                    "null_mechanism": "Restricted outcome permutation within diagnostic group, separately in frozen training and model-selection splits",
                    "null_repetitions": args.n,
                    "observed_selected_maximum": observed_maximum,
                    "null_max_mean": float(np.mean(reference)),
                    "null_max_q95": float(np.quantile(reference, 0.95)),
                    "null_max_q99": float(np.quantile(reference, 0.99)),
                    "null_max_maximum": float(np.max(reference)),
                    "exceedances": int(np.sum(reference >= observed_maximum)),
                    "pipeline_aware_p_value": float(empirical_p(observed_maximum, reference)),
                }
            )
        summary_frame = pd.DataFrame(summary)
        summary_frame.to_csv(args.output_dir / "restricted_sensitivity_summary.csv", index=False)
        metadata = {
            "analysis": "Post hoc SUPPORT2 conditional-null sensitivity",
            "master_seed": args.seed,
            "null_repetitions": args.n,
            "n_jobs": args.jobs,
            "parallel_backend": args.parallel_backend,
            "restriction": "Outcome labels permuted within diagnostic group, separately within frozen training and model-selection splits.",
            "conditioning": "Frozen data-role assignment and predictor matrices.",
            "elapsed_seconds": time.time() - start,
            "train_rows": len(train),
            "selection_rows": len(selection),
            "train_events": int(y_train.sum()),
            "selection_events": int(y_selection.sum()),
            "diagnostic_groups_train": int(pd.Series(group_train).nunique()),
            "diagnostic_groups_selection": int(pd.Series(group_selection).nunique()),
        }
        (args.output_dir / "analysis_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(summary_frame.to_string(index=False))


if __name__ == "__main__":
    main()
