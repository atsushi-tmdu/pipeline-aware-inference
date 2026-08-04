from __future__ import annotations

import argparse
import json
from pathlib import Path

from d7_validation_core import run_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D7 continuous maximum-trigger validation."
    )
    parser.add_argument(
        "--mode",
        choices=("smoke", "full"),
        required=True,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent
    result = run_validation(
        root,
        mode=args.mode,
        output_dir=args.output_dir,
    )
    summary = result["summary"]

    print("=" * 80)
    print(
        "D7 continuous maximum-trigger "
        f"{args.mode} validation"
    )
    print("=" * 80)
    print(f"Status: {summary['status']}")
    print(f"Scientific evidence: {summary['scientific_evidence']}")
    print(f"Main cells: {summary['main_cells']}")
    print(
        "Main replication rows: "
        f"{summary['main_replication_rows']}"
    )
    print(f"Bootstrap cells: {summary['bootstrap_cells']}")
    print(
        "Bootstrap outer rows: "
        f"{summary['bootstrap_outer_rows']}"
    )
    print(f"Diagnostic cells: {summary['diagnostic_cells']}")
    print(
        "Diagnostic replication rows: "
        f"{summary['diagnostic_replication_rows']}"
    )
    print(f"Elapsed seconds: {summary['elapsed_seconds']:.3f}")
    print(f"Output directory: {result['output_dir']}")

    if summary["status"] != "PASS":
        failed_fatal = [
            key
            for key, value in result["adjudication"][
                "fatal_checks"
            ].items()
            if not value
        ]
        failed_scientific = [
            key
            for key, value in result["adjudication"][
                "scientific_checks"
            ].items()
            if not value
        ]
        print(f"Failed fatal checks: {failed_fatal}")
        print(f"Failed scientific checks: {failed_scientific}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
