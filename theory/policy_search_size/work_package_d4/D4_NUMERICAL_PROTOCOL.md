# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D4: locked numerical validation protocol

**Protocol version:** D4 numerical v1
**Date:** 2 August 2026
**Status:** To be locked before the scientific run
**Required theory branch:** `tess-top-tier-theory`
**Frozen architecture tag:** `tess-top-tier-manuscript-architecture-v1-final-20260802`
**Preceding D2 results tag:** `tess-theory-work-package-d2-v1-results-final-20260802`
**Planned D4 lock tag:** `tess-theory-work-package-d4-v1-lock-20260802`

---

## 1. Purpose

D4 validates paired two-bank inference for the fixed-threshold contrast between:

1. an adaptive policy that activates the optional branch according to the observed activation score; and
2. a random comparator with the same population activation rate.

On one null state, define the base rejection indicator `R0`, activation indicator `A`, and nested optional increment `D`. The population targets are

\[
\pi_A=E(R_0+AD),
\qquad
\pi_C=E(R_0)+E(A)E(D),
\]

\[
\delta_\pi=\pi_A-\pi_C=\operatorname{Cov}(A,D),
\]

and

\[
\Delta_S=g_\alpha(\pi_A)-g_\alpha(\pi_C).
\]

The plug-in comparator uses the activation rate realized in the same evaluation bank,

\[
\widehat\pi_C
=
\widehat e_0+
\widehat\rho\widehat\mu.
\]

No extra random activation coin is generated. Both policies use the same reference and evaluation replications, so the target estimator is intrinsically paired.

The validation evaluates:

- the evaluation-bank influence function;
- the three-component reference-bank influence function;
- the full paired two-bank asymptotic variance;
- paired complete-replication bootstrap standard errors and intervals;
- the cost of discarding pairing;
- the failure of evaluation-only inference when reference calibration is first-order.

This protocol validates the regular one-candidate-per-branch D4 theorem. It is not direct evidence for the exact 20-candidate winner-selection pipeline.

---

## 2. Runtime-only preflight decision

The local runtime-only preflight used:

- `B = n = 1000`;
- 30 outer datasets;
- 100 paired bootstrap repetitions per dataset;
- a correlated Gaussian code-path benchmark with nonzero contrast.

It produced:

- six of six unit tests passing;
- derivative maximum absolute error approximately `5.68e-08`;
- elapsed time approximately `0.471` seconds;
- approximately `0.000157` seconds per paired bootstrap replicate;
- peak resident memory approximately `147.1 MiB`;
- status `PASS`.

The preflight benchmark had `Delta_S` approximately `0.407557`. It is a runtime and derivative-check benchmark, not one of the locked scientific DGP definitions below. Debug means from 30 outer datasets are not scientific evidence and are not used to choose success criteria.

The observed runtime supports 3,000 outer repetitions, 999 paired bootstrap repetitions, and 24 worker processes.

---

## 3. Prospective interval hierarchy

Before the scientific run, D4 declares:

1. **Primary interval:** centered paired complete-replication two-bank bootstrap-normal interval;
2. **Secondary interval:** paired percentile bootstrap interval;
3. **Diagnostic interval:** paired basic bootstrap interval;
4. **Oracle diagnostic:** influence-function normal interval using the known simulation benchmark;
5. **Misspecification diagnostic:** evaluation-only oracle normal interval;
6. **Pairing diagnostic:** deliberately unpaired policy bootstrap on a prespecified subset of outer datasets.

The unpaired bootstrap is not an alternative estimator and does not determine PASS or REVIEW. It independently resamples the adaptive and comparator policies to show the standard-error inflation produced by discarding their common-data covariance.

---

## 4. Data-generating laws

All laws use independent latent variables `U`, `epsilon0`, and `epsilon1` distributed as standard normal. The activation rule is `A = I(U > c)`. Scores are continuous.

### 4.1 Independent normal negative control

\[
X_0=\varepsilon_0,
\qquad
X_1=\varepsilon_1.
\]

Here `A` is independent of `D`, so

\[
\delta_\pi=0,
\qquad
\Delta_S=0,
\]

and the first-order reference influence function for the paired contrast vanishes. This is an important negative control: evaluation-only inference should be adequate to first order in this law.

### 4.2 Gaussian one-factor positive contrast

\[
X_0=0.60U+0.80\varepsilon_0,
\]

\[
X_1=0.75U+\sqrt{1-0.75^2}\,\varepsilon_1.
\]

At `alpha = 0.05` and activation rate `0.50`, the population TESS contrast is approximately

\[
\Delta_S=0.401077.
\]

This law has positive allocation premium and material reference-bank uncertainty.

### 4.3 Nonlinear smooth negative contrast

\[
X_0=0.55U+\sqrt{1-0.55^2}\,\varepsilon_0,
\]

\[
X_1=
2\{\exp(-U^2/2)-2^{-1/2}\}
+0.45\varepsilon_1.
\]

The optional score is smoothly and nonmonotonically related to the activation variable. At `alpha = 0.05`, the population TESS contrast is approximately

\[
\Delta_S=-0.005603.
\]

This law checks a small negative contrast and a non-Gaussian joint score distribution.

Population quantiles, rejection probabilities, boundary coefficients, covariance terms, and influence-function variances for the three laws are computed by deterministic one-dimensional quadrature and root finding before the Monte Carlo run.

---

## 5. Locked scientific design

- Target activation rate: `0.50`.
- Local thresholds: `alpha in {0.01, 0.05, 0.10}`.
- Designs:
  - `(B,n) = (500,500)`;
  - `(B,n) = (1000,1000)`;
  - `(B,n) = (3000,3000)`;
  - `(B,n) = (3000,5000)`.
- Data-generating laws: 3.
- Total cells: 36.
- Outer Monte Carlo repetitions per cell: 3,000.
- Paired two-bank bootstrap repetitions per outer dataset: 999.
- Master seed: `20261117`.
- Worker processes: 24.
- Chunk size: 25.
- Confidence level: 95%.

Reference and evaluation banks are independently generated in every outer replication. All coordinates from one reference replication are resampled together. Adaptive and comparator estimates use identical reference and evaluation bootstrap indices.

### Prespecified unpaired diagnostic

For the first 100 outer datasets in every cell:

- unpaired bootstrap repetitions: 199;
- adaptive and comparator policies use independent reference resamples;
- adaptive and comparator policies use independent evaluation resamples.

The resulting unpaired-to-paired bootstrap-SD ratio is reported descriptively.

---

## 6. Exact benchmark quantities

For each law, threshold, and `n/B` ratio, the validation computes:

- candidate quantiles `q0` and `q1`;
- activation threshold `c`;
- `e0`, `rho`, `mu`, and `nu`;
- `pi_A`, `pi_C`, `delta_pi`, and `Delta_S`;
- adaptive boundary coefficients `a0`, `b1`, and `d_U`;
- comparator boundary coefficients `a0_bar`, `b1_bar`, and `dU_bar`;
- paired reference coefficients on rejection and TESS scales;
- `F01`, `F0U`, and `F1U`;
- evaluation-, reference-, and total asymptotic variances for `delta_pi`;
- evaluation-, reference-, and total asymptotic variances for `Delta_S`;
- the reference variance fraction.

The independent law must have a numerically zero reference variance fraction within `1e-10`. Failure of this check is fatal because it indicates a benchmark or implementation error.

---

## 7. Recorded quantities

Every outer dataset records:

- all three estimated thresholds;
- realized evaluation-bank activation rate;
- adaptive and comparator rejection estimates;
- adaptive and comparator TESS estimates;
- rejection-probability premium estimate;
- TESS contrast estimate;
- paired bootstrap standard deviations;
- oracle, bootstrap-normal, percentile, basic, and evaluation-only intervals;
- coverage indicators for both contrast scales.

The cell summary additionally records:

- standardized bias;
- empirical-to-exact variance ratios;
- paired bootstrap-SD-to-empirical-SD ratios;
- interval coverages;
- reference variance fractions;
- unpaired-to-paired bootstrap-SD ratios.

---

## 8. Prespecified success criteria

### 8.1 Primary cells

All three DGPs at:

- `alpha = 0.05`;
- `(B,n) = (3000,3000)` or `(3000,5000)`.

For both `delta_pi` and `Delta_S`:

- absolute standardized bias at most `0.12`;
- empirical/exact variance ratio in `[0.88, 1.12]`;
- paired mean bootstrap SD/empirical SD ratio in `[0.88, 1.12]`;
- oracle-normal coverage in `[0.93, 0.97]`;
- paired bootstrap-normal coverage in `[0.93, 0.97]`.

### 8.2 Other main cells

All three laws with `B = 3000` and `alpha = 0.01` or `0.10`.

For both contrast scales:

- absolute standardized bias at most `0.20`;
- empirical/exact variance ratio in `[0.80, 1.20]`;
- paired mean bootstrap SD/empirical SD ratio in `[0.80, 1.20]`;
- oracle-normal coverage in `[0.91, 0.99]`;
- paired bootstrap-normal coverage in `[0.91, 0.99]`.

### 8.3 Stress cells

Cells with `B = 500` or `B = 1000` are declared finite-reference stress tests. They are reported completely but do not determine PASS versus REVIEW. Nonfinite values and code-integrity or benchmark failures remain fatal.

### 8.4 Global diagnostics

The following are reported but do not determine the scientific status:

- dependent-law cells with evaluation-only TESS-contrast coverage below `0.93`;
- dependent-law cells in which paired bootstrap-normal coverage improves on evaluation-only coverage by at least `0.01`;
- percentile and basic interval coverage;
- unpaired-to-paired bootstrap-SD ratios;
- reference variance fractions;
- activation-rate estimation behavior.

The protocol expects at least six dependent-law cells to show evaluation-only undercoverage and at least six to show improvement from paired two-bank inference. Failure is labeled diagnostic rather than scientific because finite-sample coverage can vary by threshold and design.

---

## 9. Adjudication

- **PASS:** every primary and other-main scientific check passes and no fatal check fails.
- **REVIEW:** one or more primary or other-main agreement checks fail; all results are preserved for transparent inspection.
- **FAIL:** a code-integrity, benchmark, independent-negative-control, nonfinite-output, or manifest verification check fails.

A REVIEW classification does not automatically invalidate the analytic theorem. Locked criteria will not be changed after the scientific run.

---

## 10. Reproducibility and locking

Track before the scientific run:

- D4 theory memo;
- D4 core and runtime-preflight code;
- D4 numerical protocol and both configurations;
- DGP, benchmark, validation, and bootstrap code;
- unit tests;
- smoke and full-run scripts;
- lock-manifest scripts;
- references, README files, and `.gitignore`.

Planned lock tag:

```text
tess-theory-work-package-d4-v1-lock-20260802
```

The scientific full run may start only after the complete D4 directory has been committed, the lock tag has been created and pushed, and the tracked working tree is clean. Full-run results will be preserved in a separate results commit, tag, and external SHA-256 archive.
