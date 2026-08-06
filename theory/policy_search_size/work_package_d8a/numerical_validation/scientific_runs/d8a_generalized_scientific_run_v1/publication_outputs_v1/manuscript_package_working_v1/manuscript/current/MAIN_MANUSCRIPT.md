# Second-Order Finite-Sample Bias in Threshold-Adaptive Statistical Policies

## Abstract

Adaptive statistical policies are often evaluated using thresholds estimated from a finite reference sample and outcomes observed in an independent evaluation sample. First-order asymptotic theory describes stochastic variation but does not quantify the resulting centering bias, and an ordinary smooth second-order expansion can fail when a base-candidate rejection threshold coincides with the added-candidate rejection threshold. We study the finite-sample estimation of a fixed continuous, monotone-augmentation policy contrast against a marginal-rate-matched comparator. For empirical-quantile calibration from a reference bank of size \(B\), we derive a fixed-dimensional joint moment expansion that retains the exact order-statistic convention and complete-vector dependence. At candidate-threshold coincidence, the policy functional has a continuous piecewise-quadratic expansion containing one-sided positive-part-square terms rather than a single ordinary Hessian. This yields a generalized reference-bias coefficient \(C_{\Delta,B}^{\mathrm{gen}}\). For an independent evaluation sample of size \(n\), the policy-contrast estimator satisfies an exact conditional identity, producing

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-\frac{\Delta_\pi}{n}
-\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
+o(B^{-1}+n^{-1}).
\]

We additionally derive a nonlinear expansion for the finite-status tail-equivalent search-size contrast, conditional on both empirical policy probabilities being below 1, and bound the complementary boundary-status probability exponentially. A prospectively locked numerical study comprising 17 primary and 8 diagnostic equivalence classes, 75 simulation jobs, and 126,000 Monte Carlo replicates formally passed every prespecified criterion. Raw diagnostics provided strong support for the policy-probability expansion, all 85 exact finite-\(n\) checks passed, and the finite-status TESS result passed formally but remained limited by Monte Carlo resolution. These results separate finite-reference and finite-evaluation effects while showing that threshold coincidence requires generalized second-order geometry in the declared policy class.

**Keywords:** adaptive policy; empirical quantile; finite-reference bias; finite-status TESS; second-order delta method; threshold coincidence; two-bank estimation

## 1. Introduction

Adaptive statistical and machine-learning workflows may condition later search on information generated earlier in the same development process, creating problems related to post-selection inference, selective inference, and adaptive data reuse (Berk et al., 2013; Taylor and Tibshirani, 2015; Dwork et al., 2015). Even when the candidate family is finite, the evaluated policy can depend on thresholds estimated from a finite reference sample. A second, independent sample may then be used to estimate the rejection probability or another policy-level performance functional. This two-bank construction separates calibration from evaluation, but it creates two distinct finite-sample effects: error in the estimated reference thresholds and finite-sample bias in the evaluation estimator.

Classical sample-quantile theory supplies first-order representations of empirical quantiles and their relation to the empirical distribution function (Bahadur, 1966; Kiefer, 1967), but first-order asymptotic theory is not designed to quantify the centering error caused by reference-threshold estimation. That error is typically of order \(B^{-1}\), where \(B\) is the reference-bank size, and depends on both the mean and covariance structure of the empirical quantiles. In particular, thresholds estimated from the same complete reference vectors are dependent; candidate–candidate and candidate–trigger cross terms cannot generally be discarded. For a smooth map, a moment-based second-order delta approximation suggests a gradient contribution plus a Hessian–covariance contraction (Oehlert, 1992). This smooth formula is sufficient only when the policy map is twice differentiable at the population thresholds.

Threshold-adaptive policies introduce an additional complication. Extended delta methods for directionally differentiable or nondifferentiable maps are well established, especially for weak limits and bootstrap validity (Shapiro, 1991; Dümbgen, 1993; Fang and Santos, 2019), and second-order nondifferentiability has also been studied in first-order-degenerate problems (Chen and Fang, 2019). The present target is different: an expectation-level \(B^{-1}\) expansion for a specific policy map whose first derivative generally remains nonzero. Incremental rejection after adding a candidate depends on a moving maximum between an existing winner score and the added candidate's threshold. When a base-candidate threshold coincides with the added-candidate threshold, the active branch of this maximum changes exactly at the expansion point. The policy map retains the same value and first derivative across the boundary, but its curvature changes one-sidedly. Consequently, the relevant local approximation is continuous and piecewise quadratic rather than globally represented by one ordinary Hessian. Figure 1 illustrates this distinction.

Finite evaluation creates a separate effect. For the empirical covariance convention used by the policy-contrast estimator, conditional expectation is available exactly: the estimator targets \((1-1/n)\Delta_\pi\), where \(n\) is the evaluation-sample size. Thus the evaluation contribution contains an exact \(-\Delta_\pi/n\) term rather than merely an asymptotic approximation. Combining this identity with the generalized reference expansion also produces an explicit algebraic \(B^{-1}n^{-1}\) product term.

We develop a theory-and-validation framework for these effects in a declared finite-candidate policy class. The matched comparator is used here to define a fixed plug-in functional; the paper does not compare promising, rescue, or other policy-design strategies, and it does not study whether equal candidate budgets imply equal inferential burden. The paper makes four contributions. First, it establishes a fixed-dimensional joint empirical-quantile moment expansion under the exact order-statistic convention. Second, it derives a generalized local policy expansion with positive-part-square terms at candidate-threshold coincidence. Third, it combines the generalized \(B^{-1}\) reference bias with the exact finite-\(n\) evaluation identity. Fourth, it propagates the expansion through the nonlinear tail-equivalent search-size transformation on the event that both empirical probabilities remain below 1, quantifies the complementary boundary-status probability, and evaluates the resulting approximations in a prospectively locked numerical study.

The contribution is deliberately narrower than a general theory of arbitrary adaptive pipelines. In particular, the present policy is monotone in rejection: optional expansion may add a rejection but cannot revoke a base rejection. This differs from selected-winner pipelines with candidate-specific empirical calibration, in which the full-minus-base rejection difference may also take the value \(-1\). The results concern continuous scores, fixed finite candidate pools, almost-surely unique winners, independent reference and evaluation banks, and strict separation between candidate thresholds and the activation threshold. Discrete plus-one empirical \(p\)-values, winner or trigger ties, failed-fit fallback rules, and growing candidate dimension require separate analysis. In particular, randomly sampled permutation distributions create genuinely discrete null laws rather than continuous tail-probability estimates (Phipson and Smyth, 2010).

---

## 2. Policy functional and two-bank estimation

### 2.1 Threshold-adaptive policy

All probabilities and expectations are taken under a fixed target law \(P\); in the multiplicity application that motivates the construction, \(P\) is the declared global-null law.

Consider continuous candidate scores \(X=(X_0,X_1,X_2)\). The base candidate pool is \(\{0,1\}\), and the full pool after optional expansion is \(\{0,1,2\}\). Define the almost-surely unique winners

\[
J_0
=
\arg\max_{j\in\{0,1\}}X_j,
\qquad
J_1
=
\arg\max_{j\in\{0,1,2\}}X_j.
\]

Candidate-specific rejection thresholds are \(q_0,q_1,q_2\). The base and full rejection indicators are

\[
R_0
=
I(X_{J_0}>q_{J_0}),
\qquad
R_1
=
I(X_{J_1}>q_{J_1}).
\]

Let

\[
T=\max(X_0,X_1)
\]

be the base-stage activation score, let \(c\) be its activation threshold, and define

\[
A=I(T>c).
\]

Collect the reference-calibrated parameters in

\[
\theta=(q_0,q_1,q_2,c)^\top.
\]

The incremental rejection opportunity is

\[
M=(1-R_0)R_1.
\]

Thus \(M=1\) only when adding candidate 2 converts a base nonrejection into a rejection, and \(R_0M=0\). The adaptive policy is a monotone augmentation: it preserves every base rejection and uses the full pool only to create additional rejections. This restriction excludes the loss state that can arise when a selected winner is recalibrated by a candidate-specific discrete empirical null. The adaptive-policy rejection indicator is

\[
R_A=R_0+AM.
\]

Write

\[
e_0(\theta)=E_\theta(R_0),\qquad
\rho(\theta)=E_\theta(A),\qquad
\mu(\theta)=E_\theta(M),\qquad
\nu(\theta)=E_\theta(AM).
\]

When no ambiguity arises, the dependence on \(\theta\) is suppressed. The adaptive-policy rejection probability is

\[
\pi_A=e_0+\nu.
\]

For comparison, let \(A^\circ\sim\operatorname{Bernoulli}(\rho)\) be independent of \((R_0,M)\), and define the marginal-rate-matched comparator rejection indicator

\[
R_C=R_0+A^\circ M.
\]

Its rejection probability is

\[
\pi_C=e_0+\rho\mu.
\]

The policy-probability contrast is

\[
\Delta_\pi
=
\pi_A-\pi_C
=
\nu-\rho\mu
=
P_{AM}-P_AP_M
=
\operatorname{Cov}(A,M),
\]

where \(P_A=\rho\), \(P_M=\mu\), and \(P_{AM}=\nu\). The covariance identity defines and interprets the estimand; covariance estimation itself is not the scientific endpoint.

### 2.2 Independent reference and evaluation banks

Let

\[
\mathcal R_B=\{W_b:b=1,\ldots,B\}
\]

be a reference bank used to estimate the candidate and activation thresholds, and let

\[
\mathcal E_n=\{O_i:i=1,\ldots,n\}
\]

be an independent evaluation bank used after the reference-calibrated policy has been fixed.

Each coordinate of \(\theta\) is an empirical quantile of a component variable generated by the complete reference vector. In the declared policy,

\[
(Y_0,Y_1,Y_2,Y_3)
=
(X_0,X_1,X_2,T),
\]

with target probabilities \((p_0,p_1,p_2,p_A)\); thus \(c\) is the population \(p_A\)-quantile of the base maximum \(T\). More generally, for coordinate \(\ell\), let

\[
Y_\ell=g_\ell(W),\qquad
P(Y_\ell\le\theta_\ell)=p_\ell,
\]

and use the exact order-statistic convention

\[
\widehat\theta_{\ell,R}
=
Y_{\ell,(k_{B,\ell})},
\qquad
k_{B,\ell}=\lceil Bp_\ell\rceil.
\]

Because all thresholds are obtained from the same complete reference vectors, their joint covariance includes candidate–candidate and candidate–trigger dependence.

Conditional on \(\widehat\theta_R\), define

\[
\widehat\pi_A
=
\overline{R_A}
=
\overline{R_0}+\overline{AM},
\]

\[
\widehat\pi_C
=
\overline{R_0}+\bar A\bar M,
\]

and

\[
\widehat\Delta_\pi
=
\widehat\pi_A-\widehat\pi_C
=
\overline{AM}-\bar A\bar M.
\]

Because \(R_0M=0\), \(\widehat\pi_C\) is a valid probability estimator:

\[
0\le \widehat\pi_C
\le
\overline{R_0}+\bar M
\le1.
\]

Reference-bank and evaluation-bank randomness are kept distinct throughout.

### 2.3 TESS contrast and finite-status estimand

For a fixed nominal level \(\alpha\in(0,1)\), define

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)},
\qquad 0\le x<1.
\]

The population tail-equivalent search-size contrast is

\[
\Delta_S
=
g_\alpha(\pi_A)-g_\alpha(\pi_C).
\]

At finite \(n\), an empirical probability can equal 1, so the raw logarithmic transform need not be finite. Define the finite-status event

\[
\mathcal F_{B,n}
=
\{
\widehat\pi_A<1,\,
\widehat\pi_C<1
\}.
\]

On \(\mathcal F_{B,n}\), define

\[
\widehat\Delta_S^{\mathrm{fin}}
=
g_\alpha(\widehat\pi_A)
-
g_\alpha(\widehat\pi_C).
\]

Outside \(\mathcal F_{B,n}\), the analysis retains a structured boundary status—positive infinity, negative infinity, or indeterminate when both empirical probabilities equal 1—rather than clipping or replacing the observation. The theoretical mean target is

\[
E(
\widehat\Delta_S^{\mathrm{fin}}
\mid
\mathcal F_{B,n}
).
\]

TESS is used only as an interpretable smooth standardization of rejection probability; the transformation itself is not the claimed methodological contribution. The primary theoretical object remains \(\Delta_\pi\).

### 2.4 Role of the comparator and separation of targets

The marginal-rate-matched comparator is used to expose the finite-sample behavior of a fixed scalar policy contrast. The present paper does not estimate the effect of choosing a promising rather than a rescue activation rule, does not analyze candidate-count or expected-budget identifiability, and does not evaluate fitted machine-learning libraries or clinical-data-anchored experiments. Its reference and evaluation samples are generated solely for the finite-sample theory declared here. Accordingly, the shared algebraic definitions of a matched comparator and TESS do not imply shared empirical evidence or a shared principal claim.

---

## 3. Generalized second-order theory

### 3.1 Joint reference-threshold expansion

The full primitive conditions are stated in the Supplement. In brief, the number of reference-calibrated coordinates is fixed; each component distribution is continuous with a positive and sufficiently smooth density near its target quantile; the scalar Bahadur remainders vanish in \(L^2\); and a common moment bound of order greater than two holds.

**Theorem 1 (joint empirical-quantile moment expansion).**  
Let \(\widehat\theta_R\) be the fixed-dimensional vector of empirical quantiles computed from \(B\) independent complete reference vectors. Under the stated regularity and moment conditions,

\[
E_R(\widehat\theta_R-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

\[
\sqrt B(\widehat\theta_R-\theta)
\ \Rightarrow\
Z\sim N(0,\Sigma_\theta),
\]

\[
B\,E_R\left[
(\widehat\theta_R-\theta)
(\widehat\theta_R-\theta)^\top
\right]
=
\Sigma_\theta+o(1),
\]

and, for some \(\eta>0\),

\[
\sup_B
E_R\left\|
\sqrt B(\widehat\theta_R-\theta)
\right\|^{2+\eta}
<
\infty.
\]

For coordinates \(\ell\) and \(m\),

\[
\Sigma_{\theta,\ell m}
=
\frac{
P(Y_\ell\le\theta_\ell,\,
Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)
f_m(\theta_m)
}.
\]

The bounded coefficient \(b_{\theta,B}\) retains the exact empirical-quantile lattice contribution and may depend on \(B\).

### 3.2 Threshold-coincidence geometry

Away from equality between a base-candidate threshold and the added-candidate threshold, the policy map is twice continuously differentiable. At coincidence, the moving maximum in the incremental rejection event changes its active branch.

Consider the generic winner-cell contribution

\[
U(a,q)
=
\int_{-\infty}^{a}
K\{w,\max(w,q)\}\,dw,
\]

where \(K(w,s)\) is an integrated-tail kernel whose derivatives required below are continuous and admit parameter-uniform integrable envelopes over the full lower integration range. Define

\[
J_s(t)=\int_{-\infty}^{t}\partial_sK(w,t)\,dw,
\qquad
J_{ss}(t)=\int_{-\infty}^{t}\partial_{ss}K(w,t)\,dw.
\]

At \(a=q=t\), local increments \(u\) and \(v\) yield

\[
\begin{aligned}
U(t+u,t+v)
&=
U(t,t)
+
K(t,t)u
+
J_s(t)v
\\
&\quad
+
\frac12
\left[
K_w(t,t)u^2
+
2K_s(t,t)uv
+
J_{ss}(t)v^2
\right]
\\
&\quad
+
\frac12K_s(t,t)(u-v)_+^2
+
o(u^2+v^2),
\end{aligned}
\]

where \((x)_+=\max(x,0)\). The value and first derivative are preserved across the boundary, but the curvature changes through the one-sided positive-part-square term.

For the declared candidate pools, the only nonempty base/full winner pairs are

\[
(0,0),\quad(0,2),\quad(1,1),\quad(1,2).
\]

Only cells \((0,2)\) and \((1,2)\) contribute to incremental rejection. The only relevant candidate-threshold coincidence hyperplanes are therefore

\[
q_0=q_2
\qquad\text{and}\qquad
q_1=q_2.
\]

Define

\[
\mathcal A_0
=
\{a\in\{0,1\}:q_a=q_2\},
\qquad
d_a=e_a-e_2,
\qquad
s_a=I(c<q_a),
\]

where \(e_j\) is the standard basis vector corresponding to coordinate \(q_j\) in \(\theta\). Strict candidate–trigger separation means that \(c\) differs from every candidate threshold locally, so each \(s_a\) is locally constant and no candidate–trigger coincidence contributes to the expansion.

For the incremental winner-cell kernel \(K_a\), let

\[
\kappa_a
=
\frac12\partial_s K_a(q_a,q_2),
\qquad
\lambda_a
=
\{s_a-\rho(\theta)\}\kappa_a.
\]

**Theorem 2 (generalized local policy expansion).**  
Under fixed candidate pools \(\{0,1\}\subset\{0,1,2\}\), almost-surely unique winners, strict candidate–trigger threshold separation, winner-cell kernel regularity, and dominated second derivatives for the smooth terms,

\[
\begin{aligned}
\Delta_\pi(\theta+u)
&=
\Delta_\pi(\theta)
+
g_\Delta^\top u
+
\frac12u^\top H_\Delta^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
\lambda_a(d_a^\top u)_+^2
+
o(\|u\|^2).
\end{aligned}
\]

The second-order map is continuous and piecewise quadratic over the finite arrangement generated by the active hyperplanes. When \(\mathcal A_0\) is empty, the result reduces to the ordinary smooth expansion.

### 3.3 Generalized reference-bias coefficient

**Theorem 3 (generalized second-order reference bias).**  
Under Theorems 1 and 2,

\[
E_R\{
\Delta_\pi(\widehat\theta_R)
\}
=
\Delta_\pi(\theta)
+
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
+
o(B^{-1}),
\]

where

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\left(
H_\Delta^{\mathrm{sm}}\Sigma_\theta
\right)
\\
&\quad
+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

The three terms represent reference-threshold centering, ordinary smooth curvature, and the threshold-coincidence correction. For a centered Gaussian limit \(Z\),

\[
E(d_a^\top Z)_+^2
=
\frac12d_a^\top\Sigma_\theta d_a,
\]

which produces the final factor \(1/2\).

### 3.4 Exact finite-\(n\) identity and combined expansion

**Proposition 1 (exact conditional evaluation identity).**  
Conditional on the reference bank,

\[
E_E\left(
\widehat\Delta_\pi
\mid
\widehat\theta_R
\right)
=
\left(1-\frac1n\right)
\Delta_\pi(\widehat\theta_R).
\]

This follows from the divisor-\(n\) sample covariance convention.

**Corollary 1 (combined finite-reference and finite-evaluation bias).**

\[
\begin{aligned}
E(\widehat\Delta_\pi)-\Delta_\pi
&=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
\\
&\quad
+
o(B^{-1}+n^{-1}).
\end{aligned}
\]

The first term is reference-threshold centering and curvature bias; the second is the exact evaluation covariance bias; and the third is the explicit product term obtained when the exact factor \(1-1/n\) multiplies the reference expansion. Because the stated remainder is \(o(B^{-1}+n^{-1})\), the product term is retained as an algebraically determined finite-sample component, not claimed to be separately resolved as an asymptotic order.

### 3.5 Finite-status nonlinear propagation to TESS

For \(r\in\{A,C\}\), the adaptive and comparator probability maps have generalized local expansions

\[
\begin{aligned}
\pi_r(\theta+u)
&=
\pi_r(\theta)
+
g_r^\top u
+
\frac12u^\top H_r^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
\lambda_{r,a}(d_a^\top u)_+^2
+
o(\|u\|^2),
\end{aligned}
\]

where

\[
\lambda_{A,a}=s_a\kappa_a,
\qquad
\lambda_{C,a}=\rho(\theta)\kappa_a.
\]

Their difference recovers

\[
\lambda_{A,a}-\lambda_{C,a}
=
\{s_a-\rho(\theta)\}\kappa_a
=
\lambda_a.
\]

Define the generalized reference coefficients

\[
\begin{aligned}
C_{r,B}^{\mathrm{gen}}
&=
g_r^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\left(
H_r^{\mathrm{sm}}\Sigma_\theta
\right)
\\
&\quad
+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_{r,a}
d_a^\top\Sigma_\theta d_a
\end{aligned}
\]

and

\[
V_{R,r}
=
g_r^\top
\Sigma_\theta
g_r.
\]

For the evaluation bank, let

\[
\zeta_A=R_A-\pi_A,
\]

\[
\zeta_C
=
(R_0-e_0)
+
\mu(A-\rho)
+
\rho(M-\mu),
\]

with

\[
V_{E,A}=E(\zeta_A^2),
\qquad
V_{E,C}=E(\zeta_C^2).
\]

Define

\[
\begin{aligned}
C_{S,R,B}^{\mathrm{gen}}
&=
g_\alpha'(\pi_A)C_{A,B}^{\mathrm{gen}}
+
\frac12g_\alpha''(\pi_A)V_{R,A}
\\
&\quad
-
g_\alpha'(\pi_C)C_{C,B}^{\mathrm{gen}}
-
\frac12g_\alpha''(\pi_C)V_{R,C},
\end{aligned}
\]

and

\[
C_{S,E}
=
\frac12g_\alpha''(\pi_A)V_{E,A}
-
g_\alpha'(\pi_C)\Delta_\pi
-
\frac12g_\alpha''(\pi_C)V_{E,C}.
\]

Assume the strengthened interiority, exponential-localization, local-Lipschitz, and mild relative-growth conditions stated in the Supplement. In particular, the adaptive and comparator population probabilities are uniformly bounded away from 1 in a neighborhood of \(\theta\).

**Corollary 2 (finite-status second-order TESS bias).**  
There exist constants \(C,c>0\) such that

\[
P(\mathcal F_{B,n}^c)
\le
C\{
e^{-cB}+e^{-cn}
\},
\]

and

\[
E(
\widehat\Delta_S^{\mathrm{fin}}
\mid
\mathcal F_{B,n}
)
-
\Delta_S
=
\frac{C_{S,R,B}^{\mathrm{gen}}}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]

Candidate-threshold coincidence affects the reference contribution through the generalized coefficients. The evaluation coefficient retains the comparator-product centering term and the adaptive and comparator curvature terms. Boundary statuses remain separate finite-sample outcomes and are not absorbed into the conditional mean.

### 3.6 Scope

The policy-probability theory applies to fixed finite candidate pools, continuous scores, almost-surely unique winners, fixed-dimensional empirical-quantile calibration, strict candidate–trigger threshold separation, candidate-threshold coincidences at \(q_0=q_2\) or \(q_1=q_2\), and independent reference and evaluation banks. The TESS corollary additionally concerns the finite-status conditional mean, requires local population probabilities uniformly bounded away from 1, and retains boundary-status probabilities separately.

The results do not cover discrete plus-one empirical \(p\)-values, discrete winner or trigger ties, candidate–trigger threshold coincidence, failed-fit fallback rules, growing candidate dimension, arbitrary nonsmooth adaptive pipelines, or an unconditional finite expectation for the raw logarithmic TESS estimator.

## 4. Prospectively locked numerical validation

### 4.1 Objectives and scientific units

Following established guidance for the design and reporting of statistical simulation studies (Burton et al., 2006; Morris et al., 2019), we conducted a new, prospectively specified, and computationally locked numerical study. It used only latent-equivalence-class simulations; no fitted-model library, clinical dataset, or simulation output from a policy-allocation experiment was reused. The four targets were the reference-only \(B^{-1}\) expansion, the exact finite-\(n\) identity, the combined reference/evaluation expansion retaining the algebraic \(B^{-1}n^{-1}\) product term, and nonlinear propagation to TESS at \(\alpha=0.01\) and \(0.05\).

The scientific units were 25 latent equivalence classes: 17 primary and 8 diagnostic. They arose from three dependence structures and prespecified candidate- and trigger-probability settings subject to the locked separation rule. All three latent candidate margins were standard normal and used the same candidate probability, so \(q_0=q_1=q_2\) and both candidate-coincidence branches were active. Identity, exponential, and hyperbolic-sine representations were exactly equivalent under the common monotone transformation. Only the identity member was simulated; the 50 nonidentity rows were deterministic invariance audits and did not enlarge the formal denominator. Formal acceptance was determined exclusively by the primary classes.

Three simulation families were evaluated: reference-only, evaluation-only, and combined reference/evaluation. Each family contained 25 jobs, for 75 jobs in total. Reference-bank and evaluation-sample sizes were

\[
B,n\in\{250,500,1000,3000,10000\}.
\]

### 4.2 Random-number contract and stopping

The master seed was 20260804. Reference and evaluation streams were independent. Nested prefixes were used within each simulation family, batch outputs were written atomically, and completed jobs could be resumed deterministically. No effect-dependent stopping or post-hoc class deletion was permitted.

Primary classes were assigned 2,000–20,000 replicates and diagnostic classes 1,000–5,000 replicates, in batches of 250. Stopping required

\[
\frac{\mathrm{MCSE}}{1+|\tau|}
\le 0.03,
\]

where \(\tau\) was the locked population target. The observed Monte Carlo mean did not enter the stopping scale.

### 4.3 Bias predictions and residual metrics

The reference-only prediction was

\[
b_R(B)
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B},
\]

and the combined policy-probability prediction was

\[
b_{R,E}(B,n)
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}.
\]

For the finite-status TESS mean,

\[
b_S(B,n;\alpha)
=
\frac{C_{S,R,B}^{\mathrm{gen}}(\alpha)}{B}
+
\frac{C_{S,E}(\alpha)}{n}.
\]

Let \(\widehat\mu\) be a Monte Carlo mean, \(\tau\) the locked population target, \(b_{\mathrm{pred}}\) the predicted bias, \(s\) the locked scale, and MCSE the Monte Carlo standard error. The raw normalized residual was

\[
R_{\mathrm{raw}}
=
\frac{|(\widehat\mu-\tau)-b_{\mathrm{pred}}|}{s}.
\]

The formal MCSE-adjusted residual was

\[
R_{\mathrm{adj}}
=
\frac{
\max\{
|(\widehat\mu-\tau)-b_{\mathrm{pred}}|
-z_{\mathrm{sim}}\mathrm{MCSE},
0
\}
}{s},
\]

with the locked simultaneous factor \(z_{\mathrm{sim}}=4.23728\) (the full numerical value is given in the Supplement). Thus \(R_{\mathrm{adj}}=0\) indicates containment within the simultaneous Monte Carlo allowance, not a zero raw residual.

The locked policy-probability scales were

\[
s_R(B)
=
\frac{1+|C_{\Delta,B}^{\mathrm{gen}}|}{B}
\]

for the reference-only family and

\[
s_{R,E}(B,n)
=
\left(\frac1B+\frac1n\right)
\left(
1+|C_{\Delta,B}^{\mathrm{gen}}|+|\Delta_\pi|
\right)
\]

for the combined family. For TESS,

\[
s_S(B,n;\alpha)
=
\left(\frac1B+\frac1n\right)
\left(
1+|C_{S,R,B}^{\mathrm{gen}}(\alpha)|
+|C_{S,E}(\alpha)|
\right).
\]

For the 85 exact finite-\(n\) checks, the signed discrepancy was

\[
Z_{c,n}
=
\frac{
\widehat\mu_{c,n}
-
(1-1/n)\Delta_{\pi,c}
}{
\mathrm{MCSE}_{c,n}
},
\]

with the locked two-sided Bonferroni boundary \(z_{\mathrm{id}}=3.85098\) (full numerical value in the Supplement).

### 4.4 Acceptance criteria

At \(B=10{,}000\), the reference-only median and 90th percentile of \(R_{\mathrm{adj}}\) had to be no greater than 0.15 and 0.40. The locked median-improvement statistic compared the adjusted medians at \(B=500\) and \(B=10{,}000\) and had to be at least 40%; under the prespecified zero-denominator rule it equaled 1 when both medians were zero. A primary class counted as improved when the unadjusted absolute residual of the generalized prediction was strictly smaller than that of the zero-bias prediction. At least 75% of primary classes had to improve.

At \(B=n=10{,}000\), the combined-policy median and 90th percentile had to be no greater than 0.15 and 0.40. For finite-status TESS, assessed separately at each alpha level, the limits were 0.25 and 0.60; boundary-status counts were retained separately, and any nonfinite primary record constituted failure.

All 85 exact-identity comparisons had to lie within \(\pm z_{\mathrm{id}}\). At most one of the 17 primary classes could be precision limited. Formal PASS required every scientific criterion and fatal implementation check to pass.

---

## 5. Results

### 5.1 Completion and adjudication

All 75 jobs completed, with 25 jobs in each simulation family and 126,000 Monte Carlo replicates. All jobs met the precision target; no primary class was precision limited. No prospective criterion was changed, no class was dropped, and the scientific simulation was not rerun after results were inspected.

The formal contract status was PASS. The overall interpretation was a formal pass with qualified numerical support. Evidence for the policy-probability expansion was classified as strong, whereas finite-sample TESS evidence was classified as formally passing but limited by Monte Carlo resolution.

### 5.2 Reference-only approximation

At \(B=10{,}000\), the adjusted normalized-residual median and 90th percentile were both zero, satisfying the limits of 0.15 and 0.40. The raw median and 90th percentile were 0.0355 and 0.0958 (Figure 2A). The class-specific generalized predictions tracked the observed reference bias across the 17 primary classes (Figure 2B).

The generalized correction reduced absolute bias error relative to no correction in 15 of 17 classes (88.2%) and relative to the gradient-only approximation in 14 of 17 classes (82.4%). It improved 9 of 17 classes (52.9%) relative to the smooth-only approximation; this comparison was descriptive and nonfatal (Figure 2C).

The prespecified median-improvement statistic from \(B=500\) to \(B=10{,}000\) was formally 1 because both adjusted medians were floored at zero. The criterion passed but was non-discriminating. The raw median increased from 0.0049 to 0.0355 and therefore did not show monotone improvement with increasing \(B\).

### 5.3 Combined policy-probability approximation

At \(B=n=10{,}000\), the adjusted median and 90th percentile were both zero. The raw median and 90th percentile were 0.0495 and 0.1474, respectively (Figure 4A). These values provided strong numerical support for the joint finite-sample prediction. The design evaluated the complete prediction and did not attempt to identify the smaller \(B^{-1}n^{-1}\) product term separately from the stated remainder.

### 5.4 Finite-status TESS approximation

At \(\alpha=0.01\), the adjusted median and 90th percentile were both zero; the corresponding raw values were 0.5288 and 1.4612. At \(\alpha=0.05\), the adjusted values were again zero, with raw values of 0.4073 and 0.8891. No nonfinite record occurred in any primary largest-pair TESS cell, so the finite-status mean in those cells used the complete set of Monte Carlo records.

For every primary class at both alpha levels, the absolute raw residual was smaller than the simultaneous Monte Carlo allowance, so all adjusted residuals were zero (Figure 3C). The finite-status TESS criteria therefore passed formally, but the raw diagnostics did not establish the same degree of finite-sample accuracy as the policy-probability results. The absence of observed boundary records supports numerical stability in the evaluated regime; it does not convert the raw finite-sample logarithmic transform into an everywhere-finite random variable.

### 5.5 Exact finite-\(n\) identity

All 85 simultaneous checks passed across the 17 primary classes and five evaluation-sample sizes (Figure 4B). The absolute standardized discrepancies had a median of 0.6308, a 90th percentile of 1.705, and a maximum of 2.99695, below the boundary of 3.85098. This fatal implementation check strongly supported the exact evaluation identity used in the combined expansion.

---

## 6. Discussion

We derived and numerically evaluated a generalized second-order finite-sample expansion for a threshold-adaptive policy contrast estimated from independent reference and evaluation banks. Three features distinguish the result. First, the reference-bank contribution depends on the exact empirical-quantile convention and the complete-vector covariance of the estimated thresholds. Second, candidate-threshold coincidence changes the local second-order geometry: the policy map is continuous with a common first derivative, but its curvature includes one-sided positive-part-square contributions. Third, the evaluation contribution is available exactly at the policy-probability level, yielding an \(n^{-1}\) bias and an explicit algebraic \(B^{-1}n^{-1}\) product term. For TESS, the finite-status formulation separates the conditional mean expansion from exponentially rare boundary statuses.

The threshold-coincidence term is not a cosmetic refinement of an ordinary Hessian formula. Existing directional-delta theory explains why nondifferentiable maps require nonstandard local derivatives and why ordinary bootstrap procedures may fail (Dümbgen, 1993; Fang and Santos, 2019), but it does not by itself provide the policy-specific expectation coefficient derived here. At the coincidence boundary, the moving maximum changes its active branch. Replacing the policy map by a globally smooth quadratic approximation omits a term whose expectation is determined by the variance of the threshold-difference direction. The resulting correction depends on both the branch coefficient and \(d_a^\top\Sigma_\theta d_a\). This identifies precisely how reference-threshold dependence enters the bias when candidate thresholds are estimated from common reference vectors.

The exact evaluation identity clarifies the relationship between reference and evaluation effects. Conditional on the reference bank, the covariance-style estimator has expectation \((1-1/n)\Delta_\pi(\widehat\theta_R)\). The finite-\(n\) contribution is therefore structurally different from the reference contribution: it is induced by the product of evaluation-sample means rather than threshold estimation. The joint expansion preserves this distinction while retaining the product term produced by applying the exact factor \(1-1/n\) to the reference expansion. That product is algebraically determined, although the present remainder does not resolve it as a separate asymptotic order.

The numerical results supported this decomposition. The raw reference-only and combined-policy residual summaries were small relative to the locked natural scales, and the generalized correction improved most primary classes relative to no correction and the gradient-only approximation. All exact finite-\(n\) checks passed. The reference median-improvement criterion was less informative: MCSE flooring set both adjusted medians to zero, while the raw median did not improve monotonically with \(B\). This discrepancy illustrates why the formal decision and raw interpretability diagnostics should be reported separately.

The TESS result requires greater caution. TESS is a nonlinear logarithmic transformation, and an empirical probability can equal 1 at finite \(n\). We therefore formulate the theorem for the finite-status conditional mean and report positive-infinite, negative-infinite, and indeterminate boundary statuses separately. No nonfinite record occurred in the primary largest-pair cells, but every adjusted residual was zero only after subtracting the simultaneous MCSE allowance. The raw normalized residuals were materially larger than those for the policy-probability contrast. We interpret the finite-status TESS validation as a formal pass whose raw finite-sample accuracy remains unresolved at the available Monte Carlo precision, rather than as strong numerical confirmation of uniformly accurate TESS bias correction.

The present theory is intentionally local and finite dimensional. It does not establish a universal second-order delta method for arbitrary nonsmooth policies. It also does not assign a finite unconditional expectation to the raw logarithmic TESS estimator, and it does not address plus-one empirical \(p\)-value lattices, discrete ties, failed model fits, or growing candidate pools. These exclusions matter because discreteness may alter the order of the approximation or create additional boundary events. The results instead provide a clean continuous benchmark and isolate the candidate-threshold coincidence effect without conflating it with those separate complications.

The matched comparator has a deliberately limited role in this paper. We do not ask which activation rule creates greater inferential burden or whether policies with equal expected budgets have equal rejection laws. We instead hold the policy functional fixed and ask how its plug-in estimator is centered when thresholds and evaluation probabilities are estimated from finite independent samples. The paper therefore shares a small set of algebraic definitions with policy-allocation analyses but shares neither their empirical comparisons nor their central scientific claim.

Several extensions are natural. A discrete bridge could determine when continuous-threshold expansions remain informative for plus-one empirical \(p\)-values, whose exact-null interpretation is intrinsically lattice based (Phipson and Smyth, 2010). A broader generalized delta method could treat finite polyhedral arrangements beyond the present winner-cell construction. Uniform process theory could extend the pointwise TESS result to simultaneous inference across \(\alpha\). These are separate problems; none is required for the finite-sample expansion proved and validated here.

---

## 7. Conclusion

Finite-reference and finite-evaluation biases in threshold-adaptive policy estimation arise from different mechanisms and can be separated analytically. Empirical-quantile calibration contributes an order-\(B^{-1}\) bias that must retain complete-vector dependence and, at candidate-threshold coincidence, positive-part-square curvature terms. Independent evaluation contributes an exact order-\(n^{-1}\) covariance bias and an explicit finite-sample product with the reference term. The resulting generalized expansion received strong numerical support at the policy-probability level and qualified support after finite-status nonlinear propagation to TESS. These results provide a principled finite-sample approximation for the declared continuous, fixed-candidate, monotone-augmentation policy class.

---

## Declarations

### Funding

No external funding was received for this study.

### Conflict of interest

The author declares no competing interests.

### Ethics approval

Not applicable. The study used mathematical derivations and simulated data only.

### Data availability

All numerical-validation outputs required to reproduce the reported summaries will be made available in a public repository upon publication. **[Replace with repository DOI and permanent URL before submission.]**

### Code availability

Source code, locked protocols, manifests, numerical outputs, and available figure-source files will be made available in the accompanying repository. **[Replace with repository DOI and release tag before submission.]**

### Author contributions

A.S. conceived the study, developed the theory, designed and conducted the numerical validation, interpreted the results, and wrote the manuscript.

### AI assistance disclosure

**[Finalize according to the target journal's current policy.]**

---

## Figure captions

### Figure 1. Threshold geometry and the generalized second-order expansion

(A) Two-dimensional slice of the threshold parameter space. Away from candidate-threshold coincidence, the policy-value map lies in a regular region and admits an ordinary smooth second-order expansion. The diagonal represents \(q_{\mathrm{add}}=q_{\mathrm{base}}\).  
(B) Local behavior along a signed direction \(\ell(h)\). The ordinary quadratic approximation and generalized expansion agree in value and first derivative at the boundary. The generalized expansion differs through a one-sided positive-part-square contribution, changing curvature without creating a first-order cusp. The displayed ordering illustrates one sign of the branch coefficient; the gap reverses when that coefficient changes sign.  
(C) Regular and coincidence-boundary expansions. At coincidence, the smooth quadratic term is augmented by active positive-part-square contributions, where \(\mathcal A_0=\{a:q_a=q_2\}\), \(d_a=e_a-e_2\), and \([x]_+=\max(x,0)\).

### Figure 2. Reference-only numerical validation

(A) Class-specific raw normalized residuals across the five prospectively specified reference-bank sizes. Thin trajectories represent the 17 primary equivalence classes; solid and dashed summary trajectories denote the median and 90th percentile.  
(B) Observed reference bias versus the generalized prediction \(C_{\Delta,B}^{\mathrm{gen}}/B\) at \(B=10{,}000\); the diagonal denotes equality.  
(C) Numbers of primary classes for which the generalized correction reduced absolute bias error relative to no correction, gradient-only correction, and smooth-only correction. The smooth-only comparison was descriptive and nonfatal.

### Figure 3. Alpha-specific finite-status TESS-bias agreement and Monte Carlo resolution

(A–B) Observed finite-status TESS bias versus the generalized finite-sample prediction at \(B=n=10{,}000\), separately for \(\alpha=0.01\) and \(0.05\).  
(C) Ratios of the absolute raw residual to the simultaneous Monte Carlo allowance. Values below 1 have an adjusted residual of zero. All 17 primary classes were below the boundary at both alpha levels, and no nonfinite primary TESS record occurred.

### Figure 4. Combined-policy approximation and exact finite-\(n\) identity

(A) Observed combined-policy bias versus the generalized joint reference/evaluation prediction at \(B=n=10{,}000\).  
(B) Signed standardized discrepancies for the exact identity \(E(\widehat\Delta_\pi)=(1-1/n)\Delta_\pi\) across 17 primary classes and five evaluation-sample sizes. All 85 comparisons passed the simultaneous Bonferroni boundary.

---

## Tables

**Table 1.** Prospectively specified numerical-validation design.  
**Table 2.** Numerical-validation results under the prospectively specified criteria.  
**Supplementary Table S1.** Detailed prospectively specified numerical-validation design.

---

## References

Bahadur RR. A note on quantiles in large samples. *Annals of Mathematical Statistics*. 1966;37(3):577–580. doi:10.1214/aoms/1177699450.

Berk R, Brown L, Buja A, Zhang K, Zhao L. Valid post-selection inference. *Annals of Statistics*. 2013;41(2):802–837. doi:10.1214/12-AOS1077.

Burton A, Altman DG, Royston P, Holder RL. The design of simulation studies in medical statistics. *Statistics in Medicine*. 2006;25(24):4279–4292. doi:10.1002/sim.2673.

Chen Q, Fang Z. Inference on functionals under first order degeneracy. *Journal of Econometrics*. 2019;210(2):459–481. doi:10.1016/j.jeconom.2019.01.011.

Dümbgen L. On nondifferentiable functions and the bootstrap. *Probability Theory and Related Fields*. 1993;95(1):125–140. doi:10.1007/BF01197342.

Dwork C, Feldman V, Hardt M, Pitassi T, Reingold O, Roth A. The reusable holdout: preserving validity in adaptive data analysis. *Science*. 2015;349(6248):636–638. doi:10.1126/science.aaa9375.

Fang Z, Santos A. Inference on directionally differentiable functions. *Review of Economic Studies*. 2019;86(1):377–412. doi:10.1093/restud/rdy049.

Hoeffding W. Probability inequalities for sums of bounded random variables. *Journal of the American Statistical Association*. 1963;58(301):13–30. doi:10.1080/01621459.1963.10500830.

Kiefer J. On Bahadur's representation of sample quantiles. *Annals of Mathematical Statistics*. 1967;38(5):1323–1342. doi:10.1214/aoms/1177698690.

Morris TP, White IR, Crowther MJ. Using simulation studies to evaluate statistical methods. *Statistics in Medicine*. 2019;38:2074–2102. doi:10.1002/sim.8086.

Oehlert GW. A note on the delta method. *American Statistician*. 1992;46(1):27–29. doi:10.1080/00031305.1992.10475842.

Phipson B, Smyth GK. Permutation \(p\)-values should never be zero: calculating exact \(p\)-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*. 2010;9(1):Article 39. doi:10.2202/1544-6115.1585.

Shapiro A. Asymptotic analysis of stochastic programs. *Annals of Operations Research*. 1991;30(1):169–186. doi:10.1007/BF02204815.

Taylor J, Tibshirani RJ. Statistical learning and selective inference. *Proceedings of the National Academy of Sciences of the United States of America*. 2015;112(25):7629–7634. doi:10.1073/pnas.1507583112.
