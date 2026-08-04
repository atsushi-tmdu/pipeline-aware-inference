# Work Package D7 Protocol

## Maximum-score activation trigger for finite-candidate inference

**Status:** mathematically completed draft after runtime-only preflight; not locked

**Parent:** Work Package D6
**Parent lock tag:** `tess-theory-work-package-d6-v1-lock-20260803`

# 1. Purpose

D7 replaces the separate scalar activation score used in D4-D6 with the actual
base-stage maximum,

\[
T(X)=\max_{j\in\mathcal J_0}X_j=X_{J_0(X)}.
\]

The activation rule becomes

\[
A(c)=I\{T(X)>c\}.
\]

D7 retains fixed finite nested candidate pools, candidate-specific calibration,
almost-surely unique winners, the paired adaptive-versus-budget-matched-random
contrast, and complete-vector two-bank resampling.

D7 excludes deterministic trigger-tie randomization, failed-fit fallback,
growing candidate dimension, and simultaneous alpha-process inference.

# 2. Model

Let

\[
\mathcal J_0\subset\mathcal J_1=\{1,\ldots,K\}
\]

be fixed finite candidate pools. Each complete replication is

\[
X=(X_1,\ldots,X_K).
\]

For branch \(b\),

\[
J_b(X)=\operatorname*{arg\,max}_{j\in\mathcal J_b}X_j,
\qquad
R_b(q)=I\{X_{J_b(X)}>q_{J_b(X)}\}.
\]

The base maximum is

\[
T(X)=X_{J_0(X)}.
\]

Reference and evaluation banks are independent i.i.d. samples of the complete
candidate-score vector.

# 3. Calibration and policy

Let \(p=1-\alpha\) and \(s=1-r\). Define

\[
q_j=F_j^{-1}(p),
\qquad
c=F_T^{-1}(s).
\]

Both the candidate thresholds and the maximum-trigger threshold are estimated
from the same complete-vector reference bank.

Define

\[
M(q)=\{1-R_0(q)\}R_1(q),
\]

\[
H_A(q,c)=R_0(q)+A(c)M(q).
\]

With

\[
e_0=E(R_0),\quad
\rho=E(A),\quad
\mu=E(M),\quad
\nu=E(AM),
\]

the paired rejection contrast remains

\[
\boxed{
\Delta_\pi=\nu-\rho\mu=\operatorname{Cov}(A,M).
}
\]

# 4. Candidate-threshold derivatives

D7 retains the D6 exact candidate jump field

\[
D_j
=
I\{j\in\mathcal J_0,J_0=j,J_1\ne j\}R_1
-
I\{j\in\mathcal J_1\setminus\mathcal J_0,J_1=j\}(1-R_0).
\]

Because \(A\) depends on the raw score vector but not on \(q\),

\[
\beta_j^\Delta
=
E\{(A-\rho)D_j\mid X_j=q_j\}.
\]

# 5. Maximum-trigger boundary

Up to the null winner-tie set,

\[
\{T=c\}
=
\bigcup_{j\in\mathcal J_0}\{J_0=j,X_j=c\}.
\]

Hence

\[
f_T(c)
=
\sum_{j\in\mathcal J_0}
f_j(c)P(J_0=j\mid X_j=c),
\]

and

\[
f_T(c)E(M\mid T=c)
=
\sum_{j\in\mathcal J_0}
f_j(c)E\{MI(J_0=j)\mid X_j=c\}.
\]

The trigger coefficient is

\[
\boxed{
\beta_c^\Delta=\mu-E(M\mid T=c).
}
\]


# 6. Formal regularity assumptions

## D7-A1. Fixed finite nested pools

The candidate dimension and both candidate pools are fixed.

## D7-A2. Independent complete-vector banks

Reference and evaluation banks are independent i.i.d. samples of complete
candidate-score vectors.

## D7-A3. Almost-sure unique winners

Pairwise candidate-score ties have probability zero.

## D7-A4. Regular candidate quantiles

Candidate densities are continuous, positive, and finite at the required
thresholds.

## D7-A5. Regular maximum quantile

The base-maximum density is continuous, positive, and finite at the trigger
threshold.

## D7-A6. Smooth boundary probabilities

Candidate and maximum-trigger boundary conditional expectations admit locally
continuous versions.

## D7-A7. Strict threshold separation

Every base-candidate threshold differs from the maximum-trigger threshold.

## D7-A8. Negligible distinct-boundary intersections

Distinct candidate-boundary slabs have product-order intersection
probabilities, and winner-tie surfaces are null.

## D7-A9. Fixed declared policy

Candidate order, pool nesting, alpha, activation rate, score directions,
quantile conventions, and comparator construction are fixed independently of
both banks.

## D7-A10. Interior TESS domain

The two policy rejection probabilities remain bounded away from one.

---

# 7. Influence targets

The reference influence function is

\[
\boxed{
\phi_R^\Delta
=
\sum_{j=1}^K
\beta_j^\Delta\{p-I(X_j^R\le q_j)\}
+
\beta_c^\Delta\{s-I(T^R\le c)\}.
}
\]

The evaluation influence function is

\[
\boxed{
\phi_E^\Delta=(A-\rho)(M-\mu)-\Delta_\pi.
}
\]

Complete-vector resampling is required because candidate quantiles, the maximum
quantile, winner identities, and all policy states are dependent.

# 8. Main theorem targets

1. Maximum-density winner-region decomposition.
2. Joint differentiability under threshold separation.
3. Two-bank asymptotic linearity.
4. TESS-scale delta-method expansion.
5. Complete-replication two-bank bootstrap validity.
6. Candidate-wise plus-one bridge with the maximum trigger held paired.
7. Threshold-coincidence directional nonregularity.

# 9. Coincidence boundary

Suppose \(q_j=c\) for a base candidate. On the region where \(j\) wins the
base pool but another candidate wins the full pool, the adaptive incremental
term locally contains

\[
I(T>c)I(T\le q_j)R_1.
\]

For perturbations \(h_j,h_c\), this contributes

\[
\boxed{
\kappa_j(h_j-h_c)_+,
}
\]

where

\[
\kappa_j
=
f_j(c)
E\{I(J_0=j,J_1\ne j)R_1\mid X_j=c\}.
\]

If \(\kappa_j>0\), the derivative is directional but not linear. The ordinary
influence-function expansion and ordinary bootstrap must not be presumed valid.

This is a threshold-coincidence problem, not a winner tie.

# 10. Empirical audit before lock

Before D7 numerical lock, record from the frozen empirical reference banks:

- the maximum-trigger threshold;
- all base candidate thresholds over the alpha grid;
- \(\min_j|q_j-c|\);
- the ordering of \(c\) relative to the candidate thresholds;
- exact trigger ties;
- the number affected by deterministic trigger-tie randomization.

# 11. Numerical plan

The future numerical protocol must separate:

- regular cells with \(c<q_j\);
- regular cells with \(c>q_j\);
- near-coincidence sequences;
- exact-coincidence nonregular diagnostics.

Exact-coincidence cells must not be pooled with regular coverage criteria.

# 12. Scope

D7 establishes only the continuous maximum-trigger bridge. It does not yet
establish exact validity for discrete AUROC triggers, deterministic tie
randomization, failed-fit fallback, or growing candidate libraries.

# 13. Directional-derivative guardrail

At a coincidence \(q_j=c\), the full directional derivative contains both:

- the ordinary linear contributions from noncoincident candidate boundaries,
  the marginal activation rate, and the incremental-rejection probability;
- the nonadditive coincidence contribution
  \[
  \kappa_j(h_j-h_c)_+.
  \]

The displayed positive-part term is the obstruction to ordinary
differentiability. It is not intended to represent the entire directional
derivative by itself.

# 14. Empirical-audit outcome

The historical 20-candidate raw banks supported strict candidate/trigger
threshold separation over the declared alpha grid. They did not show exact
threshold coincidence or a pair within one local discrete score spacing.

The same banks contained a small but positive number of base-winner ties.
Because no available raw bank matched the current confirmatory manifest hashes,
the audit is diagnostic rather than a formal empirical bridge.

The D7 scientific design will therefore validate the continuous
unique-winner, separated-threshold theorem. Discrete winner ties and the
declared tie-breaking rule remain outside D7.
