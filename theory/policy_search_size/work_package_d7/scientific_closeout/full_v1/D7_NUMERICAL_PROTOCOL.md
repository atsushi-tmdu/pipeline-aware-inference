# D7 Continuous Scientific Numerical Validation Protocol

**Status:** prospective draft; not yet numerically locked
**Parent checkpoint:** `d7-theory-prelock-v1`
**Parent commit:** `4f206b3236c8a943d4fc204698189979ca11bf7a`

## 1. Scientific question

Does the D7 two-bank asymptotic expansion and complete-replication bootstrap
accurately describe finite-sample inference when activation is determined by

\[
T=\max_{j\in\mathcal J_0}X_j
\]

in the continuous fixed-finite-candidate, almost-surely unique-winner,
strictly separated-threshold regime?

The formal validation excludes discrete winner ties and exact
candidate/trigger threshold coincidence.

## 2. DGPs

Three multivariate-Gaussian DGPs are fixed:

1. `transparent_k3_max_trigger`;
2. `gain_coupled_k20_max_trigger`;
3. `loss_coupled_k20_max_trigger`.

The two 20-candidate DGPs use a latent-factor covariance construction. In the
gain DGP, the base maximum and extra-library scores share a positive coupling
factor. In the loss DGP, the corresponding loadings have opposite signs.

All covariance matrices, means, pool definitions, and factor loadings are
stored in `D7_DGP_SPECIFICATIONS.json`.

## 3. Trigger construction

For every DGP and alpha, two regular trigger orderings are used.

### Below all candidate thresholds

\[
c
=
\min_{j\in\mathcal J_0}q_j(\alpha)
-
0.25\,\operatorname{median}_{j\in\mathcal J_0}\sigma_j.
\]

### Above all candidate thresholds

\[
c
=
\max_{j\in\mathcal J_0}q_j(\alpha)
+
0.25\,\operatorname{median}_{j\in\mathcal J_0}\sigma_j.
\]

The corresponding trigger quantile probability is calculated from the
multivariate-normal distribution of the base maximum. Reference banks estimate
that quantile prospectively.

This construction guarantees both regular orderings without selecting trigger
rates after observing scientific results.

## 4. Main grid

- DGPs: 3
- alpha values: \(0.01,0.05,0.10\)
- trigger orderings: 2
- \((B,n)\):
  \[
  (1000,1000),\ (3000,3000),\ (3000,5000),\ (5000,5000).
  \]
- outer repetitions: 2,000 per cell

This gives 72 cells and 144,000 main replication rows.

## 5. Bootstrap grid

For every DGP, alpha, and trigger ordering at \(B=n=3000\):

- 500 outer datasets;
- 249 complete-reference and complete-evaluation resamples per dataset.

This gives 18 bootstrap cells and 9,000 outer bootstrap rows.

## 6. Population benchmark

Candidate quantiles are analytic Gaussian marginal quantiles. Trigger
probabilities are computed with a deterministic multivariate-normal CDF.

Policy truths, boundary coefficients, influence-function variances, and TESS
quantities are evaluated using independent locked benchmark streams.

Benchmark precision is a fatal check: its Monte Carlo standard error must be at
most 3% of the smallest corresponding main-grid standard error.

## 7. Near-coincidence diagnostic

A nonadjudicative sequence uses the transparent DGP at alpha \(0.05\), with

\[
c=q_0+\delta\sigma_0,
\]

for

\[
\delta\in
\{-0.20,-0.10,-0.05,-0.025,0.025,0.05,0.10,0.20\}.
\]

These cells study deterioration toward the nonregular boundary but are not
pooled with regular-cell PASS/FAIL criteria.

## 8. Exact-coincidence diagnostic

One transparent-DGP diagnostic sets \(c=q_0\) exactly. Ordinary bootstrap
coverage is reported but prospectively nonadjudicative. The cell is intended
to exhibit the positive-part kink, not to validate the regular theorem.

## 9. Plus-one bridge

Candidate regular empirical quantiles and candidate plus-one thresholds are
computed in paired form in every main replication. The maximum-trigger
construction is held paired. Support violations, RMS bridge size relative to
sampling variation, and sign changes are assessed prospectively.

## 10. Formal decision

Formal PASS requires all fatal implementation checks and all adjudicative
scientific checks in `D7_SCIENTIFIC_CRITERIA.json`.

The two trigger-ordering strata must each pass. Results may not be rescued by
pooling a failing ordering with a passing ordering.

Near- and exact-coincidence diagnostics cannot cause a regular-theorem FAIL and
cannot be used to rescue one.

## 11. Interpretation boundary

Even a successful D7 result will establish only the continuous,
unique-winner, separated-threshold theorem.

It will not validate:

- discrete AUROC winner ties;
- deterministic candidate-tie rules;
- trigger-tie allocation;
- the current empirical policy without an exact raw-bank hash bridge;
- failed-fit fallback;
- growing candidate dimension.
