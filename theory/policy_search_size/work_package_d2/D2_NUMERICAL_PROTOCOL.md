# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D2: locked numerical validation protocol

**Protocol version:** D2 numerical v1
**Date:** 2 August 2026
**Status:** To be locked before the scientific run
**Required theory branch:** `tess-top-tier-theory`
**Parent D0 lock tag:** `tess-theory-work-package-d0-v1-lock-20260802`
**Preceding D1 results tag:** `tess-theory-work-package-d1-v1-results-review-20260802`
**Planned D2 lock tag:** `tess-theory-work-package-d2-v1-lock-20260802`

---

## 1. Purpose

D2 evaluates the fixed-threshold two-bank theory when all three calibration thresholds are estimated from the same complete null-reference replications:

\[
\widehat q_{0,B},\qquad \widehat q_{1,B},\qquad \widehat c_B.
\]

The scientific targets are:

1. the population-calibrated policy rejection probability and TESS;
2. the full three-component reference-bank influence variance;
3. the trigger-estimation contribution isolated by the paired D2-minus-D1 estimator;
4. complete-replication two-bank bootstrap estimation of the total standard error;
5. interval coverage under the prospective interval hierarchy informed by D1.

This protocol validates the regular D2 theorem. It is not evidence for the locked empirical TESS application.

---

## 2. Prospective changes motivated by D1

D1 retained the automatic status `REVIEW`. Its first-order variance and bootstrap standard-error theory were supported, but the basic bootstrap interval undercovered in some finite-reference settings. The D2 design therefore declares, before execution:

1. **Primary interval:** centered complete-replication two-bank bootstrap-normal interval;
2. **Secondary interval:** percentile two-bank bootstrap interval;
3. **Diagnostic interval:** basic two-bank bootstrap interval;
4. **Oracle diagnostic:** influence-function normal interval using the known simulation benchmark;
5. **Misspecification diagnostic:** evaluation-only normal interval;
6. **Main scientific regime:** reference-bank size \(B=3000\);
7. **Stress regimes:** \(B=500\) and \(B=1000\), which do not determine PASS versus REVIEW.

These are prospective D2 choices and do not alter the D1 adjudication.

---

## 3. Data-generating laws

All laws use independent latent variables \(U,\varepsilon_0,\varepsilon_1\sim N(0,1)\), continuous scores, and one candidate per branch.

### 3.1 Independent normal

\[
X_0=\varepsilon_0,\qquad X_1=\varepsilon_1.
\]

This law has closed-form population and finite-reference benchmarks.

### 3.2 Gaussian one-factor dependence

\[
X_0=0.60U+0.80\varepsilon_0,
\]

\[
X_1=0.75U+\sqrt{1-0.75^2}\,\varepsilon_1.
\]

The marginal candidate laws remain standard normal, while complete reference replications carry nonzero candidate-trigger and candidate-candidate dependence.

### 3.3 Nonlinear smooth dependence

\[
X_0=0.55U+\sqrt{1-0.55^2}\,\varepsilon_0,
\]

\[
X_1=
2.00\left\{\exp(-U^2/2)-2^{-1/2}\right\}
+0.45\varepsilon_1.
\]

This is a continuous, smooth, nonmonotone trigger-candidate dependence construction. It produces a more material trigger-boundary contribution than the independent benchmark.

Population quantiles, rejection probabilities, boundary coefficients, and influence-function variances for the dependent laws are computed by deterministic one-dimensional quadrature and root finding before the Monte Carlo run.

---

## 4. Locked design

- Activation rate: \(r=0.50\)
- Local thresholds: \(\alpha\in\{0.01,0.05,0.10\}\)
- Designs:
  - \((B,n)=(500,500)\)
  - \((B,n)=(1000,1000)\)
  - \((B,n)=(3000,3000)\)
  - \((B,n)=(3000,5000)\)
- Data-generating laws: 3
- Total cells: 36
- Outer Monte Carlo repetitions per cell: 3,000
- Two-bank bootstrap repetitions per outer dataset: 999
- Master seed: 20261017
- Worker processes: 24
- Chunk size: 25
- Confidence level: 95%

Reference and evaluation banks are independently generated in every outer replication. All coordinates from a reference replication are resampled together. D2 and the paired known-trigger D1 estimator use identical banks and identical bootstrap indices.

---

## 5. Exact benchmark quantities

For each law and threshold, the validation computes:

- population candidate quantiles \(q_0,q_1\);
- population trigger \(c\);
- population rejection probability \(\pi\) and TESS;
- boundary coefficients \(a_0,b_1,d_U\);
- pairwise reference CDF terms \(F_{01},F_{0U},F_{1U}\);
- evaluation contribution \(\sigma_E^2\);
- known-trigger reference contribution \(\sigma_{R,D1}^2\);
- trigger-only contribution \(\sigma_{R,\mathrm{trig}}^2\);
- complete estimated-trigger reference contribution \(\sigma_{R,D2}^2\);
- total D1 and D2 asymptotic variances under \(\sqrt n\) scaling.

For the paired difference

\[
\widehat\Delta_{\mathrm{trig}}
=
\widehat\pi_{D2}-\widehat\pi_{D1},
\]

the first-order variance under \(\sqrt n\) scaling is

\[
\lambda r(1-r)d_U^2,
\qquad \lambda=n/B.
\]

This directly validates the third reference influence component.

---

## 6. Recorded interval methods

For rejection probability and TESS, every outer dataset records:

1. oracle influence-function normal interval;
2. two-bank bootstrap-normal interval (**primary**);
3. percentile two-bank bootstrap interval (**secondary**);
4. basic two-bank bootstrap interval (**diagnostic**);
5. evaluation-only oracle normal interval (**diagnostic**).

For the paired trigger-estimation effect, the validation records empirical variance, exact first-order variance, bootstrap standard deviation, and bootstrap-normal coverage for the population target zero. Coverage is descriptive because finite-reference order-statistic bias may be nonnegligible in stress cells.

---

## 7. Prespecified success criteria

### 7.1 Primary cells

All three data-generating laws at

- \(\alpha=0.05\);
- \((B,n)=(3000,3000)\) or \((3000,5000)\).

For both rejection probability and TESS:

- absolute standardized bias \(\le0.12\);
- empirical/exact variance ratio in \([0.88,1.12]\);
- mean bootstrap SD/empirical SD ratio in \([0.88,1.12]\);
- oracle-normal coverage in \([0.93,0.97]\);
- primary bootstrap-normal coverage in \([0.93,0.97]\).

The paired trigger-estimation effect is recorded as a diagnostic rather than a PASS criterion. Its first-order variance can be very small, in which case finite-sample shrinking-boundary evaluation noise may dominate the isolated difference even while the full D2 expansion is accurate.

### 7.2 Other main cells

All three laws with \(B=3000\) and \(\alpha=0.01\) or \(0.10\).

- absolute standardized bias \(\le0.20\);
- empirical/exact variance ratio in \([0.80,1.20]\);
- mean bootstrap SD/empirical SD ratio in \([0.80,1.20]\);
- oracle-normal coverage in \([0.91,0.99]\);
- bootstrap-normal coverage in \([0.91,0.99]\);
- trigger-effect variance and bootstrap-SD ratios are reported diagnostically.

### 7.3 Stress cells

Cells with \(B=500\) or \(B=1000\) are declared finite-reference stress tests. They are reported completely but do not determine PASS versus REVIEW. Nonfinite values, code failure, or manifest failure remain fatal diagnostics.

### 7.4 Global diagnostics

The following do not determine the scientific status but must be reported:

- number of cells in which evaluation-only coverage is below 0.93;
- number of cells in which bootstrap-normal coverage improves on evaluation-only coverage by at least 0.01;
- percentile and basic interval coverage in every cell;
- exact independent-law finite-reference mean and bias;
- D2-minus-D1 mean, variance, bootstrap SD, and zero-coverage diagnostic;
- reference variance fraction and trigger-only variance fraction.

---

## 8. Adjudication

- **PASS:** every primary and other-main scientific check passes, and no fatal diagnostic fails.
- **REVIEW:** one or more primary or other-main checks fail; all results are preserved and inspected transparently.
- **FAIL:** code-integrity, benchmark, nonfinite-output, or manifest verification fails.

A REVIEW classification does not automatically invalidate the analytic theorem. The locked criteria will not be changed after the scientific run.

---

## 9. Runtime basis

The local runtime-only preflight used \(B=n=1000\), 30 outer replications, and 100 bootstrap replications. It completed in approximately 0.317 seconds with peak resident memory approximately 27.9 MiB. This output was used only to establish computational feasibility.

The preflight also reproduced the expected scale of the independent benchmark and the exact finite-reference mean. Its debug aggregates are not scientific evidence and are not used to alter the locked settings.

---

## 10. Reproducibility and locking

Track before the scientific run:

- D2 theory memo;
- D2 core and validation code;
- DGP and benchmark code;
- numerical protocol and locked configuration;
- smoke configuration;
- unit tests;
- run scripts;
- lock manifest;
- references and README files.

Planned lock tag:

```text
tess-theory-work-package-d2-v1-lock-20260802
```

The scientific full run must start only after this tag has been committed and pushed. Full-run outputs will be frozen in a separate results commit and tag.
