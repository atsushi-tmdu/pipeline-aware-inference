# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package D0: Protocol for two-bank process inference

**Protocol version:** D0 v1  
**Date:** 2 August 2026  
**Status:** Draft for scientific review; not yet locked  
**Repository base:** `tess-top-tier-theory` at commit `737a752`  
**Preceding frozen work:** Work Packages A and B

---

## Executive decision

Work Packages A and B established a policy-level theory of adaptive search burden: sharp same-budget envelopes, an exact identifiability criterion, unbounded deep-tail mismatch at fixed expected candidate count, threshold-rank coherence, and arbitrary policy-curve crossing. The remaining high-value inferential problem is to quantify uncertainty when the policy itself is calibrated by a finite null-reference bank and then evaluated on an independent evaluation bank.

Work Package D will study this as a genuine two-sample plug-in problem. D0 deliberately fixes a simplified model before any theorem proof or new simulation. The first theorem will retain the features that create the two-bank structure:

1. candidate-specific null calibration from a reference bank;
2. a trigger threshold estimated from the same reference bank;
3. policy rejection evaluated on an independent bank;
4. a TESS curve obtained by nonlinear transformation of the rejection curve.

The first theorem will omit multiple-model winner selection, score ties, failed fits, and exact finite-bank plus-one discreteness. Those features enter only after the regular two-bank core is understood.

The main target is an asymptotic linear expansion with separate reference-bank and evaluation-bank influence terms, followed by validity of the complete-replication two-bank bootstrap. A process result over an interval of local thresholds is the preferred endpoint, but a rigorous fixed-threshold theorem with an estimated trigger is sufficient for D to be scientifically successful.

---

# 1. Scientific question

Let a null-reference bank estimate candidate-wise tail maps and an activation trigger. Let an independent evaluation bank estimate the global-null rejection law of the resulting adaptive policy. The central question is:

> Under what regularity conditions can the policy rejection curve and TESS curve be estimated with a joint first-order contribution from both banks, and when does independently resampling complete reference and evaluation replications consistently approximate their sampling law?

This is distinct from the already established conditional theory, which treats the realized reference bank as fixed. D targets the population-calibrated policy functional and propagates finite-reference-bank uncertainty.

---

# 2. Simplified population model

## 2.1 Two independent banks

Let

\[
Z_1,\ldots,Z_B \overset{\mathrm{iid}}\sim P_0
\]

be the null-reference bank and

\[
Y_1,\ldots,Y_n \overset{\mathrm{iid}}\sim P_0
\]

be the evaluation bank, independent of the reference bank.

Each complete replication is a vector

\[
Z=(U,X_0,X_1),
\]

where:

- \(U\) is the scalar information used by the activation rule;
- \(X_0\) is the base-candidate score;
- \(X_1\) is the optional-candidate score;
- larger \(X_j\) is more extreme under the global null.

The vector components may be dependent. The two banks share the same global-null law in D0. Extensions allowing different but linked calibration and evaluation laws are outside the first theorem.

## 2.2 Population calibration

Fix an activation rate \(r\in(0,1)\). Let

\[
c=F_U^{-1}(1-r)
\]

be the population trigger threshold. For local threshold \(\alpha\in(0,1)\), let

\[
q_j(\alpha)=F_j^{-1}(1-\alpha),\qquad j\in\{0,1\},
\]

where \(F_j\) is the marginal distribution function of \(X_j\).

The population policy rejects when the base candidate rejects, or when the optional branch is activated and the optional candidate rejects:

\[
h_\alpha(y;\theta_\alpha)
=
I\{x_0>q_0(\alpha)\}
+
I\{x_0\le q_0(\alpha),\ u>c,\ x_1>q_1(\alpha)\},
\]

with

\[
\theta_\alpha=
\{q_0(\alpha),q_1(\alpha),c\}.
\]

Thus

\[
\pi(\alpha)=P_0 h_\alpha(Y;\theta_\alpha)
\]

and

\[
S(\alpha)
=
\frac{\log\{1-\pi(\alpha)\}}{\log(1-\alpha)}.
\]

This model is the smallest nontrivial policy that contains candidate-specific calibration, adaptive branching, and reference-estimated policy parameters.

---

# 3. Two-bank estimator

Let \(\widehat F_{U,B},\widehat F_{0,B},\widehat F_{1,B}\) be empirical distribution functions from complete reference replications. Define

\[
\widehat c_B=\widehat F_{U,B}^{-1}(1-r),
\]

and

\[
\widehat q_{j,B}(\alpha)
=
\widehat F_{j,B}^{-1}(1-\alpha).
\]

Write

\[
\widehat\theta_{B,\alpha}
=
\{\widehat q_{0,B}(\alpha),
  \widehat q_{1,B}(\alpha),
  \widehat c_B\}.
\]

The two-bank rejection-curve estimator is

\[
\widehat\pi_{B,n}(\alpha)
=
\frac{1}{n}\sum_{i=1}^n
h_\alpha(Y_i;\widehat\theta_{B,\alpha}),
\]

and

\[
\widehat S_{B,n}(\alpha)
=
\frac{\log\{1-\widehat\pi_{B,n}(\alpha)\}}
{\log(1-\alpha)}.
\]

D0 treats empirical quantiles as the canonical asymptotic representation. The exact plus-one empirical p-value rule will later be compared with this quantile implementation. It must not be silently assumed equivalent at finite \(B\).

---

# 4. Estimands and the conditional/population distinction

Three objects must remain distinct.

## 4.1 Population-calibrated target

\[
\pi(\alpha)
=
P_0 h_\alpha(Y;\theta_\alpha),
\]

where all calibration quantities are population functionals of \(P_0\). This is the primary target of Work Package D.

## 4.2 Conditional finite-reference target

For a realized reference bank \(\mathcal R_B\),

\[
\pi_{\mid\mathcal R_B}(\alpha)
=
P_0\{h_\alpha(Y;\widehat\theta_{B,\alpha})=1
\mid \mathcal R_B\}.
\]

The previously established DKW and conditional bootstrap theory concerns estimation of this object with \(\mathcal R_B\) fixed.

## 4.3 Unconditional finite-bank sampling law

The distribution of

\[
\widehat\pi_{B,n}(\alpha)-\pi(\alpha)
\]

contains both reference- and evaluation-bank variation. The two-bank bootstrap is intended to estimate this law.

The locked empirical paper's primary interval remains conditional on its frozen reference bank. Work Package D does not retroactively redefine that primary estimand.

---

# 5. Asymptotic regime

The primary asymptotic regime is

\[
B\to\infty,\qquad n\to\infty,
\qquad \frac{n}{B}\to\lambda\in(0,\infty).
\]

The main expansion will use \(\sqrt n\) scaling. Under this convention, the reference contribution appears multiplied by \(\sqrt\lambda\). Regimes \(\lambda=0\) and \(\lambda=\infty\) may be recorded as corollaries but are not required for the first theorem.

For curve-level results, thresholds are restricted to

\[
\alpha\in I=[\alpha_L,\alpha_U]
\subset(0,1),
\]

with \(\alpha_L>0\) and \(\alpha_U<1\). Deep-tail sequences \(\alpha\downarrow0\) require separate extreme-value or intermediate-quantile asymptotics and are outside D0.

---

# 6. Regularity assumptions

The assumptions below are protocol targets. They may be weakened only after the first theorem is proved.

## D0-A1. Independent complete-replication banks

Reference and evaluation replications are iid within bank and independent across banks. All coordinates from a replication are resampled together.

## D0-A2. Continuous marginal calibration laws

The marginal distribution functions of \(U,X_0,X_1\) are continuous. Their densities exist, are continuous, and are bounded away from zero and infinity in neighborhoods of the required trigger and candidate quantiles.

## D0-A3. Smooth boundary probabilities

The map

\[
(q_0,q_1,c)
\mapsto
P_0\{X_0>q_0\ \text{or}\ (U>c,X_1>q_1)\}
\]

is continuously differentiable in a neighborhood of the true threshold vector. Sufficient conditions may be stated through a continuous joint density or regular conditional boundary densities.

## D0-A4. No boundary mass

For all \(\alpha\in I\),

\[
P_0\{X_j=q_j(\alpha)\}=0,
\qquad
P_0(U=c)=0.
\]

## D0-A5. Nondegenerate TESS transformation

There exists \(\eta>0\) such that

\[
\mathop{\mathrm{sup}}_{\alpha\in I}\pi(\alpha)\le 1-\eta.
\]

## D0-A6. Fixed declared policy

The policy form, activation rate, direction of score extremeness, and threshold interval are fixed independently of the evaluation bank.

## D0-A7. No first-stage winner ties or failed fits

D0 contains one candidate per branch and therefore no winner selection. Score ties, algorithm failures, and fallback rules are excluded from the first theorem.

## D0-A8. Standard empirical quantiles

The first theorem uses empirical quantiles, with a fixed and explicitly declared generalized-inverse convention.

## D0-A9. Uniform conditions for process results

For the process theorem, density bounds, boundary derivatives, and stochastic equicontinuity conditions hold uniformly over \(I\). The relevant classes of threshold sets must be shown to be Glivenko-Cantelli and Donsker rather than assumed informally.

## D0-A10. Complete-replication bootstrap

The reference bootstrap samples \(B\) complete reference vectors with replacement. Independently, the evaluation bootstrap samples \(n\) complete evaluation vectors with replacement. All calibration quantities are recomputed inside every reference bootstrap draw.

---

# 7. Candidate first-order expansion

Define

\[
m_\alpha(q_0,q_1,c)
=
P_0 h_\alpha(Y;q_0,q_1,c).
\]

Let

\[
\dot m_\alpha
=
\left(
\frac{\partial m_\alpha}{\partial q_0},
\frac{\partial m_\alpha}{\partial q_1},
\frac{\partial m_\alpha}{\partial c}
\right)^{\!T}
\]

at the true threshold vector. Under joint-density regularity, the derivative components have boundary-flux interpretations:

\[
\frac{\partial m_\alpha}{\partial q_0}
=
-f_0\{q_0(\alpha)\}
P_0\{U\le c\ \text{or}\ X_1\le q_1(\alpha)
\mid X_0=q_0(\alpha)\},
\]

\[
\frac{\partial m_\alpha}{\partial q_1}
=
-f_1\{q_1(\alpha)\}
P_0\{X_0\le q_0(\alpha),U>c
\mid X_1=q_1(\alpha)\},
\]

and

\[
\frac{\partial m_\alpha}{\partial c}
=
-f_U(c)
P_0\{X_0\le q_0(\alpha),X_1>q_1(\alpha)
\mid U=c\}.
\]

These formulas are theorem targets, not assumptions to be quoted without proof.

For a \(p\)-quantile \(q=F^{-1}(p)\), use the conventional influence function

\[
\operatorname{IF}_q(x)
=
\frac{p-I(x\le q)}{f(q)}.
\]

Thus the reference-bank threshold influence vector is

\[
\operatorname{IF}_{\theta,\alpha}(Z)
=
\begin{pmatrix}
\{1-\alpha-I(X_0\le q_0(\alpha))\}/f_0\{q_0(\alpha)\}\\
\{1-\alpha-I(X_1\le q_1(\alpha))\}/f_1\{q_1(\alpha)\}\\
\{1-r-I(U\le c)\}/f_U(c)
\end{pmatrix}.
\]

The candidate influence functions for the rejection curve are

\[
\phi_{E,\alpha}(Y)
=
h_\alpha(Y;\theta_\alpha)-\pi(\alpha),
\]

and

\[
\phi_{R,\alpha}(Z)
=
\dot m_\alpha^{T}
\operatorname{IF}_{\theta,\alpha}(Z).
\]

The primary fixed-threshold expansion to prove is

\[
\widehat\pi_{B,n}(\alpha)-\pi(\alpha)
=
\frac1n\sum_{i=1}^n\phi_{E,\alpha}(Y_i)
+
\frac1B\sum_{b=1}^B\phi_{R,\alpha}(Z_b)
+
o_p(n^{-1/2}+B^{-1/2}).
\]

Consequently,

\[
\sqrt n\{\widehat\pi_{B,n}(\alpha)-\pi(\alpha)\}
\rightsquigarrow
N\left(0,
\operatorname{Var}\{\phi_{E,\alpha}\}
+
\lambda\operatorname{Var}\{\phi_{R,\alpha}\}
\right).
\]

Because the banks are independent, no cross-bank covariance term appears.

For

\[
g_\alpha(\pi)
=
\frac{\log(1-\pi)}{\log(1-\alpha)},
\]

\[
g_\alpha'(\pi)
=
\frac{-1}{(1-\pi)\log(1-\alpha)}.
\]

The TESS influence functions are

\[
\phi^S_{E,\alpha}
=g_\alpha'\{\pi(\alpha)\}\phi_{E,\alpha},
\qquad
\phi^S_{R,\alpha}
=g_\alpha'\{\pi(\alpha)\}\phi_{R,\alpha}.
\]

---

# 8. Theorem ladder

## D1. Fixed \(\alpha\), known trigger

Estimate candidate quantiles from the reference bank but treat \(c\) as fixed and known.

**Required result:** asymptotic linearity, asymptotic normality, consistently estimable variance, and independent two-bank bootstrap validity.

**Purpose:** isolate the effect of candidate-wise reference calibration.

## D2. Fixed \(\alpha\), estimated trigger

Estimate \(c\) from the reference bank together with candidate quantiles.

**Required result:** the full three-component influence expansion above and validity of the independently resampled complete-replication two-bank bootstrap.

**This is the minimum scientific success criterion for Work Package D.**

## D3. TESS process on a compact threshold interval

For \(\alpha\in I\), prove in \(\ell^\infty(I)\) that

\[
\sqrt n\{\widehat S_{B,n}(\cdot)-S(\cdot)\}
\rightsquigarrow
\mathbb Z_S(\cdot),
\]

where

\[
\mathbb Z_S(\alpha)
=
\mathbb G_E\phi^S_{E,\alpha}
+
\sqrt\lambda\,\mathbb G_R\phi^S_{R,\alpha}.
\]

Prove bootstrap consistency in the same function space and construct a simultaneous confidence band from the conditional distribution of the supremum over \(\alpha\in I\) of

\[
\left|
\sqrt n\{\widehat S^{\mathrm{boot}}_{B,n}(\alpha)-\widehat S_{B,n}(\alpha)\}
\right|.
\]

## D4. Paired policy contrasts

For two policies evaluated using the same banks, derive the joint influence representation and bootstrap for

\[
\Delta_S(\alpha)=S_a(\alpha)-S_b(\alpha).
\]

Within-bank covariance must be retained. This theorem is the closest asymptotic analogue of the locked promising-minus-matched-random analysis.

---

# 9. Bootstrap protocol

For bootstrap repetition \(k\):

1. sample \(B\) complete reference vectors with replacement;
2. recompute every candidate quantile and the activation threshold;
3. sample \(n\) complete evaluation vectors with replacement, independently of step 1;
4. recompute the policy rejection curve and TESS curve;
5. for paired policies, use the same reference and evaluation bootstrap indices across policies;
6. retain the bootstrap process or fixed-threshold contrast.

The primary bootstrap statistic is centered at the observed estimator:

\[
\sqrt n\{\widehat S^{\mathrm{boot}}_{B,n}(\alpha)-\widehat S_{B,n}(\alpha)\}.
\]

The theorem must justify this ordinary nonparametric bootstrap under the regular D0 model. If the functional is only directionally differentiable after winner selection or ties are introduced, ordinary bootstrap validity must not be presumed. Directionally differentiable maps may require modified resampling or explicit derivative estimation.

---

# 10. Plus-one empirical p-values and finite-bank discreteness

The locked study uses

\[
\widehat p_j(x)
=
\frac{1+\sum_{b=1}^{B}I(X_{jb}\ge x)}{B+1}.
\]

D0 does not replace this construction in the empirical paper. Instead, D will investigate the following sequence.

## D-plus-1. Order-statistic equivalence

Express the event \(\widehat p_j(x)<\alpha\) exactly as comparison with a declared reference order statistic, including the integer rounding convention.

## D-plus-2. First-order equivalence

Determine conditions under which replacing the exact plus-one boundary by the empirical \((1-\alpha)\)-quantile changes the rejection estimator by

\[
o_p(n^{-1/2}+B^{-1/2})
\]

uniformly over a compact interval bounded away from zero.

## D-plus-3. Non-negligible discreteness regimes

Identify regimes in which the difference is first-order, including very small \(\alpha\), fixed \(B\), or thresholds near attainable p-value grid boundaries.

The Phipson-Smyth principle remains the finite-sample rationale for plus-one Monte Carlo p-values. The asymptotic simplification is a separate mathematical statement that must be proved.

---

# 11. Extension ladder toward the locked pipeline

The regular core will be extended only in this order:

1. **one candidate per branch, known trigger;**
2. **one candidate per branch, estimated trigger;**
3. **paired policy contrast;**
4. **uniform threshold process;**
5. **exact plus-one boundary;**
6. **finite multiple candidates with unique winner almost surely;**
7. **base trigger defined by a maximum score;**
8. **winner ties and deterministic randomization;**
9. **failed-fit fallback rules.**

A higher extension will not be attempted until the preceding level has a clean theorem or a documented impossibility result.

---

# 12. Numerical validation plan after D0 lock

Numerical work begins only after this protocol is reviewed and tagged.

## 12.1 Data-generating families

Use continuous trivariate null laws for \((U,X_0,X_1)\):

- independent standard normal;
- Gaussian copula with moderate positive dependence;
- a nonlinear but smooth dependence construction.

Marginals will be transformed to known continuous distributions when useful, so population quantiles and high-accuracy benchmark probabilities can be calculated.

## 12.2 Designs

Primary settings:

- \(r=0.50\);
- \(\alpha\in\{0.01,0.05,0.10\}\);
- \((B,n)\in\{(500,500),(1000,1000),(3000,3000),(3000,5000)\}\);
- paired comparison of known-trigger and estimated-trigger estimators.

Quick preflight may use smaller repetition counts but must be labeled computational debugging only.

## 12.3 Quantities checked

- bias of \(\widehat\pi\) and \(\widehat S\);
- empirical variance versus influence-function variance;
- contribution of each bank to total variance;
- coverage of normal, influence-function, and two-bank bootstrap intervals;
- undercoverage of evaluation-only intervals when reference variation is material;
- fixed-threshold and simultaneous-band coverage when D3 is reached.

## 12.4 Separate numerical lock

D0 locks the mathematical model, estimands, theorem ladder, and admissible data-generating families. A separate D1 numerical protocol will be created after a runtime-only preflight. The preflight may measure execution time and memory use but must not be used to select scientific settings from favorable results. The D1 numerical protocol will freeze outer Monte Carlo repetitions, bootstrap repetitions, seeds, tolerances, and coverage criteria before the scientific validation run.

After the D0 lock, changes to the mathematical DGP families, sample-size grid, estimands, or success rules require a new D0 protocol version and must not overwrite v1.

---

# 13. Success and stopping rules

## Core success

D2 is completed rigorously: a fixed-threshold asymptotic linear representation with an estimated trigger and a valid independent complete-replication two-bank bootstrap.

## Strong success

At least one of the following is additionally completed:

1. a uniform TESS-process theorem with a valid simultaneous bootstrap band;
2. a paired-policy TESS-contrast process theorem directly matching the empirical estimand;
3. a first-order bridge from the exact plus-one implementation to the regular quantile representation over a scientifically relevant threshold interval.

## Partial success

D1 is completed, and the obstruction to D2 is characterized transparently. This may support a technical appendix but is not sufficient by itself to make two-bank inference a central top-tier contribution.

## Stop and preserve A/B if

- differentiability requires assumptions with no interpretable relationship to the locked pipeline;
- ordinary bootstrap fails even in the continuous two-candidate model and the repair becomes the dominant subject of the paper;
- exact plus-one discreteness contributes at first order throughout the scientifically relevant threshold range;
- the multiple-candidate extension cannot be stated without hiding winner-selection irregularity;
- D produces only standard quantile asymptotics without a meaningful policy-level theorem.

Stopping D does not invalidate Work Packages A and B. It only determines whether the final top-tier paper is primarily conceptual or also contains a full two-bank inference theory.

---

# 14. Prior-art boundary

The functional delta method, empirical-process weak convergence, quantile asymptotics, and nonparametric bootstrap are established tools. Standard sources treat these components in general form. The potential new contribution is not a new bootstrap theorem in isolation; it is the representation and inference theory for a policy rejection functional whose calibration and evaluation are supplied by independent banks.

The principal regular-theory sources are:

- van der Vaart's functional delta method, quantile asymptotics, and bootstrap chapters;
- van der Vaart and Wellner for weak convergence and empirical processes;
- Kosorok for bootstrap empirical processes and semiparametric inference;
- Bickel and Freedman for classical bootstrap validity and failure examples;
- Phipson and Smyth for finite-sample plus-one Monte Carlo p-values.

Fang and Santos become relevant if later policy maps are only Hadamard directionally differentiable: ordinary bootstrap consistency cannot then be assumed merely from directional differentiability.

---

# 15. Repository and locking plan

Place the reviewed protocol at:

```text
theory/policy_search_size/work_package_d0/
```

Track:

- `D0_PROTOCOL.md`
- `D0_CONFIG.json`
- `README.md`
- `references.bib`

After scientific review but before D1 proof or simulation, commit and tag:

```text
commit: Add two-bank inference protocol D0
tag:    tess-theory-work-package-d0-v1-lock-20260802
```

Work Package D1/D2 outputs must be committed after the D0 lock, never amended into the protocol commit.

---

# 16. Immediate next action after protocol review

The first mathematical task is not the full process theorem. It is to prove D1 for fixed \(\alpha\) and known \(c\):

1. establish a joint Bahadur representation for the two candidate quantiles from the reference bank;
2. differentiate the rejection-set probability with respect to \(q_0\) and \(q_1\);
3. derive the two-bank asymptotic linear expansion;
4. verify the variance formula by direct Monte Carlo calculation;
5. prove ordinary independent two-bank bootstrap validity.

Only after D1 is clean will the estimated trigger be introduced.

---

# References

1. Bickel PJ, Freedman DA. Some asymptotic theory for the bootstrap. *Annals of Statistics*. 1981;9(6):1196-1217. doi:10.1214/aos/1176345637.
2. Fang Z, Santos A. Inference on directionally differentiable functions. *Review of Economic Studies*. 2019;86(1):377-412. doi:10.1093/restud/rdy049.
3. Kosorok MR. *Introduction to Empirical Processes and Semiparametric Inference*. Springer; 2008. doi:10.1007/978-0-387-74978-5.
4. Phipson B, Smyth GK. Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*. 2010;9(1):Article 39. doi:10.2202/1544-6115.1585.
5. van der Vaart AW. *Asymptotic Statistics*. Cambridge University Press; 1998. doi:10.1017/CBO9780511802256.
6. van der Vaart AW, Wellner JA. *Weak Convergence and Empirical Processes: With Applications to Statistics*. Springer; 1996. doi:10.1007/978-1-4757-2545-2.
