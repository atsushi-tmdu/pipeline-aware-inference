# Work Package D5

Exact plus-one/order-statistic bridge for the frozen D4 paired policy contrast.

## Current state

The D5 protocol, theory, implementation, tests, and scientific configuration are locked for the exact plus-one bridge. A scientific run is permitted only from the commit carrying the annotated tag `tess-theory-work-package-d5-v1-lock-20260803`. Raw smoke output is computational debugging only and is not scientific evidence.

## Parent result

- D4 results tag: `d4-validation-full-v1`
- D4 commit: `9b0a2530bfb5e363f59bd7b290d1c064c82b5eaa`
- D4 master seed: `20261117`

## Pre-protocol reproduction audit

One outer dataset from each of the 36 D4 cells was regenerated from the frozen
seed identity. The overall maximum absolute error across stored D4 estimates
was `4.441e-16`, below the prospective `1e-12` tolerance.

## Validation layer

After protocol and core review, D5 contains a separate numerical validator.

- `D5_THEORY_MEMO.md`: exact boundary and bridge-rate arguments
- `D5_NUMERICAL_PROTOCOL.md`: prospective numerical rules
- `D5_NUMERICAL_CONFIG_SMOKE.json`: runtime-only smoke settings
- `D5_NUMERICAL_CONFIG.json`: scientific draft; not runnable until locked
- `d5_validate.py`: paired D4-bank regeneration and bridge analysis
- `run_d5_validation_smoke.sh`: smoke runner
- `run_d5_validation_full.sh`: refuses to run before lock-manifest creation
