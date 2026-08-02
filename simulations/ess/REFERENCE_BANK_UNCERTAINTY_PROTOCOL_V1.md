# TESS Reference-Bank Uncertainty Sensitivity v1

**Status:** LOCKED BEFORE EXECUTION
**Analysis label:** Post hoc sensitivity
**Primary adjudication:** Unchanged
**Configuration SHA-256:** `a8c8d1293675f89187703d52b12aa0a59b99822712814ede5e2f47b8b279c500`

## 1. Purpose

The locked primary paired-bootstrap interval resampled the independent evaluation
bank while conditioning on the frozen null-reference bank. The null-reference
bank determines both:

1. the candidate-specific plus-one empirical p-value mappings; and
2. the promising-expansion trigger threshold and threshold-tie probability.

This sensitivity analysis quantifies uncertainty from both finite banks without
refitting a model, generating a new dataset, or changing the locked primary
adjudication.

## 2. Locked estimand

The analysis is restricted to the original primary estimand:

- library: `mixed_realistic_20`
- local alpha: `0.05`
- contrast: promising-triggered TESS minus budget-matched random TESS

The recomputed raw-bank point estimate must match `0.7949499185` within
`1e-8` before bootstrap execution is permitted.

## 3. Source evidence

Source confirmatory tag:

```text
tess-confirmatory-policy-v1-final-20260802
```

Required frozen files from the mixed-realistic confirmatory run:

```text
candidate_library_manifest.csv
null_reference_model_metrics.csv
evaluation_model_metrics.csv
```

No candidate order, score, failed-fit value, or replication is altered.

## 4. Two-bank resampling scheme

For each of 20,000 bootstrap repetitions:

1. Draw 5,000 null-reference replication IDs with replacement.
2. Give every candidate score from the same reference replication one shared
   integer bootstrap weight. This preserves within-replication dependence
   across all 20 candidates.
3. Reconstruct every candidate-specific plus-one empirical upper-tail p-value
   mapping from the weighted reference bank.
4. Recalibrate the promising trigger threshold and exact threshold-tie
   probability from the weighted reference base-stage maxima.
5. Draw 5,000 evaluation replication IDs with replacement.
6. Give all quantities from the same evaluation replication one shared
   bootstrap weight.
7. Recompute promising activation, fixed-base and fixed-full rejection,
   promising-policy rejection, and the budget-matched random benchmark at the
   realized weighted activation rate.
8. Transform the two rejection probabilities to TESS and save their difference.

Reference and evaluation resampling are independent. Pairing across candidates
and policies is retained within each bank.

## 5. Randomness and interval

- bootstrap seed: `20260829`
- bootstrap repetitions: `20,000`
- interval: two-sided percentile 95%
- checkpoint interval: every 250 repetitions

## 6. Interpretation rule

- `ROBUST`: two-bank 95% CI lower bound is greater than zero.
- `INCONCLUSIVE_SENSITIVITY`: two-bank 95% CI includes or crosses zero.

The locked primary result remains `CONFIRMED` in either case. This analysis is a
post hoc uncertainty sensitivity and is not a new confirmatory adjudication.

## 7. Outputs

```text
simulations/ess/outputs/reference_bank_uncertainty_v1/
```

Expected files:

```text
reference_bank_uncertainty_bootstrap_replicates.csv
reference_bank_uncertainty_summary.csv
reference_bank_uncertainty_summary.json
REFERENCE_BANK_UNCERTAINTY_SENSITIVITY.md
reference_bank_uncertainty_manifest.json
preflight_manifest.json
```

## 8. Prohibited changes after locking

Do not change the library, alpha, estimand, bootstrap count, bootstrap seed,
resampling units, candidate order, base/optional split, trigger rule, tie rule,
or failed-fit rule after this protocol and code are committed and tagged.

Any software correction must be documented and must not depend on the observed
sensitivity result.
