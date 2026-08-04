# D7 Scientific Validation Implementation

This implementation reads the locked D7 numerical design without modifying it.

## Execution paths

- `run_d7_validation_smoke.sh`: implementation smoke only;
- `run_d7_validation_full.sh`: locked scientific validation.

Both paths verify the theory checkpoint and numerical lock before execution.

## Computation

The engine implements:

- deterministic Gaussian DGP construction;
- deterministic maximum-CDF calibration;
- independent complete-vector reference and evaluation banks;
- candidate empirical quantiles and paired plus-one thresholds;
- empirical maximum-trigger quantiles;
- population truth and influence-variance benchmarks;
- main-grid bias, variance, and coverage evaluation;
- complete-replication two-bank bootstrap;
- near- and exact-coincidence diagnostics;
- prospective PASS/FAIL adjudication.

Smoke outputs and full outputs are written under the pre-existing ignored
`outputs/` directory.

The exact-coincidence diagnostic is nonadjudicative. The implementation does
not claim validity for discrete winner ties or the current frozen empirical
pipeline.
