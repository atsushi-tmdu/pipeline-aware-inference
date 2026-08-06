# D8-A Literature and Novelty Audit v1

## 1. Audit scope

This audit examined primary research sources relevant to:

1. empirical-quantile representations and finite-reference centering;
2. smooth expectation delta methods;
3. directionally differentiable and nondifferentiable functionals;
4. second-order nondifferentiability;
5. adaptive and post-selection analysis;
6. simulation-study design and Monte Carlo uncertainty; and
7. discrete plus-one permutation \(p\)-values.

The audit was focused rather than encyclopedic. It supports careful positioning
but does not justify an absolute priority claim.

## 2. Established prior art

### 2.1 Empirical quantiles

Bahadur (1966) established the classical asymptotic representation of sample
quantiles, and Kiefer (1967) refined the relationship between sample quantiles
and the empirical distribution function. These papers support the first-order
linearization and empirical-process component of Theorem 1.

They do not supply the manuscript's complete result, which additionally retains:

- the exact order-statistic convention \(k_B=\lceil Bp\rceil\);
- the bounded, potentially \(B\)-dependent lattice coefficient;
- complete-vector cross-covariances among several empirical quantiles; and
- propagation through a threshold-adaptive policy map.

The scalar \(B^{-1}\) mean formula itself follows directly from beta
order-statistic moments and inverse-cdf Taylor expansion; it should not be
presented as a general new quantile theorem.

### 2.2 Smooth expectation delta methods

Oehlert (1992) reviews the use of Taylor expansion to approximate moments of
smooth functions. This is the correct reference point for the ordinary
gradient-plus-Hessian expectation formula.

Novelty should not be claimed for the smooth trace term

\[
\frac12\operatorname{tr}(H\Sigma).
\]

The distinctive contribution is its repair at the declared coincidence
boundary and its integration with the finite-reference lattice term.

### 2.3 Nonsmooth and directionally differentiable maps

Shapiro (1991), Dümbgen (1993), and Fang and Santos (2019) establish broad
extended-delta frameworks for directionally differentiable or
nondifferentiable maps, with emphasis on weak limits and bootstrap validity.
Chen and Fang (2019) develop second-order inference when the first derivative
is degenerate and allow second-order nondifferentiability.

Accordingly, the manuscript should not claim:

- the first delta method for a nonsmooth functional;
- the first second-order directionally differentiable expansion; or
- a general bootstrap theory for piecewise-quadratic maps.

The current policy map is unusual in a more specific way: it is first-order
smooth at candidate-threshold coincidence but has one-sided second-order
curvature. The paper derives the resulting expectation-level \(B^{-1}\)
coefficient, including

\[
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a d_a^\top\Sigma_\theta d_a,
\]

for this threshold-adaptive winner-cell structure.

### 2.4 Adaptive and post-selection analysis

Berk et al. (2013), Taylor and Tibshirani (2015), and Dwork et al. (2015)
establish the broader inferential difficulty created by data-dependent
selection and adaptive reuse.

The current paper is not a replacement for selective-inference or adaptive-data
analysis methods. Its target is the finite-sample mean of a declared
two-bank policy functional after its policy class and estimation scheme have
already been specified.

### 2.5 Simulation-study design

Burton et al. (2006) and Morris et al. (2019) support prespecification of aims,
data-generating mechanisms, estimands, methods, performance measures, Monte
Carlo uncertainty, and transparent reporting. The locked design, precision-only
stopping, explicit MCSE adjustment, and separation of formal and raw diagnostics
fit naturally within this literature.

### 2.6 Discrete plus-one \(p\)-values

Phipson and Smyth (2010) emphasize that randomly sampled permutation
distributions generate exact discrete null laws and that zero permutation
\(p\)-values are inappropriate. This supports the manuscript's decision not to
silently transfer the continuous-threshold theory to plus-one empirical
\(p\)-values.

## 3. Closest conceptual comparison

The closest general theoretical literature is the directionally
differentiable delta-method literature. The present work differs along four
dimensions:

1. **Target:** expectation bias rather than only a weak limit or confidence procedure.
2. **First-order status:** the first derivative generally remains nonzero.
3. **Geometry:** the second-order term is a finite sum of policy-derived
   positive-part squares attached to candidate-threshold coincidence.
4. **Two-bank combination:** the reference coefficient is combined with an
   exact evaluation identity, producing separate \(B^{-1}\) and \(n^{-1}\)
   mechanisms and an algebraically determined product term.

A focused search did not identify a prior paper deriving this exact combination
for threshold-adaptive statistical policies. This is a defensible
differentiation statement, but not yet a universal priority claim.

## 4. Recommended novelty language

### Safe language

- “We derive a generalized second-order expectation expansion for the declared
  threshold-adaptive policy class.”
- “At candidate-threshold coincidence, the policy-specific second-order map
  contains positive-part-square terms.”
- “The resulting reference coefficient is combined with an exact finite-\(n\)
  evaluation identity.”
- “Existing directional-delta theory provides the broader nonsmooth
  background; our contribution is the policy-specific expectation coefficient
  and two-bank finite-sample decomposition.”

### Language to avoid

- “We introduce the first nonsmooth second-order delta method.”
- “No previous work has studied second-order nondifferentiability.”
- “The scalar empirical-quantile bias formula is new.”
- “The theory applies to arbitrary adaptive pipelines.”
- “The continuous result automatically covers plus-one permutation
  \(p\)-values.”

### Priority statement

No “first” or “to our knowledge” statement is necessary for the paper to be
strong. If one is later desired, it should be limited to the exact
policy-specific combination and repeated after a database-level search by a
human reviewer.

## 5. Manuscript citation map

| Manuscript location | Citation role |
|---|---|
| Introduction, adaptive analysis | Berk et al. (2013); Taylor and Tibshirani (2015); Dwork et al. (2015) |
| Introduction, quantile linearization | Bahadur (1966); Kiefer (1967) |
| Introduction, smooth moment expansion | Oehlert (1992) |
| Introduction and Discussion, nonsmooth maps | Shapiro (1991); Dümbgen (1993); Fang and Santos (2019); Chen and Fang (2019) |
| Numerical validation | Burton et al. (2006); Morris et al. (2019) |
| Limitations and future plus-one bridge | Phipson and Smyth (2010) |
| Supplement, concentration | Hoeffding (1963) |

## 6. Novelty risk assessment

| Component | Novelty risk | Recommended role |
|---|---:|---|
| Scalar empirical-quantile mean expansion | High risk if claimed new | Supporting lemma |
| Joint complete-vector covariance | Moderate | Necessary technical component |
| Ordinary Hessian–covariance expectation term | High risk if claimed new | Background |
| Positive-part-square winner-cell coefficient | Low-to-moderate | Central theorem |
| Exact divisor-\(n\) covariance identity | Moderate; algebra elementary | Central structural identity, not standalone novelty |
| Combined two-bank decomposition | Low-to-moderate | Main result |
| TESS nonlinear propagation | Moderate | Corollary |
| Prospectively locked validation | Low | Major evidential contribution |

## 7. Overall positioning

The strongest framing is not “a new delta method.” It is:

> A policy-specific finite-sample theory showing how empirical-quantile
> centering, common-reference dependence, candidate-threshold coincidence,
> exact evaluation covariance bias, and nonlinear TESS curvature combine in one
> declared adaptive policy functional.

This positioning is both stronger and safer than a broad methodological
priority claim.
