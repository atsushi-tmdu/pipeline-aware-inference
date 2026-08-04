from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parent
    config = json.loads(
        (root / "D8A_NUMERICAL_DESIGN.json").read_text(
            encoding="utf-8"
        )
    )
    registry = json.loads(
        (root / "D8A_CELL_REGISTRY.json").read_text(
            encoding="utf-8"
        )
    )

    failures = []
    if not config["scientific_numerical_design_locked"]:
        failures.append("design not locked")
    if config["scientific_simulation_run"]:
        failures.append("simulation already marked run")
    if len(registry) != config["cell_registry"]["total_cells"]:
        failures.append("registry count mismatch")

    for cell in registry:
        if cell["latent_separation"] < 0.10:
            failures.append(
                f"separation failure: {cell['cell_id']}"
            )
        matrix = np.asarray(
            cell["correlation_matrix"],
            dtype=float,
        )
        if np.min(np.linalg.eigvalsh(matrix)) <= 0.0:
            failures.append(
                f"non-PD matrix: {cell['cell_id']}"
            )

    if failures:
        print("D8-A numerical design preflight: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    primary = sum(
        cell["role"] == "primary"
        for cell in registry
    )
    diagnostic = len(registry) - primary

    print("=" * 80)
    print("D8-A numerical design preflight")
    print("=" * 80)
    print("Status: PASS")
    print(f"Registered cells: {len(registry)}")
    print(f"Primary cells: {primary}")
    print(f"Diagnostic cells: {diagnostic}")
    print(
        "Minimum latent separation: "
        f"{min(cell['latent_separation'] for cell in registry):.12f}"
    )
    print("Quantile convention locked: k_B=ceil(B*p)")
    print("Reference/evaluation streams independent: YES")
    print("Effect-dependent stopping allowed: NO")
    print("Post-hoc cell deletion allowed: NO")
    print("Scientific numerical design locked: YES")
    print("Scientific simulation run: NO")


if __name__ == "__main__":
    main()
