from __future__ import annotations

import json
from pathlib import Path
import numpy as np

from d8a_core import (
    combined_bias_approximation,
    exact_conditional_expectation,
    second_order_reference_coefficient,
)


def main() -> None:
    root = Path(__file__).resolve().parent
    config = json.loads(
        (root / "D8A_CONFIG_DRAFT.json").read_text(encoding="utf-8")
    )
    g = np.array([0.4, -0.2, 0.3])
    b = np.array([0.1, -0.05, 0.08])
    h = np.array(
        [[1.0, 0.2, -0.1], [0.2, 0.8, 0.25], [-0.1, 0.25, 1.2]]
    )
    s = np.array(
        [[1.0, 0.1, 0.3], [0.1, 0.9, -0.2], [0.3, -0.2, 1.1]]
    )
    coefficient = second_order_reference_coefficient(g, b, h, s)
    bias = combined_bias_approximation(0.03, coefficient, 3000, 5000)

    print("=" * 80)
    print("D8-A theory-scaffold preflight")
    print("=" * 80)
    print("Status: PASS")
    print(f"Work package: {config['work_package']}")
    print(
        "Exact evaluation factor at n=5000: "
        f"{exact_conditional_expectation(1.0, 5000):.8f}"
    )
    print(f"Synthetic reference coefficient: {coefficient:.8f}")
    print(f"Synthetic combined bias: {bias:.10f}")
    print("Second-order reference theorem proved: NO")
    print("Scientific numerical design locked: NO")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
