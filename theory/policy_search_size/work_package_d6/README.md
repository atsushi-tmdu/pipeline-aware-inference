# Work Package D6

Finite-candidate unique-winner extension of the D4-D5 paired two-bank theory.

## Current state

Protocol and theory scaffold only. No D6 scientific computation has been run.

## Core modeling decision

The selected candidate is a random per-replication argmax over a fixed finite
candidate pool. D6 does not estimate one deterministic population-best model.

## Scope

D6 includes:

- fixed finite nested candidate pools;
- almost-surely unique per-replication winners;
- candidate-specific reference calibration;
- paired adaptive-versus-budget-matched-random policy contrast;
- complete-vector two-bank resampling;
- candidate-wise exact plus-one bridge.

D6 excludes:

- maximum-score activation triggers;
- positive-probability ties and deterministic tie rules;
- failed-fit fallback rules;
- growing candidate dimension;
- simultaneous threshold-process inference.

## Initial implementation scaffold

The initial `d6_core.py` implements:

- nested finite candidate-pool validation;
- almost-sure unique winner enforcement for observed continuous-score draws;
- branch and adaptive-policy rejection maps;
- the exact covariance representation of the rejection contrast;
- the centered evaluation influence target;
- the corrected nested-pool candidate-threshold jump field;
- complete-replication resampling;
- the nominal-alpha TESS transform and derivative.

The initial unit tests are implementation and algebra checks only. They are not
scientific numerical validation and do not lock the D6 design.

## Runtime-only derivative preflight

`d6_preflight.py` uses a transparent continuous four-dimensional Gaussian
benchmark with two base candidates, one optional candidate, and a separate
activation score. It compares:

- common-random-number finite differences of the policy contrast;
- conditional-Gaussian winner-region boundary coefficients.

The preflight output is ignored by Git. It is computational and mathematical
debugging only, not scientific validation and not a protocol lock.

## Theory completion

`D6_THEORY_MEMO.md` now contains the formal assumptions, winner-region
derivative lemmas, two-bank asymptotic linearity theorem, TESS expansion,
complete-replication bootstrap theorem, and fixed-finite-K plus-one bridge.

The theory is complete as a prelock draft. A prospective numerical validation
protocol must be frozen before any scientific D6 run.

## Prospective numerical validation

`D6_NUMERICAL_PROTOCOL.md` and the draft full/smoke configs prospectively
define the scientific validation design.

No scientific D6 numerical run may begin until:

1. the validation implementation is complete;
2. all tests and runtime-only smoke checks pass;
3. final repetition counts are fixed from runtime alone;
4. the protocol, implementation, config, and manifest are committed and tagged.

## Validation engine

`d6_validation_core.py` and `d6_validate.py` implement the prospective
fixed-finite-candidate validation design.

The engine:

- constructs all three declared Gaussian DGPs;
- computes independent population and conditional-boundary benchmarks;
- runs the full 36-cell asymptotic grid;
- runs the 12 prespecified complete-replication bootstrap cells;
- compares regular and exact plus-one candidate boundaries;
- enforces pathwise support and covariance identities;
- writes machine-readable summaries, checks, adjudication, and SHA-256 hashes.

`run_d6_validation_smoke.sh` uses only the runtime-only smoke config. It does
not run the scientific design.

## Numerical lock

The D6 theory, implementation, DGPs, scientific counts, bootstrap cells,
seeds, success criteria, and full-run command are frozen before scientific
execution.

Run the scientific design only through:

```bash
PYTHON="$PY" bash theory/policy_search_size/work_package_d6/run_d6_validation_full.sh
```

The runner verifies the D6 lock manifest before computation.
