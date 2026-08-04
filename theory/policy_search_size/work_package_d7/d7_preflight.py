from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from d7_preflight_core import run_preflight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the D7 maximum-trigger runtime-only preflight."
    )
    parser.add_argument("--unconditional-size", type=int, default=1048576)
    parser.add_argument("--conditional-size", type=int, default=262144)
    parser.add_argument("--seed", type=int, default=20270107)
    parser.add_argument("--relative-step", type=float, default=0.0125)
    parser.add_argument("--batches", type=int, default=32)
    parser.add_argument("--absolute-tolerance", type=float, default=0.003)
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


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# D7 Maximum-Trigger Preflight",
        "",
        f"**Status: {result['status']}**",
        "",
        "Runtime-only mathematical and implementation debugging.",
        "Not scientific evidence and not a numerical lock.",
        "",
        "## Thresholds",
        "",
        (
            f"- trigger: {result['thresholds']['trigger']:.8f}"
        ),
        (
            "- minimum base-candidate/trigger separation: "
            f"{result['thresholds']['minimum_absolute_separation']:.8f}"
        ),
        "",
        "## Candidate derivatives",
        "",
        "| Candidate | Finite difference | Boundary | Difference | Tolerance | Pass |",
        "|---:|---:|---:|---:|---:|:---:|",
    ]
    for item in result["candidate_derivative_checks"]:
        lines.append(
            "| {candidate} | {finite_difference:.8f} | "
            "{boundary_derivative:.8f} | {difference:.8f} | "
            "{tolerance:.8f} | {status} |".format(
                candidate=item["candidate"],
                finite_difference=item["finite_difference"],
                boundary_derivative=item["boundary_derivative"],
                difference=item["difference"],
                tolerance=item["tolerance"],
                status="PASS" if item["pass"] else "FAIL",
            )
        )

    trigger = result["trigger_derivative_check"]
    density = result["maximum_density_check"]
    kink = result["coincidence_kink_check"]
    lines.extend(
        [
            "",
            "## Trigger derivative",
            "",
            (
                f"- finite difference: "
                f"{trigger['finite_difference']:.8f}"
            ),
            (
                f"- boundary derivative: "
                f"{trigger['boundary_derivative']:.8f}"
            ),
            f"- difference: {trigger['difference']:.8f}",
            f"- tolerance: {trigger['tolerance']:.8f}",
            f"- pass: {trigger['pass']}",
            "",
            "## Maximum-density decomposition",
            "",
            (
                "- winner-region decomposition: "
                f"{density['winner_region_decomposition']:.8f}"
            ),
            (
                "- CDF finite difference: "
                f"{density['cdf_finite_difference']:.8f}"
            ),
            f"- pass: {density['pass']}",
            "",
            "## Coincidence kink",
            "",
            (
                "- empirical nonadditivity: "
                f"{kink['empirical_nonadditivity']:.8f}"
            ),
            f"- boundary kappa: {kink['boundary_kappa']:.8f}",
            f"- difference: {kink['difference']:.8f}",
            f"- tolerance: {kink['tolerance']:.8f}",
            f"- pass: {kink['pass']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_preflight(
        unconditional_size=args.unconditional_size,
        conditional_size=args.conditional_size,
        seed=args.seed,
        relative_step=args.relative_step,
        batches=args.batches,
        absolute_tolerance=args.absolute_tolerance,
        standard_error_multiplier=args.standard_error_multiplier,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "D7_PREFLIGHT_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "D7_PREFLIGHT_REPORT.md").write_text(
        render_report(result) + "\n",
        encoding="utf-8",
    )

    print("=" * 76)
    print("D7 maximum-trigger preflight")
    print("=" * 76)
    print(f"Status: {result['status']}")
    print(
        "Minimum separation: "
        f"{result['thresholds']['minimum_absolute_separation']:.8f}"
    )
    for item in result["candidate_derivative_checks"]:
        print(
            "Candidate {candidate}: finite={finite_difference:.8f}, "
            "boundary={boundary_derivative:.8f}, "
            "difference={difference:.8f}, tolerance={tolerance:.8f}, "
            "{status}".format(
                candidate=item["candidate"],
                finite_difference=item["finite_difference"],
                boundary_derivative=item["boundary_derivative"],
                difference=item["difference"],
                tolerance=item["tolerance"],
                status="PASS" if item["pass"] else "FAIL",
            )
        )
    trigger = result["trigger_derivative_check"]
    print(
        "Trigger: "
        f"finite={trigger['finite_difference']:.8f}, "
        f"boundary={trigger['boundary_derivative']:.8f}, "
        f"difference={trigger['difference']:.8f}, "
        f"tolerance={trigger['tolerance']:.8f}, "
        f"{'PASS' if trigger['pass'] else 'FAIL'}"
    )
    density = result["maximum_density_check"]
    print(
        "Maximum density: "
        f"decomposition={density['winner_region_decomposition']:.8f}, "
        f"CDF-FD={density['cdf_finite_difference']:.8f}, "
        f"{'PASS' if density['pass'] else 'FAIL'}"
    )
    kink = result["coincidence_kink_check"]
    print(
        "Coincidence kink: "
        f"empirical={kink['empirical_nonadditivity']:.8f}, "
        f"kappa={kink['boundary_kappa']:.8f}, "
        f"difference={kink['difference']:.8f}, "
        f"tolerance={kink['tolerance']:.8f}, "
        f"{'PASS' if kink['pass'] else 'FAIL'}"
    )
    print(f"Output directory: {args.output_dir.resolve()}")
    print("Scientific evidence: NO (runtime-only preflight)")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
