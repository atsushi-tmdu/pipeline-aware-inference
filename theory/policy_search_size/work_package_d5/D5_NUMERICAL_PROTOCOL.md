# D5 Numerical Validation Protocol

## Exact plus-one/order-statistic bridge

**Status:** locked before scientific run
**Scientific run permitted:** only from the commit carrying `tess-theory-work-package-d5-v1-lock-20260803`

---

# 1. Objective

Numerically quantify the fully paired difference between the exact plus-one
candidate boundary and the D1-D4 empirical-quantile boundary for the frozen D4
adaptive-versus-budget-matched-random policy contrast.

This validation does not rerun D4 bootstrap inference. It reuses the exact D4
outer datasets by deterministic seed regeneration.

---

# 2. Parent integrity

Before computation, the validator must verify:

- D4 annotated results tag `d4-validation-full-v1`;
- D4 results commit
  `9b0a2530bfb5e363f59bd7b290d1c064c82b5eaa`;
- every file hash in `D4_LOCK_MANIFEST.json`;
- every raw D4 output hash in the frozen SHA-256 manifest;
- the frozen D4 replication file identity.

A failure is fatal.

---

# 3. Design

The scientific D5 design inherits D4 exactly:

- DGPs:
  - independent normal;
  - Gaussian factor;
  - nonlinear smooth;
- activation rate: 0.50;
- alpha values: 0.01, 0.05, 0.10;
- designs:
  - \(B=500,n=500\);
  - \(B=1000,n=1000\);
  - \(B=3000,n=3000\);
  - \(B=3000,n=5000\);
- 3000 outer repetitions per cell;
- 36 cells;
- 108,000 outer datasets;
- master seed 20261117.

The same reference and evaluation banks are used for both boundary modes.

---

# 4. Full quantile-mode reproduction

For every one of the 108,000 regenerated datasets, all stored quantile-mode D4
estimates must agree with the frozen D4 replication record to absolute
tolerance \(10^{-12}\).

This all-record comparison is a fatal integrity condition.

---

# 5. Primary quantities

For each dataset:

\[
D_{\pi,B,n}
=
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q,
\]

\[
D_{S,B,n}
=
\widehat\Delta_S^+
-
\widehat\Delta_S^Q.
\]

Record raw, absolute, \(\sqrt n\)-scaled, \(\sqrt B\)-scaled, and \(B\)-scaled
versions.

Both modes use nominal \(\alpha\) in the TESS denominator.

---

# 6. Sign reporting

Report separately:

- strict sign reversal:
  \(\widehat\Delta^Q\widehat\Delta^+<0\);
- zero-status change:
  exactly one of the two contrasts equals zero.

The two concepts must not be combined.

---

# 7. Cell summaries

For each of the 36 cells, report:

- mean, median, standard deviation, RMS;
- mean absolute discrepancy;
- selected quantiles and maximum absolute discrepancy;
- exact-equality frequency;
- strict-sign-reversal frequency;
- zero-status-change frequency;
- Monte Carlo standard errors for means, RMS values, and frequencies;
- RMS bridge discrepancy divided by the empirical SD of the quantile-mode D4
  contrast;
- descriptive magnitude label.

Magnitude labels:

- negligible: ratio below 0.10;
- small: 0.10 to below 0.25;
- material: 0.25 or greater.

These labels are not pass/fail criteria.

---

# 8. Fatal checks

The run fails if:

- parent integrity fails;
- cell or replication counts are incorrect;
- identity keys are duplicated;
- any required numeric output is nonfinite;
- the two boundary modes use different activation thresholds or activation
  realizations;
- the integer-boundary identities fail;
- all-record D4 reproduction exceeds \(10^{-12}\);
- output or manifest creation fails.

Scientific magnitude does not determine implementation PASS or FAIL.

---

# 9. Smoke run

The smoke run is computational debugging only. It uses the locked scientific
DGP families and selected design points with a very small outer count.

Smoke output must be labeled:

> RUNTIME-ONLY SMOKE - NOT SCIENTIFIC EVIDENCE

Smoke findings may not be cited as scientific results and may not be used to
change the scientific grid based on favorable outcomes.

---

# 10. Outputs

- `D5_BRIDGE_REPLICATIONS.csv.gz`
- `D5_BRIDGE_CELL_SUMMARY.csv`
- `D5_BOUNDARY_TABLE.csv`
- `D5_VALIDATION_CHECKS.json`
- `D5_VALIDATION_SUMMARY.json`
- `D5_VALIDATION_ADJUDICATION.md`
- `D5_VALIDATION_MANIFEST.json`

Raw outputs remain ignored by Git. Compact evidence will be frozen after the
scientific run.

---

# 11. Lock sequence

After smoke review:

1. resolve implementation defects only;
2. rename/finalize the scientific config;
3. set status to `locked_before_run`;
4. generate the D5 lock manifest;
5. run all tests and verify the manifest;
6. commit and tag the D5 protocol/implementation lock;
7. only then run the full scientific validation.
