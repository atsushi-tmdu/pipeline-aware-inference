# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D1: Post-run scientific adjudication

**Adjudication version:** D1 results v1
**Date:** 2 August 2026
**Locked numerical protocol tag:** `tess-theory-work-package-d1-v1-lock-20260802`
**Locked protocol commit:** `01e8c0b`
**Automatic locked status:** `REVIEW`
**Scientific interpretation:** D1 first-order two-bank theory supported; basic bootstrap interval not uniformly validated.

---

## Executive decision

The locked D1 scientific validation must retain its automatic status of **REVIEW**. Fourteen prespecified scientific checks failed, while all diagnostic checks passed. The failed checks were concentrated in the smallest reference-bank settings, particularly at alpha = 0.01, and in the prespecified basic bootstrap interval at B = n = 1000 and alpha = 0.05.

The results do **not** indicate failure of the D1 asymptotic linear representation. Empirical variances agreed closely with the exact influence-function variance in the larger designs, and the complete-replication two-bank bootstrap estimated standard errors accurately. Evaluation-only intervals undercovered in all 12 cells, whereas two-bank intervals improved coverage in all 12 cells.

The defensible conclusion is:

> The regular D1 two-bank first-order theory and variance decomposition were numerically supported. Finite-sample basic bootstrap intervals were not uniformly reliable, especially for small reference banks and deep thresholds.

The locked criteria will not be changed, and the D1 scientific run will not be repeated to obtain a more favorable status.

---

## Locked design and execution

- Cells: 12
- Alpha grid: 0.01, 0.05, 0.10
- Designs: (B,n) = (500,500), (1000,1000), (3000,3000), and (3000,5000)
- Outer Monte Carlo repetitions: 3,000 per cell
- Two-bank bootstrap repetitions: 999 per outer dataset
- Activation rate: 0.50
- Master seed: 20260921
- Worker processes: 24
- Elapsed time: 560.743 seconds
- Diagnostic check failures: 0
- Scientific check failures: 14

---

## Principal findings

### 1. First-order variance theory was supported

At alpha = 0.05:

| B | n | pi empirical/exact variance | TESS empirical/exact variance | pi bootstrap SD/empirical SD | TESS bootstrap SD/empirical SD |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 1,000 | 1.062 | 1.067 | 1.011 | 1.013 |
| 3,000 | 3,000 | 1.012 | 1.014 | 1.015 | 1.016 |
| 3,000 | 5,000 | 1.017 | 1.018 | 1.013 | 1.013 |

The agreement improves as the reference bank grows. This is consistent with the D1 expansion separating evaluation-bank and reference-bank first-order terms.

### 2. Reference-bank uncertainty was material

Evaluation-only pi coverage ranged from approximately 0.789 to 0.854 across the 12 cells. The global diagnostics showed:

- evaluation-only coverage below its declared threshold in all 12 cells;
- two-bank coverage improvement in all 12 cells.

Thus, treating the reference bank as fixed materially understates uncertainty in the population-calibrated two-bank target.

### 3. Basic bootstrap intervals undercovered at finite sample sizes

At B = n = 1,000 and alpha = 0.05:

| Quantity | pi | TESS |
|---|---:|---:|
| Oracle-normal coverage | 0.942 | 0.942 |
| Basic two-bank bootstrap coverage | 0.916 | 0.917 |
| Percentile two-bank bootstrap coverage | 0.954 | 0.954 |
| Bootstrap-normal coverage | 0.947 | 0.949 |

The bootstrap standard errors were accurate, but inversion by the basic interval produced undercoverage. Percentile and bootstrap-normal intervals performed well descriptively, but they were not the locked primary interval and must not be retroactively declared primary.

### 4. The deepest finite-bank stress cell was B = n = 500, alpha = 0.01

In this cell:

- pi and TESS basic coverage were both 0.885;
- oracle-normal coverage was 0.907;
- percentile coverage was 0.961;
- bootstrap-normal coverage was approximately 0.964-0.966;
- empirical/exact variance ratios were 1.205 and 1.220.

At alpha = 0.01, a reference bank of 500 supplies only about five expected observations in the relevant marginal tail. The result is consistent with finite-order-statistic and finite-bank bias effects outside the most accurate asymptotic regime.

### 5. Finite-reference bias decreased with B

At alpha = 0.05, mean pi bias was:

| B | n | Mean pi bias |
|---:|---:|---:|
| 500 | 500 | 0.002903 |
| 1,000 | 1,000 | 0.001364 |
| 3,000 | 3,000 | 0.000462 |
| 3,000 | 5,000 | 0.000351 |

This pattern is compatible with an order 1/B finite-reference calibration bias. An analytic bias expansion is a possible later extension, but it is not required to preserve the D1 first-order theorem.

---

## Formal D1 adjudication

### Locked numerical status

**REVIEW**

This status is immutable for D1 numerical validation v1.

### Scientific status

**D1 first-order theory: SUPPORTED**

Supported components:

1. two-bank asymptotic variance decomposition;
2. complete-vector preservation of reference-bank dependence;
3. bootstrap estimation of the total two-bank standard error;
4. material contribution of reference-bank uncertainty;
5. convergence toward the theoretical benchmark as B increases.

Not uniformly validated:

1. finite-sample basic bootstrap interval coverage;
2. the smallest reference-bank/deep-threshold cells;
3. a claim of uniformly accurate inference over all declared B and alpha settings.

### Consequence for Work Package D2

D2 may proceed. Its independently locked protocol should:

- use influence-function normal or bootstrap-normal inference as the primary regular interval;
- retain percentile intervals as a secondary method;
- retain the basic interval as a finite-sample diagnostic rather than the primary method;
- make B >= 3,000 the main validation regime;
- retain B = 500 and B = 1,000 as stress-test regimes;
- evaluate finite-reference order-statistic effects explicitly at alpha = 0.01;
- preserve complete-replication resampling within both banks.

These choices are prospective adaptations informed by D1 and must be declared before the D2 scientific run.

---

## Preservation rule

The following materials should be retained in Git:

- this post-run adjudication;
- D1 validation summary;
- D1 validation checks;
- cell-level summary;
- original automatic adjudication;
- validation manifest;
- full-run log;
- a results-freeze manifest containing SHA-256 hashes.

The full replication-level output should be stored in an external deterministic archive with its SHA-256 recorded in Git. The locked D1 configuration, code, and lock tag must not be modified.

Recommended result tag:

```text
tess-theory-work-package-d1-v1-results-review-20260802
```

Recommended commit message:

```text
Add D1 two-bank numerical validation review results
```
