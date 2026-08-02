# SUPPORT2-Anchored TESS Supplementary Validation v1

**Status:** LOCKED BEFORE SCIENTIFIC RUN  
**Study ID:** `TESS_SUPPORT2_VALIDATION_V1`  
**Configuration SHA-256:** `eb89a6b42b0ea080c689aae37c3476ac9338f9bd5f923d41bb9ca8e9e552f2da`

## 1. Purpose and role

The primary TESS adaptive-policy simulation has already been prospectively
locked, completed, and confirmed. This additional study is not a replacement
primary analysis and cannot overturn or redefine that result.

Its purpose is narrower: determine whether the adaptive allocation effect is
also observed under a real clinical covariate and missing-data structure.
SUPPORT2 supplies the observed covariates; the global null is imposed by
permuting the in-hospital-death outcome.

The study is described as a **real-data-anchored global-null experiment** or a
**semi-synthetic clinical-data validation**, not as external clinical
validation and not as an ordinary prognostic-model application.

## 2. Data source

The SUPPORT2 dataset contains 9,105 seriously ill hospitalized adults. The
analysis outcome is `hospdead` (in-hospital death).

Primary source:

```text
https://hbiostat.org/data/repo/support2csv.zip
```

Fallback retrieval uses UCI dataset ID 880. The prepared analysis file is
canonicalized locally and its SHA-256 is recorded in a committed data manifest
before the scientific run.

Required acknowledgment:

> Data obtained from hbiostat.org/data courtesy of the Vanderbilt University
> Department of Biostatistics.

## 3. Predictors

### Numeric

age, num.co, scoma, meanbp, wblc, hrt, resp, temp, pafi, alb, bili, crea, sod, ph, glucose, bun, urine

### Categorical

sex, dzgroup, ca, diabetes, dementia

The prior SUPPORT/APACHE scores (`aps`, `sps`, `surv2m`, `surv6m`), physician
prognoses, DNR variables, outcomes, follow-up variables, costs, and
post-baseline summaries are excluded. Variables are not added or removed after
locking.

## 4. Fixed data structure

A single stratified fixed split is created before any outcome permutations:

- training observations: **500**
- selection observations: **2,000**
- split seed: **20260901**

The remaining SUPPORT2 observations are unused. The experiment is conditional
on this fixed observed covariate and missingness structure.

Numeric preprocessing is training-set median imputation with missingness
indicators followed by standardization. Categorical preprocessing is
training-set most-frequent imputation followed by one-hot encoding.
Preprocessing is outcome-independent, so it is fitted once to the frozen
training covariates and reused for all outcome permutations; this is
algebraically equivalent to refitting the same deterministic preprocessing in
each replication.

## 5. Global-null generation

Within every replication, `hospdead` is independently permuted within the
fixed training set and within the fixed selection set. This preserves the
observed number of deaths in each set while breaking all association between
predictors and outcome.

Banks:

- null-reference bank: **3,000 replications**, seed `20260903`
- independent evaluation bank: **5,000 replications**, seed `20260907`

The same permuted labels are used for all 20 candidates within a replication.

## 6. Candidate library

The first seven prespecified candidates are the base family. The remaining 13
form the optional expansion family. The full order and hyperparameters are
stored in `configs/ess/support2_validation_v1.json` and may not be altered
after lock.

The base family contains regularized logistic and linear-SVM candidates. The
optional family adds further linear regularization, RBF SVMs, trees,
ensembles, Gaussian naive Bayes, and k-nearest neighbors.

## 7. Failed fits

A failed fit is not deleted or replaced. Its selection ROC AUC is set to 0.5,
and the failure type and message are retained. Every failure count is reported.
A nonzero failure count generates a technical warning but does not authorize a
change to the candidate library.

## 8. Adaptive policies

The activation statistic is the maximum selection ROC AUC among the seven base
candidates. The promising threshold is calibrated only in the independent
reference bank to target an expansion probability of 0.50, including the
predefined deterministic tie rule.

Policies:

1. fixed base, K=7
2. fixed full, K=20
3. random expansion
4. promising-triggered expansion
5. rescue-triggered expansion

Budget-standardized random benchmarks are computed from the fixed-base/full
incremental rejection effect at the observed activation rate.

## 9. Primary supplementary estimand

At alpha 0.05:

\[
\Delta_{\mathrm{SUPPORT2}}
=
\mathrm{TESS}_{\mathrm{promising}}
-
\mathrm{TESS}_{\mathrm{random,matched}}.
\]

The SUPPORT2 result is called supportive when the two-sided paired-bootstrap
95% confidence interval has a lower bound greater than zero.

This rule concerns supplementary support only. The result is reported whether
positive, null, or negative, and it does not change the adjudication of the
already completed primary confirmatory study.

## 10. Secondary estimands

- promising-policy effect on the rejection-probability scale
- covariance between activation and incremental rejection effect
- rescue minus its budget-matched random benchmark
- gain-capture fraction
- TESS curves at alpha 0.10, 0.025, and 0.01
- alpha 0.005 is extreme-tail exploratory output

Paired bootstrap repetitions: **20,000**, seed `20260913`.

## 11. Technical integrity requirements

- exact expected replication-by-candidate row count
- exactly 20 unique candidates and 7 base candidates
- no duplicate replication/candidate rows
- finite selection ROC AUC for every row after applying the failed-fit rule
- finite policy p-values
- promising/rescue decomposition identity errors below numerical tolerance
- data SHA-256 equals the committed data manifest
- clean `ess-study` working tree at the full-run preflight

## 12. Prohibited post-lock changes

No result-dependent modification of predictors, split, seeds, repetition
counts, candidate order, hyperparameters, base/extra allocation, alpha,
primary estimand, supportive rule, or failed-fit rule is permitted.

Any unavoidable software correction must be documented, committed separately,
and justified without reference to whether the observed SUPPORT2 result became
more favorable.

## 13. Output locations

Raw permutation model banks:

```text
results_ess_support2/validation_v1_seed20260903/
```

Processed results:

```text
simulations/ess/outputs/support2_validation_v1/
```

Final adjudication:

```text
simulations/ess/outputs/support2_validation_v1/SUPPORT2_VALIDATION_ADJUDICATION.md
```
