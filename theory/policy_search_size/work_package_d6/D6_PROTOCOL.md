# Work Package D6 Protocol

## Finite-candidate unique-winner bridge for the paired two-bank policy contrast

**Status:** locked before D6 scientific numerical execution
**Parent results:** `d4-validation-full-v1`, `d5-validation-full-v1`
**Parent branch:** `tess-top-tier-theory`

---

# 1. Purpose

Work Package D6 extends the regular one-candidate-per-branch D4-D5 theory to
finite candidate libraries in which the winner is unique almost surely.

D6 isolates winner selection only. It does not yet introduce:

- a trigger defined by a maximum candidate score;
- positive-probability winner ties or deterministic tie randomization;
- failed-fit fallback rules;
- simultaneous threshold-process inference.

Those remain later steps in the D0 extension ladder.

---

# 2. Empirical mechanism being bridged

The empirical pipeline uses a fixed declared candidate order and a finite
candidate library. Within each complete replication and active candidate pool,
the selected candidate is the highest-scoring candidate on the model-selection
metric.

The selected output contains:

- winner identity;
- winner raw selection performance;
- the candidate-specific naive empirical p-value;
- the resulting rejection indicator over the alpha grid.

The null-reference bank supplies candidate-specific empirical upper-tail maps.
The independent evaluation bank supplies complete candidate-score vectors on
which winner selection and policy rejection are evaluated.

D6 abstracts this mechanism while excluding the empirical max-score trigger,
tie rule, and failed-fit rule.

---

# 3. Mathematical model

Let the finite full candidate set be

\[
\mathcal J_1=\{1,\ldots,K_1\},
\]

and let the base candidate set be a fixed subset

\[
\mathcal J_0\subset\mathcal J_1,
\qquad
|\mathcal J_0|=K_0.
\]

The empirical motivation is \(K_0=7\) and \(K_1=20\), but the D6 theory is
stated for arbitrary fixed finite \(K_0,K_1\).

Each complete replication contains

\[
Z=(U,X_1,\ldots,X_{K_1}),
\]

where:

- \(U\) is the scalar activation score inherited from D4;
- \(X_j\) is the declared selection score for candidate \(j\);
- all within-replication dependence is preserved.

The reference bank is

\[
\mathcal R_B=(Z_1^R,\ldots,Z_B^R),
\]

and the independent evaluation bank is

\[
\mathcal E_n=(Z_1^E,\ldots,Z_n^E).
\]

---

# 4. Winner maps

For branch \(b\in\{0,1\}\), define

\[
J_b(x)
=
\operatorname*{arg\,max}_{j\in\mathcal J_b}x_j.
\]

D6 assumes

\[
P\{X_j=X_k\}=0
\qquad
(j\ne k),
\]

so \(J_b(X)\) is unique almost surely.

Define winner regions

\[
\mathcal W_{b,j}
=
\left\{
x:
x_j>x_k
\text{ for every }
k\in\mathcal J_b\setminus\{j\}
\right\}.
\]

The regions partition the candidate-score space up to a null tie set.

No population-best candidate and no selection-consistency target are introduced.
The winner remains random across complete replications.

---

# 5. Candidate-specific calibration

For every candidate \(j\), define its population candidate threshold

\[
q_j(\alpha)=F_j^{-1}(1-\alpha),
\]

and its reference-bank estimator using the declared generalized-inverse
quantile convention,

\[
\widehat q_{j,B}(\alpha).
\]

The exact plus-one threshold from D5 may be substituted candidate by candidate.
D6 keeps both representations explicit:

- regular quantile representation for first-order theory;
- exact plus-one implementation for the finite-bank bridge.

All candidate thresholds are estimated from one complete-vector reference bank,
thereby preserving candidate dependence.

---

# 6. Branch rejection maps

For branch \(b\), define

\[
R_b(q)
=
\sum_{j\in\mathcal J_b}
I\{X\in\mathcal W_{b,j}\}
I\{X_j>q_j\}.
\]

Equivalently,

\[
R_b(q)
=
I\left\{
X_{J_b(X)}>q_{J_b(X)}
\right\}.
\]

This is not generally equivalent to thresholding one common maximum score,
because the candidate thresholds are candidate specific.

The base and expanded branch maps are

\[
R_0(q),\qquad R_1(q).
\]

---

# 7. Adaptive policy and comparator

Retain the D4 activation map

\[
A(c)=I(U>c),
\]

where \(c\) is fixed or estimated from the scalar \(U\) reference coordinate.

Define the finite-candidate adaptive rejection indicator

\[
H_A(q,c)
=
R_0(q)
+
A(c)\{1-R_0(q)\}R_1(q).
\]

Let

\[
M(q)=\{1-R_0(q)\}R_1(q)
\]

be the incremental-rejection indicator.

The budget-matched comparator remains

\[
\pi_C(q,c)
=
e_0(q)+\rho(c)\mu(q),
\]

where

\[
e_0(q)=P\{R_0(q)=1\},
\qquad
\rho(c)=P\{A(c)=1\},
\qquad
\mu(q)=P\{M(q)=1\}.
\]

The primary contrast is

\[
\Delta_\pi(q,c)
=
\pi_A(q,c)-\pi_C(q,c).
\]

Writing

\[
\nu(q,c)=E\{A(c)M(q)\},
\]

gives the exact simplification

\[
\boxed{
\Delta_\pi(q,c)
=
\nu(q,c)-\rho(c)\mu(q)
=
\operatorname{Cov}\{A(c),M(q)\}.
}
\]

Thus the base rejection term cancels exactly from the rejection-probability
contrast, although it remains present in each policy-specific rejection
probability and therefore remains relevant on the nonlinear TESS-contrast
scale.

The corresponding nominal-alpha TESS contrast is

\[
\Delta_S(q,c)
=
g_\alpha\{\pi_A(q,c)\}
-
g_\alpha\{\pi_C(q,c)\}.
\]

---


# 8. Regularity assumptions

D6 uses the following assumptions.

## D6-A1. Fixed finite nested pools

The candidate dimension and the nested base/full candidate pools are fixed as
the reference and evaluation bank sizes diverge.

## D6-A2. Independent complete-vector banks

Reference and evaluation banks are independent i.i.d. samples of complete
vectors containing the scalar activation score and all candidate scores.

## D6-A3. Almost-sure unique winners

Pairwise candidate-score ties have probability zero.

## D6-A4. Regular marginal quantiles

Candidate and activation marginal densities are continuous, positive, and
finite at the required thresholds.

## D6-A5. Smooth winner-region boundary probabilities

The candidate-boundary and activation-boundary conditional expectations used
in the influence coefficients admit locally continuous versions.

## D6-A6. Second-order distinct-boundary intersections

Simultaneous slabs around two distinct threshold surfaces have product-order
probability. A shared candidate winning both nested pools is treated instead
as one coincident first-order boundary with exact zero incremental jump.

## D6-A7. Fixed declared policy

Candidate order, pool nesting, score direction, activation rule, quantile
convention, and comparator construction are fixed independently of both banks.

## D6-A8. Interior TESS domain

Adaptive and comparator rejection probabilities remain bounded away from one.

---

# 9. Boundary notation and exact influence targets

For candidate \(j\), define

\[
B_{0j}
=
I\{j\in\mathcal J_0,\ J_0(X)=j\},
\qquad
B_{1j}
=
I\{j\in\mathcal J_1,\ J_1(X)=j\}.
\]

Because the base pool is nested in the full pool, a base candidate that wins
the full pool also wins the base pool. The exact signed jump in

\[
M(q)=\{1-R_0(q)\}R_1(q)
\]

when \(q_j\) increases across the boundary \(X_j=q_j\) is

\[
\boxed{
D_j
=
I\{j\in\mathcal J_0,\ J_0=j,\ J_1\ne j\}R_1
-
I\{j\in\mathcal J_1\setminus\mathcal J_0,\ J_1=j\}(1-R_0).
}
\]

Thus:

- a base winner displaced by a different full-pool winner contributes a
  positive boundary jump when the base rejection is switched off;
- an extra-candidate full winner contributes a negative boundary jump when
  the full rejection is switched off;
- a shared candidate that wins both pools contributes zero, because changing
  its common threshold switches \(R_0\) and \(R_1\) together and leaves
  \(M=(1-R_0)R_1\) equal to zero on both sides.

The last case is a first-order coincident-boundary effect. It must not be
discarded as a codimension-two intersection.

Let \(p=1-\alpha\) and \(s=1-r\). The target candidate coefficient for the
rejection-probability contrast is

\[
\beta_j^\Delta
=
E\left[
\{A(c)-\rho(c)\}D_j
\mid X_j=q_j
\right].
\]

The activation-threshold coefficient is

\[
\beta_c^\Delta
=
\mu(q)-E\{M(q)\mid U=c\}.
\]

The prospective reference influence function is therefore

\[
\boxed{
\phi_R^\Delta(Z^R)
=
\sum_{j=1}^{K_1}
\beta_j^\Delta
\left[
p-I\{X_j^R\le q_j\}
\right]
+
\beta_c^\Delta
\left[
s-I\{U^R\le c\}
\right].
}
\]

The evaluation influence function has the exact covariance-functional form

\[
\boxed{
\phi_E^\Delta(Z^E)
=
\{A-\rho\}\{M-\mu\}-\Delta_\pi.
}
\]

For the two policy-specific rejection probabilities, define

\[
\beta_j^A
=
-
E(B_{0j}\mid X_j=q_j)
+
E(AD_j\mid X_j=q_j),
\]

\[
\beta_j^C
=
-
E(B_{0j}\mid X_j=q_j)
+
\rho E(D_j\mid X_j=q_j),
\]

and

\[
\beta_c^A=-E(M\mid U=c),
\qquad
\beta_c^C=-\mu.
\]

These coefficients multiply the same centered quantile indicators in the
reference influence functions for \(\pi_A\) and \(\pi_C\).

The evaluation influence functions are

\[
\phi_E^A
=
R_0+AM-\pi_A,
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

Consequently, with

\[
g_\alpha'(\pi)
=
-\frac{1}{(1-\pi)\log(1-\alpha)},
\]

the TESS-contrast influence functions are

\[
\phi_E^S
=
g_\alpha'(\pi_A)\phi_E^A
-
g_\alpha'(\pi_C)\phi_E^C,
\]

and

\[
\phi_R^S
=
g_\alpha'(\pi_A)\phi_R^A
-
g_\alpha'(\pi_C)\phi_R^C.
\]

These formulas are theorem targets until the boundary-differentiability proof
is completed.

---

# 10. Main theorem targets

## D6-T1. Winner-region representation

Prove that, under almost-sure winner uniqueness,

\[
R_b(q)
=
\sum_{j\in\mathcal J_b}
I(\mathcal W_{b,j})I(X_j>q_j)
\]

and that the branch map is a finite union of fixed winner regions intersected
with candidate-specific threshold half-spaces.

The winner regions do not depend on the estimated candidate thresholds.

## D6-T2. Winner-region boundary derivative

Under a continuous joint density and regular conditional laws near the
candidate threshold surfaces, establish differentiability of branch and policy
rejection probabilities with respect to the vector

\[
q=(q_1,\ldots,q_{K_1}).
\]

The derivative with respect to candidate \(j\) must be expressed through a
winner-region boundary probability of the form

\[
P\left\{
J_b(X)=j,\
\text{policy-relevant state}
\mid
X_j=q_j
\right\}.
\]

The scalar D4 boundary coefficients are replaced by a finite vector of
winner-region boundary coefficients. The proof must explicitly retain the
coincident base/full threshold change when one shared candidate wins both
pools; the exact jump is zero in that case.

## D6-T3. Finite-candidate two-bank asymptotic linearity

Prove

\[
\widehat\Delta_{\pi,B,n}
-
\Delta_\pi
=
P_n\phi_E^\Delta
+
P_B\phi_R^\Delta
+
o_p(n^{-1/2}+B^{-1/2}),
\]

using the explicit influence targets in Section 8.

The proof must show that:

1. each candidate marginal density cancels against its quantile influence
   function exactly as in D1-D4;
2. all cross-candidate dependence is retained through complete-vector
   covariance;
3. winner-tie surfaces and intersections of distinct candidate-threshold
   surfaces have zero probability under the continuous-law assumptions;
4. the same-candidate base/full threshold is treated as one coincident
   first-order boundary, using the exact zero-jump case in \(D_j\);
5. no deterministic population winner or positive winner gap is used.

## D6-T4. TESS-scale expansion

Under rejection probabilities bounded away from one,

\[
\widehat\Delta_{S,B,n}
-
\Delta_S
=
P_n\phi_E^S
+
P_B\phi_R^S
+
o_p(n^{-1/2}+B^{-1/2}).
\]

## D6-T5. Complete-replication two-bank bootstrap

Establish validity of independently resampling:

- complete reference vectors across all candidates and the activation score;
- complete evaluation vectors across all candidates and the activation score.

Every candidate threshold, branch rejection map, activation threshold,
comparator component, and TESS contrast must be recomputed from the resampled
complete vectors. Winner identity is deterministically re-evaluated from each
resampled complete candidate-score vector.

Because the winner regions are fixed measurable regions and ties have
probability zero, D6 does not invoke a positive fixed winner gap or reduction to
one deterministic population winner. Candidate-wise independent resampling is
an invalid negative diagnostic because it destroys the joint winner-region
geometry.

## D6-T6. Finite-\(K\) plus-one bridge

For fixed finite \(K_1\), extend D5 candidate by candidate and show that the
aggregate quantile-versus-plus-one discrepancy remains bounded by a finite sum
of adjacent-order-statistic interval contributions.

A conservative fixed-alpha union bound gives the target rate

\[
O_p\left(
\frac{K_1}{B}
+
\sqrt{\frac{K_1}{Bn}}
\right).
\]

For fixed \(K_1\), this is

\[
O_p\left(
B^{-1}+(Bn)^{-1/2}
\right)
=
o_p(B^{-1/2}+n^{-1/2}),
\]

recovering first-order equivalence with the regular quantile representation.

The theorem should preserve the exact finite-\(K_1\) dependence rather than
silently treating \(K_1\) as one. No claim is made for candidate counts
increasing with \(B\) or \(n\).

---

# 11. Why a positive winner gap is not the main assumption

D6 does not estimate one population-best candidate.

The winner is a random function of the complete candidate-score vector within
each replication. Therefore a fixed positive gap between population criteria is
neither natural nor required for the regular D6 theorem.

The required regularity is instead:

- almost-sure uniqueness of the within-replication winner;
- null probability for tie surfaces;
- smooth candidate-threshold boundary probabilities within winner regions;
- fixed finite candidate dimension.

A margin condition may be useful for quantitative near-tie diagnostics, but it
is not the primary route to first-order theory.

---

# 12. Tie and nonregular boundary

If

\[
P\{X_j=X_k\}>0
\]

for some pair, the winner map depends on the declared deterministic tie rule on
a positive-probability set.

That case is outside D6. It belongs to the later tie-randomization extension and
ordinary bootstrap validity must not be assumed from the D6 result.

Finite floating-point ties in an empirical implementation also remain outside
the mathematical D6 theorem even when they are resolved by declared candidate
order.

---

# 13. Failed-fit boundary

D6 assumes all candidate scores are finite and defined.

Assigning a fallback score to a failed fit changes the candidate-score law and
can create atoms or ties. Candidate deletion, replacement, or fallback scoring
is therefore excluded until the later failed-fit extension.

---

# 14. Numerical strategy before lock

The first numerical layer should be synthetic and transparent rather than
refitting the full ML pipeline.

Candidate score vectors should be generated from continuous finite-dimensional
laws with:

- candidate-specific marginal distributions;
- tunable within-library dependence;
- base pool nested inside the full pool;
- a separate scalar activation score;
- nonzero paired policy contrasts in at least one dependent design.

Initial debugging may use \(K_0=2,K_1=3\).

The scientific grid should include the empirically relevant
\(K_0=7,K_1=20\), but only after runtime review and before protocol lock.

The numerical validation should check:

1. analytic winner-region derivatives against finite differences;
2. empirical variance against the finite-candidate influence variance;
3. complete-replication two-bank bootstrap SD and coverage;
4. failure of candidate-wise independent resampling as a negative diagnostic;
5. quantile-versus-plus-one discrepancy for fixed finite \(K\);
6. exact agreement between direct winner selection and winner-region
   representation.

---

# 15. Stop rule

D6 should stop or narrow its claim if:

- winner-region boundary derivatives cannot be stated transparently;
- the ordinary complete-replication bootstrap fails under continuous unique
  winners;
- the theorem requires a deterministic population winner unrelated to the
  empirical per-replication selection mechanism;
- the trigger maximum, tie rule, or failed-fit rule must be imported to make
  the D6 model meaningful;
- candidate dimension must grow with bank size to obtain the claimed result.

A clean fixed-finite-\(K\) theorem is sufficient.

---

# 16. Scope boundary

D6 does not establish validity for the complete empirical pipeline because it
still excludes:

- the base trigger defined by the maximum score among the first seven
  candidates;
- deterministic tie handling;
- failed-fit fallback scores;
- growing candidate libraries;
- process inference over an alpha interval.

The next extension after D6 is the maximum-score trigger.
