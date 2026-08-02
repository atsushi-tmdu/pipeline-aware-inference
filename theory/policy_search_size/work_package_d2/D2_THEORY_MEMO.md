# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D2: fixed-threshold two-bank inference with a reference-estimated activation trigger

**Theory memo version:** D2 v1
**Date:** 2 August 2026
**Status:** Theoretical derivation completed; numerical validation protocol not yet locked
**Locked parent protocol:** Work Package D0, tag `tess-theory-work-package-d0-v1-lock-20260802`
**Frozen D1 result:** tag `tess-theory-work-package-d1-v1-results-review-20260802`

---

## Executive assessment

Work Package D2 is mathematically successful in the regular one-candidate-per-branch model fixed by D0.

D1 treated the activation threshold as known and isolated candidate-calibration uncertainty. D2 estimates the activation threshold from the same complete-vector reference bank that estimates the two candidate thresholds. The rejection estimator again admits a two-bank asymptotic linear representation, now with a third reference influence component. The trigger contribution has the same boundary-flux interpretation as the candidate contributions: trigger-quantile fluctuation matters only on states for which moving the activation boundary can change the final policy decision.

The main results are:

1. a joint Bahadur representation for the two candidate quantiles and the activation quantile estimated from one complete-vector reference bank;
2. an explicit derivative of the policy rejection probability with respect to the activation threshold;
3. a three-component reference influence function in which all marginal density factors cancel;
4. an explicit reference-bank variance formula retaining every within-replication covariance among candidate and activation indicators;
5. fixed-threshold asymptotic normality for the rejection probability and TESS;
6. validity of the independently resampled complete-replication two-bank nonparametric bootstrap under the regular D2 model;
7. an exact independent-normal benchmark, including the extra trigger-uncertainty term;
8. an exact finite-reference expectation under independent continuous coordinates, exposing the order $B^{-1}$ calibration bias observed in D1.

Thus the **theoretical** D0 core success criterion is met for the regular model: a fixed-threshold asymptotic linear representation with an estimated trigger and a valid complete-replication two-bank bootstrap. Scientific numerical validation remains prospective and must be locked independently after runtime-only preflight.

The D1 locked status remains REVIEW. D2 does not revise, replace, or rerun D1. It uses the D1 findings prospectively: influence-function normal or bootstrap-normal intervals will be primary in D2 validation, percentile intervals secondary, and basic intervals diagnostic.

---

# 1. Model, target, and estimator

Fix

$$
\alpha\in(0,1),\qquad p=1-\alpha,
$$

and a target activation rate

$$
r\in(0,1),\qquad s=1-r.
$$

Let

$$
Z_b=(U_b,X_{0b},X_{1b}),\qquad b=1,\ldots,B,
$$

be iid complete null-reference replications, and let

$$
Y_i=(\widetilde U_i,\widetilde X_{0i},\widetilde X_{1i}),
\qquad i=1,\ldots,n,
$$

be iid evaluation replications from the same global-null law $P_0$. The banks are independent. Coordinates within a complete replication may be dependent.

Larger candidate scores and larger activation scores are more extreme. Define the population thresholds

$$
q_j=F_j^{-1}(p),\qquad j\in\{0,1\},
$$

and

$$
c=F_U^{-1}(s).
$$

The population policy rejects when the base candidate rejects, or when the base does not reject, the optional branch is activated, and the optional candidate rejects:

$$
h_\theta(y)
=
I(x_0>q_0)
+
I(x_0\le q_0,\ u>c,\ x_1>q_1),
$$

where

$$
\theta=(q_0,q_1,c)^T.
$$

The indicator terms are disjoint. Define

$$
\pi=P_0h_\theta(Y)
$$

and

$$
S
=
\frac{\log(1-\pi)}{\log(1-\alpha)}.
$$

The D2 target is population-calibrated: all three thresholds are population functionals of $P_0$.

For a sample $W_1,\ldots,W_B$, use the empirical generalized inverse

$$
\widehat F_B^{-1}(t)
=
\inf\{w:\widehat F_B(w)\ge t\}.
$$

The reference-bank estimators are

$$
\widehat q_{j,B}=\widehat F_{j,B}^{-1}(p),
\qquad
\widehat c_B=\widehat F_{U,B}^{-1}(s),
$$

and

$$
\widehat\theta_B
=(\widehat q_{0,B},\widehat q_{1,B},\widehat c_B)^T.
$$

The two-bank estimators are

$$
\widehat\pi_{B,n}
=
\frac1n\sum_{i=1}^n h_{\widehat\theta_B}(Y_i)
$$

and

$$
\widehat S_{B,n}
=
\frac{\log(1-\widehat\pi_{B,n})}{\log(1-\alpha)}.
$$

---

# 2. Assumptions

The assumptions are the D2 specialization of the locked D0 protocol.

## D2-A1. Independent complete-replication banks

Reference vectors are iid, evaluation vectors are iid, and the banks are independent. Every bootstrap draw resamples all coordinates from one replication together.

## D2-A2. Regular marginal quantiles

The marginal distribution functions of $X_0$, $X_1$, and $U$ are continuously differentiable near $q_0$, $q_1$, and $c$, with

$$
0<f_0(q_0),f_1(q_1),f_U(c)<\infty.
$$

## D2-A3. Smooth policy boundary

The joint law of $(U,X_0,X_1)$ has a density continuous near the three boundary surfaces and their relevant intersections. The conditional boundary probabilities defined below exist and vary continuously locally.

## D2-A4. No boundary mass

$$
P_0(X_j=q_j)=0,
\qquad
P_0(U=c)=0.
$$

## D2-A5. Comparable bank growth

$$
B\to\infty,
\qquad
n\to\infty,
\qquad
\frac nB\to\lambda\in(0,\infty).
$$

## D2-A6. Nondegenerate TESS transformation

$$
0<\pi<1.
$$

## D2-A7. Fixed declared design

The local threshold $\alpha$, target activation rate $r$, score directions, policy form, and quantile conventions are fixed independently of both banks.

The model still excludes multiple-model winner selection, ties, failed fits, and exact plus-one finite-bank boundaries. Those remain later extensions under the D0 ladder.

---

# 3. Joint three-quantile expansion

Define the centered threshold indicators

$$
W_0=I(X_0\le q_0)-p,
$$

$$
W_1=I(X_1\le q_1)-p,
$$

and

$$
W_U=I(U\le c)-s.
$$

The conventional quantile influence functions are

$$
\psi_0(Z)=\frac{p-I(X_0\le q_0)}{f_0(q_0)},
$$

$$
\psi_1(Z)=\frac{p-I(X_1\le q_1)}{f_1(q_1)},
$$

and

$$
\psi_U(Z)=\frac{s-I(U\le c)}{f_U(c)}.
$$

Let

$$
\psi_\theta(Z)
=
(\psi_0(Z),\psi_1(Z),\psi_U(Z))^T.
$$

## Lemma D2.1. Joint Bahadur representation

Under D2-A1 and D2-A2,

$$
\widehat\theta_B-\theta
=
\frac1B\sum_{b=1}^B\psi_\theta(Z_b)
+o_p(B^{-1/2}).
$$

Consequently,

$$
\sqrt B(\widehat\theta_B-\theta)
\rightsquigarrow
N(0,\Sigma_\theta),
$$

where

$$
\Sigma_\theta=\operatorname{Var}\{\psi_\theta(Z)\}.
$$

### Proof

Apply the fixed-probability Bahadur representation to all three marginal quantiles. Because they are estimated from the same complete reference vectors, the three scalar expansions combine into one vector expansion. A multivariate central limit theorem gives the joint Gaussian limit and preserves all within-replication covariance terms. $\square$

The covariance matrix contains, for example,

$$
\operatorname{Cov}(\psi_0,\psi_U)
=
\frac{P(X_0\le q_0,U\le c)-ps}
{f_0(q_0)f_U(c)},
$$

with analogous expressions for $(X_1,U)$ and $(X_0,X_1)$.

---

# 4. Differentiating the rejection law in three directions

For generic thresholds $(t_0,t_1,d)$, define

$$
m(t_0,t_1,d)
=
P_0\{X_0>t_0\}
+
P_0\{X_0\le t_0,U>d,X_1>t_1\}.
$$

Then $\pi=m(q_0,q_1,c)$.

Define the three boundary relevance probabilities

$$
a_0
=
P_0\{U\le c\ \text{or}\ X_1\le q_1\mid X_0=q_0\},
$$

$$
b_1
=
P_0\{X_0\le q_0,U>c\mid X_1=q_1\},
$$

and

$$
d_U
=
P_0\{X_0\le q_0,X_1>q_1\mid U=c\}.
$$

## Lemma D2.2. Three boundary derivatives

Under D2-A3 and D2-A4,

$$
\frac{\partial m}{\partial t_0}(q_0,q_1,c)
=-f_0(q_0)a_0,
$$

$$
\frac{\partial m}{\partial t_1}(q_0,q_1,c)
=-f_1(q_1)b_1,
$$

and

$$
\boxed{
\frac{\partial m}{\partial d}(q_0,q_1,c)
=-f_U(c)d_U.
}
$$

### Proof

The first two derivatives are the D1 boundary-flux formulas. For the activation threshold, increase $d$ by a small amount. This removes from the rejection region the thin slice where

$$
X_0\le q_0,
\qquad
X_1>q_1,
\qquad
c<U\le c+\Delta.
$$

Differentiating the probability of this slice gives

$$
-f_U(c)
P_0\{X_0\le q_0,X_1>q_1\mid U=c\}.
$$

This is the claimed expression. $\square$

### Interpretation

The coefficient $d_U$ is the probability that the state at the activation boundary is an incremental-rejection state: the base would not reject, while the optional candidate would reject. Trigger estimation is irrelevant to first order when $d_U=0$.

---

# 5. D2 reference influence function

The evaluation influence function remains

$$
\phi_E(Y)=h_\theta(Y)-\pi.
$$

By the chain rule,

$$
\phi_R(Z)
=
\nabla m(\theta)^T\psi_\theta(Z).
$$

Using Lemmas D2.1 and D2.2, all marginal densities cancel:

$$
\boxed{
\phi_R(Z)
=
a_0W_0+b_1W_1+d_UW_U.
}
$$

Equivalently,

$$
\phi_R(Z)
=
a_0\{I(X_0\le q_0)-p\}
+b_1\{I(X_1\le q_1)-p\}
+d_U\{I(U\le c)-s\}.
$$

The new D2 term is therefore

$$
\phi_{R,\mathrm{trigger}}(Z)
=
d_U\{I(U\le c)-(1-r)\}.
$$

This form is directly interpretable:

> trigger-boundary relevance multiplied by trigger-quantile fluctuation.

---

# 6. Two-bank asymptotic linearity

## Theorem D2.1. Estimated-trigger two-bank expansion

Under D2-A1--D2-A7,

$$
\boxed{
\widehat\pi_{B,n}-\pi
=
\frac1n\sum_{i=1}^n\phi_E(Y_i)
+
\frac1B\sum_{b=1}^B\phi_R(Z_b)
+o_p(n^{-1/2}+B^{-1/2}).
}
$$

### Proof

Let $P_n$ be the evaluation empirical measure and $P$ expectation under $P_0$. Decompose

$$
\widehat\pi_{B,n}-\pi
=
(P_n-P)h_\theta
+P(h_{\widehat\theta_B}-h_\theta)
+(P_n-P)(h_{\widehat\theta_B}-h_\theta).
$$

The first term is the evaluation influence average. By differentiability of $m$ and Lemma D2.1,

$$
P(h_{\widehat\theta_B}-h_\theta)
=
\nabla m(\theta)^T(\widehat\theta_B-\theta)
+o_p(B^{-1/2})
$$

$$
=
\frac1B\sum_{b=1}^B\phi_R(Z_b)
+o_p(B^{-1/2}).
$$

The local class

$$
\mathcal H
=
\{h_{(t_0,t_1,d)}:(t_0,t_1,d)\text{ near }(q_0,q_1,c)\}
$$

is a finite Boolean combination of coordinate threshold sets and is a VC class. Under consistency of all three quantiles and no boundary mass,

$$
\|h_{\widehat\theta_B}-h_\theta\|_{P,2}\to_p0.
$$

Conditional asymptotic equicontinuity of the evaluation empirical process, using independence of the banks, gives

$$
\sqrt n(P_n-P)(h_{\widehat\theta_B}-h_\theta)=o_p(1).
$$

Combining the terms proves the expansion. $\square$

## Corollary D2.1. Asymptotic normality

If $n/B\to\lambda\in(0,\infty)$, then

$$
\sqrt n(\widehat\pi_{B,n}-\pi)
\rightsquigarrow
N(0,\sigma_\pi^2),
$$

where

$$
\sigma_\pi^2
=
\sigma_E^2+\lambda\sigma_R^2,
$$

$$
\sigma_E^2=\pi(1-\pi),
$$

and

$$
\sigma_R^2=\operatorname{Var}\{a_0W_0+b_1W_1+d_UW_U\}.
$$

The banks are independent, so there is no cross-bank covariance term.

---

# 7. Explicit reference-bank variance

Define

$$
F_{01}=P(X_0\le q_0,X_1\le q_1),
$$

$$
F_{0U}=P(X_0\le q_0,U\le c),
$$

and

$$
F_{1U}=P(X_1\le q_1,U\le c).
$$

Then

$$
\operatorname{Var}(W_0)
=
\operatorname{Var}(W_1)
=
\alpha(1-\alpha),
$$

$$
\operatorname{Var}(W_U)=r(1-r),
$$

and the pairwise covariances are

$$
\operatorname{Cov}(W_0,W_1)=F_{01}-p^2,
$$

$$
\operatorname{Cov}(W_0,W_U)=F_{0U}-ps,
$$

$$
\operatorname{Cov}(W_1,W_U)=F_{1U}-ps.
$$

Therefore,

$$
\boxed{
\begin{aligned}
\sigma_R^2
={}&\alpha(1-\alpha)(a_0^2+b_1^2)
+r(1-r)d_U^2\\
&+2a_0b_1(F_{01}-p^2)\\
&+2a_0d_U(F_{0U}-ps)\\
&+2b_1d_U(F_{1U}-ps).
\end{aligned}
}
$$

The three pairwise covariance terms are why the complete reference vector must be resampled intact. Separate resampling of the candidate columns or of the trigger column would generally be invalid.

## Corollary D2.2. Difference from the known-trigger reference variance

Let

$$
\phi_R^{(1)}=a_0W_0+b_1W_1
$$

be the D1 known-trigger reference influence function. Then

$$
\sigma_{R,D2}^2-\sigma_{R,D1}^2
=
r(1-r)d_U^2
+2d_U\{a_0(F_{0U}-ps)+b_1(F_{1U}-ps)\}.
$$

This difference need not be positive under arbitrary dependence. Estimating an additional threshold adds a new random component, but its covariance with the candidate-calibration components can be negative. Under independent coordinates, the covariance terms vanish and the difference is positive.

## Corollary D2.3. Isolating trigger estimation

Let $\widehat\pi^{\mathrm{known}}_{B,n}$ use the same reference-estimated candidate thresholds and evaluation bank, but the population trigger $c$. Then

$$
\widehat\pi_{B,n}
-
\widehat\pi^{\mathrm{known}}_{B,n}
=
\frac1B\sum_{b=1}^B d_UW_{U,b}
+o_p(n^{-1/2}+B^{-1/2}).
$$

This contrast isolates the first-order contribution of estimating the trigger.

---

# 8. TESS transformation

Let

$$
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)}
$$

and

$$
g_\alpha'(x)
=
\frac{-1}{(1-x)\log(1-\alpha)}.
$$

## Corollary D2.4. TESS asymptotic normality

$$
\sqrt n(\widehat S_{B,n}-S)
\rightsquigarrow
N(0,\sigma_S^2),
$$

where

$$
\sigma_S^2
=
\{g_\alpha'(\pi)\}^2
\{\sigma_E^2+\lambda\sigma_R^2\}.
$$

The TESS influence functions are

$$
\phi_E^S=g_\alpha'(\pi)\phi_E,
\qquad
\phi_R^S=g_\alpha'(\pi)\phi_R.
$$

---

# 9. Complete-replication two-bank bootstrap

Independently sample with replacement

$$
Z_1^*,\ldots,Z_B^*
$$

from the complete reference vectors and

$$
Y_1^*,\ldots,Y_n^*
$$

from the complete evaluation vectors. Inside every reference bootstrap draw, recompute

$$
\widehat q_{0,B}^*,
\qquad
\widehat q_{1,B}^*,
\qquad
\widehat c_B^*.
$$

Define

$$
\widehat\pi_{B,n}^*
=
\frac1n\sum_{i=1}^n h_{\widehat\theta_B^*}(Y_i^*).
$$

## Theorem D2.2. Bootstrap consistency

Under D2-A1--D2-A7, conditionally on the observed banks and in outer probability,

$$
\sqrt n(\widehat\pi_{B,n}^*-\widehat\pi_{B,n})
\rightsquigarrow_*
N(0,\sigma_\pi^2).
$$

The same conclusion holds after the TESS transformation:

$$
\sqrt n(\widehat S_{B,n}^*-\widehat S_{B,n})
\rightsquigarrow_*
N(0,\sigma_S^2).
$$

### Bootstrap linear representation

With independent multinomial bootstrap counts $M_b^R$ and $M_i^E$,

$$
\widehat\pi_{B,n}^*-\widehat\pi_{B,n}
=
\frac1n\sum_{i=1}^n(M_i^E-1)\phi_E(Y_i)
+
\frac1B\sum_{b=1}^B(M_b^R-1)\phi_R(Z_b)
+o_{P^*}(n^{-1/2}+B^{-1/2}).
$$

### Proof sketch

1. The ordinary nonparametric bootstrap consistently reproduces the joint three-quantile process at the fixed probabilities $p,p,s$.
2. The local three-threshold policy class is VC and the bootstrap evaluation empirical process is conditionally asymptotically equicontinuous.
3. Differentiability of $m$ transfers the three-quantile bootstrap expansion through the policy rejection functional.
4. The complete-vector reference bootstrap preserves every covariance term in $\sigma_R^2$.
5. Independent reference and evaluation bootstrap counts reproduce the original two-bank independence.
6. The ordinary delta method transfers consistency to TESS.

$\square$

### Interval implication after D1

Bootstrap consistency concerns the centered sampling distribution and consistent standard-error estimation. It does not guarantee that every interval transformation has equal finite-sample accuracy. D1 showed that basic intervals undercovered in small and moderate reference banks even when bootstrap standard errors were accurate. Consequently, the prospective D2 numerical protocol will use influence-function normal or bootstrap-normal intervals as primary regular intervals, percentile intervals as secondary, and basic intervals only as diagnostics.

---

# 10. Exact independent-normal benchmark

Assume

$$
U,X_0,X_1\overset{\mathrm{ind}}\sim N(0,1),
$$

with

$$
c=\Phi^{-1}(1-r),
\qquad
q_0=q_1=\Phi^{-1}(1-\alpha).
$$

Then

$$
\boxed{
\pi
=
\alpha+(1-\alpha)r\alpha.
}
$$

The boundary coefficients are

$$
\boxed{
a_0=1-r\alpha,
\qquad
b_1=r(1-\alpha),
\qquad
d_U=(1-\alpha)\alpha.
}
$$

Because the three threshold indicators are independent,

$$
\boxed{
\sigma_R^2
=
\alpha(1-\alpha)
\left[
(1-r\alpha)^2+
\{r(1-\alpha)\}^2
\right]
+
r(1-r)\{(1-\alpha)\alpha\}^2.
}
$$

The D2 trigger term is

$$
\boxed{
\sigma_{R,\mathrm{trigger}}^2
=
r(1-r)\{(1-\alpha)\alpha\}^2.
}
$$

At

$$
\alpha=0.05,
\qquad
r=0.50,
\qquad
\lambda=1,
$$

one obtains

$$
\pi=0.07375,
\qquad
S\approx1.493589,
$$

$$
a_0=0.975,
\qquad
b_1=0.475,
\qquad
d_U=0.0475,
$$

$$
\sigma_E^2\approx0.06831094,
$$

$$
\sigma_{R,D1}^2\approx0.05587188,
$$

$$
\sigma_{R,\mathrm{trigger}}^2\approx0.00056406,
$$

$$
\sigma_{R,D2}^2\approx0.05643594,
$$

and

$$
\boxed{
\sigma_\pi^2
\approx0.12474688.
}
$$

The trigger term is modest in this independent benchmark, but it can be larger under dependence or different activation regimes.

---

# 11. Exact finite-reference expectation under independent coordinates

The D1 validation revealed an order $B^{-1}$ finite-reference bias. In the independent continuous benchmark, this bias can be calculated exactly.

Let

$$
k_\alpha=\lceil B(1-\alpha)\rceil,
\qquad
k_r=\lceil B(1-r)\rceil.
$$

For an independent evaluation score and the empirical generalized-inverse candidate threshold,

$$
\tau_B
:=
P(X_{\mathrm{eval}}>X_{(k_\alpha)})
=
\frac{B+1-k_\alpha}{B+1}.
$$

Likewise, for the estimated activation threshold,

$$
\rho_B
:=
P(U_{\mathrm{eval}}>U_{(k_r)})
=
\frac{B+1-k_r}{B+1}.
$$

## Proposition D2.1. Exact finite-$B$ mean

Under independent continuous coordinates,

$$
\boxed{
E(\widehat\pi_{B,n})
=
\tau_B+(1-\tau_B)\rho_B\tau_B.
}
$$

This expectation does not depend on $n$.

### Proof

By the probability integral transform, the transformed candidate order statistic is Beta$(k_\alpha,B+1-k_\alpha)$, so its mean is $k_\alpha/(B+1)$. Therefore an independent evaluation score exceeds it with probability $(B+1-k_\alpha)/(B+1)=\tau_B$. The same argument gives $\rho_B$ for activation. Under coordinate independence, the three reference order statistics and the three evaluation coordinates factor, yielding the displayed policy probability. $\square$

For a known population trigger, replace $\rho_B$ by $r$. Thus the D1 known-trigger exact finite-$B$ mean is

$$
E(\widehat\pi_{B,n}^{\mathrm{known}})
=
\tau_B+(1-\tau_B)r\tau_B.
$$

The difference between $\tau_B$ and $\alpha$, and between $\rho_B$ and $r$, is order $B^{-1}$. This formula explains the D1 independent-benchmark bias nearly exactly and provides a sharper benchmark for D2 validation.

At $\alpha=0.05$ and $r=0.50$, the D2 population-target bias predicted by the exact finite-$B$ mean is approximately:

| $B$ | Exact mean minus population $\pi$ |
|---:|---:|
| 500 | 0.002797 |
| 1,000 | 0.001400 |
| 3,000 | 0.000467 |

These are finite-calibration effects, not contradictions of the first-order theorem.

---

# 12. Runtime-only preflight and numerical-validation implications

The accompanying preflight code checks the independent-normal D2 estimator, the complete-replication two-bank bootstrap, analytic derivatives, the D2 influence variance, and the exact finite-$B$ mean.

The preflight is labeled

> **RUNTIME-ONLY PREFLIGHT - NOT SCIENTIFIC EVIDENCE**

and uses only a small outer loop and small bootstrap count to measure runtime and code-path integrity.

The later D2 numerical protocol will be locked only after the local preflight is reviewed. Consistent with the frozen D1 adjudication, it will prospectively distinguish:

- main regimes with $B\ge3000$;
- stress regimes with $B=500$ and $B=1000$;
- $\alpha=0.01$ as a finite-order-statistic stress threshold;
- influence-function normal or bootstrap-normal intervals as primary;
- percentile intervals as secondary;
- basic intervals as finite-sample diagnostics;
- evaluation-only intervals as negative controls;
- known-trigger and estimated-trigger estimators evaluated on paired banks.

No D2 scientific simulation settings, outer repetitions, bootstrap repetitions, scientific seeds, or success criteria are locked in this memo.

---

# 13. What D2 completes and what remains

## Completed theoretically in D2

- fixed local threshold;
- one candidate per branch;
- candidate quantiles estimated from the reference bank;
- activation threshold estimated from the same reference bank;
- a population-calibrated policy rejection target;
- three-component reference influence function;
- explicit covariance-preserving reference variance;
- asymptotic normality on rejection and TESS scales;
- complete-replication two-bank bootstrap validity;
- exact independent-normal benchmark;
- exact independent-coordinate finite-$B$ mean.

## Still open after D2

- scientific numerical validation of D2;
- paired adaptive-policy contrasts matching promising versus random expansion;
- threshold-indexed weak convergence and simultaneous bands;
- exact plus-one finite-bank boundaries;
- multiple candidates and winner selection;
- base activation scores defined by maxima;
- ties, deterministic tie randomization, and failed-fit fallback rules.

---

# 14. Decision after D2 theory

**D2 theoretical status: complete in the regular model.**

The regular D0 core success criterion is met at theorem level. The new trigger component is explicit and interpretable:

$$
\phi_R
=
\text{base-boundary relevance}
\times
\text{base-quantile fluctuation}
$$

$$
+
\text{optional-boundary relevance}
\times
\text{optional-quantile fluctuation}
$$

$$
+
\text{activation-boundary relevance}
\times
\text{trigger-quantile fluctuation}.
$$

The next actions are:

1. install and locally reproduce the D2 unit tests and runtime-only preflight;
2. use runtime only to design a separate prospective D2 numerical-validation protocol;
3. lock that protocol before the scientific run;
4. conduct and freeze D2 numerical validation;
5. decide whether the next theoretical priority is a paired-policy contrast or the threshold-indexed process.

D1 remains frozen with status REVIEW and is not modified by D2.

---

# References

1. Bahadur RR. A note on quantiles in large samples. *Annals of Mathematical Statistics*. 1966;37(3):577-580. doi:10.1214/aoms/1177699450.
2. Kiefer J. On Bahadur's representation of sample quantiles. *Annals of Mathematical Statistics*. 1967;38(5):1323-1342. doi:10.1214/aoms/1177698690.
3. Bickel PJ, Freedman DA. Some asymptotic theory for the bootstrap. *Annals of Statistics*. 1981;9(6):1196-1217. doi:10.1214/aos/1176345637.
4. Gine E, Zinn J. Bootstrapping general empirical measures. *Annals of Probability*. 1990;18(2):851-869. doi:10.1214/aop/1176990862.
5. David HA, Nagaraja HN. *Order Statistics*. 3rd ed. Wiley; 2003.
6. van der Vaart AW. *Asymptotic Statistics*. Cambridge University Press; 1998. doi:10.1017/CBO9780511802256.
7. van der Vaart AW, Wellner JA. *Weak Convergence and Empirical Processes: With Applications to Statistics*. Springer; 1996. doi:10.1007/978-1-4757-2545-2.
8. Kosorok MR. *Introduction to Empirical Processes and Semiparametric Inference*. Springer; 2008. doi:10.1007/978-0-387-74978-5.
