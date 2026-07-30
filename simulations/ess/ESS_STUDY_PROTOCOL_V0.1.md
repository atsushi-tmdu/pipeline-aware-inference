# Pipeline Effective Search Size (ESS): Study Protocol v0.1

## Working title

**Effective search size after adaptive machine-learning development: a tail-dependent pipeline-level measure of search multiplicity**

## Central problem

Nominal candidate count is not the multiplicity actually induced by a search.
Highly dependent candidates may add little search burden, while heterogeneous
candidate libraries can create much greater tail inflation. A correlation
matrix or eigenvalue participation ratio describes structural dimension, but
does not directly answer the inferential question:

> How many independent prespecified searches would produce the same
> global-null false-positive probability as this complete adaptive pipeline?

## Primary estimand

For a candidate-wise local significance level \(\alpha\), define

\[
\pi(\alpha)
=
P_0\{\text{the pipeline-selected result is naively rejected at level }\alpha\}.
\]

The **tail effective search size** is

\[
ESS(\alpha)
=
\frac{\log\{1-\pi(\alpha)\}}{\log(1-\alpha)}.
\]

Interpretation: \(ESS(\alpha)\) is the number of independent valid searches
that would yield the same global-null rejection probability under a Šidák
model.

Boundary checks:

- one prespecified search: \(ESS(\alpha)=1\);
- \(K\) independent valid searches with minimum-p selection:
  \(ESS(\alpha)=K\);
- exact duplicates: approximately 1;
- dependence and pipeline behavior are allowed to make ESS vary with alpha.

ESS is therefore a **curve**, not necessarily a single constant.

## Distinction from the current manuscript

The current pipeline-aware manuscript uses an eigenvalue participation-ratio
effective candidate count as a descriptive summary of null-performance
dependence. It explicitly does not substitute that count into inference.

The new study should make the inferential quantity itself the target:

1. structural ESS: participation ratio and related correlation summaries;
2. tail ESS: rejection-equivalent, alpha-specific pipeline multiplicity;
3. exact max-statistic calibration: reference inferential procedure.

The main thesis is that (1) need not recover (2), and (2) should not replace
(3) until independently validated.

## Immediate Phase 0: reuse frozen Phase 3C

Use the existing null results for:

- high-dependency linear library, K=7 and K=20;
- mixed-realistic library, K=7 and K=20;
- local alpha = 0.05;
- 2,000 independent null evaluation replications.

The aggregate pilot already indicates that tail ESS is materially larger than
the participation-ratio count, especially for the mixed-realistic K=20
library.

## Phase 1: raw-null ESS curve

The frozen Phase 3C full runs already retain one-row-per-replication naive
p-values in `independent_inference_results.csv`. Therefore, the initial ESS
curve can be estimated without rerunning model fitting. The primary p-value is
`naive_empirical`; `naive_mannwhitney` is a prespecified sensitivity analysis.

Required output from each null replication:

- selected candidate identity;
- selected raw performance;
- candidate-specific naive p-value or naive rejection indicator over an alpha grid;
- complete candidate performance vector;
- fit-failure and tie information.

Prespecified alpha grid:

\[
0.20,\ 0.10,\ 0.05,\ 0.025,\ 0.01,\ 0.005.
\]

Estimate ESS(alpha) with independent uncertainty intervals. Use separate:

- **ESS-estimation null bank**; and
- **evaluation null bank**.

Do not estimate and validate an ESS-based correction on the same null bank.

## Phase 2: controlled simulation design

### Candidate count

K = 1, 3, 7, 20, 50.

### Dependence structures

1. exact duplicates;
2. equicorrelated Gaussian score vectors;
3. block dependence;
4. nested near-duplicate pipelines;
5. realistic linear-only libraries;
6. heterogeneous classical ML libraries;
7. mixed nonlinear libraries.

### Pipeline dimensions

- no feature selection vs LASSO;
- 20, 100, and 500 model-selection events;
- AUROC, average precision, and standardized partial AUROC;
- balanced and low-event-prevalence settings;
- deterministic failed-fit and tie rules.

### Comparators

- nominal K;
- mean pairwise correlation;
- eigenvalue participation ratio;
- Li–Ji effective number;
- Galwey effective number;
- cluster-count summaries;
- tail ESS(alpha);
- exact pipeline max-statistic calibration.

### Primary outcomes

1. error in estimating the observed global-null rejection probability;
2. calibration of an ESS-based approximate adjustment on an independent bank;
3. difference between structural ESS and tail ESS;
4. stability of ESS across alpha, event count, metric, and candidate library;
5. Monte Carlo cost required for stable tail ESS estimation.

## Phase 3: practical approximation question

Only after Phase 2:

\[
p_{\mathrm{ESS}}
=
1-(1-p_{\mathrm{naive}})^{ESS}.
\]

Evaluate whether an ESS estimated from a smaller pilot null bank can
approximate exact pipeline-aware p-values. The exact max-statistic method
remains the reference. A failed approximation result is still scientifically
useful: it would establish ESS as an audit metric rather than a replacement
inferential method.

## Primary hypotheses

1. Tail ESS is substantially smaller than nominal K in highly dependent
   libraries.
2. Tail ESS is larger than the eigenvalue participation-ratio count in
   heterogeneous libraries.
3. ESS depends on alpha; a single constant does not fully characterize
   search multiplicity.
4. Increasing K with near-duplicate candidates changes structural dimension
   little, but may still increase tail ESS.
5. Exact pipeline max-statistic calibration controls type I error regardless
   of whether a scalar ESS is stable.

## Recommended first manuscript figure set

1. **ESS curves:** ESS(alpha) across candidate libraries and K.
2. **Structural versus inferential ESS:** participation ratio against
   tail ESS at alpha=0.05.
3. **Calibration:** observed versus ESS-predicted global-null rejection.
4. **Scalability:** K versus nominal K, participation ratio, and tail ESS.
5. **Clinical or public-data illustration:** optional and only after the
   simulation estimand is frozen.

## Commands

Copy `simulations/ess/` into the current repository, then run:

```bash
python simulations/ess/pilot_phase3c_aggregate.py --repo-root .
python -m unittest simulations.ess.tests.test_ess_estimators
```

The pilot writes CSV and figure outputs under:

```text
simulations/ess/pilot_outputs/
```
