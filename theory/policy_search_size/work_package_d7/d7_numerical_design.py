from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class GaussianDGP:
    name: str
    mean: FloatArray
    covariance: FloatArray
    base_pool: tuple[int, ...]
    full_pool: tuple[int, ...]


def _as_float_array(values: Any) -> FloatArray:
    return np.asarray(values, dtype=float)


def build_dgp(name: str, specification: dict[str, Any]) -> GaussianDGP:
    construction = specification["construction"]
    mean = _as_float_array(specification["mean"])

    if construction == "explicit_covariance":
        covariance = _as_float_array(specification["covariance"])
    elif construction == "latent_factor":
        loadings = np.column_stack(
            [
                _as_float_array(values)
                for values in specification["factor_loadings"].values()
            ]
        )
        loading_variance = np.sum(loadings**2, axis=1)
        residual_variance = 1.0 - loading_variance
        if np.any(residual_variance <= 0.0):
            raise ValueError(
                f"{name}: latent-factor residual variance is not positive"
            )
        covariance = (
            loadings @ loadings.T
            + np.diag(residual_variance)
        )
    else:
        raise ValueError(f"{name}: unknown construction {construction}")

    base_pool = tuple(int(value) for value in specification["base_pool"])
    full_pool = tuple(int(value) for value in specification["full_pool"])

    dgp = GaussianDGP(
        name=name,
        mean=mean,
        covariance=covariance,
        base_pool=base_pool,
        full_pool=full_pool,
    )
    validate_dgp(dgp)
    return dgp


def validate_dgp(dgp: GaussianDGP) -> None:
    dimension = len(dgp.mean)
    if dgp.covariance.shape != (dimension, dimension):
        raise ValueError(f"{dgp.name}: covariance shape mismatch")
    if not np.allclose(dgp.covariance, dgp.covariance.T):
        raise ValueError(f"{dgp.name}: covariance is not symmetric")
    if float(np.min(np.linalg.eigvalsh(dgp.covariance))) <= 0.0:
        raise ValueError(f"{dgp.name}: covariance is not positive definite")
    if not dgp.base_pool:
        raise ValueError(f"{dgp.name}: base pool is empty")
    if not set(dgp.base_pool).issubset(dgp.full_pool):
        raise ValueError(f"{dgp.name}: pools are not nested")
    if max(dgp.full_pool) >= dimension:
        raise ValueError(f"{dgp.name}: full-pool index is out of range")


def marginal_standard_deviations(dgp: GaussianDGP) -> FloatArray:
    return np.sqrt(np.diag(dgp.covariance))


def candidate_thresholds(dgp: GaussianDGP, alpha: float) -> FloatArray:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    return (
        dgp.mean
        + marginal_standard_deviations(dgp)
        * norm.ppf(1.0 - alpha)
    )


def trigger_boundary(
    dgp: GaussianDGP,
    alpha: float,
    regime_name: str,
    regime: dict[str, Any],
) -> dict[str, float]:
    thresholds = candidate_thresholds(dgp, alpha)
    base = np.asarray(dgp.base_pool, dtype=np.int64)
    base_thresholds = thresholds[base]
    base_sds = marginal_standard_deviations(dgp)[base]
    scale = float(np.median(base_sds))
    offset = float(regime["offset"])

    if regime_name == "below_all_base_thresholds":
        boundary = float(np.min(base_thresholds) - offset * scale)
        signed_gaps = base_thresholds - boundary
        ordering_pass = bool(np.all(signed_gaps > 0.0))
    elif regime_name == "above_all_base_thresholds":
        boundary = float(np.max(base_thresholds) + offset * scale)
        signed_gaps = base_thresholds - boundary
        ordering_pass = bool(np.all(signed_gaps < 0.0))
    else:
        raise ValueError(f"unknown trigger regime: {regime_name}")

    standardized = np.abs(signed_gaps) / base_sds
    return {
        "trigger_boundary": boundary,
        "minimum_absolute_gap": float(np.min(np.abs(signed_gaps))),
        "minimum_standardized_gap": float(np.min(standardized)),
        "ordering_pass": ordering_pass,
    }


def enumerate_main_cells(
    config: dict[str, Any],
    dgp_order: list[str],
) -> list[dict[str, Any]]:
    cells = []
    index = 0
    for dgp, alpha, regime, design in product(
        dgp_order,
        config["alpha_grid"],
        config["trigger_regimes"],
        config["main_designs"],
    ):
        cells.append(
            {
                "cell_index": index,
                "dgp": dgp,
                "alpha": float(alpha),
                "trigger_regime": regime,
                "reference_size": int(design["reference_size"]),
                "evaluation_size": int(design["evaluation_size"]),
                "outer_repetitions": int(
                    config["main_outer_repetitions_per_cell"]
                ),
            }
        )
        index += 1
    return cells


def enumerate_bootstrap_cells(
    config: dict[str, Any],
    dgp_order: list[str],
) -> list[dict[str, Any]]:
    design = config["bootstrap_design"]["main_design"]
    cells = []
    index = 0
    for dgp, alpha, regime in product(
        dgp_order,
        config["alpha_grid"],
        config["trigger_regimes"],
    ):
        cells.append(
            {
                "bootstrap_cell_index": index,
                "dgp": dgp,
                "alpha": float(alpha),
                "trigger_regime": regime,
                "reference_size": int(design["reference_size"]),
                "evaluation_size": int(design["evaluation_size"]),
                "outer_datasets": int(
                    config["bootstrap_design"][
                        "outer_datasets_per_cell"
                    ]
                ),
                "resamples": int(
                    config["bootstrap_design"][
                        "resamples_per_outer_dataset"
                    ]
                ),
            }
        )
        index += 1
    return cells


def enumerate_near_coincidence_cells(
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    diagnostic = config["near_coincidence_diagnostic"]
    return [
        {
            "diagnostic_cell_index": index,
            "dgp": diagnostic["dgp"],
            "alpha": float(diagnostic["alpha"]),
            "anchor_candidate": int(diagnostic["anchor_candidate"]),
            "offset_in_anchor_sd": float(offset),
            "reference_size": int(diagnostic["reference_size"]),
            "evaluation_size": int(diagnostic["evaluation_size"]),
            "outer_repetitions": int(
                diagnostic["outer_repetitions_per_cell"]
            ),
            "adjudicative": False,
        }
        for index, offset in enumerate(
            diagnostic["offsets_in_anchor_sd"]
        )
    ]


def validate_design(
    config: dict[str, Any],
    dgp_specifications: dict[str, Any],
    criteria: dict[str, Any],
) -> dict[str, Any]:
    dgp_order = list(dgp_specifications["dgp_order"])
    built = {
        name: build_dgp(
            name,
            dgp_specifications["dgps"][name],
        )
        for name in dgp_order
    }

    main_cells = enumerate_main_cells(config, dgp_order)
    bootstrap_cells = enumerate_bootstrap_cells(config, dgp_order)
    near_cells = enumerate_near_coincidence_cells(config)

    separation_rows = []
    for name, dgp in built.items():
        for alpha in config["alpha_grid"]:
            for regime_name, regime in config[
                "trigger_regimes"
            ].items():
                result = trigger_boundary(
                    dgp,
                    float(alpha),
                    regime_name,
                    regime,
                )
                separation_rows.append(
                    {
                        "dgp": name,
                        "alpha": float(alpha),
                        "trigger_regime": regime_name,
                        **result,
                    }
                )

    minimum_separation = min(
        row["minimum_standardized_gap"]
        for row in separation_rows
    )
    expected = config["expected_counts"]
    fatal = criteria["fatal_implementation_checks"]

    checks = {
        "dgp_count": len(built) == 3,
        "covariance_positive_definite": all(
            float(np.min(np.linalg.eigvalsh(dgp.covariance))) > 0.0
            for dgp in built.values()
        ),
        "main_cell_count": len(main_cells) == expected["main_cells"],
        "main_row_count": sum(
            cell["outer_repetitions"] for cell in main_cells
        ) == expected["main_replication_rows"],
        "bootstrap_cell_count": (
            len(bootstrap_cells) == expected["bootstrap_cells"]
        ),
        "bootstrap_outer_row_count": sum(
            cell["outer_datasets"] for cell in bootstrap_cells
        ) == expected["bootstrap_outer_rows"],
        "near_cell_count": (
            len(near_cells) == expected["near_coincidence_cells"]
        ),
        "near_offsets_exclude_zero": all(
            cell["offset_in_anchor_sd"] != 0.0
            for cell in near_cells
        ),
        "both_trigger_orderings_present": (
            set(config["trigger_regimes"])
            == {
                "below_all_base_thresholds",
                "above_all_base_thresholds",
            }
        ),
        "trigger_ordering_construction_passes": all(
            row["ordering_pass"] for row in separation_rows
        ),
        "minimum_standardized_separation": (
            minimum_separation
            >= fatal[
                "minimum_standardized_main_threshold_separation"
            ]
        ),
        "exact_diagnostic_is_nonadjudicative": (
            config["exact_coincidence_diagnostic"][
                "ordinary_bootstrap_coverage_is_adjudicative"
            ]
            is False
        ),
    }

    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "minimum_standardized_main_threshold_separation": (
            minimum_separation
        ),
        "main_cells": main_cells,
        "bootstrap_cells": bootstrap_cells,
        "near_coincidence_cells": near_cells,
        "separation_rows": separation_rows,
    }
