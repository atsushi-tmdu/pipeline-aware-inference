# Work Package D7 Theory Memo

## Maximum-score activation trigger for finite-candidate policy inference

**Status:** mathematically completed draft after runtime-only preflight; not locked

**Parent theory:** Work Package D6
**Parent lock tag:** `tess-theory-work-package-d6-v1-lock-20260803`

---

# 1. Result

Work Package D7 replaces the separate scalar activation coordinate from D4-D6
with the actual base-stage maximum score,

\[
T(X)=\max_{j\in\mathcal J_0}X_j=X_{J_0(X)}.
\]

Under fixed finite nested candidate pools, continuous almost-surely unique
winners, regular candidate and maximum quantiles, and strict separation between
the maximum-trigger threshold and every base-candidate rejection threshold:

1. the maximum-trigger policy functional is continuously differentiable;
2. the paired rejection contrast has a two-bank asymptotic linear expansion;
3. the reference influence function contains both candidate-quantile and
   maximum-trigger-quantile components;
4. the complete-replication two-bank bootstrap is valid;
5. the fixed-finite-\(K\) candidate plus-one bridge remains first-order
   negligible.

At a threshold coincidence \(q_j=c\), the directional derivative contains the
nonlinear term

\[
\kappa_j(h_j-h_c)_+.
\]

If \(\kappa_j>0\), ordinary linear differentiability fails and the ordinary
bootstrap is not justified by the regular theorem.

---

# 2. Model and estimands

Let

\[
\mathcal J_0\subset\mathcal J_1=\{1,\ldots,K\}
\]

be fixed finite nested candidate pools.

A complete replication is

\[
X=(X_1,\ldots,X_K).
\]

For branch \(b\in\{0,1\}\), define

\[
J_b(X)=\operatorname*{arg\,max}_{j\in\mathcal J_b}X_j.
\]

The base maximum is

\[
T(X)=X_{J_0(X)}.
\]

Let

\[
p=1-\alpha,
\qquad
s=1-r.
\]

Define candidate thresholds

\[
q_j=F_j^{-1}(p)
\]

and the maximum-trigger threshold

\[
c=F_T^{-1}(s).
\]

The branch rejection maps are

\[
R_b(q)=I\{X_{J_b(X)}>q_{J_b(X)}\}.
\]

Activation and incremental rejection are

\[
A(c)=I\{T(X)>c\},
\]

\[
M(q)=\{1-R_0(q)\}R_1(q).
\]

The adaptive rejection indicator is

\[
H_A(q,c)=R_0(q)+A(c)M(q).
\]

Define

\[
e_0=E(R_0),
\quad
\rho=E(A),
\quad
\mu=E(M),
\quad
\nu=E(AM).
\]

Then

\[
\pi_A=e_0+\nu,
\qquad
\pi_C=e_0+\rho\mu,
\]

and

\[
\boxed{
\Delta_\pi
=
\pi_A-\pi_C
=
\nu-\rho\mu
=
\operatorname{Cov}(A,M).
}
\]

For

\[
g_\alpha(\pi)
=
\frac{\log(1-\pi)}{\log(1-\alpha)},
\]

the TESS contrast is

\[
\Delta_S
=
g_\alpha(\pi_A)-g_\alpha(\pi_C).
\]

---

# 3. Assumptions

## D7-A1. Fixed finite nested pools

The candidate dimension \(K\) and both candidate pools are fixed as
\(B,n\to\infty\).

## D7-A2. Independent complete-vector banks

The reference and evaluation banks are independent i.i.d. samples from the law
of the complete candidate-score vector. All within-replication candidate
dependence is retained.

## D7-A3. Almost-sure unique winners

For every distinct \(j,k\in\mathcal J_1\),

\[
P(X_j=X_k)=0.
\]

## D7-A4. Regular candidate quantiles

Every candidate marginal distribution is continuously differentiable near its
required quantile, with density positive and finite there.

## D7-A5. Regular maximum quantile

The distribution of \(T\) is continuously differentiable near \(c\), with
density \(f_T(c)\) positive and finite.

## D7-A6. Smooth boundary probabilities

The candidate-threshold and maximum-trigger boundary conditional expectations
used below admit versions continuous at their required boundaries.

## D7-A7. Strict threshold separation

For every base candidate,

\[
q_j\ne c.
\]

Since the pool is fixed and finite,

\[
\eta
=
\min_{j\in\mathcal J_0}|q_j-c|
>
0.
\]

## D7-A8. Negligible distinct-boundary intersections

Simultaneous slabs around two distinct candidate-threshold surfaces have
product-order probability. Winner-tie surfaces have probability zero.

## D7-A9. Fixed declared policy

Candidate order, pool nesting, alpha, activation rate, score directions,
quantile conventions, and comparator construction are fixed independently of
both banks.

## D7-A10. Interior TESS domain

For the TESS result, \(\pi_A\) and \(\pi_C\) remain in a compact subset of
\([0,1)\).

---

# 4. Winner-region representation of the maximum boundary

For candidate \(j\in\mathcal J_0\), define

\[
\mathcal W_{0j}
=
\{J_0(X)=j\}.
\]

Up to the null winner-tie set,

\[
\{T\in dt\}
=
\sum_{j\in\mathcal J_0}
\{J_0=j,\ X_j\in dt\}.
\]

## Lemma D7.1. Maximum-density decomposition

Under D7-A1 to D7-A6,

\[
\boxed{
f_T(t)
=
\sum_{j\in\mathcal J_0}
f_j(t)P(J_0=j\mid X_j=t).
}
\]

More generally, for every bounded measurable policy variable \(Y\),

\[
\boxed{
f_T(t)E(Y\mid T=t)
=
\sum_{j\in\mathcal J_0}
f_j(t)
E\{YI(J_0=j)\mid X_j=t\}.
}
\]

### Proof

For a small interval \((t,t+h]\), the event
\(\{T\in(t,t+h]\}\) is the disjoint union, up to winner ties, of

\[
\{J_0=j,\ X_j\in(t,t+h]\},
\qquad
j\in\mathcal J_0.
\]

Divide the corresponding probabilities by \(h\), use conditional
disintegration with respect to \(X_j\), and let \(h\downarrow0\). The bounded
\(Y\) version is identical after weighting each event by \(Y\). \(\square\)

---

# 5. Candidate-threshold derivatives

Retain the D6 exact signed jump field

\[
D_j
=
I\{j\in\mathcal J_0,J_0=j,J_1\ne j\}R_1
-
I\{j\in\mathcal J_1\setminus\mathcal J_0,J_1=j\}(1-R_0).
\]

Because activation depends on the raw score vector but not on the candidate
threshold vector,

\[
\frac{\partial\mu}{\partial q_j}
=
f_j(q_j)E(D_j\mid X_j=q_j),
\]

and

\[
\frac{\partial\nu}{\partial q_j}
=
f_j(q_j)E(AD_j\mid X_j=q_j).
\]

Therefore,

\[
\boxed{
\frac{\partial\Delta_\pi}{\partial q_j}
=
f_j(q_j)\beta_j^\Delta,
}
\]

where

\[
\boxed{
\beta_j^\Delta
=
E\{(A-\rho)D_j\mid X_j=q_j\}.
}
\]

Strict separation in D7-A7 ensures that moving \(q_j\) locally does not cross
the maximum-trigger boundary on the same coordinate.

---

# 6. Maximum-trigger derivative

Only the activation indicator depends on \(c\).

## Lemma D7.2. Trigger derivative

Under D7-A1 to D7-A7,

\[
\frac{\partial\rho}{\partial c}
=
-f_T(c),
\]

\[
\frac{\partial\nu}{\partial c}
=
-f_T(c)E(M\mid T=c),
\]

and

\[
\boxed{
\frac{\partial\Delta_\pi}{\partial c}
=
f_T(c)\beta_c^\Delta,
}
\]

where

\[
\boxed{
\beta_c^\Delta
=
\mu-E(M\mid T=c).
}
\]

### Proof

Increasing \(c\) removes activation only on the slab \(c<T\le c+h\). The first
two formulas follow from the density and conditional expectation of \(T\) at
the boundary. Since \(\Delta_\pi=\nu-\rho\mu\) and \(\mu\) does not depend on
\(c\), the third formula follows. \(\square\)

Lemma D7.1 expresses both \(f_T(c)\) and
\(f_T(c)E(M\mid T=c)\) through the base-winner boundary pieces.

---

# 7. Joint differentiability

## Proposition D7.3

Under D7-A1 to D7-A9,

\[
(e_0,\rho,\mu,\nu,\pi_A,\pi_C,\Delta_\pi)
\]

is continuously differentiable in a neighborhood of \((q,c)\).

### Proof

D7-A7 gives a positive neighborhood in which each base candidate boundary
remains separated from the maximum-trigger boundary. Candidate derivatives are
therefore the D6 winner-region derivatives and the trigger derivative is given
by Lemma D7.2. Distinct candidate-boundary interactions are second order under
D7-A8. The candidate dimension is fixed and finite. \(\square\)

---

# 8. Joint reference quantile process

Let

\[
\widehat q_j=\widehat F_{j,B}^{-1}(p)
\]

and

\[
\widehat c=\widehat F_{T,B}^{-1}(s),
\qquad
T_i^R=\max_{j\in\mathcal J_0}X_{ij}^R.
\]

The finite-dimensional Bahadur representations are

\[
\widehat q_j-q_j
=
P_B\psi_j+o_p(B^{-1/2}),
\]

where

\[
\psi_j(X^R)
=
\frac{p-I(X_j^R\le q_j)}{f_j(q_j)},
\]

and

\[
\widehat c-c
=
P_B\psi_c+o_p(B^{-1/2}),
\]

where

\[
\psi_c(X^R)
=
\frac{s-I(T^R\le c)}{f_T(c)}.
\]

All covariance between candidate quantiles and the maximum quantile is retained
because they are estimated from the same complete reference vectors.

---

# 9. Main two-bank theorem

## Theorem D7.4. Maximum-trigger asymptotic linearity

Under D7-A1 to D7-A9,

\[
\boxed{
\widehat\Delta_\pi-\Delta_\pi
=
P_n\phi_E^\Delta
+
P_B\phi_R^\Delta
+
o_p(n^{-1/2}+B^{-1/2}),
}
\]

where

\[
\boxed{
\phi_E^\Delta
=
(A-\rho)(M-\mu)-\Delta_\pi,
}
\]

and

\[
\boxed{
\phi_R^\Delta
=
\sum_{j=1}^K
\beta_j^\Delta
\{p-I(X_j^R\le q_j)\}
+
\beta_c^\Delta
\{s-I(T^R\le c)\}.
}
\]

Consequently,

\[
\frac{
\widehat\Delta_\pi-\Delta_\pi
}{
\left[
\operatorname{Var}(\phi_E^\Delta)/n
+
\operatorname{Var}(\phi_R^\Delta)/B
\right]^{1/2}
}
\rightsquigarrow N(0,1)
\]

whenever the denominator is nonzero.

### Proof

For fixed thresholds, the evaluation estimator is the same smooth covariance
functional as in D6, yielding \(\phi_E^\Delta\).

For the reference term, combine Proposition D7.3 with the joint candidate and
maximum quantile process from Section 8. Candidate densities and the maximum
density cancel against the corresponding quantile influence functions.

The local evaluation class is a finite Boolean combination of candidate
winner regions, candidate threshold half-spaces, and the maximum threshold
event. Under fixed finite \(K\), it is VC type and stochastically
equicontinuous. Independence of the two banks completes the expansion.
\(\square\)

---

# 10. TESS expansion

Let

\[
\phi_E^A=R_0+AM-\pi_A,
\]

and

\[
\phi_E^C
=
(R_0-e_0)
+
\mu(A-\rho)
+
\rho(M-\mu).
\]

The corresponding reference influence functions are obtained by applying the
candidate and maximum-trigger derivatives to \(\pi_A\) and \(\pi_C\).

## Corollary D7.5

Under D7-A1 to D7-A10,

\[
\widehat\Delta_S-\Delta_S
=
P_n\phi_E^S
+
P_B\phi_R^S
+
o_p(n^{-1/2}+B^{-1/2}),
\]

where

\[
\phi_E^S
=
g_\alpha'(\pi_A)\phi_E^A
-
g_\alpha'(\pi_C)\phi_E^C,
\]

and analogously for \(\phi_R^S\).

---

# 11. Complete-replication bootstrap

Reference bootstrap draws resample complete candidate-score vectors and
recompute:

- every candidate threshold;
- every base maximum;
- the maximum-trigger threshold.

Evaluation bootstrap draws resample complete candidate-score vectors and
recompute:

- base and full winners;
- the base maximum and activation;
- branch and incremental rejection;
- the adaptive and comparator estimates;
- rejection and TESS contrasts.

## Theorem D7.6. Bootstrap validity

Under D7-A1 to D7-A10, the independently resampled complete-replication
two-bank bootstrap consistently estimates the centered sampling laws of
\(\widehat\Delta_\pi\) and \(\widehat\Delta_S\).

### Proof

The reference bootstrap consistently reproduces the joint finite-dimensional
candidate and maximum quantile process. The evaluation bootstrap reproduces the
bounded finite-VC empirical process. Proposition D7.3 supplies ordinary
Hadamard differentiability in the separated regime. The bootstrap delta method
gives the result. \(\square\)

---

# 12. Candidate plus-one bridge

D7 changes the activation statistic but not the support of a
candidate-quantile versus candidate-plus-one disagreement.

## Theorem D7.7. Fixed-finite-\(K\) plus-one bridge

Hold the maximum-trigger construction paired between the regular and candidate
plus-one modes. For fixed finite \(K\),

\[
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
=
O_p\left(
\frac{K}{B}
+
\sqrt{\frac{K}{Bn}}
\right).
\]

Under D7-A10, the same rate holds on the TESS scale.

The proof is the D6 adjacent-order-statistic union argument with the
maximum-trigger state held fixed and paired.

---

# 13. Threshold-coincidence nonregularity

Suppose a base candidate \(j\) satisfies

\[
q_j=c.
\]

Define

\[
\kappa_j
=
f_j(c)
E\{I(J_0=j,J_1\ne j)R_1\mid X_j=c\}.
\]

Consider local threshold paths

\[
q_j(t)=c+t h_j,
\qquad
c(t)=c+t h_c.
\]

On the coincidence-relevant region, activation without base rejection occurs
on an interval of width

\[
t(h_j-h_c)_++o(t).
\]

## Theorem D7.8. Directional coincidence expansion

Under the continuous unique-winner assumptions, the directional derivative of
the policy functional contains the nonlinear contribution

\[
\boxed{
\kappa_j(h_j-h_c)_+.
}
\]

All noncoincident boundaries contribute ordinary linear terms.

If \(\kappa_j>0\), the full directional derivative is not additive in
\((h_j,h_c)\). Hence the functional is not ordinarily Hadamard differentiable
at the coincidence point.

### Consequences

- no ordinary influence function represents the complete first-order behavior;
- the regular D7 asymptotic expansion does not apply unchanged;
- the ordinary nonparametric bootstrap is not justified by Theorem D7.6;
- a directional bootstrap or an explicit coincidence-specific procedure would
  be required.

This obstruction is distinct from winner ties.

---

# 14. Runtime-only preflight

The continuous Gaussian preflight verified:

- positive definite covariance;
- strict candidate/trigger separation;
- candidate-threshold derivatives against finite differences;
- the maximum-trigger derivative against finite differences;
- the maximum-density winner-region decomposition;
- the coincidence nonadditivity against the boundary coefficient
  \(\kappa_j\);
- no observed winner ties.

These checks are mathematical and implementation debugging only. They are not
scientific numerical validation.

---

# 15. Completion statement

D7 is theoretically successful in the continuous separated-threshold regime.

It also identifies an explicit nonregular boundary at candidate/trigger
threshold coincidence.

The remaining empirical-pipeline gaps are:

- discrete finite-sample AUROC trigger values;
- deterministic trigger-tie randomization;
- winner ties;
- failed-fit fallback;
- growing candidate dimension;
- simultaneous threshold-process inference.

# 16. Empirical historical-surrogate diagnostic

The available historical 20-candidate AUROC banks showed strict
candidate/trigger threshold separation over the declared alpha grid. No exact
threshold coincidence and no pair within one local score spacing was observed.

However, the base-stage maximum had positive-probability ties in the finite
banks. Therefore D7-A3 is not an exact description of the discrete empirical
AUROC pipeline. The audit also lacked an exact SHA-256 match to the current
confirmatory raw-bank manifests.

Accordingly:

- the separation audit is descriptive support for the D7 regular regime;
- it is not a formal bridge to the current frozen empirical policy;
- discrete winner ties and the declared deterministic tie rule remain the
  next theoretical extension.
