# D8-A Independent Mathematical Audit v1

## Manuscript audited

- **Main manuscript:** `D8A_MAIN_MANUSCRIPT_DRAFT_V4_OVERLAP_SAFE.md`
- **Proof supplement:** `D8A_PROOF_SUPPLEMENT_DRAFT_V3_OVERLAP_SAFE.md`
- **Frozen checkpoint:** `d8a-full-manuscript-v1-20260806`
- **Checkpoint commit:** `98bf1a95a3a277b3f1ead2c2ef53ac299ca960aa`

## Audit method

The theorem chain was re-derived from the primitive definitions rather than
accepted from the earlier internal audit. The audit covered:

1. the exact empirical-quantile lattice term;
2. scalar moment and \(L^2\) Bahadur arguments;
3. fixed-dimensional joint lifting;
4. the moving-maximum expansion on both local cones;
5. the winner-cell inventory;
6. the sign and assembly of the coincidence coefficient;
7. the expectation-level piecewise-quadratic delta step;
8. the exact finite-\(n\) identity;
9. the combined \(B,n\) expansion;
10. the TESS reference and evaluation expansions; and
11. agreement between the manuscript, locked numerical protocol, and runner
    boundary conventions.

## Executive adjudication

**Overall status: MAJOR REVISION REQUIRED.**

The central policy-probability theory survives the independent audit:

- Theorem 1: **PASS with minor exposition repairs**
- Theorem 2: **PASS conditional on making the policy and kernel assumptions explicit**
- Theorem 3: **PASS conditional on the same repairs**
- Proposition 1: **PASS**
- Corollary 1: **PASS**
- Corollary 2 for raw TESS: **FAIL AS STATED**

The failure is localized but mathematically important. The raw TESS estimator
can be \(+\infty\), \(-\infty\), or indeterminate with positive probability at
every finite evaluation-sample size. Therefore its ordinary expectation is not
the finite quantity expanded in the current Corollary 2. The locked numerical
engine already recognizes this issue by recording boundary statuses and
summarizing finite TESS values separately.

The policy-probability results, exact finite-\(n\) identity, Figures 2 and 4,
and their numerical conclusions are not invalidated. The TESS theorem must be
reformulated before submission.

---

# 1. Scalar empirical-quantile expansion

## Finding 1.1 — exact lattice coefficient

**Status: PASS.**

For

\[
\widehat q_{p,B}=Y_{(\lceil Bp\rceil)}
\]

and

\[
a_{p,B}=\lceil Bp\rceil-(B+1)p,
\]

the coefficient

\[
b_{p,B}
=
\frac{a_{p,B}}{f(q_p)}
-
\frac{p(1-p)f'(q_p)}{2f(q_p)^3}
\]

is correct. The first term follows from the exact beta-order-statistic mean,
and the second follows from the inverse-cdf curvature term. Replacing
\((B+1)^{-1}\) by \(B^{-1}\) creates only \(O(B^{-2})\) error because
\(a_{p,B}=O(1)\).

It is also correct that \(b_{p,B}\) may remain bounded without converging.

## Finding 1.2 — complementary-tail control

**Status: PASS, but the proof should be made one line more explicit.**

The finite \(s\)-th moment and exponential central-order-statistic
concentration are sufficient to make the complementary contribution
\(o(B^{-1})\). The manuscript currently states this correctly but compactly.

---

# 2. Moment bound and Bahadur remainder

## Finding 2.1 — scalar \(2+\eta\) moment bound

**Status: PASS.**

The local binomial-deviation argument and the complementary-tail Hölder bound
are sufficient for a uniform \(r\)-th moment bound with \(r>2\). The resulting
uniform integrability of

\[
B(\widehat q-q)^2
\]

is valid.

## Finding 2.2 — \(L^2\) Bahadur remainder

**Status: PASS with an exposition repair.**

The stochastic-equicontinuity step is mathematically appropriate for the VC
class of half-lines. However, the present wording cites the classical
Bahadur–Kiefer representation while proving a Bahadur-type representation.
This can look circular.

**Required repair:** cite or state empirical-process stochastic
equicontinuity directly, then derive the representation. Bahadur and Kiefer
may remain historical references.

---

# 3. Joint empirical-quantile theorem

## Finding 3.1 — Gaussian limit

**Status: PASS.**

The componentwise \(L^2\) remainders imply

\[
B E\|r_B\|^2\to0,
\]

hence \(\sqrt B r_B\to0\) in probability. The multivariate CLT for the bounded
influence vector \(\psi(W)\), followed by Slutsky's theorem, gives

\[
\sqrt B(\widehat\theta_R-\theta)
\Rightarrow
N(0,\Sigma_\theta).
\]

## Finding 3.2 — second-moment convergence

**Status: PASS.**

The cross terms between the leading empirical average and the remainder vanish
by Cauchy–Schwarz. The complete-vector covariance formula correctly retains
candidate–candidate and candidate–trigger dependence.

## Finding 3.3 — higher moment

**Status: PASS.**

For fixed dimension, the vector \(2+\eta\) bound follows from the component
bounds through the standard finite-dimensional norm inequality.

---

# 4. Moving-maximum and coincidence geometry

## Finding 4.1 — cone-wise formula and sign

**Status: PASS.**

For

\[
U(a,q)
=
\int_{-\infty}^{a}
K\{w,\max(w,q)\}\,dw,
\]

the expansion at \(a=q=t\) is

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
&\quad+
\frac12
\left[
K_w(t,t)u^2
+
2K_s(t,t)uv
+
J_{ss}(t)v^2
\right]
\\
&\quad+
\frac12K_s(t,t)(u-v)_+^2
+
o(u^2+v^2).
\end{aligned}
\]

Independent expansion on the cones \(u\le v\) and \(u>v\) confirms both the
orientation \((u-v)_+^2\) and the factor \(1/2\).

## Finding 4.2 — kernel assumptions are too compressed

**Status: MATERIAL REPAIR REQUIRED.**

The proof differentiates integrals over \((-\infty,t]\), but Assumption P says
only that the kernel is smooth “near every relevant coincidence point” with
locally dominated derivatives.

**Required repair:** explicitly require integrable domination, uniformly for
the local threshold parameters, of the derivatives that are integrated over
the whole lower range. The theorem should not rely on a domination condition
that is only local in \(w\).

## Finding 4.3 — uniform remainder wording

**Status: MINOR–MODERATE REPAIR.**

Assumption P currently includes uniform second-order remainders, which is close
to assuming part of the theorem. It should instead state primitive uniform
continuity and domination conditions from which the finite-cone uniform
remainder follows.

---

# 5. Policy definition and winner-cell inventory

## Finding 5.1 — the current manuscript is underdefined

**Status: MATERIAL REPAIR REQUIRED.**

The main manuscript and supplement introduce \(R_0\) and \(R_1\) as rejection
indicators but do not formally define the base and full winners or the
activation statistic. The locked protocol contains the needed definitions:

\[
J_0=\arg\max_{j\in\{0,1\}}X_j,
\qquad
J_1=\arg\max_{j\in\{0,1,2\}}X_j,
\]

\[
R_0=I(X_{J_0}>q_{J_0}),
\qquad
R_1=I(X_{J_1}>q_{J_1}),
\]

and

\[
A=I\{\max(X_0,X_1)>c\}.
\]

These definitions must be imported into both the main manuscript and the
Supplement. The activation threshold \(c\) must also be identified as the
quantile of the base maximum in the declared calibration model.

## Finding 5.2 — winner inventory

**Status: PASS once Finding 5.1 is repaired.**

Conditional on base winner \(a\), the full winner is either \(a\) or candidate
2. Thus the only nonempty winner pairs are

\[
(0,0),\ (0,2),\ (1,1),\ (1,2).
\]

The only active candidate-threshold hyperplanes are

\[
q_0=q_2,
\qquad
q_1=q_2.
\]

## Finding 5.3 — coincidence coefficient

**Status: PASS.**

The incremental probability has branch coefficient \(\kappa_a\), while the
activated incremental probability has coefficient \(s_a\kappa_a\). Since

\[
\Delta_\pi=P_{AM}-P_AP_M,
\]

the policy coefficient is correctly

\[
\lambda_a
=
(s_a-P_A)\kappa_a
=
\{s_a-\rho(\theta)\}\kappa_a.
\]

The coefficient \(\lambda_a\) can have either sign. Figure 1B should be
described as an illustrative orientation rather than implying that the
generalized curve must always lie above the smooth curve.

---

# 6. Generalized expectation lemma

## Finding 6.1 — quadratic expectation

**Status: PASS.**

For a continuous homogeneous degree-two piecewise-quadratic map \(Q\),

\[
B Q(U_B)=Q(\sqrt B\,U_B).
\]

The \(2+\eta\) moment bound gives uniform integrability, so weak convergence
yields

\[
B E\{Q(U_B)\}\to E\{Q(Z)\}.
\]

## Finding 6.2 — tail proof needs one explicit bound

**Status: MINOR REPAIR.**

On the event \(\|U_B\|>\delta\), the proof mentions boundedness of \(h\) and
the quadratic terms but does not explicitly bound the linear term. The result
is still valid: define the remainder globally by subtraction and bound it by

\[
C_0+C_1\|U_B\|+C_2\|U_B\|^2.
\]

The \(2+\eta\) moment condition makes each tail contribution \(o(B^{-1})\)
after multiplication by \(B\).

## Finding 6.3 — generalized coefficient

**Status: PASS.**

For \(Z\sim N(0,\Sigma_\theta)\),

\[
E(d_a^\top Z)_+^2
=
\frac12d_a^\top\Sigma_\theta d_a,
\]

so

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12\operatorname{tr}
(H_\Delta^{\mathrm{sm}}\Sigma_\theta)
\\
&\quad+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a d_a^\top\Sigma_\theta d_a
\end{aligned}
\]

is correct.

---

# 7. Exact finite-\(n\) identity

## Finding 7.1 — exact expectation

**Status: PASS without qualification.**

The diagonal and off-diagonal decomposition gives

\[
E(\bar A\bar M)
=
\rho\mu+\frac{\nu-\rho\mu}{n},
\]

and hence

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

This is exact for every \(n\ge1\).

## Finding 7.2 — combined expansion

**Status: PASS.**

Multiplying the reference expansion by \(1-1/n\) yields

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

The manuscript correctly qualifies the \(B^{-1}n^{-1}\) term as an
algebraically determined product term rather than a separately resolved
asymptotic order.

---

# 8. TESS corollary

## Finding 8.1 — raw TESS expectation does not exist as a finite quantity

**Status: FATAL FOR COROLLARY 2 AS WRITTEN.**

The transform is

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)}.
\]

For \(0<\pi_A<1\), the adaptive estimator is a Bernoulli sample mean and

\[
P(\widehat\pi_A=1)
=
\pi_A^n
>
0.
\]

Therefore

\[
g_\alpha(\widehat\pi_A)=+\infty
\]

with positive probability for every finite \(n\). The comparator can also
reach 1. Consequently,

\[
E\{
g_\alpha(\widehat\pi_A)
-
g_\alpha(\widehat\pi_C)
\}
\]

is not, in general, a finite ordinary expectation; it can also be
indeterminate when both transformed estimates are infinite.

The current assumption that the *population* probabilities lie in a compact
subset of \([0,1)\) does not prevent the *sample* estimates from attaining 1.

The locked runner already encodes this mathematical fact. It does not clip the
boundary. It records four statuses:

- finite;
- positive infinity;
- negative infinity; and
- indeterminate when both probabilities equal 1.

It summarizes only the finite values and reports the boundary-status
proportions separately.

## Finding 8.2 — the numerical TESS target and theorem target are mismatched

**Status: MATERIAL REPAIR REQUIRED.**

The numerical finite-value mean is not literally an estimate of the
unconditional expectation stated in Corollary 2. The absence of observed
nonfinite primary records does not repair the theorem: a positive but
exponentially small boundary probability remains mathematically nonzero.

## Finding 8.3 — correct repair

**Recommended theorem:** finite-status TESS expansion.

Assume there are a neighborhood \(\mathcal N\) of \(\theta\) and
\(\varepsilon>0\) such that

\[
\sup_{\vartheta\in\mathcal N}
\max\{\pi_A(\vartheta),\pi_C(\vartheta)\}
\le
1-2\varepsilon.
\]

Let

\[
\mathcal F_{B,n}
=
\{\widehat\pi_A<1,\ \widehat\pi_C<1\}
\]

be the finite-TESS event. Under the strengthened localization assumptions,

\[
P(\mathcal F_{B,n}^c)
\le
C\{\exp(-cB)+\exp(-cn)\}.
\]

Then

\[
E(
\widehat\Delta_S
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

A rigorous proof can use a bounded \(C^3\) extension of \(g_\alpha\) that
equals \(g_\alpha\) on \([0,1-\varepsilon]\). The raw finite TESS and the
extended transform differ only on an exponentially rare event. On the finite
grid,

\[
|g_\alpha(\widehat\pi_A)|
+
|g_\alpha(\widehat\pi_C)|
=
O(\log n),
\]

so the difference is negligible relative to \(B^{-1}+n^{-1}\).

This formulation aligns with the runner's finite-value summary and separate
boundary-status accounting.

## Finding 8.4 — missing component expansions

**Status: MATERIAL REPAIR REQUIRED.**

The TESS result uses
\(C_{A,B}^{\mathrm{gen}}\) and \(C_{C,B}^{\mathrm{gen}}\), but the Supplement
does not explicitly state the generalized local expansions for \(\pi_A\) and
\(\pi_C\).

They should be added with coincidence coefficients

\[
\lambda_{A,a}=s_a\kappa_a,
\qquad
\lambda_{C,a}=\rho(\theta)\kappa_a,
\]

so that

\[
\lambda_{A,a}-\lambda_{C,a}
=
\lambda_a.
\]

## Finding 8.5 — \(O_p\) is insufficient in an expectation proof

**Status: MATERIAL REPAIR REQUIRED.**

The current proof replaces the random evaluation coefficient at
\(\widehat\theta_R\) by its population value using an
\(O_p(B^{-1/2})\) statement. Because the argument is inside an expectation, an
\(L^1\) bound is required.

Theorem S1 supplies the needed repair:

\[
E\|\widehat\theta_R-\theta\|
=
O(B^{-1/2}),
\]

and local Lipschitz continuity then gives the required expected
\(O(B^{-1/2}n^{-1})\) cross term.

---

# 9. Numerical-design wording and manuscript consistency

## Finding 9.1 — candidate-threshold equality

**Status: WORDING REPAIR.**

The main manuscript says that common candidate probabilities imply
\(q_0=q_1=q_2\). Equal probabilities alone are insufficient if the candidate
marginal distributions differ.

The locked design does have equal thresholds because all three latent candidate
margins are standard normal and use the same target probability. The sentence
should say exactly that.

## Finding 9.2 — formal policy definitions

The locked protocol already contains the precise \(J_0,J_1,R_0,R_1,A,M\)
definitions required by Finding 5.1. Importing them changes no simulation or
estimand.

## Finding 9.3 — implementation evidence

The locked implementation provides strong supporting engineering evidence:

- 55/55 engineering tests passed;
- all 25 scientific classes were audited;
- the directional approximation error was below the predeclared tolerance;
- the kink-identity error was at floating-point precision; and
- transformation invariance passed.

This supports the implementation but does not substitute for the theorem
repairs above.

## Finding 9.4 — minor text defects

Before typesetting:

1. update the Supplement header, which still labels itself “v1” and refers to
   Main Draft v2;
2. repair the duplicated wording around the Bonferroni boundary;
3. replace the remaining use of “interaction” by “algebraic product term”;
4. state that Figure 1B illustrates one sign of \(\lambda_a\); and
5. define why \(\widehat\pi_C\in[0,1]\):
   \(R_0M=0\) implies
   \(\bar R_0+\bar A\bar M\le\bar R_0+\bar M\le1\).

---

# 10. Final theorem-level adjudication

| Result | Independent audit |
|---|---|
| Scalar quantile mean expansion | PASS |
| Scalar moment bound | PASS |
| \(L^2\) Bahadur remainder | PASS, exposition repair |
| Joint quantile theorem | PASS |
| Moving-maximum lemma | PASS, assumptions must be strengthened |
| Winner-cell inventory | PASS after formal definitions are imported |
| Generalized policy expansion | PASS conditional on assumption repairs |
| Generalized reference coefficient | PASS conditional on same repairs |
| Exact finite-\(n\) identity | PASS |
| Combined policy-probability expansion | PASS |
| Raw unconditional TESS expansion | FAIL AS STATED |
| Finite-status TESS expansion | REPAIR AVAILABLE; proof required in manuscript |

## Overall scientific consequence

The paper's central finite-reference/finite-evaluation policy-probability
contribution remains viable. The audit does **not** imply that the D8-A
scientific run must be repeated. Figures 2 and 4 and the corresponding policy
claims remain usable.

For TESS, the stored finite values and boundary-status records can likely be
reused without rerunning the scientific simulation. Before making that
decision final, a deterministic audit should verify that the manuscript's
repaired finite-status estimand matches the runner summary and that all
reported primary TESS means were calculated from the complete finite set, as
the logs indicate.

## Recommended next checkpoint

Create a repair checkpoint, not a replacement of the frozen v1 tag:

- `D8A_MAIN_MANUSCRIPT_DRAFT_V5_MATH_REPAIRED.md`
- `D8A_PROOF_SUPPLEMENT_DRAFT_V4_MATH_REPAIRED.md`
- `D8A_TESS_FINITE_STATUS_ALIGNMENT_AUDIT_V1.md`

The old tag should remain unchanged as the pre-audit checkpoint.
