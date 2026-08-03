from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from d6_preflight_core import run_derivative_preflight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the D6 runtime-only winner-region derivative preflight."
        )
    )
    parser.add_argument("--unconditional-size", type=int, default=524288)
    parser.add_argument("--conditional-size", type=int, default=131072)
    parser.add_argument("--seed", type=int, default=20261203)
    parser.add_argument("--relative-step", type=float, default=0.015)
    parser.add_argument("--batches", type=int, default=32)
    parser.add_argument("--absolute-tolerance", type=float, default=0.0025)
    parser.add_argument(
        "--standard-error-multiplier",
        type=float,
        default=4.0,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("preflight_output"),
    )
    return parser.parse_args()


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# D6 winner-region derivative preflight",
        "",
        f"**Status: {result['status']}**",
        "",
        "This is runtime-only mathematical and implementation debugging.",
        "It is not scientific evidence and does not lock the D6 design.",
        "",
        "## Benchmark",
        "",
        (
            f"- Delta_pi: "
            f"{result['population_benchmark']['delta_pi']:.8f}"
        ),
        (
            f"- Base rejection probability: "
            f"{result['population_benchmark']['e0']:.8f}"
        ),
        (
            f"- Incremental rejection probability: "
            f"{result['population_benchmark']['mu']:.8f}"
        ),
        "",
        "## Candidate-boundary checks",
        "",
        "| Candidate | Finite difference | Conditional boundary | Difference | Tolerance | Pass |",
        "|---:|---:|---:|---:|---:|:---:|",
    ]
    for item in result["candidate_derivative_checks"]:
        lines.append(
            "| {candidate} | {finite_difference:.8f} | "
            "{conditional_boundary:.8f} | {difference:.8f} | "
            "{tolerance:.8f} | {status} |".format(
                candidate=item["candidate"],
                finite_difference=item["finite_difference"],
                conditional_boundary=item["conditional_boundary"],
                difference=item["difference"],
                tolerance=item["tolerance"],
                status="PASS" if item["pass"] else "FAIL",
            )
        )

    activation = result["activation_derivative_check"]
    lines.extend(
        [
            "",
            "## Activation-boundary check",
            "",
            (
                f"- Finite difference: "
                f"{activation['finite_difference']:.8f}"
            ),
            (
                f"- Conditional boundary: "
                f"{activation['conditional_boundary']:.8f}"
            ),
            f"- Difference: {activation['difference']:.8f}",
            f"- Tolerance: {activation['tolerance']:.8f}",
            f"- Pass: {activation['pass']}",
            "",
            "## Guardrails",
            "",
            f"- Observed winner ties: {result['observed_winner_ties']}",
            "- Candidate dimension is fixed and finite.",
            "- Maximum-score activation, deterministic ties, and failed fits remain excluded.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_derivative_preflight(
        unconditional_size=args.unconditional_size,
        conditional_size=args.conditional_size,
        seed=args.seed,
        relative_step=args.relative_step,
        batches=args.batches,
        absolute_tolerance=args.absolute_tolerance,
        standard_error_multiplier=args.standard_error_multiplier,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "D6_PREFLIGHT_RESULTS.json"
    markdown_path = args.output_dir / "D6_PREFLIGHT_REPORT.md"
    json_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(
        render_markdown(result),
        encoding="utf-8",
    )

    print("=" * 72)
    print("D6 winner-region derivative preflight")
    print("=" * 72)
    print(f"Status: {result['status']}")
    print(
        "Delta_pi: "
        f"{result['population_benchmark']['delta_pi']:.8f}"
    )
    for item in result["candidate_derivative_checks"]:
        print(
            "Candidate {candidate}: finite={finite_difference:.8f}, "
            "boundary={conditional_boundary:.8f}, "
            "difference={difference:.8f}, tolerance={tolerance:.8f}, "
            "{status}".format(
                candidate=item["candidate"],
                finite_difference=item["finite_difference"],
                conditional_boundary=item["conditional_boundary"],
                difference=item["difference"],
                tolerance=item["tolerance"],
                status="PASS" if item["pass"] else "FAIL",
            )
        )
    activation = result["activation_derivative_check"]
    print(
        "Activation: "
        f"finite={activation['finite_difference']:.8f}, "
        f"boundary={activation['conditional_boundary']:.8f}, "
        f"difference={activation['difference']:.8f}, "
        f"tolerance={activation['tolerance']:.8f}, "
        f"{'PASS' if activation['pass'] else 'FAIL'}"
    )
    print(f"Output directory: {args.output_dir.resolve()}")
    print("Scientific evidence: NO (runtime-only preflight)")

    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
