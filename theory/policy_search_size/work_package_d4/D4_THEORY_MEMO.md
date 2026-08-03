# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D4: paired two-bank inference for a budget-matched policy TESS contrast

**Theory memo version:** D4 v1\
**Date:** 2 August 2026\
**Status:** Theoretical derivation completed; numerical validation protocol not yet locked\
**Frozen architecture:** tag `tess-top-tier-manuscript-architecture-v1-final-20260802`\
**Frozen D2 result:** tag `tess-theory-work-package-d2-v1-results-final-20260802`

---

## Executive assessment

Work Package D4 closes the regular-model inferential loop between the structural policy calculus and the locked promising-versus-budget-matched-random empirical estimand.

At a fixed local threshold, define a base rejection indicator, an optional incremental-rejection indicator, and an adaptive activation indicator on the same null data state. The adaptive policy rejects through state-dependent activation. Its budget-matched comparator activates independently of the state at the same population rate. Their rejection-probability difference is the allocation premium

$$
\delta_\pi
=
\operatorname{Cov}(A,D),
$$

and their policy search-size difference is

$$
\Delta_S
=
g_\alpha(\pi_A)-g_\alpha(\pi_C).
$$

The plug-in estimator uses one complete-vector reference bank to calibrate the base, optional, and activation thresholds, and one independent evaluation bank to estimate both policies on exactly the same replications. The random comparator is not simulated by additional coin flips. Its rejection probability is estimated analytically as the product of the realized evaluation-bank activation rate and the realized incremental-rejection rate. This is the paired, Rao-Blackwellized version of the matched-random benchmark.

The main D4 results are:

1. an explicit evaluation influence function for the paired TESS contrast;
2. an explicit three-component reference influence function whose coefficients compare adaptive and random-comparator boundary relevance;
3. a two-bank asymptotic linear representation and normal limit;
4. validity of a paired complete-replication two-bank bootstrap using identical bootstrap indices for both policies;
5. an exact independent-Gaussian null benchmark in which the population contrast and first-order reference term vanish;
6. a correlated-Gaussian benchmark with a nonzero policy contrast and nonzero reference contribution for runtime and derivative checks.

D4 is intentionally narrow. It does not establish a simultaneous threshold process, a general policy directed acyclic graph, exact finite-bank plus-one boundaries, or validity for the full 20-candidate winner-selection pipeline. Those are separate bridge or extension problems.

---

# 1. Population model and policy contrast

Fix

$$
\alpha\in(0,1),
\qquad
p=1-\alpha,
$$

and a target activation rate

$$
\rho\in(0,1),
\qquad
s=1-\rho.
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

be iid evaluation replications from the same global-null law $P_0$. The two banks are independent, but the three coordinates within a replication may be dependent.

Larger values are more extreme. Define

$$
q_j=F_j^{-1}(p),
\qquad j\in\{0,1\},
$$

and

$$
c=F_U^{-1}(s).
$$

For one evaluation state, define

$$
R_0=I(X_0>q_0),
$$

$$
A=I(U>c),
$$

and the nested optional increment

$$
D=I(X_0\le q_0,\ X_1>q_1).
$$

Thus $R_0D=0$ and the expanded fixed policy rejects through

$$
R_1=R_0+D.
$$

The adaptive policy rejection indicator is

$$
R_A=R_0+AD.
$$

Write

$$
e_0=E(R_0),
\qquad
\rho=E(A),
\qquad
\mu=E(D),
\qquad
\nu=E(AD).
$$

Then the adaptive-policy rejection probability is

$$
\pi_A=e_0+\nu.
$$

The budget-matched random comparator activates independently of the state with probability $\rho$. Its rejection probability is

$$
\pi_C=e_0+\rho\mu.
$$

Therefore

$$
\boxed{
\delta_\pi
=
\pi_A-\pi_C
=
\nu-\rho\mu
=
\operatorname{Cov}(A,D).
}
$$

The policy search-size transform is

$$
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)},
$$

and the D4 target is

$$
\boxed{
\Delta_S
=
g_\alpha(\pi_A)-g_\alpha(\pi_C).
}
$$

The sign of $\Delta_S$ agrees with the sign of $\delta_\pi$, because $g_\alpha$ is strictly increasing.

---

# 2. Estimator and matched-budget convention

Use the empirical generalized inverse

$$
\widehat F_B^{-1}(t)
=
\inf\{x:\widehat F_B(x)\ge t\}.
$$

The complete reference bank gives

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

Using the evaluation bank and these thresholds, define

$$
\widehat e_0=P_n\widehat R_0,
\qquad
\widehat\rho=P_n\widehat A,
$$

$$
\widehat\mu=P_n\widehat D,
\qquad
\widehat\nu=P_n(\widehat A\widehat D).
$$

The paired rejection-probability estimators are

$$
\widehat\pi_A
=
\widehat e_0+\widehat\nu
=
P_n(\widehat R_0+\widehat A\widehat D),
$$

and

$$
\widehat\pi_C
=
\widehat e_0+\widehat\rho\widehat\mu.
$$

Finally,

$$
\widehat\delta_\pi
=
\widehat\pi_A-\widehat\pi_C,
$$

and

$$
\widehat\Delta_S
=
g_\alpha(\widehat\pi_A)-g_\alpha(\widehat\pi_C).
$$

## Why the comparator uses $\widehat\rho=P_n\widehat A$

The empirical benchmark is matched to the activation budget actually realized in the evaluation bank. Simulating an additional random activation coin would add avoidable Monte Carlo noise. The product estimator

$$
\widehat e_0+\widehat\rho\widehat\mu
$$

integrates that randomization out and preserves the exact pairing with the adaptive policy.

The same evaluation replications must be used for $\widehat e_0$, $\widehat\rho$, $\widehat\mu$, $\widehat\nu$, and both policy estimators.

---

# 3. Assumptions

## D4-A1. Independent complete-replication banks

Reference vectors are iid, evaluation vectors are iid, and the banks are independent. Complete vectors, not coordinate columns, are the resampling units.

## D4-A2. Regular marginal quantiles

The marginal distributions of $X_0$, $X_1$, and $U$ are continuously differentiable near $q_0$, $q_1$, and $c$, with positive finite densities there.

## D4-A3. Smooth boundary probabilities

The joint law has a density continuous near the three boundary surfaces and their relevant intersections. All boundary conditional probabilities used below exist and vary continuously locally.

## D4-A4. No boundary mass

$$
P(X_j=q_j)=0,
\qquad
P(U=c)=0.
$$

## D4-A5. Comparable bank growth

$$
B\to\infty,
\qquad
n\to\infty,
\qquad
\frac nB\to\lambda\in(0,\infty).
$$

## D4-A6. Nondegenerate TESS arguments

$$
0<\pi_A<1,
\qquad
0<\pi_C<1.
$$

## D4-A7. Fixed declared design

The threshold $\alpha$, target activation rate $\rho$, score directions, nested branch form, quantile convention, and matched-comparator definition are fixed independently of both banks.

---

# 4. Evaluation-bank influence function

At fixed population thresholds, consider the vector

$$
\eta=(e_0,\rho,\mu,\nu)^T.
$$

The corresponding observation vector is

$$
\ell(Y)=(R_0,A,D,AD)^T.
$$

Define

$$
H(\eta)
=
g_\alpha(e_0+\nu)-g_\alpha(e_0+\rho\mu).
$$

Because $H$ is continuously differentiable whenever both rejection probabilities are below one, the ordinary multivariate delta method applies to $P_n\ell$.

Let

$$
g_A'=g_\alpha'(\pi_A),
\qquad
g_C'=g_\alpha'(\pi_C),
$$

where

$$
g_\alpha'(x)
=
\frac{-1}{(1-x)\log(1-\alpha)}.
$$

## Lemma D4.1. Evaluation influence function

The evaluation-bank influence function for the TESS contrast is

$$
\boxed{
\begin{aligned}
\phi_E^\Delta(Y)
={}&g_A'\{R_0+AD-\pi_A\}\\
&-g_C'\left[\{R_0-e_0\}
+\mu(A-\rho)
+\rho(D-\mu)\right].
\end{aligned}
}
$$

### Proof

The adaptive rejection functional $e_0+\nu$ has influence function

$$
R_0+AD-\pi_A.
$$

For the comparator $e_0+\rho\mu$, the product rule gives

$$
(R_0-e_0)+\mu(A-\rho)+\rho(D-\mu).
$$

Applying the derivative of $g_\alpha$ to each component and subtracting proves the result. $\square$

## Corollary D4.1. Rejection-probability premium

The evaluation influence function for

$$
\delta_\pi=\nu-\rho\mu
$$

is

$$
\phi_E^{\delta}(Y)
=
AD-\nu-\mu(A-\rho)-\rho(D-\mu).
$$

Equivalently,

$$
\phi_E^{\delta}(Y)
=
(A-\rho)(D-\mu)-\delta_\pi.
$$

Thus the paired estimator is the empirical covariance functional, including its usual centering correction.

---

# 5. Boundary derivatives for the two policies

For generic thresholds $(t_0,t_1,d)$, define the adaptive rejection law

$$
\pi_A(t_0,t_1,d)
=
P(X_0>t_0)
+P(X_0\le t_0,U>d,X_1>t_1),
$$

and the random-comparator law

$$
\pi_C(t_0,t_1,d)
=
e_0(t_0)+\rho(d)\mu(t_0,t_1),
$$

where

$$
e_0(t_0)=P(X_0>t_0),
$$

$$
\rho(d)=P(U>d),
$$

and

$$
\mu(t_0,t_1)=P(X_0\le t_0,X_1>t_1).
$$

The adaptive boundary coefficients inherited from D2 are

$$
a_0
=
P(U\le c\ \text{or}\ X_1\le q_1\mid X_0=q_0),
$$

$$
b_1
=
P(X_0\le q_0,U>c\mid X_1=q_1),
$$

and

$$
d_U
=
P(X_0\le q_0,X_1>q_1\mid U=c).
$$

For the random comparator, define

$$
s_0=P(X_1>q_1\mid X_0=q_0),
$$

$$
t_1=P(X_0\le q_0\mid X_1=q_1),
$$

and the comparator boundary coefficients

$$
\bar a_0=1-\rho s_0,
$$

$$
\bar b_1=\rho t_1,
$$

$$
\bar d_U=\mu.
$$

## Lemma D4.2. Paired boundary gradients

At the population thresholds,

$$
\nabla\pi_A
=
\begin{pmatrix}
-f_0(q_0)a_0\\
-f_1(q_1)b_1\\
-f_U(c)d_U
\end{pmatrix},
$$

and

$$
\boxed{
\nabla\pi_C
=
\begin{pmatrix}
-f_0(q_0)\bar a_0\\
-f_1(q_1)\bar b_1\\
-f_U(c)\bar d_U
\end{pmatrix}.
}
$$

### Proof

The adaptive gradient is the D2 boundary-flux result. For the comparator,

$$
\frac{\partial e_0}{\partial t_0}=-f_0(t_0),
$$

$$
\frac{\partial\mu}{\partial t_0}
=f_0(t_0)P(X_1>t_1\mid X_0=t_0),
$$

and therefore

$$
\frac{\partial\pi_C}{\partial t_0}
=-f_0(q_0)\{1-\rho s_0\}.
$$

Likewise,

$$
\frac{\partial\mu}{\partial t_1}
=-f_1(t_1)P(X_0\le t_0\mid X_1=t_1),
$$

which gives the second component. Finally,

$$
\frac{\partial\rho}{\partial d}=-f_U(d),
$$

and $\mu$ does not depend on $d$, giving the third component. $\square$

---

# 6. Reference-bank influence function

Define the centered lower-tail indicators

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

The joint quantile expansion is the D2 Bahadur representation

$$
\widehat\theta_B-\theta
=
\frac1B\sum_{b=1}^B\psi_\theta(Z_b)
+o_p(B^{-1/2}).
$$

Let

$$
\kappa_0=g_A'a_0-g_C'\bar a_0,
$$

$$
\kappa_1=g_A'b_1-g_C'\bar b_1,
$$

and

$$
\kappa_U=g_A'd_U-g_C'\bar d_U.
$$

## Lemma D4.3. Reference influence function

All three marginal density factors cancel, and the reference contribution is

$$
\boxed{
\phi_R^\Delta(Z)
=
\kappa_0W_0+\kappa_1W_1+\kappa_UW_U.
}
$$

### Proof

By the chain rule,

$$
\phi_R^\Delta
=
\left\{g_A'\nabla\pi_A-g_C'\nabla\pi_C\right\}^T
\psi_\theta.
$$

Each threshold derivative contains its marginal density, while the corresponding quantile influence function contains the reciprocal density with the opposite centered-indicator sign. Substituting Lemma D4.2 yields the displayed coefficients. $\square$

## Interpretation

Each coefficient is a difference of boundary relevance on the TESS scale:

- $\kappa_0$ compares how moving the base threshold affects adaptive and random-comparator search size;
- $\kappa_1$ compares optional-threshold relevance;
- $\kappa_U$ compares activation-boundary relevance.

The reference term can be small through genuine cancellation. This is not evidence that reference calibration is generally ignorable.

---

# 7. Paired two-bank asymptotic linearity

## Theorem D4.1. Paired TESS-contrast expansion

Under D4-A1--D4-A7,

$$
\boxed{
\widehat\Delta_S-\Delta_S
=
\frac1n\sum_{i=1}^n\phi_E^\Delta(Y_i)
+
\frac1B\sum_{b=1}^B\phi_R^\Delta(Z_b)
+o_p(n^{-1/2}+B^{-1/2}).
}
$$

### Proof sketch

Let

$$
f_\theta(Y)=(R_0(\theta),A(\theta),D(\theta),A(\theta)D(\theta))^T.
$$

The estimator is

$$
H\{P_nf_{\widehat\theta_B}\}.
$$

Decompose the difference from $H\{Pf_\theta\}$ into:

1. the evaluation empirical-process term at fixed $\theta$;
2. the change in the population functional induced by $\widehat\theta_B-\theta$;
3. the empirical-process remainder produced by replacing $\theta$ with $\widehat\theta_B$.

The first term gives Lemma D4.1 by the multivariate delta method. The second gives Lemma D4.3 through the joint quantile expansion and boundary differentiability. The local class generated by $(R_0,A,D,AD)$ is a finite Boolean combination of coordinate threshold sets and is VC. Quantile consistency, no boundary mass, and asymptotic equicontinuity make the third term negligible. $\square$

## Corollary D4.2. Asymptotic normality

If $n/B\to\lambda\in(0,\infty)$, then

$$
\sqrt n(\widehat\Delta_S-\Delta_S)
\rightsquigarrow
N(0,\sigma_\Delta^2),
$$

where

$$
\boxed{
\sigma_\Delta^2
=
\operatorname{Var}(\phi_E^\Delta)
+\lambda\operatorname{Var}(\phi_R^\Delta).
}
$$

The two variance contributions add because the banks are independent.

---

# 8. Complete-vector covariance and reference variance

Let

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
\operatorname{Var}(W_U)=\rho(1-\rho),
$$

with the three pairwise covariances inherited from D2. Hence

$$
\begin{aligned}
\operatorname{Var}(\phi_R^\Delta)
={}&\alpha(1-\alpha)(\kappa_0^2+\kappa_1^2)
+\rho(1-\rho)\kappa_U^2\\
&+2\kappa_0\kappa_1(F_{01}-p^2)\\
&+2\kappa_0\kappa_U(F_{0U}-ps)\\
&+2\kappa_1\kappa_U(F_{1U}-ps).
\end{aligned}
$$

This formula is the reason the reference vector must remain intact. Resampling $U$, $X_0$, and $X_1$ separately would generally change the paired contrast variance.

---

# 9. Paired complete-replication two-bank bootstrap

In every bootstrap replication:

1. sample $B$ complete reference vectors with replacement;
2. recompute both candidate thresholds and the activation threshold;
3. independently sample $n$ complete evaluation vectors with replacement;
4. use the same reference and evaluation bootstrap indices for the adaptive and comparator policies;
5. recompute $\widehat e_0^*$, $\widehat\rho^*$, $\widehat\mu^*$, $\widehat\nu^*$, both rejection probabilities, and the TESS contrast.

## Theorem D4.2. Paired bootstrap consistency

Under D4-A1--D4-A7, conditionally on the observed banks and in outer probability,

$$
\sqrt n(\widehat\Delta_S^*-\widehat\Delta_S)
\rightsquigarrow_*
N(0,\sigma_\Delta^2).
$$

The bootstrap linear representation is

$$
\widehat\Delta_S^*-\widehat\Delta_S
=
\frac1n\sum_{i=1}^n(M_i^E-1)\phi_E^\Delta(Y_i)
+
\frac1B\sum_{b=1}^B(M_b^R-1)\phi_R^\Delta(Z_b)
+o_{P^*}(n^{-1/2}+B^{-1/2}).
$$

### Why pairing is non-negotiable

The adaptive and comparator estimators share $R_0$, $A$, $D$, the thresholds, and the evaluation observations. Independent bootstrap indices for the two policies would destroy these covariance gains and estimate the wrong contrast variance.

### Interval choice

D1 showed that bootstrap standard errors can be accurate while basic intervals under-cover in finite reference banks. D2 then prospectively validated centered bootstrap-normal inference in the main regime. D4 therefore carries forward the same hierarchy:

- primary: paired two-bank bootstrap-normal;
- secondary: paired percentile;
- diagnostic: paired basic and evaluation-only intervals.

No numerical success criteria are locked in this memo.

---

# 10. Gaussian benchmarks

## 10.1 Independent benchmark

Assume

$$
U,X_0,X_1\overset{\mathrm{ind}}\sim N(0,1).
$$

Then $A$ and $D$ are independent, so

$$
\pi_A=\pi_C,
\qquad
\delta_\pi=0,
\qquad
\Delta_S=0.
$$

Moreover,

$$
a_0=\bar a_0,
\qquad
b_1=\bar b_1,
\qquad
d_U=\bar d_U,
$$

and therefore

$$
\boxed{
\phi_R^\Delta=0.
}
$$

This is an exact cancellation, not a claim that reference uncertainty always vanishes. Under independence, the population contrast is identically zero for every threshold triple.

The evaluation influence function simplifies to

$$
\phi_E^\Delta
=
g_\alpha'(\pi)(A-\rho)(D-\mu),
$$

and

$$
\operatorname{Var}(\phi_E^\Delta)
=
\{g_\alpha'(\pi)\}^2
\rho(1-\rho)\mu(1-\mu).
$$

## 10.2 Correlated benchmark for preflight

For a nonzero regular contrast, use a trivariate standard normal law ordered as $(U,X_0,X_1)$ with correlation matrix

$$
\Sigma
=
\begin{pmatrix}
1 & 0.50 & 0.65\\
0.50 & 1 & 0.30\\
0.65 & 0.30 & 1
\end{pmatrix}.
$$

At

$$
\alpha=0.05,
\qquad
\rho=0.50,
\qquad
\lambda=1,
$$

numerical Gaussian integration gives approximately

$$
\pi_A=0.090643,
\qquad
\pi_C=0.071433,
$$

$$
\delta_\pi=0.019210,
$$

and

$$
\boxed{
\Delta_S=0.407557.
}
$$

The exact-gradient benchmark has

$$
\operatorname{Var}(\phi_E^\Delta)\approx4.68965,
$$

$$
\operatorname{Var}(\phi_R^\Delta)\approx2.91131,
$$

and therefore

$$
\sigma_\Delta^2\approx7.60096
$$

under $\sqrt n$ scaling when $n/B\to1$.

The accompanying code checks the analytic threshold gradient against a finite-difference derivative. This benchmark exercises both evaluation and reference components and is therefore preferable to independence for runtime preflight.

---

# 11. Runtime-only preflight

The bundled preflight uses the correlated Gaussian benchmark with

- $B=n=1000$;
- 30 outer replications;
- 100 paired two-bank bootstrap replications per outer dataset;
- seed 20261103.

Its purpose is to check:

- finite outputs;
- empirical generalized-inverse quantiles;
- paired estimator construction;
- complete-vector bootstrap code paths;
- exact Gaussian functionals;
- analytic versus finite-difference gradients;
- runtime and peak memory.

It is labeled

> **RUNTIME-ONLY PREFLIGHT - NOT SCIENTIFIC EVIDENCE**

and must not be cited as validation evidence.

---

# 12. Prospective numerical-validation implications

After local preflight review, D4 should receive a separately locked numerical protocol. The natural starting design is inherited from D2:

- the independent-normal, Gaussian-factor, and nonlinear-smooth DGP families;
- $\alpha\in\{0.01,0.05,0.10\}$;
- $(B,n)\in\{(500,500),(1000,1000),(3000,3000),(3000,5000)\}$;
- $B\ge3000$ as the main regime;
- smaller banks and $\alpha=0.01$ as stress diagnostics;
- paired bootstrap-normal as the primary interval;
- percentile as secondary;
- basic and evaluation-only inference as diagnostics.

D4 adds contrast-specific checks:

1. empirical versus exact asymptotic variance for $\widehat\Delta_S$;
2. paired bootstrap SD versus empirical SD;
3. paired bootstrap-normal coverage;
4. variance inflation caused by deliberately unpaired bootstrap indices as a negative diagnostic;
5. preservation of the sign and magnitude of the allocation premium in nonzero-contrast DGPs.

Outer repetitions, bootstrap repetitions, seeds, thresholds, and pass criteria are not locked here.

---

# 13. What D4 completes and what remains

## Completed theoretically in D4

- fixed-threshold adaptive-versus-budget-matched-random rejection contrast;
- evaluation-rate-matched comparator estimator;
- explicit evaluation influence function;
- explicit reference influence function;
- paired two-bank asymptotic linearity;
- paired complete-replication bootstrap validity;
- independent and correlated Gaussian benchmarks;
- runtime-only implementation and unit checks.

## Still open after D4 theory

- locked D4 scientific numerical validation;
- exact plus-one/order-statistic bridge;
- finite-candidate unique-winner bridge;
- rank-coherence proof audit;
- curve-crossing scope repair;
- frozen empirical signed gain/loss extraction;
- optional D3 threshold-process theory.

## Stop rule

Do not broaden D4 into a general policy graph or simultaneous threshold process before a complete Biometrika-length manuscript exists. D4 is successful when the regular paired theorem is rigorous, the paired bootstrap is validated in the main regime, and the result can be stated compactly as the inference theorem for the paper's primary policy contrast.

---

# References

1. Bahadur RR. A note on quantiles in large samples. *Annals of Mathematical Statistics*. 1966;37(3):577-580.
2. Bickel PJ, Freedman DA. Some asymptotic theory for the bootstrap. *Annals of Statistics*. 1981;9(6):1196-1217.
3. Gine E, Zinn J. Bootstrapping general empirical measures. *Annals of Probability*. 1990;18(2):851-869.
4. van der Vaart AW. *Asymptotic Statistics*. Cambridge University Press; 1998.
5. van der Vaart AW, Wellner JA. *Weak Convergence and Empirical Processes*. Springer; 1996.
6. Kosorok MR. *Introduction to Empirical Processes and Semiparametric Inference*. Springer; 2008.
