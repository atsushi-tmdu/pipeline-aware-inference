#!/usr/bin/env python3
"""Reproduce the first aggregate Phase 3C tail-ESS pilot.

Expected repository inputs
--------------------------
simulations/phase3c/frozen_results/phase3c_type1_error.csv
simulations/phase3c/frozen_results/candidate_dependence_summary.csv

The script compares:
1. eigenvalue participation-ratio effective candidate count; and
2. alpha=0.05 Šidák-equivalent tail ESS derived from the naive post-search
   global-null rejection rate.

Run from the repository root:

    python simulations/ess/pilot_phase3c_aggregate.py --repo-root .

Outputs are written to simulations/ess/pilot_outputs/.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ess_estimators import estimate_tail_ess


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Defaults to simulations/ess/pilot_outputs under repo-root.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    frozen = repo_root / "simulations" / "phase3c" / "frozen_results"
    type1_path = frozen / "phase3c_type1_error.csv"
    dependence_path = frozen / "candidate_dependence_summary.csv"
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else repo_root / "simulations" / "ess" / "pilot_outputs"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    type1 = read_csv(type1_path)
    dependence = read_csv(dependence_path)
    pr_by_key = {
        (row["library"], int(row["pool_size"])): float(row["effective_candidate_count"])
        for row in dependence
    }

    output_rows: list[dict[str, object]] = []
    for row in type1:
        if row["method"] != "naive_empirical":
            continue
        if float(row["target_auc"]) != 0.5:
            continue

        repetitions = int(row["n"])
        rejection_rate = float(row["rejection_rate"])
        rejections = round(repetitions * rejection_rate)
        estimate = estimate_tail_ess(
            rejections=rejections,
            repetitions=repetitions,
            local_alpha=args.alpha,
        )
        key = (row["library"], int(row["pool_size"]))
        pr = pr_by_key[key]

        output_rows.append(
            {
                "library": key[0],
                "nominal_candidate_count": key[1],
                "local_alpha": args.alpha,
                "null_repetitions": repetitions,
                "naive_rejections": rejections,
                "naive_rejection_rate": estimate.rejection_probability,
                "tail_ess": estimate.ess,
                "tail_ess_low_95": estimate.ess_low,
                "tail_ess_high_95": estimate.ess_high,
                "participation_ratio_count": pr,
                "tail_minus_participation_ratio": estimate.ess - pr,
                "tail_to_participation_ratio": estimate.ess / pr,
            }
        )

    output_rows.sort(key=lambda x: (str(x["library"]), int(x["nominal_candidate_count"])))
    output_csv = output_dir / "phase3c_tail_ess_alpha005.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print(f"Wrote {output_csv}")
        print("matplotlib not installed; skipped figure.")
        return

    labels = [
        f'{row["library"]}\nK={row["nominal_candidate_count"]}'
        for row in output_rows
    ]
    x = list(range(len(output_rows)))
    tail = [float(row["tail_ess"]) for row in output_rows]
    tail_low = [float(row["tail_ess_low_95"]) for row in output_rows]
    tail_high = [float(row["tail_ess_high_95"]) for row in output_rows]
    pr = [float(row["participation_ratio_count"]) for row in output_rows]
    lower_error = [m - lo for m, lo in zip(tail, tail_low)]
    upper_error = [hi - m for m, hi in zip(tail, tail_high)]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(
        x,
        tail,
        yerr=[lower_error, upper_error],
        marker="o",
        linestyle="-",
        capsize=4,
        label="Tail ESS at alpha=0.05",
    )
    ax.plot(
        x,
        pr,
        marker="s",
        linestyle="--",
        label="Participation-ratio count",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Effective search size")
    ax.set_title("Phase 3C: structural dimension versus tail search multiplicity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "phase3c_tail_ess_alpha005.png", dpi=300)
    fig.savefig(output_dir / "phase3c_tail_ess_alpha005.svg")
    plt.close(fig)

    print(f"Wrote {output_csv}")
    print(f"Wrote figures to {output_dir}")


if __name__ == "__main__":
    main()
