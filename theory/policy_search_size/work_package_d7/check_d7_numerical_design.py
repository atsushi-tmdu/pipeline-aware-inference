from __future__ import annotations

import json
from pathlib import Path

from d7_numerical_design import validate_design


def main() -> None:
    root = Path(__file__).resolve().parent
    config = json.loads(
        (root / "D7_NUMERICAL_CONFIG.json").read_text(
            encoding="utf-8"
        )
    )
    specifications = json.loads(
        (root / "D7_DGP_SPECIFICATIONS.json").read_text(
            encoding="utf-8"
        )
    )
    criteria = json.loads(
        (root / "D7_SCIENTIFIC_CRITERIA.json").read_text(
            encoding="utf-8"
        )
    )
    result = validate_design(config, specifications, criteria)

    print("=" * 80)
    print("D7 prospective numerical-design check")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Main cells: {len(result['main_cells'])}")
    print(
        "Main replication rows: "
        f"{sum(cell['outer_repetitions'] for cell in result['main_cells'])}"
    )
    print(f"Bootstrap cells: {len(result['bootstrap_cells'])}")
    print(
        "Bootstrap outer rows: "
        f"{sum(cell['outer_datasets'] for cell in result['bootstrap_cells'])}"
    )
    print(
        "Minimum standardized main separation: "
        f"{result['minimum_standardized_main_threshold_separation']:.8f}"
    )
    print(
        "Near-coincidence diagnostic cells: "
        f"{len(result['near_coincidence_cells'])}"
    )
    print("Exact-coincidence cells: 1")
    print("Scientific simulation run: NO")
    print("Numerical lock created: NO")

    if result["status"] != "PASS":
        failed = [
            name
            for name, value in result["checks"].items()
            if not value
        ]
        print(f"Failed checks: {failed}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
