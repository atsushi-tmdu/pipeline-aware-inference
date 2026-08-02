# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D2: Post-run scientific adjudication

**Adjudication version:** D2 results v1
**Date:** 2 August 2026
**Locked numerical protocol tag:** `tess-theory-work-package-d2-v1-lock-20260802`
**Locked protocol commit:** `1ed5cac`
**Automatic locked status:** `PASS`
**Scientific interpretation:** The estimated-trigger two-bank first-order theory and centered complete-replication bootstrap-normal inference were validated in every prespecified primary and main-regime cell.

---

## Executive decision

Work Package D2 achieved the core success criterion fixed in Work Package D0.

The locked D2 validation completed 36 cells spanning three global-null data-generating structures, three local thresholds, and four reference/evaluation bank-size designs. All prespecified primary and main-regime scientific checks passed. All diagnostic checks also passed.

The formal adjudication is:

> **D2 numerical validation v1: PASS.**

The results support the fixed-threshold asymptotic linear representation when candidate thresholds and the activation threshold are estimated from the same complete-vector reference bank. They also support the centered complete-replication two-bank bootstrap-normal interval in the declared main regime.

This validation concerns the regular D2 model. It is not direct evidence for the empirical 20-candidate TESS application, winner-selection irregularities, exact plus-one discreteness, or simultaneous inference over an alpha interval.

---

## Locked design and execution

- Data-generating structures: independent normal, Gaussian one-factor dependence, and nonlinear smooth dependence.
- Cells: 36.
- Alpha grid: 0.01, 0.05, 0.10.
- Designs: (B,n) = (500,500), (1000,1000), (3000,3000), and (3000,5000).
- Outer Monte Carlo repetitions: 3,000 per cell.
- Two-bank bootstrap repetitions: 999 per outer dataset.
- Master seed: 20261017.
- Primary interval: centered complete-replication two-bank bootstrap-normal interval.
- Worker processes: 24.
- Elapsed time: 1,917.194 seconds.
- Diagnostic check failures: 0.
- Scientific check failures: 0.

---

## Principal findings

### 1. Every prespecified primary and main-regime check passed

The automatic locked status was PASS. The B = 500 and B = 1,000 settings were prospectively designated stress diagnostics. Scientific success was determined in the B = 3,000 main regime.

Across the main cells:

- empirical-to-theoretical variance ratios stayed within the locked range;
- bootstrap-to-empirical standard-deviation ratios stayed within the locked range;
- oracle-normal coverage stayed within the locked range;
- bootstrap-normal coverage stayed within the locked range;
- standardized bias stayed within the locked range.

### 2. Primary alpha = 0.05 results were strong across all three structures

| DGP | B | n | pi variance ratio | TESS variance ratio | pi bootstrap-normal coverage | TESS bootstrap-normal coverage |
|---|---:|---:|---:|---:|---:|---:|
| Independent normal | 3,000 | 3,000 | 1.022 | 1.025 | 0.947 | 0.948 |
| Independent normal | 3,000 | 5,000 | 0.999 | 1.001 | 0.949 | 0.949 |
| Gaussian factor | 3,000 | 3,000 | 1.022 | 1.025 | 0.950 | 0.950 |
| Gaussian factor | 3,000 | 5,000 | 1.030 | 1.032 | 0.945 | 0.945 |
| Nonlinear smooth | 3,000 | 3,000 | 0.993 | 0.995 | 0.955 | 0.955 |
| Nonlinear smooth | 3,000 | 5,000 | 1.000 | 1.002 | 0.951 | 0.951 |

These results support both the explicit influence-function variance and the complete-replication bootstrap approximation.

### 3. Complete-vector reference resampling remained essential

D2 estimates candidate quantiles and the activation quantile from the same reference vectors. The reference influence function contains three centered indicator components and all pairwise covariance terms. The successful validation across independent, Gaussian-factor, and nonlinear structures supports preserving the complete reference vector in every resample.

### 4. Evaluation-only inference remained inadequate

Evaluation-only pi coverage was below its declared diagnostic threshold in all 36 cells. The bootstrap-normal two-bank interval improved coverage in all 36 cells.

In the B = 3,000, n = 5,000 cells, evaluation-only pi coverage ranged approximately from 0.763 to 0.801, whereas two-bank bootstrap-normal coverage remained approximately 0.945 to 0.957.

This confirms that reference-bank calibration uncertainty remains first-order when n/B does not vanish.

### 5. D1 finite-reference lessons were handled successfully

D1 showed that the basic interval could under-cover at finite B even when bootstrap standard errors were accurate. D2 prospectively changed the primary regular interval to bootstrap-normal, retained percentile inference as secondary, and treated the basic interval diagnostically.

That prospective choice performed as intended. The PASS classification does not retroactively change the D1 REVIEW classification.

### 6. Trigger-only variance ratios require careful interpretation

The isolated trigger-difference variance ratio was recorded as a diagnostic, not a success criterion. Some ratios were very large, especially in Gaussian-factor alpha = 0.01 cells.

This does not contradict the total D2 validation. In those settings, the theoretical variance of the difference between estimated-trigger and known-trigger estimators is extremely close to zero. Dividing a small finite-sample variance by an even smaller asymptotic benchmark produces an unstable ratio. The total policy estimator's variance ratios, bootstrap standard errors, and coverage remained accurate.

The trigger-only diagnostic should therefore be described using absolute variance and practical contribution to total uncertainty, not by a variance ratio alone when the denominator is near zero.

---

## Formal D2 adjudication

### Locked numerical status

**PASS**

This status is fixed for D2 numerical validation v1.

### Scientific status

**D2 fixed-threshold estimated-trigger two-bank theory: VALIDATED IN THE DECLARED REGULAR MODEL**

Validated components:

1. joint reference influence of base-candidate, optional-candidate, and activation quantiles;
2. two-bank asymptotic variance decomposition;
3. preservation of all within-reference covariance terms through complete-vector resampling;
4. centered complete-replication bootstrap estimation of the total two-bank standard error;
5. bootstrap-normal interval coverage in every declared primary and main-regime cell;
6. material undercoverage of evaluation-only inference;
7. robustness across independent, correlated Gaussian, and nonlinear smooth structures.

Not established by D2:

1. simultaneous weak convergence over an alpha interval;
2. simultaneous confidence bands;
3. paired adaptive-policy TESS contrasts;
4. exact finite-B plus-one empirical-p-value boundaries;
5. multiple candidates, winner selection, ties, or failed-fit rules;
6. direct validity for the locked 20-candidate empirical pipeline.

---

## Consequence for the theory program

D0's core success criterion has now been achieved. The project no longer depends on D3 for basic viability.

The next decision should be strategic:

- **D3 route:** develop the threshold-indexed TESS process and simultaneous bands;
- **D4 route:** develop paired policy-contrast inference closest to the empirical promising-minus-random estimand;
- **manuscript route:** pause new theory, consolidate Work Packages A, B, D1, and D2 into a top-tier manuscript architecture, and identify the minimum remaining theorem needed for the target journal.

A sensible order is to draft the consolidated theorem architecture now, then decide whether D3 or D4 supplies the most valuable missing result. D4 may be more directly connected to the locked empirical study, whereas D3 may provide a broader JASA/JRSS-B inference contribution.

---

## Preservation rule

The following materials should be retained in Git:

- this post-run adjudication;
- D2 validation summary;
- D2 validation checks;
- D2 benchmark definitions;
- cell-level summary;
- original automatic adjudication;
- validation manifest;
- full-run log;
- a results-freeze manifest containing SHA-256 hashes.

The complete replication-level output and review-output text should be stored in an external deterministic archive with its SHA-256 recorded in Git. The locked D2 protocol, configuration, code, and lock tag must not be modified.

Recommended results tag:

```text
tess-theory-work-package-d2-v1-results-final-20260802
```

Recommended commit message:

```text
Add D2 estimated-trigger two-bank validation results
```
