# D8-A Post-Repair Independent Mathematical Audit v2

## Materials audited

- `D8A_MAIN_MANUSCRIPT_DRAFT_V5_MATH_REPAIRED.md`
- `D8A_PROOF_SUPPLEMENT_DRAFT_V4_MATH_REPAIRED.md`
- `D8A_TESS_FINITE_STATUS_ALIGNMENT_AUDIT_RESULT_V3.json`
- pre-repair checkpoint:
  `d8a-full-manuscript-v1-20260806`

## Overall adjudication

**Status: PASS AFTER MATHEMATICAL REPAIR**

The material defect identified in the first independent audit has been
repaired. The manuscript no longer assigns a finite ordinary expectation to
the raw logarithmic TESS contrast. It now separates:

1. the finite-status conditional mean; and
2. positive-infinite, negative-infinite, and indeterminate boundary statuses.

The repaired theorem is aligned with the prospectively locked runner and the
frozen scientific output. No scientific simulation rerun is required.

## 1. Policy definition

**PASS.**

The repaired manuscript formally defines

\[
J_0
=
\arg\max_{j\in\{0,1\}}X_j,
\qquad
J_1
=
\arg\max_{j\in\{0,1,2\}}X_j,
\]

\[
R_0
=
I(X_{J_0}>q_{J_0}),
\qquad
R_1
=
I(X_{J_1}>q_{J_1}),
\]

\[
T=\max(X_0,X_1),
\qquad
A=I(T>c),
\]

and

\[
M=(1-R_0)R_1.
\]

The reference-coordinate definition now identifies \(c\) as the population
quantile of the base maximum \(T\). This makes the winner-cell inventory and
candidate–trigger separation assumptions operational rather than implicit.

## 2. Empirical-quantile theory

**PASS.**

The following parts are unchanged in substance and remain valid:

- the exact order-statistic convention;
- the bounded lattice coefficient;
- the scalar \(B^{-1}\) mean expansion;
- the \(2+\eta\) moment bound;
- the primitive \(L^2\) Bahadur remainder;
- the fixed-dimensional Gaussian limit;
- the complete-vector covariance matrix; and
- joint second-moment convergence.

The wording around stochastic equicontinuity no longer appears to invoke the
desired Bahadur representation circularly.

## 3. Moving-maximum geometry

**PASS under the strengthened stated assumptions.**

The cone-wise re-derivation confirms

\[
\frac12K_s(t,t)(u-v)_+^2
\]

with the stated orientation and coefficient. The repaired Assumption P now
requires parameter-uniform integrable envelopes over the complete lower
integration range rather than only local smoothness at the moving boundary.

The theorem now derives the individual probability-map coefficients

\[
\lambda_{A,a}=s_a\kappa_a,
\qquad
\lambda_{C,a}=\rho(\theta)\kappa_a,
\]

and therefore

\[
\lambda_a
=
\lambda_{A,a}-\lambda_{C,a}
=
\{s_a-\rho(\theta)\}\kappa_a.
\]

## 4. Generalized expectation expansion

**PASS.**

The repaired tail argument explicitly controls the constant, linear, and
quadratic parts of the globally defined remainder. Under the \(2+\eta\) moment
bound, each tail contribution is \(o(B^{-1})\).

The generalized reference coefficient remains

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
(
H_\Delta^{\mathrm{sm}}\Sigma_\theta
)
\\
&\quad+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

## 5. Exact finite-\(n\) identity and combined expansion

**PASS.**

The exact conditional identity remains

\[
E_E(
\widehat\Delta_\pi
\mid
\widehat\theta_R
)
=
\left(1-\frac1n\right)
\Delta_\pi(\widehat\theta_R).
\]

Consequently,

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
+
o(B^{-1}+n^{-1})
\]

is correct. The \(B^{-1}n^{-1}\) contribution is consistently described as an
algebraically determined product term.

## 6. Finite-status TESS theorem

**PASS under Assumption T.**

Define

\[
\mathcal F_{B,n}
=
\{
\widehat\pi_A<1,\,
\widehat\pi_C<1
\}.
\]

The repaired theorem states

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

The proof is valid because:

1. a bounded \(C^3\) extension agrees with the logarithmic transform near the
   population targets;
2. the extension admits ordinary expectation expansion;
3. the finite raw transform is at most \(O(1+\log n)\);
4. entering the upper boundary neighborhood has exponentially decreasing
   probability;
5. the mild relative-growth condition controls the reference-tail term; and
6. replacing a random evaluation coefficient by its population value now uses
   the \(L^1\) bound
   \[
   E\|\widehat\theta_R-\theta\|=O(B^{-1/2}),
   \]
   rather than only an \(O_p\) statement.

The theorem does not claim a finite unconditional expectation for the raw
logarithmic estimator.

## 7. Numerical alignment

**PASS.**

The alignment audit verified:

- source finite-status contract: PASS;
- frozen publication output: PASS;
- primary combined jobs: 17/17;
- largest-pair TESS records: 34/34;
- \(\alpha=0.01\): 17 records;
- \(\alpha=0.05\): 17 records;
- Monte Carlo observations checked: 68,000;
- nonfinite records: 0;
- all finite-value means: finite;
- scientific simulation rerun: no; and
- repository modification: no.

Therefore, at the primary largest-pair cells, the finite-status mean equals the
mean over all simulated records. The reported TESS biases, residuals, and
Figure 3 do not require numerical recalculation.

## 8. Text and notation audit

**PASS after one mechanical repair.**

A hidden bell control character had replaced the backslash in `\alpha` in the
Figure 3 caption. It was corrected. The current files have:

- no control characters;
- balanced display-math delimiters;
- balanced inline-math delimiters;
- no `[REF]` placeholders;
- no raw unconditional TESS expectation formula; and
- consistent finite-status terminology.

## Final result

| Component | Final status |
|---|---|
| Joint empirical-quantile theorem | PASS |
| Moving-maximum lemma | PASS under stated assumptions |
| Generalized policy expansion | PASS |
| Generalized reference coefficient | PASS |
| Exact finite-\(n\) identity | PASS |
| Combined policy-probability expansion | PASS |
| Finite-status TESS expansion | PASS under Assumption T |
| TESS numerical alignment | PASS |
| Scientific rerun required | NO |

## Remaining pre-submission work

The remaining tasks are not repairs to the proved theorem chain:

1. human external mathematical review;
2. target-journal formatting and length control;
3. Figure 1 editable-vector production;
4. repository DOI and release metadata;
5. final AI-assistance statement; and
6. journal-specific cover letter and declarations.
