# Work Package D6 Numerical Validation Protocol

## Fixed-finite-candidate unique-winner two-bank inference

**Status:** locked after runtime-only smoke and before scientific computation

**Theory parent:** `D6_THEORY_MEMO.md`
**Parent validated results:** `d4-validation-full-v1`,
`d5-validation-full-v1`

---

# 1. Purpose

This protocol prospectively defines the scientific numerical validation of the
D6 fixed-finite-candidate unique-winner theory.

The validation has five targets:

1. finite-candidate two-bank asymptotic linearity;
2. separation of reference- and evaluation-bank variance;
3. complete-replication two-bank bootstrap validity;
4. fixed-finite-\(K\) quantile-versus-plus-one equivalence;
5. preservation of the nested-pool winner-region identities.

This protocol does not validate:

- a maximum-score activation trigger;
- positive-probability winner ties;
- deterministic tie randomization;
- failed-fit fallback rules;
- candidate dimension increasing with bank size;
- simultaneous inference over an alpha interval.

---

# 2. Validation architecture

The scientific validation has two layers.

## 2.1 Full asymptotic grid

Every declared data-generating process, alpha value, and bank-size design is
used to evaluate:

- bias;
- empirical variance;
- influence-function variance;
- reference/evaluation variance decomposition;
- normal interval coverage;
- paired quantile-versus-plus-one discrepancy;
- winner and boundary identities.

## 2.2 Prespecified bootstrap subset

Complete-replication two-bank bootstrap validation is performed on a smaller
prespecified subset of representative cells.

This separation is computational only. The bootstrap cells are fixed before
the scientific run and are not chosen from favorable outcomes.

---

# 3. Fixed candidate architectures

## 3.1 Transparent three-candidate architecture

\[
K_0=2,
\qquad
K_1=3.
\]

The complete vector is

\[
(U,X_1,X_2,X_3).
\]

This architecture provides transparent winner-region boundary diagnostics and
direct continuity with the runtime-only derivative preflight.

## 3.2 Empirical-scale architecture

\[
K_0=7,
\qquad
K_1=20.
\]

The first seven candidates form the base pool and all twenty form the full
pool.

The candidate dimension is fixed throughout the scientific validation.

---

# 4. Data-generating processes

All scientific DGPs are continuous multivariate Gaussian constructions.
Consequently, candidate winners are unique almost surely.

Candidate marginals are deliberately heterogeneous. Candidate-specific
calibration therefore cannot be replaced by one common threshold.

## 4.1 `transparent_k3`

Use the explicit four-dimensional Gaussian law

\[
E(U,X_1,X_2,X_3)
=
(0,0,0.08,0.15),
\]

with marginal standard deviations

\[
(1,1,0.9,1.1)
\]

and correlation matrix

\[
\begin{pmatrix}
1 & 0.55 & -0.20 & 0.65\\
0.55 & 1 & 0.35 & 0.25\\
-0.20 & 0.35 & 1 & -0.15\\
0.65 & 0.25 & -0.15 & 1
\end{pmatrix}.
\]

This DGP is retained without modification after its runtime-only derivative
preflight.

## 4.2 `gain_coupled_k20`

Use independent standard-normal latent variables:

- activation factor \(H\);
- global candidate factor \(G\);
- one base-block factor;
- three optional-block factors;
- candidate-specific residuals.

The standardized activation score is

\[
U=0.75H+\sqrt{1-0.75^2}\,\varepsilon_U.
\]

For base candidates \(j=1,\ldots,7\), the standardized candidate component is

\[
Z_j
=
0.10H+0.45G+0.55B_0
+
\sqrt{1-0.10^2-0.45^2-0.55^2}\,\varepsilon_j.
\]

For optional candidates \(j=8,\ldots,20\),

\[
Z_j
=
0.55H+0.45G+0.30B_{1+(j-8\bmod 3)}
+
\sqrt{1-0.55^2-0.45^2-0.30^2}\,\varepsilon_j.
\]

This construction makes high activation scores preferentially align with the
optional family, creating a prespecified gain-coupled mechanism.

## 4.3 `loss_coupled_k20`

Use independent standard-normal latent variables:

- activation factor \(H\);
- global candidate factor \(G\);
- two base-block factors;
- four optional-block factors;
- candidate-specific residuals.

Again,

\[
U=0.75H+\sqrt{1-0.75^2}\,\varepsilon_U.
\]

For base candidates,

\[
Z_j
=
0.55H+0.25G+0.35B_{j\bmod 2}
+
\sqrt{1-0.55^2-0.25^2-0.35^2}\,\varepsilon_j.
\]

For optional candidates,

\[
Z_j
=
-0.30H+0.20G+0.55B_{2+(j-8\bmod 4)}
+
\sqrt{1-0.30^2-0.20^2-0.55^2}\,\varepsilon_j.
\]

This construction makes high activation scores preferentially align with the
base family and low activation scores with the optional family, creating a
prespecified loss-coupled mechanism.

## 4.4 Candidate marginal heterogeneity

For each \(K=20\) construction, candidate \(j=1,\ldots,20\) has

\[
m_j
=
0.06\sin(2\pi j/20)
+
0.02\{(j-1\bmod 3)-1\},
\]

and

\[
\sigma_j
=
0.85+0.05\{(j-1\bmod 5)\}.
\]

The observed candidate score is

\[
X_j=m_j+\sigma_jZ_j.
\]

No DGP coefficient may be altered after numerical lock.

---

# 5. Thresholds and policy

The local thresholds are

\[
\alpha\in\{0.01,0.05,0.10\}.
\]

The target activation rate is

\[
r=0.50.
\]

For every candidate,

\[
q_j(\alpha)=F_j^{-1}(1-\alpha),
\]

and

\[
c=F_U^{-1}(1-r).
\]

The reference bank estimates all candidate thresholds and the scalar activation
threshold using the declared generalized-inverse convention.

The evaluation bank computes:

- base and full winners;
- candidate-specific branch rejections;
- activation;
- incremental rejection;
- adaptive rejection;
- the evaluation-rate-matched comparator;
- rejection and TESS contrasts.

The comparator uses the realized evaluation-bank activation rate and realized
incremental-rejection rate, exactly as in D4.

---

# 6. Bank-size grid

Use

\[
(B,n)\in
\{
(500,500),
(1000,1000),
(3000,3000),
(3000,5000)
\}.
\]

The \(500/500\) cells are finite-sample stress diagnostics.

The main asymptotic regime is:

- \(B,n\ge1000\) for \(\alpha\in\{0.05,0.10\}\);
- \(B,n\ge3000\) for \(\alpha=0.01\).

There are

\[
3\times3\times4=36
\]

full-grid cells.

---

# 7. Population benchmarks

Population quantities are calculated independently of the outer Monte Carlo
replications.

## 7.1 Unconditional benchmark

For each DGP, use \(2^{22}=4,194,304\) independent benchmark draws, generated
in deterministic batches from the frozen benchmark seed.

Estimate:

- \(e_0,\rho,\mu,\nu\);
- \(\pi_A,\pi_C,\Delta_\pi,\Delta_S\);
- evaluation influence-function variance;
- winner frequencies;
- relevant event probabilities.

## 7.2 Conditional boundary benchmarks

For each candidate boundary and the activation boundary, use
\(2^{19}=524,288\) conditional-Gaussian draws.

Estimate:

- every \(\beta_j^\Delta,\beta_j^A,\beta_j^C\);
- \(\beta_c^\Delta,\beta_c^A,\beta_c^C\);
- reference influence-function variance;
- reference/evaluation covariance components internal to each complete vector.

## 7.3 Benchmark uncertainty

All benchmark calculations are divided into 32 deterministic batches.

Benchmark Monte Carlo standard errors must be retained and propagated into
bias and variance-comparison diagnostics. Benchmark uncertainty is not silently
treated as zero.

---

# 8. Outer Monte Carlo design

The locked full-grid outer repetition count is

\[
R_{\mathrm{full}}=2000
\]

per cell.

This count was retained after runtime-only smoke profiling. It may not be
changed without creating a new D6 numerical-protocol version.

Every outer replication independently generates:

1. one complete-vector reference bank;
2. one independent complete-vector evaluation bank;
3. the regular quantile estimator;
4. the exact candidate-wise plus-one estimator;
5. the influence-function variance estimate;
6. the evaluation-only variance estimate as a negative diagnostic.

---

# 9. Prespecified bootstrap cells

Bootstrap validation uses the following twelve cells.

## 9.1 Alpha 0.05 across balanced and asymmetric designs

For all three DGPs:

\[
\alpha=0.05,
\qquad
(B,n)\in\{(1000,1000),(3000,5000)\}.
\]

This gives six cells.

## 9.2 Tail variation at the largest design

For all three DGPs:

\[
(B,n)=(3000,5000),
\qquad
\alpha\in\{0.01,0.10\}.
\]

This gives six additional cells.

The locked bootstrap design is:

\[
R_{\mathrm{boot}}=500
\]

outer datasets per bootstrap cell and

\[
M_{\mathrm{boot}}=249
\]

bootstrap resamples per outer dataset.

These counts were retained after runtime-only smoke profiling and may not be
changed without a new D6 numerical-protocol version.

---

# 10. Complete-replication bootstrap

Reference and evaluation banks are resampled independently.

Within each reference bootstrap draw:

- one integer weight is assigned to each complete reference replication;
- that weight is shared across \(U,X_1,\ldots,X_K\);
- all candidate thresholds are recomputed;
- the activation threshold is recomputed.

Within each evaluation bootstrap draw:

- one integer weight is assigned to each complete evaluation replication;
- all candidate scores and the activation score retain the same weight;
- winner identities and all policy-state quantities are re-evaluated;
- adaptive, comparator, rejection-contrast, and TESS-contrast estimates are
  recomputed.

The primary bootstrap interval is the centered bootstrap-normal interval.

Percentile intervals are secondary. Basic intervals are diagnostic only.

---

# 11. Exact plus-one comparison

The regular and exact modes use the same:

- DGP draw;
- reference bank;
- evaluation bank;
- winner identities;
- activation threshold;
- comparator construction.

Only the candidate rejection boundaries differ.

The implementation must verify pathwise that every regular-versus-plus-one
policy disagreement is contained in the union of the candidate-specific
adjacent order-statistic intervals.

The primary bridge quantities are:

- signed paired rejection-contrast difference;
- signed paired TESS-contrast difference;
- RMS differences;
- first-order-SE-standardized RMS differences;
- disagreement probability;
- candidate-interval union probability.

---

# 12. Seeds

Use the following frozen seed roots.

- population benchmarks: `20261213`
- full-grid outer Monte Carlo: `20261217`
- bootstrap outer datasets: `20261219`
- bootstrap resampling: `20261223`
- runtime-only smoke: `20261229`

Full-grid outer replication \(m\) uses

```text
SeedSequence([
  20261217,
  dgp_index,
  alpha_index,
  design_index,
  m
])
```

Bootstrap outer datasets and bootstrap resamples use separate corresponding
seed roots.

No seed may be reused between reference and evaluation banks.

---

# 13. Recorded quantities

For every full-grid cell, record:

- empirical mean and bias of \(\widehat\Delta_\pi\);
- empirical mean and bias of \(\widehat\Delta_S\);
- empirical variances;
- mean estimated influence variances;
- exact benchmark influence variances;
- reference and evaluation variance shares;
- normal interval coverage;
- evaluation-only interval coverage;
- quantile and plus-one estimates;
- paired bridge differences;
- winner frequencies;
- observed exact ties;
- identity and support-check errors;
- Monte Carlo standard errors.

For bootstrap cells, additionally record:

- mean bootstrap standard error;
- bootstrap-SD/empirical-SD ratio;
- centered bootstrap-normal coverage;
- percentile coverage;
- basic interval coverage as diagnostic;
- bootstrap failure counts;
- nonfinite result counts.

---

# 14. Fatal implementation checks

The scientific run is invalid if any of the following occurs:

1. a covariance or factor construction is not positive definite;
2. a declared candidate score is nonfinite;
3. an exact winner tie is observed under the continuous generator;
4. the base pool is not nested in the full pool;
5. the direct and winner-region branch maps disagree;
6. the covariance identity fails beyond \(10^{-12}\);
7. the vectorized candidate-jump field disagrees with direct perturbation;
8. a quantile-versus-plus-one disagreement falls outside the declared interval
   union;
9. reference and evaluation seeds overlap;
10. a bootstrap resample breaks complete-vector weighting;
11. a required output is missing or empty;
12. a locked manifest or config hash differs.

Any fatal failure gives overall status `FAIL`.

---

# 15. Scientific success criteria

The success criteria are evaluated only after all fatal checks pass.

## 15.1 Bias

In every main-regime cell, the absolute rejection-contrast bias divided by the
exact total asymptotic standard deviation must not exceed 0.20.

The median absolute standardized bias across main-regime cells must not exceed
0.10.

The same criteria apply to the TESS contrast.

## 15.2 Influence variance

For every main-regime cell,

\[
0.80
\le
\frac{\text{empirical variance}}
     {\text{exact influence variance}}
\le
1.20.
\]

The median ratio across main-regime cells must lie in

\[
[0.90,1.10].
\]

The same criteria apply to rejection and TESS contrasts.

## 15.3 Influence-normal coverage

For every main-regime cell, nominal 95% influence-normal coverage must lie in

\[
[0.92,0.98].
\]

The mean main-regime coverage must lie in

\[
[0.94,0.96].
\]

## 15.4 Bootstrap standard errors

Across the twelve bootstrap cells,

\[
0.85
\le
\frac{\text{mean bootstrap SD}}
     {\text{empirical SD}}
\le
1.15
\]

in at least eleven cells, and the median ratio must lie in

\[
[0.90,1.10].
\]

## 15.5 Bootstrap coverage

Centered bootstrap-normal coverage must lie in

\[
[0.91,0.99]
\]

for every bootstrap cell, with mean coverage in

\[
[0.935,0.965].
\]

Because \(R_{\mathrm{boot}}=500\) is smaller than the full-grid repetition
count, the wider per-cell tolerance is prespecified.

## 15.6 Plus-one bridge

All pathwise support identities must pass.

Across the nine DGP-by-alpha sequences, the median
first-order-SE-standardized RMS discrepancy at the largest reference-bank
design must be smaller than at \(B=500\).

At least eight of the nine individual sequences must not increase by more than
25%.

The bridge magnitude is reported even when these criteria pass.

## 15.7 Reference-bank uncertainty diagnostic

Evaluation-only coverage is descriptive and not a primary success criterion.

Whenever the exact reference variance share is at least 0.20, evaluation-only
coverage must not be reported as a valid two-bank interval.

---

# 16. Magnitude labels

The following labels describe, but do not determine, scientific PASS or FAIL.

For a plus-one RMS difference divided by total first-order SD:

- `<0.10`: negligible;
- `0.10-0.25`: small;
- `0.25-0.50`: material;
- `>0.50`: large.

For reference variance share:

- `<0.10`: minor;
- `0.10-0.30`: meaningful;
- `>0.30`: major.

---

# 17. Runtime-only smoke

Before lock, a smoke configuration may use:

- reduced benchmark draws;
- 8 full-grid outer repetitions per cell;
- 4 bootstrap outer datasets per bootstrap cell;
- 19 bootstrap resamples.

Smoke output is computational debugging only.

Scientific settings may be changed after smoke solely for runtime, memory, or
software-correctness reasons. They may not be changed in response to favorable
or unfavorable scientific estimates.

---

# 18. Lock procedure

Before scientific execution:

1. complete the validation implementation;
2. run all unit tests;
3. run the runtime-only smoke;
4. document runtime and memory;
5. finalize repetition and bootstrap counts;
6. rename the draft numerical config to its locked name;
7. generate a SHA-256 manifest;
8. verify Git cleanliness;
9. commit and annotate the numerical lock tag;
10. verify that the tag resolves to the lock commit;
11. only then run scientific validation.

The scientific output directory must remain ignored until a compact results
freeze is prepared after adjudication.

---

# 19. Scope statement

A D6 scientific PASS supports only the fixed-finite-candidate,
continuous-unique-winner, separate-scalar-trigger theory.

It is not direct evidence for the complete empirical 20-candidate pipeline
until the maximum-score trigger, deterministic tie rule, and failed-fit rule
are addressed.

---

# 20. Lock completion record

The runtime-only smoke passed with 288 full-grid rows, 48 bootstrap outer rows,
and no fatal implementation failures. The prospective scientific counts were
retained without reduction.

The locked scientific configuration is `D6_NUMERICAL_CONFIG.json`. The
scientific runner verifies `D6_LOCK_MANIFEST_SHA256.txt` before execution.
