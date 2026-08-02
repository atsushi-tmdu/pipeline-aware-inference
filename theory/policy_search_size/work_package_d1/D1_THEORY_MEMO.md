# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D1: fixed-threshold two-bank inference with a known activation trigger

**Theory memo version:** D1 v1
**Date:** 2 August 2026
**Status:** Theoretical derivation completed; numerical protocol not yet locked
**Locked parent protocol:** Work Package D0, tag `tess-theory-work-package-d0-v1-lock-20260802`

---

## Executive assessment

Work Package D1 is mathematically successful.

For the regular two-bank model fixed in D0, with one base score, one optional score, a known activation threshold, and candidate quantiles estimated from an independent reference bank, the policy rejection estimator admits an explicit two-sample asymptotic linear representation. The reference-bank influence function simplifies substantially: the marginal score densities cancel, leaving two boundary transition probabilities multiplied by centered quantile indicators. This makes the source of reference-bank uncertainty interpretable and exposes how dependence between candidate scores enters the variance.

The main results are:

1. a joint Bahadur expansion for the two candidate quantiles estimated from complete reference replications;
2. explicit derivatives of the adaptive rejection probability with respect to both candidate thresholds;
3. a two-bank influence-function expansion with separate reference and evaluation contributions;
4. asymptotic normality for the rejection probability and TESS at a fixed local threshold;
5. an explicit variance decomposition, including covariance induced by using the same complete reference replications for both candidate calibrations;
6. validity of the independently resampled complete-replication two-bank nonparametric bootstrap under the regular D1 model;
7. an exact independent-normal benchmark for numerical validation.

D1 isolates candidate-calibration uncertainty. It does **not** yet estimate the activation trigger. The estimated-trigger term required by D2 remains the minimum scientific success criterion for Work Package D.

---

# 1. Model and estimand

Fix a local threshold

$$
\alpha\in(0,1),
\qquad p=1-\alpha.
$$

Let

$$
Z_b=(U_b,X_{0b},X_{1b}),
\qquad b=1,\ldots,B,
$$

be iid complete null-reference replications, and let

$$
Y_i=(\widetilde U_i,\widetilde X_{0i},\widetilde X_{1i}),
\qquad i=1,\ldots,n,
$$

be iid evaluation replications from the same global-null law $P_0$. The two banks are independent.

Larger candidate scores are more extreme. Let

$$
q_j=F_j^{-1}(p),
\qquad j\in\{0,1\},
$$

be the population candidate thresholds. The activation threshold $c$ is fixed and known in D1.

The policy rejects if the base candidate rejects, or if the base candidate does not reject, the optional branch is activated, and the optional candidate rejects:

$$
h_\theta(y)
=
I(x_0>q_0)
+
I(x_0\le q_0,\ u>c,\ x_1>q_1),
$$

where

$$
\theta=(q_0,q_1)^T.
$$

The two indicator terms are disjoint, so $h_\theta\in\{0,1\}$. Define

$$
\pi
=
P_0 h_\theta(Y)
$$

and

$$
S
=
\frac{\log(1-\pi)}{\log(1-\alpha)}.
$$

The D1 estimand is population-calibrated. The candidate thresholds are population quantiles of the null score laws, whereas their estimators are obtained from the finite reference bank.

---

# 2. Estimator and quantile convention

For a sample $x_1,\ldots,x_B$, define the empirical generalized-inverse quantile by

$$
\widehat F_B^{-1}(p)
=
\inf\{x:\widehat F_B(x)\ge p\}.
$$

Equivalently, for continuous data this is the order statistic with index

$$
k_B(p)=\lceil Bp\rceil.
$$

The reference-bank candidate thresholds are

$$
\widehat q_{j,B}
=
\widehat F_{j,B}^{-1}(p),
\qquad j\in\{0,1\}.
$$

Write

$$
\widehat\theta_B
=(\widehat q_{0,B},\widehat q_{1,B})^T.
$$

The two-bank rejection estimator is

$$
\widehat\pi_{B,n}
=
\frac1n\sum_{i=1}^n h_{\widehat\theta_B}(Y_i),
$$

and

$$
\widehat S_{B,n}
=
\frac{\log(1-\widehat\pi_{B,n})}
{\log(1-\alpha)}.
$$

The empirical-quantile convention is part of the estimator. Exact finite-bank plus-one p-value boundaries remain outside D1 and are reserved for the later D-plus sequence specified in D0.

---

# 3. Assumptions

The following are D1 specializations of the locked D0 assumptions.

## D1-A1. Independent complete-replication banks

The reference vectors are iid, the evaluation vectors are iid, and the two banks are independent. Dependence among $U,X_0,X_1$ within a complete replication is unrestricted except where smoothness is imposed below.

## D1-A2. Regular candidate quantiles

For $j=0,1$, the marginal distribution $F_j$ is continuously differentiable in a neighborhood of $q_j$, with density

$$
0<f_j(q_j)<\infty.
$$

## D1-A3. Smooth rejection boundary

The joint law of $(U,X_0,X_1)$ has a density that is continuous in neighborhoods of the boundary surfaces $X_0=q_0$ and $X_1=q_1$. The boundary conditional probabilities defined below exist and are continuous locally.

## D1-A4. No boundary mass

$$
P_0(X_j=q_j)=0,
\qquad
P_0(U=c)=0.
$$

## D1-A5. Comparable bank growth

$$
B\to\infty,
\qquad
n\to\infty,
\qquad
\frac{n}{B}\to\lambda\in(0,\infty).
$$

## D1-A6. Nondegenerate TESS transform

$$
0<\pi<1.
$$

## D1-A7. Fixed declared policy

The direction of extremeness, local threshold $\alpha$, and known activation threshold $c$ are fixed independently of both banks.

---

# 4. Joint reference-quantile expansion

Define the quantile influence functions

$$
\psi_j(Z)
=
\frac{p-I(X_j\le q_j)}{f_j(q_j)},
\qquad j=0,1,
$$

and

$$
\psi_\theta(Z)
=
\begin{pmatrix}
\psi_0(Z)\\
\psi_1(Z)
\end{pmatrix}.
$$

## Lemma D1.1. Joint Bahadur representation

Under D1-A1 and D1-A2,

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
\Sigma_\theta
=
\operatorname{Var}\{\psi_\theta(Z)\}.
$$

### Proof

The marginal Bahadur representation applies at the fixed probability $p$ because each density is positive and continuous at the corresponding quantile. Applying the two marginal representations to the same complete reference replications gives the vector expansion. The multivariate central limit theorem then yields the joint Gaussian limit. The off-diagonal entry of $\Sigma_\theta$ retains dependence between $X_0$ and $X_1$ within a reference replication. $\square$

### Explicit covariance

Let

$$
I_j=I(X_j\le q_j).
$$

Because $E(I_j)=p$,

$$
\operatorname{Cov}(\psi_0,\psi_1)
=
\frac{P(X_0\le q_0,X_1\le q_1)-p^2}
{f_0(q_0)f_1(q_1)}.
$$

Thus candidate calibrations are generally not independent even though they are marginal quantiles.

---

# 5. Differentiating the adaptive rejection law

For thresholds $(t_0,t_1)$, define

$$
m(t_0,t_1)
=
P_0\{X_0>t_0\}
+
P_0\{X_0\le t_0,U>c,X_1>t_1\}.
$$

Then $\pi=m(q_0,q_1)$.

Define the boundary transition probabilities

$$
a_0
=
P_0\{U\le c\ \text{or}\ X_1\le q_1\mid X_0=q_0\},
$$

and

$$
b_1
=
P_0\{X_0\le q_0,U>c\mid X_1=q_1\}.
$$

Both lie in $[0,1]$.

## Lemma D1.2. Boundary derivatives

Under D1-A3 and D1-A4, $m$ is differentiable at $(q_0,q_1)$, with

$$
\frac{\partial m}{\partial t_0}(q_0,q_1)
=
-f_0(q_0)a_0,
$$

and

$$
\frac{\partial m}{\partial t_1}(q_0,q_1)
=
-f_1(q_1)b_1.
$$

### Proof

Write the rejection probability as

$$
m(t_0,t_1)
=
1-P_0\{X_0\le t_0,
U\le c\ \text{or}\ X_1\le t_1\}.
$$

Increasing $t_0$ adds an infinitesimal boundary slice to the no-rejection region whenever $U\le c$ or $X_1\le t_1$. Differentiation under the integral therefore gives

$$
\frac{\partial m}{\partial t_0}
=
-f_0(t_0)
P_0\{U\le c\ \text{or}\ X_1\le t_1\mid X_0=t_0\}.
$$

At $(q_0,q_1)$ this is the first formula.

Increasing $t_1$ enlarges the no-rejection region only for states satisfying $X_0\le t_0$ and $U>c$; states with $U\le c$ were already nonrejecting regardless of $X_1$. Hence

$$
\frac{\partial m}{\partial t_1}
=
-f_1(t_1)
P_0\{X_0\le t_0,U>c\mid X_1=t_1\},
$$

which gives the second formula. $\square$

### Interpretation

The coefficient $a_0$ is the probability that a marginal movement of the base threshold changes the policy decision. If the optional branch would already reject, moving the base threshold across its boundary does not alter the final policy decision. Similarly, $b_1$ is the probability that a marginal movement of the optional threshold matters because the base did not reject and activation occurred.

---

# 6. Two-bank asymptotic linearity

Define the evaluation influence function

$$
\phi_E(Y)
=
h_\theta(Y)-\pi.
$$

The formal reference contribution obtained by the chain rule is

$$
\phi_R(Z)
=
\nabla m(\theta)^T\psi_\theta(Z).
$$

Using Lemmas D1.1 and D1.2, the densities cancel:

$$
\boxed{
\phi_R(Z)
=
a_0\{I(X_0\le q_0)-p\}
+
b_1\{I(X_1\le q_1)-p\}.
}
$$

This cancellation is specific to quantile calibration: a threshold's sensitivity contains a marginal density factor, while the quantile influence function contains its reciprocal.

## Theorem D1.1. Fixed-threshold two-bank expansion

Under D1-A1--D1-A7,

$$
\widehat\pi_{B,n}-\pi
=
\frac1n\sum_{i=1}^n\phi_E(Y_i)
+
\frac1B\sum_{b=1}^B\phi_R(Z_b)
+
o_p(n^{-1/2}+B^{-1/2}).
$$

### Proof

Let $P_n$ denote the evaluation empirical measure and $P$ expectation under $P_0$. Decompose

$$
\widehat\pi_{B,n}-\pi
=
(P_n-P)h_\theta
+
P(h_{\widehat\theta_B}-h_\theta)
+
(P_n-P)(h_{\widehat\theta_B}-h_\theta).
$$

The first term is

$$
\frac1n\sum_{i=1}^n\phi_E(Y_i).
$$

By Lemma D1.2 and differentiability of $m$,

$$
P(h_{\widehat\theta_B}-h_\theta)
=
\nabla m(\theta)^T(\widehat\theta_B-\theta)
+o_p(B^{-1/2}).
$$

Lemma D1.1 converts this to

$$
\frac1B\sum_{b=1}^B\phi_R(Z_b)
+o_p(B^{-1/2}).
$$

It remains to control the last term. The local class

$$
\mathcal H
=
\{h_{(t_0,t_1)}:(t_0,t_1)\text{ near }(q_0,q_1)\}
$$

is a finite Boolean combination of coordinate threshold sets and hence is a VC class. It is therefore $P$-Donsker. Because $\widehat\theta_B\to_p\theta$ and there is no boundary mass,

$$
\|h_{\widehat\theta_B}-h_\theta\|_{P,2}\to_p0.
$$

Asymptotic equicontinuity of the evaluation empirical process, together with independence of the reference and evaluation banks, yields

$$
\sqrt n(P_n-P)(h_{\widehat\theta_B}-h_\theta)=o_p(1).
$$

Combining the three terms proves the expansion. $\square$

---

# 7. Asymptotic variance and TESS transformation

Let

$$
\sigma_E^2
=
\operatorname{Var}\{\phi_E(Y)\}
=
\pi(1-\pi),
$$

and

$$
\sigma_R^2
=
\operatorname{Var}\{\phi_R(Z)\}.
$$

Because the two banks are independent, there is no cross-bank covariance term.

## Corollary D1.1. Asymptotic normality

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
\sigma_E^2+\lambda\sigma_R^2.
$$

### Explicit reference variance

Let

$$
F_{01}=P(X_0\le q_0,X_1\le q_1).
$$

Then

$$
\boxed{
\sigma_R^2
=
\alpha(1-\alpha)(a_0^2+b_1^2)
+
2a_0b_1\{F_{01}-(1-\alpha)^2\}.
}
$$

The second term is the within-reference-replication covariance contribution. Resampling candidate columns separately would generally destroy this term and give an invalid uncertainty estimate.

## Corollary D1.2. TESS asymptotic normality

Let

$$
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)},
$$

so

$$
g_\alpha'(x)
=
\frac{-1}{(1-x)\log(1-\alpha)}.
$$

Then

$$
\sqrt n(\widehat S_{B,n}-S)
\rightsquigarrow
N(0,\sigma_S^2),
$$

with

$$
\sigma_S^2
=
\{g_\alpha'(\pi)\}^2
\{\sigma_E^2+\lambda\sigma_R^2\}.
$$

The corresponding influence functions are

$$
\phi_E^S=g_\alpha'(\pi)\phi_E,
\qquad
\phi_R^S=g_\alpha'(\pi)\phi_R.
$$

---

# 8. Complete-replication two-bank bootstrap

Let $Z_1^*,\ldots,Z_B^*$ be sampled with replacement from the complete reference vectors, and independently let $Y_1^*,\ldots,Y_n^*$ be sampled with replacement from the complete evaluation vectors.

Recompute

$$
\widehat q_{0,B}^*,
\qquad
\widehat q_{1,B}^*,
$$

inside the reference bootstrap sample, and define

$$
\widehat\pi_{B,n}^*
=
\frac1n\sum_{i=1}^n
h_{\widehat\theta_B^*}(Y_i^*).
$$

The known trigger $c$ is not re-estimated in D1.

## Theorem D1.2. Bootstrap consistency

Under D1-A1--D1-A7, conditionally on the observed banks and in $P_0$-probability,

$$
\sqrt n(\widehat\pi_{B,n}^*-\widehat\pi_{B,n})
\rightsquigarrow_*
N(0,\sigma_\pi^2).
$$

Equivalently, in bounded-Lipschitz distance, the conditional bootstrap law consistently estimates the sampling law of

$$
\sqrt n(\widehat\pi_{B,n}-\pi).
$$

The same conclusion holds after the TESS transform:

$$
\sqrt n(\widehat S_{B,n}^*-\widehat S_{B,n})
\rightsquigarrow_*
N(0,\sigma_S^2).
$$

### Bootstrap linear representation

The bootstrap satisfies

$$
\widehat\pi_{B,n}^*-\widehat\pi_{B,n}
=
\frac1n\sum_{i=1}^n(M_i^E-1)\phi_E(Y_i)
+
\frac1B\sum_{b=1}^B(M_b^R-1)\phi_R(Z_b)
+
o_{P^*}(n^{-1/2}+B^{-1/2}),
$$

in outer probability, where $M^E$ and $M^R$ are the independent multinomial bootstrap counts for the two banks.

### Proof sketch

1. Under D1-A2, the ordinary nonparametric bootstrap consistently reproduces the joint quantile process at the two fixed quantile probabilities. Hence
   $$
   \widehat\theta_B^*-\widehat\theta_B
   =
   \frac1B\sum_{b=1}^B(M_b^R-1)\psi_\theta(Z_b)
   +o_{P^*}(B^{-1/2})
   $$
   in outer probability.
2. The bootstrap empirical process indexed by the local VC class $\mathcal H$ is conditionally asymptotically equicontinuous. This controls replacing $h_\theta$ by $h_{\widehat\theta_B}$ and $h_{\widehat\theta_B^*}$.
3. Differentiability of $m$ transfers the reference quantile bootstrap expansion through the rejection functional.
4. The reference and evaluation bootstrap counts are conditionally independent, matching independence of the original banks.
5. Conditional central limit theorems for the two multinomially weighted sums give independent Gaussian limits with variances $\lambda\sigma_R^2$ and $\sigma_E^2$.
6. The ordinary delta method transfers bootstrap consistency to TESS because $g_\alpha$ is continuously differentiable at $\pi<1$. $\square$

## Consequence for variance estimation

The conditional variance of

$$
\sqrt n(\widehat\pi_{B,n}^*-\widehat\pi_{B,n})
$$

is a consistent estimator of $\sigma_\pi^2$. Likewise, the bootstrap variance on the TESS scale consistently estimates $\sigma_S^2$. Thus D1 obtains a consistently estimable variance without requiring nonparametric estimation of the boundary probabilities $a_0$ and $b_1$.

---

# 9. Exact independent-normal benchmark

The numerical preflight uses an exact benchmark rather than an unknown population target.

Assume

$$
U,X_0,X_1
\overset{\mathrm{ind}}\sim
N(0,1),
$$

and choose

$$
c=\Phi^{-1}(1-r),
\qquad
q_0=q_1=\Phi^{-1}(1-\alpha).
$$

Then

$$
P(U>c)=r,
\qquad
P(X_j>q_j)=\alpha.
$$

The population policy rejection probability is

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
b_1=r(1-\alpha).
}
$$

Because the candidate quantile indicators are independent,

$$
\boxed{
\sigma_R^2
=
\alpha(1-\alpha)
\left[
(1-r\alpha)^2
+
\{r(1-\alpha)\}^2
\right].
}
$$

Also,

$$
\sigma_E^2=\pi(1-\pi).
$$

Therefore, under $n/B\to\lambda$,

$$
\boxed{
\sigma_\pi^2
=
\pi(1-\pi)
+
\lambda\alpha(1-\alpha)
\left[
(1-r\alpha)^2
+
\{r(1-\alpha)\}^2
\right].
}
$$

This benchmark provides exact values for checking bias, empirical variance, reference/evaluation variance decomposition, and two-bank bootstrap output.

### Numerical value at the primary debug setting

For

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
$$

$$
S\approx1.493589,
$$

$$
\sigma_E^2\approx0.06831094,
\qquad
\sigma_R^2\approx0.05587188,
$$

and

$$
\sigma_\pi^2\approx0.12418281.
$$

These are asymptotic variances under $\sqrt n$ scaling; the approximate finite-sample variance of $\widehat\pi$ at $B=n$ is $\sigma_\pi^2/n$.

---

# 10. What D1 proves and what remains open

## Completed in D1

- fixed local threshold;
- known activation threshold;
- candidate-specific quantile calibration from a complete-vector reference bank;
- a population-calibrated policy rejection estimand;
- explicit reference and evaluation influence functions;
- asymptotic normality on rejection and TESS scales;
- an explicit variance decomposition;
- ordinary complete-replication two-bank bootstrap validity;
- an exact independent-normal benchmark.

## Not completed in D1

- reference-estimated activation threshold;
- threshold-indexed process weak convergence;
- paired policy contrasts;
- exact finite-bank plus-one boundaries;
- multiple candidates and winner selection;
- ties, failed fits, and deterministic tie randomization.

D1 is therefore a genuine partial success under the locked D0 ladder. D2 remains necessary before two-bank inference can become a central contribution of the top-tier paper.

---

# 11. Runtime-only numerical preflight

The accompanying preflight script executes the estimator and complete-replication two-bank bootstrap under the exact independent-normal benchmark. Its purpose is only to measure runtime, memory-light feasibility, and code-path integrity before locking the scientific D1 numerical protocol.

The preflight:

- uses the empirical generalized-inverse quantile convention declared above;
- fixes $\alpha=0.05$, $r=0.50$, and a known trigger;
- records Python and package versions;
- records elapsed time per outer dataset and per bootstrap replicate;
- verifies that all outputs are finite;
- performs exact formula and finite-difference derivative unit checks;
- is explicitly labeled **NOT SCIENTIFIC EVIDENCE**.

Outer Monte Carlo counts, bootstrap counts, coverage criteria, and scientific seeds will be locked only after the local runtime output is reviewed.

---

# 12. Decision after D1

**D1 status: theoretically complete.**

The reference-bank contribution is not merely an abstract nuisance term. It has an interpretable form:

$$
\phi_R
=
\text{base-boundary relevance}
\times
\text{base quantile fluctuation}
+
\text{optional-boundary relevance}
\times
\text{optional quantile fluctuation}.
$$

This directly explains why reference-bank uncertainty can materially widen the policy TESS interval and why complete-vector resampling is required.

The next steps are:

1. reproduce the D1 runtime preflight locally;
2. use runtime only to choose feasible outer and bootstrap repetition counts;
3. lock a separate D1 numerical validation protocol;
4. run and freeze the D1 scientific validation;
5. proceed to D2 by estimating the activation trigger and adding its third reference influence component.

---

# References

1. Bahadur RR. A note on quantiles in large samples. *Annals of Mathematical Statistics*. 1966;37(3):577-580. doi:10.1214/aoms/1177699450.
2. Kiefer J. On Bahadur's representation of sample quantiles. *Annals of Mathematical Statistics*. 1967;38(5):1323-1342. doi:10.1214/aoms/1177698690.
3. Bickel PJ, Freedman DA. Some asymptotic theory for the bootstrap. *Annals of Statistics*. 1981;9(6):1196-1217. doi:10.1214/aos/1176345637.
4. Gine E, Zinn J. Bootstrapping general empirical measures. *Annals of Probability*. 1990;18(2):851-869. doi:10.1214/aop/1176990862.
5. van der Vaart AW. *Asymptotic Statistics*. Cambridge University Press; 1998. doi:10.1017/CBO9780511802256.
6. van der Vaart AW, Wellner JA. *Weak Convergence and Empirical Processes: With Applications to Statistics*. Springer; 1996. doi:10.1007/978-1-4757-2545-2.
7. Kosorok MR. *Introduction to Empirical Processes and Semiparametric Inference*. Springer; 2008. doi:10.1007/978-0-387-74978-5.
