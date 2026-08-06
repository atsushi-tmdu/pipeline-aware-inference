# Second-Order Finite-Sample Bias in Threshold-Adaptive Statistical Policies

## Draft figure captions and numerical-validation sections

**Draft status:** manuscript-facing v2; theorem notation reconciled  
**Internal project:** D8-A  
**Internal project name should not appear in the submitted manuscript.**

---

# Figure captions

## Figure 1. Threshold geometry and the generalized second-order expansion

(A) Local threshold geometry for a finite-candidate adaptive policy. The diagonal represents a candidate-threshold coincidence boundary separating the two regular regions in which the base and added-candidate thresholds have a fixed ordering. Within either regular region, the policy functional admits an ordinary smooth expansion.  
(B) Local behavior at a coincidence boundary. The generalized expansion has the same value and first derivative as the smooth component at the boundary, but its second-order behavior includes a one-sided positive-part-square contribution. Thus, the functional can remain first-order smooth while not being represented by the ordinary smooth Hessian alone.  
(C) Schematic comparison of the regular and coincidence-boundary expansions. For local perturbation \(h\),

\[
V(\theta+h)
=
V(\theta)
+
g^\top h
+
\frac{1}{2}h^\top H^{\mathrm{sm}}h
+
\sum_{a\in\mathcal A_0}
\lambda_a(d_a^\top h)_+^2
+
o(\|h\|^2),
\]

where \(\mathcal A_0=\{a\in\{0,1\}:q_a=q_2\}\), \(d_a=e_a-e_2\), and \((x)_+=\max(x,0)\). The additional sum vanishes away from the coincidence boundary.

---

## Figure 2. Reference-only numerical validation

(A) Class-specific raw normalized residuals across the five prospectively specified reference-bank sizes. Thin trajectories represent the 17 primary equivalence classes; the solid and dashed summary trajectories show the median and 90th percentile, respectively. The annotation compares the summaries at \(B=10{,}000\) with the prospectively specified criteria. The panel displays the full size dependence and does not imply monotone convergence.  
(B) Class-specific observed reference bias versus the generalized prediction \(C_{\Delta,B}^{\mathrm{gen}}/B\) at \(B=10{,}000\). The diagonal denotes equality.  
(C) Numbers of primary classes for which the generalized correction reduced absolute bias error relative to no reference correction, the gradient-only correction, and the smooth-only correction. The smooth-only comparison was prospectively designated as descriptive and nonfatal.

---

## Figure 3. Alpha-specific TESS-bias agreement and Monte Carlo resolution

(A–B) Class-specific observed TESS bias versus the generalized finite-sample bias prediction at \(B=n=10{,}000\), displayed on the original bias scale separately for \(\alpha=0.01\) and \(\alpha=0.05\). Each marker represents one of the 17 prospectively specified primary equivalence classes; the diagonal denotes equality.  
(C) Class-specific ratios of the absolute raw residual to the simultaneous Monte Carlo allowance \(z_{\mathrm{sim}}\times\mathrm{MCSE}\). Values below 1 have an MCSE-adjusted normalized residual of zero; horizontal segments indicate medians. All 17 primary classes were below the boundary at both alpha levels, and no nonfinite primary TESS record occurred.

The raw median and 90th-percentile normalized residuals were 0.5288 and 1.4612 at \(\alpha=0.01\), and 0.4073 and 0.8891 at \(\alpha=0.05\), whereas both corresponding MCSE-adjusted summaries were zero. The result therefore constituted a formal pass under the prospectively specified metric, while raw finite-sample TESS accuracy remained limited by Monte Carlo resolution.

---

## Figure 4. Combined-policy approximation and the exact finite-\(n\) evaluation identity

(A) Class-specific observed combined-policy bias versus the generalized joint reference/evaluation prediction at \(B=n=10{,}000\). Each point represents one of the 17 primary equivalence classes; the diagonal denotes equality. The raw normalized-residual median and 90th percentile were 0.0495 and 0.1474, respectively, compared with the prospectively specified criteria of 0.15 and 0.40.  
(B) Signed standardized discrepancies for the exact finite-\(n\) identity

\[
E(\widehat{\Delta}_n)
=
\left(1-\frac{1}{n}\right)\Delta_\pi
\]

across 17 primary equivalence classes and five evaluation-sample sizes. Dashed horizontal lines denote the simultaneous two-sided Bonferroni boundaries \(\pm3.85098\). All 85 comparisons passed; the maximum absolute standardized discrepancy was 2.99695. The highlighted point is the comparison with the largest absolute discrepancy.

---

# Methods

## Policy and TESS estimands

Let \(A\) denote activation of the optional branch and \(M\) the incremental rejection opportunity. The policy-probability contrast was

\[
\Delta_\pi(\theta)
=
P_{AM}(\theta)
-
P_A(\theta)P_M(\theta),
\]

and its evaluation-sample estimator was

\[
\widehat{\Delta}_\pi
=
\overline{AM}
-
\bar A\bar M.
\]

For TESS, define

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)}
\]

and

\[
\Delta_S
=
g_\alpha(\pi_A)
-
g_\alpha(\pi_C),
\]

where \(\pi_A\) and \(\pi_C\) are the adaptive-policy and budget-matched comparator rejection probabilities.

## Prospectively locked numerical validation

### Validation objectives

We conducted a prospectively specified and computationally locked numerical study to evaluate four implications of the generalized finite-sample theory. First, the reference-only family assessed whether the generalized second-order coefficient approximated the \(B^{-1}\) bias induced by reference-calibrated thresholds. Second, the evaluation-only family assessed the exact finite-\(n\) identity. Third, the combined family assessed the joint reference/evaluation expansion, including the \(B^{-1}n^{-1}\) interaction. Fourth, the combined family was transformed to TESS at \(\alpha=0.01\) and \(\alpha=0.05\) to assess nonlinear propagation of the finite-sample expansion.

### Validated policy scope

The generalized policy theorem and its numerical validation concerned fixed base and full candidate pools \(\{0,1\}\subset\{0,1,2\}\), almost-surely unique winners, strict candidate-trigger threshold separation, and fixed-dimensional reference-threshold estimation. Candidate-threshold coincidences were permitted at \(q_0=q_2\) and \(q_1=q_2\) and were handled by the generalized piecewise-quadratic expansion. Reference and evaluation banks were independent. The validation did not address growing candidate dimension, discrete winner ties, or failed-fit fallback rules.

### Scientific units and simulation families

The scientific units were 25 latent equivalence classes, of which 17 were designated primary and 8 diagnostic before scientific execution. Formal acceptance was determined exclusively by the 17 primary classes. Fifty deterministic common-monotone-transform rows were used only for invariance audits and did not enlarge the formal denominator.

Three simulation families were evaluated: reference-only, evaluation-only, and combined reference/evaluation. Each family contained 25 jobs, for 75 jobs in total. Reference-bank sizes were

\[
B\in\{250,500,1000,3000,10000\},
\]

and evaluation-sample sizes were

\[
n\in\{250,500,1000,3000,10000\}.
\]

TESS quantities were evaluated separately at \(\alpha=0.01\) and \(\alpha=0.05\).

### Random-number and execution contract

The master seed was 20260804. Reference and evaluation streams were independent, and nested random-number prefixes were used within each simulation family so that increasing sample sizes reused the appropriate earlier draws. Batch outputs were written atomically, and completed jobs could be resumed deterministically without silently overwriting prior batches. No effect-dependent stopping or post-hoc class deletion was permitted.

### Replication and precision stopping

Primary classes were assigned a minimum of 2,000 and a maximum of 20,000 replicates; diagnostic classes were assigned a minimum of 1,000 and a maximum of 5,000 replicates. Replicates were added in batches of 250. Stopping was based only on Monte Carlo precision and required

\[
\frac{\mathrm{MCSE}}{1+|\tau|}
\leq 0.03,
\]

where \(\tau\) was the prospectively locked population target. TESS status proportions used unit scale. The observed Monte Carlo mean did not enter the stopping rule.

### Bias predictions

For a policy-probability contrast \(\Delta_\pi\), the reference-only generalized prediction was

\[
b_{R}(B)
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}.
\]

For the combined reference/evaluation estimator, the prospectively specified prediction was

\[
b_{R,E}(B,n)
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}.
\]

For TESS, the generalized finite-sample prediction was

\[
b_S(B,n;\alpha)
=
\frac{C_{S,R,B}^{\mathrm{gen}}(\alpha)}{B}
+
\frac{C_{S,E}(\alpha)}{n},
\]

where

\[
\begin{aligned}
C_{S,R,B}^{\mathrm{gen}}
&=
g_\alpha'(\pi_A)
C_{A,B}^{\mathrm{gen}}
+
\frac12
g_\alpha''(\pi_A)V_{R,A}
\\
&\quad
-
g_\alpha'(\pi_C)
C_{C,B}^{\mathrm{gen}}
-
\frac12
g_\alpha''(\pi_C)V_{R,C},
\end{aligned}
\]

and

\[
C_{S,E}
=
\frac12
g_\alpha''(\pi_A)V_{E,A}
-
g_\alpha'(\pi_C)\Delta_\pi
-
\frac12
g_\alpha''(\pi_C)V_{E,C}.
\]

Thus, the TESS prediction retained both centering and curvature contributions from the reference and evaluation banks.

### Residual metrics

Let \(\widehat{\mu}\) denote the Monte Carlo mean of an estimator, \(\tau\) its locked population target, \(b_{\mathrm{pred}}\) the corresponding finite-sample bias prediction, \(s\) the locked natural-oracle scale, and \(\mathrm{MCSE}\) the Monte Carlo standard error. The raw normalized residual was

\[
R_{\mathrm{raw}}
=
\frac{|(\widehat{\mu}-\tau)-b_{\mathrm{pred}}|}{s}.
\]

The formal MCSE-adjusted normalized residual was

\[
R_{\mathrm{adj}}
=
\frac{
\max\{
|(\widehat{\mu}-\tau)-b_{\mathrm{pred}}|
-
z_{\mathrm{sim}}\mathrm{MCSE},
0
\}
}{s},
\]

with the prospectively specified residual-adjustment factor

\[
z_{\mathrm{sim}}=4.2372795825947795.
\]

Thus, \(R_{\mathrm{adj}}=0\) indicates that the raw residual was contained within the simultaneous Monte Carlo uncertainty allowance; it does not indicate a numerically zero raw residual. Raw normalized residuals were retained as interpretability diagnostics and did not replace the prospectively specified formal metric.

For the policy-probability contrasts, the locked scales were

\[
s_R(B)
=
\frac{1+|C_{\Delta,B}^{\mathrm{gen}}|}{B}
\]

for the reference-only family and

\[
s_{R,E}(B,n)
=
\left(\frac{1}{B}+\frac{1}{n}\right)
\left(
1+
|C_{\Delta,B}^{\mathrm{gen}}|
+
|\Delta_\pi|
\right)
\]

for the combined family. The TESS scale was defined analogously using the reference and evaluation TESS coefficients.

### Prospectively specified acceptance criteria

For the reference-only approximation at \(B=10{,}000\), the median and 90th percentile of \(R_{\mathrm{adj}}\) had to be no greater than 0.15 and 0.40, respectively. The median improvement from \(B=500\) to \(B=10{,}000\) had to be at least 40%, and the generalized correction had to improve at least 75% of the primary classes relative to the prespecified no-correction baseline.

For the combined-policy approximation at \(B=n=10{,}000\), the median and 90th percentile of \(R_{\mathrm{adj}}\) had to be no greater than 0.15 and 0.40.

For combined TESS at \(B=n=10{,}000\), assessed separately at each alpha level, the median and 90th percentile of \(R_{\mathrm{adj}}\) had to be no greater than 0.25 and 0.60. Any nonfinite primary TESS record constituted formal failure.

The exact finite-\(n\) identity was evaluated in 85 comparisons—17 primary classes at five evaluation-sample sizes—using the signed standardized discrepancy

\[
Z_{c,n}
=
\frac{
\widehat{\mu}_{c,n}
-
(1-1/n)\Delta_{\pi,c}
}{
\mathrm{MCSE}_{c,n}
}.
\]

All comparisons had to lie within the two-sided Bonferroni limits \(\pm z_{\mathrm{id}}\), where

\[
z_{\mathrm{id}}=3.8509780194087373,
\]

corresponding to a familywise alpha level of 0.01.

No more than 10% of the 17 primary classes could reach the maximum replicate count without satisfying the precision target; operationally, this permitted at most one precision-limited primary class. Formal PASS required every scientific criterion and fatal implementation check to pass.

### Formal and auxiliary interpretation

Formal adjudication used only the prospectively specified criteria. Raw residual summaries, comparison with gradient-only and smooth-only approximations, and other baseline diagnostics were reported separately for interpretation. The smooth-only comparison was descriptive and nonfatal. The overall evidential interpretation was assigned only after the formal decision had been retained.

---

# Results

## Completion and formal adjudication

All 75 prospectively selected jobs completed, with 25 jobs in each of the reference-only, evaluation-only, and combined families. The completed study contained 126,000 committed replicates. All jobs stopped after meeting the precision target, and no primary class was precision limited. No prospective criterion was changed, no class was dropped, and the scientific simulation was not rerun after results were inspected.

The formal contract status was PASS. The overall evidential interpretation was **formal pass with qualified numerical support**. Evidence for the policy-probability expansion was classified as **strong support**, whereas finite-sample TESS evidence was classified as **formal pass but MCSE-resolution limited** (Table 2).

## Reference-only approximation

At \(B=10{,}000\), the MCSE-adjusted normalized-residual median and 90th percentile were both zero, satisfying the prospectively specified limits of 0.15 and 0.40. The corresponding raw median and 90th percentile were 0.0355 and 0.0958 (Figure 2A). In the class-specific bias comparison, the generalized prediction tracked the observed reference bias across the 17 primary classes (Figure 2B).

The generalized correction reduced absolute bias error relative to no reference correction in 15 of 17 primary classes (88.2%), exceeding the prospectively specified 75% requirement. It also improved 14 of 17 classes (82.4%) relative to the gradient-only approximation. The generalized correction improved 9 of 17 classes (52.9%) relative to the smooth-only approximation; this comparison was descriptive and nonfatal (Figure 2C).

The prospectively specified median-improvement statistic from \(B=500\) to \(B=10{,}000\) was formally equal to 1 because both MCSE-adjusted medians were truncated to zero. This criterion therefore passed but was non-discriminating under complete MCSE flooring. In the raw diagnostic, the median increased from 0.0049 at \(B=500\) to 0.0355 at \(B=10{,}000\), and thus did not demonstrate monotone improvement with increasing reference-bank size.

## Combined-policy approximation

At \(B=n=10{,}000\), the MCSE-adjusted normalized-residual median and 90th percentile were both zero, satisfying the prospectively specified limits of 0.15 and 0.40. The raw median and 90th percentile were 0.0495 and 0.1474, respectively (Figure 4A). These raw summaries remained well below the formal limits and provided strong numerical support for the joint prediction containing the reference, evaluation, and \(B^{-1}n^{-1}\) interaction terms.

## TESS finite-sample approximation

At \(\alpha=0.01\), the MCSE-adjusted normalized-residual median and 90th percentile were both zero, and no nonfinite primary record occurred. The corresponding raw median and 90th percentile were 0.5288 and 1.4612. At \(\alpha=0.05\), the adjusted median and 90th percentile were again both zero, with raw values of 0.4073 and 0.8891 and no nonfinite primary record.

For every primary class at both alpha levels, the absolute raw residual was smaller than the simultaneous Monte Carlo allowance \(z_{\mathrm{sim}}\times\mathrm{MCSE}\); consequently, all 17 classes at each alpha level had an adjusted normalized residual of zero (Figure 3C). The alpha-specific observed-versus-predicted bias plots showed broadly similar finite-sample patterns (Figure 3A–B). The TESS criteria therefore passed formally, but the raw residual summaries exceeded the nominal adjusted-metric thresholds, indicating that the available Monte Carlo resolution could not establish comparably strong raw finite-sample accuracy.

## Exact finite-\(n\) evaluation identity

All 85 simultaneous Bonferroni checks of

\[
E(\widehat{\Delta}_n)
=
\left(1-\frac{1}{n}\right)\Delta_\pi
\]

passed across the 17 primary classes and five evaluation-sample sizes (Figure 4B). The absolute standardized discrepancies had a median of 0.6308, a 90th percentile of 1.705, and a maximum of 2.99695, below the simultaneous boundary of 3.85098. This fatal implementation check therefore provided strong support for the exact evaluation-sample identity used in the combined expansion.

## Summary of numerical evidence

Taken together, the reference-only and combined-policy results supported the generalized finite-sample expansion on the raw diagnostic scale as well as under the formal MCSE-adjusted metric. The exact finite-\(n\) identity was supported in every prespecified comparison. Propagation to TESS satisfied all formal criteria and produced no nonfinite primary records; however, because every adjusted TESS residual was zero after simultaneous MCSE flooring, the strength of the raw TESS approximation remained unresolved at the available Monte Carlo precision.

---

# Drafting notes to resolve before submission

1. Replace internal theorem names with final manuscript theorem numbering once the theory section is assembled.
2. Verify that the final Figure 1 vector source displays exactly \(\mathcal A_0=\{a:q_a=q_2\}\), \(d_a=e_a-e_2\), and the chosen notation for \(\lambda_a\).
3. Decide whether the full derivations of \(z_{\mathrm{sim}}\) and \(z_{\mathrm{id}}\) remain in the main Methods or move to the supplement while retaining the numerical values in the main text.
4. Add software versions and repository/archival identifiers in the reproducibility subsection.
5. Perform a line-by-line overlap audit against the frozen empirical version 2 before submission.
