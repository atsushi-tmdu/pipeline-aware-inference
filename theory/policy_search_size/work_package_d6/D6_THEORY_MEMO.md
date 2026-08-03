# Work Package D6 Theory Memo

## Finite-candidate unique-winner bridge for the paired two-bank TESS contrast

**Status:** locked before D6 scientific numerical execution

**Parent work:** D4 paired two-bank contrast and D5 exact plus-one bridge
**Candidate dimension:** fixed and finite
**Winner target:** random per-replication winner, not one population-best model

---

# 1. Result

Work Package D6 extends the D4-D5 one-candidate-per-branch theory to fixed
finite nested candidate pools with an almost-surely unique winner in every
complete replication.

The key structural fact is that winner selection does not estimate one
deterministic population-best candidate. For every replication, the complete
candidate-score vector falls into one of finitely many fixed winner regions.
Conditional on a winner region, candidate rejection is a scalar
candidate-specific threshold event.

Under continuous joint laws and smooth boundary probabilities:

1. the finite-candidate policy functional is differentiable in the vector of
   candidate thresholds and the scalar activation threshold;
2. the candidate marginal densities cancel from the reference influence
   function exactly as in D1-D4;
3. the paired adaptive-versus-budget-matched-random contrast has separate
   evaluation- and reference-bank first-order contributions;
4. the complete-replication two-bank bootstrap is valid;
5. for fixed finite candidate count, replacing regular empirical quantiles by
   exact plus-one order-statistic thresholds is first-order negligible.

The theorem does not require a positive gap between population model criteria.

---

# 2. Model

Let

\[
\mathcal J_0\subset\mathcal J_1=\{1,\ldots,K\}
\]

be fixed finite nested base and full candidate pools.

A complete replication is

\[
Z=(U,X_1,\ldots,X_K),
\]

where \(U\) is the scalar activation score and \(X_j\) is the declared
selection score of candidate \(j\).

The null-reference bank and independent evaluation bank are

\[
\mathcal R_B=(Z_1^R,\ldots,Z_B^R),
\qquad
\mathcal E_n=(Z_1^E,\ldots,Z_n^E).
\]

For \(b\in\{0,1\}\), define the winner

\[
J_b(X)
=
\operatorname*{arg\,max}_{j\in\mathcal J_b}X_j
\]

and winner region

\[
\mathcal W_{b,j}
=
\{X_j>X_k\text{ for every }k\in\mathcal J_b\setminus\{j\}\}.
\]

Let

\[
p=1-\alpha,
\qquad
s=1-r,
\]

and define the population thresholds

\[
q_j=F_j^{-1}(p),
\qquad
c=F_U^{-1}(s).
\]

The branch rejection maps are

\[
R_b(q)
=
\sum_{j\in\mathcal J_b}
I(\mathcal W_{b,j})I(X_j>q_j).
\]

The activation and incremental-rejection maps are

\[
A(c)=I(U>c),
\qquad
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

and the primary rejection-probability contrast is

\[
\Delta_\pi
=
\pi_A-\pi_C
=
\nu-\rho\mu.
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

## D6-A1. Fixed finite nested pools

The integer \(K\) and the sets \(\mathcal J_0\subset\mathcal J_1\) are fixed
as \(B,n\to\infty\).

## D6-A2. Independent complete-vector banks

The reference and evaluation banks are independent. Within each bank, complete
vectors are i.i.d. from a common law \(P\). All candidate and activation
dependence within one replication is retained.

## D6-A3. Almost-sure unique winners

For every distinct \(j,k\in\mathcal J_1\),

\[
P(X_j=X_k)=0.
\]

Thus \(J_0\) and \(J_1\) are unique almost surely.

## D6-A4. Regular marginal quantiles

Every \(F_j\) and \(F_U\) is continuously differentiable near its required
quantile, with density positive and finite there.

## D6-A5. Smooth winner-region boundary probabilities

For every candidate \(j\), the conditional expectations appearing below admit
versions continuous at \(X_j=q_j\). The analogous activation-boundary
conditional expectations are continuous at \(U=c\).

A sufficient condition is a locally bounded continuous joint density near the
candidate-threshold, activation-threshold, and winner-comparison surfaces.

## D6-A6. Negligible distinct-boundary intersections

Probabilities of simultaneous slabs around two distinct candidate-threshold
surfaces, or around a candidate-threshold and activation-threshold surface,
are of product order in their widths.

The same candidate serving as both base and full winner is not treated as a
distinct-boundary intersection. It is one coincident first-order boundary and
is retained exactly.

## D6-A7. Fixed declared policy

The candidate order, pool nesting, score direction, activation rule, alpha,
quantile convention, and comparator construction are fixed independently of
both banks.

## D6-A8. Interior TESS domain

For the TESS result, \(\pi_A\) and \(\pi_C\) remain in a compact subset of
\([0,1)\).

---

# 4. Exact covariance identity

## Lemma D6.1

\[
\boxed{
\Delta_\pi=\operatorname{Cov}(A,M).
}
\]

### Proof

Because \(H_A=R_0+AM\),

\[
\pi_A=e_0+\nu.
\]

The budget-matched comparator is

\[
\pi_C=e_0+\rho\mu.
\]

Subtracting gives

\[
\Delta_\pi
=
\nu-\rho\mu
=
E(AM)-E(A)E(M).
\]

\(\square\)

The base rejection probability cancels exactly on the rejection-contrast
scale. It does not cancel from the two policy-specific rejection probabilities
and therefore does not disappear from the nonlinear TESS contrast.

---

# 5. Winner-region threshold jumps

For candidate \(j\), let

\[
B_{0j}
=
I\{j\in\mathcal J_0,\ J_0=j\},
\qquad
B_{1j}
=
I\{j\in\mathcal J_1,\ J_1=j\}.
\]

Because the pools are nested, \(J_1=j\) and \(j\in\mathcal J_0\) imply
\(J_0=j\).

Define the exact signed jump

\[
\boxed{
D_j
=
I\{j\in\mathcal J_0,\ J_0=j,\ J_1\ne j\}R_1
-
I\{j\in\mathcal J_1\setminus\mathcal J_0,\ J_1=j\}(1-R_0).
}
\]

This is the after-minus-before change in \(M\) when \(q_j\) is increased across
the boundary \(X_j=q_j\).

There are three nontrivial structural cases.

1. If \(j\) wins the base pool but a different candidate wins the full pool,
   switching off the base rejection exposes an existing full rejection and
   the jump is \(+R_1\).
2. If \(j\) is an extra candidate and wins the full pool, switching off the
   full rejection gives the jump \(-(1-R_0)\).
3. If the same shared candidate wins both pools, moving its common threshold
   switches \(R_0\) and \(R_1\) together and \(M\) is zero on both sides. The
   exact jump is zero.

The third case is a coincident first-order boundary, not a codimension-two
event.

---

# 6. Differentiability

## Lemma D6.2. Candidate-threshold derivatives

Under D6-A1 to D6-A6,

\[
\frac{\partial e_0}{\partial q_j}
=
-f_j(q_j)
E(B_{0j}\mid X_j=q_j),
\]

\[
\frac{\partial\mu}{\partial q_j}
=
f_j(q_j)
E(D_j\mid X_j=q_j),
\]

and

\[
\frac{\partial\nu}{\partial q_j}
=
f_j(q_j)
E(AD_j\mid X_j=q_j).
\]

Consequently,

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

### Proof

The winner regions are fixed measurable regions and do not depend on \(q\).
When only \(q_j\) changes, branch decisions can change only on the slab between
the old and new values of \(q_j\), within a region where candidate \(j\) is a
relevant winner.

For \(e_0\), increasing \(q_j\) can only remove a base rejection on
\(B_{0j}=1\), giving the first formula.

For \(M\), the exact within-state after-minus-before change is \(D_j\), giving

\[
P\{M(q+he_j)-M(q)\}
=
\int_{q_j}^{q_j+h}
E(D_j\mid X_j=x)f_j(x)\,dx
+
o(h).
\]

Continuity at \(q_j\) yields the derivative of \(\mu\). Multiplication by the
bounded factor \(A\) gives the derivative of \(\nu\).

Finally,

\[
\Delta_\pi=\nu-\rho\mu
\]

and \(\rho\) does not depend on \(q\), so

\[
\frac{\partial\Delta_\pi}{\partial q_j}
=
f_j(q_j)
\left[
E(AD_j\mid X_j=q_j)
-
\rho E(D_j\mid X_j=q_j)
\right].
\]

Distinct threshold intersections contribute only second-order remainder by
D6-A6. The shared-winner coincident threshold has already been included through
the exact zero-jump case in \(D_j\). \(\square\)

## Lemma D6.3. Activation-threshold derivatives

\[
\frac{\partial\rho}{\partial c}
=
-f_U(c),
\]

\[
\frac{\partial\nu}{\partial c}
=
-f_U(c)E(M\mid U=c),
\]

and

\[
\boxed{
\frac{\partial\Delta_\pi}{\partial c}
=
f_U(c)\beta_c^\Delta,
}
\]

where

\[
\boxed{
\beta_c^\Delta
=
\mu-E(M\mid U=c).
}
\]

### Proof

Only \(A(c)=I(U>c)\) depends on \(c\). The first two derivatives follow by
integrating over the activation-boundary slab. Since
\(\Delta_\pi=\nu-\rho\mu\), the result follows immediately. \(\square\)

## Proposition D6.4. Joint differentiability

Under D6-A1 to D6-A6, the vector

\[
(e_0,\rho,\mu,\nu,\pi_A,\pi_C,\Delta_\pi)
\]

is continuously differentiable in a neighborhood of \((q,c)\).

### Proof

Sum the one-coordinate expansions from Lemmas D6.2 and D6.3. D6-A6 makes every
distinct-boundary interaction second order. The finite value of \(K\) makes the
sum finite. \(\square\)

---

# 7. Reference-bank quantile process

Let

\[
\widehat q_j
=
\widehat F_{j,B}^{-1}(p),
\qquad
\widehat c
=
\widehat F_{U,B}^{-1}(s).
\]

The joint finite-dimensional Bahadur representation is

\[
\widehat q_j-q_j
=
P_B\psi_j+o_p(B^{-1/2}),
\]

where

\[
\psi_j(Z^R)
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
\psi_c(Z^R)
=
\frac{s-I(U^R\le c)}{f_U(c)}.
\]

All cross-candidate and candidate-activation covariance is retained because the
same complete reference vectors generate every component.

Multiplying these quantile influence functions by the derivatives in Section 6
cancels all marginal density factors.

---

# 8. Evaluation-bank empirical process

For fixed \((q,c)\), the relevant functions are bounded finite Boolean
combinations of:

- winner-region half-spaces \(X_j-X_k>0\);
- candidate threshold half-spaces \(X_j>q_j\);
- the activation threshold half-space \(U>c\).

With fixed finite \(K\), their local class is a finite VC-type class. Hence the
evaluation empirical process is stochastically equicontinuous under local
threshold perturbations.

The empirical estimators are

\[
\widehat e_0=P_nR_0,
\quad
\widehat\rho=P_nA,
\quad
\widehat\mu=P_nM,
\quad
\widehat\nu=P_n(AM),
\]

\[
\widehat\pi_A=\widehat e_0+\widehat\nu,
\]

\[
\widehat\pi_C
=
\widehat e_0+\widehat\rho\,\widehat\mu,
\]

and

\[
\widehat\Delta_\pi
=
\widehat\pi_A-\widehat\pi_C.
\]

---

# 9. Main two-bank theorem

## Theorem D6.5. Finite-candidate two-bank asymptotic linearity

Under D6-A1 to D6-A7,

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
\{s-I(U^R\le c)\}.
}
\]

Therefore,

\[
\frac{
\widehat\Delta_\pi-\Delta_\pi
}{
\left[
\frac{\operatorname{Var}(\phi_E^\Delta)}{n}
+
\frac{\operatorname{Var}(\phi_R^\Delta)}{B}
\right]^{1/2}
}
\rightsquigarrow N(0,1)
\]

whenever the denominator is nonzero.

### Proof

For fixed thresholds, apply the multivariate delta method to

\[
(\widehat\nu,\widehat\rho,\widehat\mu)
\mapsto
\widehat\nu-\widehat\rho\,\widehat\mu.
\]

This gives

\[
\phi_E^\Delta
=
(AM-\nu)-\mu(A-\rho)-\rho(M-\mu),
\]

which simplifies to the stated covariance-functional form.

For the reference contribution, Proposition D6.4 gives the derivative of
\(\Delta_\pi\) with respect to every component of \((q,c)\). Compose that
gradient with the joint Bahadur representation from Section 7. The marginal
densities cancel, leaving \(\phi_R^\Delta\).

Stochastic equicontinuity of the evaluation class makes the empirical-process
increment generated by replacing \((q,c)\) with \((\widehat q,\widehat c)\)
second order after subtracting its population derivative. Independence of the
two banks gives the sum of independent first-order terms. \(\square\)

---

# 10. Policy-specific and TESS influence functions

For the adaptive policy,

\[
\phi_E^A
=
R_0+AM-\pi_A.
\]

For the comparator,

\[
\phi_E^C
=
(R_0-e_0)
+
\mu(A-\rho)
+
\rho(M-\mu).
\]

Define

\[
\beta_j^A
=
-E(B_{0j}\mid X_j=q_j)
+
E(AD_j\mid X_j=q_j),
\]

\[
\beta_j^C
=
-E(B_{0j}\mid X_j=q_j)
+
\rho E(D_j\mid X_j=q_j),
\]

and

\[
\beta_c^A
=
-E(M\mid U=c),
\qquad
\beta_c^C=-\mu.
\]

Then

\[
\phi_R^A
=
\sum_{j=1}^K
\beta_j^A
\{p-I(X_j^R\le q_j)\}
+
\beta_c^A
\{s-I(U^R\le c)\},
\]

and

\[
\phi_R^C
=
\sum_{j=1}^K
\beta_j^C
\{p-I(X_j^R\le q_j)\}
+
\beta_c^C
\{s-I(U^R\le c)\}.
\]

Since

\[
g_\alpha'(\pi)
=
-\frac{1}{(1-\pi)\log(1-\alpha)},
\]

D6-A8 and the ordinary delta method give

\[
\boxed{
\widehat\Delta_S-\Delta_S
=
P_n\phi_E^S
+
P_B\phi_R^S
+
o_p(n^{-1/2}+B^{-1/2}),
}
\]

where

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

---

# 11. Complete-replication bootstrap

Independently resample complete reference vectors and complete evaluation
vectors with replacement.

For every reference bootstrap draw, recompute:

- all candidate thresholds;
- the activation threshold.

For every evaluation bootstrap draw, retain each complete candidate-score
vector intact and re-evaluate:

- base and full winner identities;
- branch rejection maps;
- activation;
- incremental rejection;
- adaptive and comparator estimates;
- the rejection and TESS contrasts.

## Theorem D6.6. Bootstrap validity

Under D6-A1 to D6-A8, the independently resampled complete-replication
two-bank bootstrap consistently estimates the centered sampling laws of
\(\widehat\Delta_\pi\) and \(\widehat\Delta_S\).

### Proof

The reference empirical bootstrap consistently reproduces the joint finite
quantile process. The evaluation empirical bootstrap consistently reproduces
the bounded finite-VC empirical process. Proposition D6.4 supplies the
Hadamard derivative of the population map at the regular continuous-law point.
The bootstrap delta method and bank independence give the result. \(\square\)

Candidate-wise independent resampling is invalid in general because it destroys
the joint winner-region geometry and the covariance among candidate quantile
estimators.

---

# 12. Exact plus-one bridge

For candidate \(j\), let \(q_{j,B}^Q\) be the declared regular empirical
quantile threshold and \(q_{j,B}^+\) the exact plus-one order-statistic
threshold from D5.

Assume the strict plus-one rejection event is attainable. D5 implies that the
two thresholds are identical or adjacent order statistics. Let \(I_{j,B}\) be
the interval between them.

Conditional on the reference bank, a candidate decision can differ between the
two modes only if

\[
X_j^E\in I_{j,B}.
\]

The complete finite-candidate policy difference is therefore supported on

\[
\bigcup_{j=1}^K\{X_j^E\in I_{j,B}\},
\]

intersected with bounded winner and policy-state indicators.

## Theorem D6.7. Fixed-finite-\(K\) plus-one equivalence

For fixed \(K\),

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

Under D6-A8, the same rate holds for the TESS contrast.

Consequently,

\[
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
=
o_p(B^{-1/2}+n^{-1/2}),
\]

and likewise on the TESS scale.

### Proof

Each adjacent order-statistic interval has population mass \(O_p(B^{-1})\).
A finite union bound gives total discrepancy probability \(O_p(K/B)\).
Conditional on the reference bank, the evaluation-bank empirical fluctuation
over that union is

\[
O_p\left(\sqrt{\frac{K}{Bn}}\right).
\]

All policy and comparator factors are bounded. Products of empirical rates add
only smaller or equal-order terms. The TESS statement follows from local
Lipschitz continuity under D6-A8. \(\square\)

No claim is made when \(K\) grows with \(B\) or \(n\).

---

# 13. Nonregular boundaries

D6 does not cover the following cases.

## Positive-probability winner ties

If \(P(X_j=X_k)>0\), the declared tie rule acts on a positive-probability set.
The D6 derivative and ordinary bootstrap theorem do not automatically extend.

## Failed-fit fallback

Fallback scores may introduce atoms, ties, candidate deletion, or discontinuous
policy changes. These require a separate extension.

## Maximum-score activation trigger

The empirical activation statistic is a maximum over the base candidate pool.
D6 retains the separate scalar activation score from D4. The maximum-trigger
extension is D7.

## Growing candidate libraries

All finite sums, VC bounds, and plus-one union bounds in D6 treat \(K\) as
fixed.

---

# 14. Runtime-only preflight

The initial implementation tests verify:

- exact winner-region representation;
- unique-winner enforcement;
- the covariance identity;
- the centered evaluation influence function;
- the \(+1\), \(-1\), and zero candidate-threshold jumps;
- complete-vector resampling;
- the TESS derivative.

A continuous Gaussian benchmark additionally compares common-random-number
finite differences with conditional winner-region boundary derivatives.

These checks are mathematical and implementation debugging only. They do not
constitute scientific numerical validation and did not select the future
scientific result based on favorable output.

---

# 15. Completion statement

D6 is theoretically successful at the fixed finite candidate level.

It closes the unique-winner bridge between the regular D4-D5 theory and the
finite-candidate empirical policy, subject to the explicit remaining
limitations:

- separate scalar activation trigger;
- continuous unique winners;
- no failed fits;
- fixed finite candidate dimension;
- fixed alpha rather than a simultaneous process.
