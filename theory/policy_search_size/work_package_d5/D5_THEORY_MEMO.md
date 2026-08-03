# Work Package D5 Theory Memo

## Exact plus-one/order-statistic bridge for a paired adaptive policy contrast

**Status:** theory draft before implementation lock  
**Parent result:** `d4-validation-full-v1`

---

# 1. Problem

Let \(X_1,\ldots,X_B\) be a finite null-reference bank for one candidate
score and let \(x\) be an independently evaluated score. The locked empirical
pipeline uses the plus-one Monte Carlo p-value

\[
\widehat p_B^+(x)
=
\frac{1+\sum_{b=1}^B I(X_b\ge x)}{B+1}
\]

and rejects when \(\widehat p_B^+(x)<\alpha\).

Work Packages D1-D4 use the regular empirical-quantile representation

\[
x>X_{(k_B^Q(\alpha))},
\qquad
k_B^Q(\alpha)
=
\left\lceil B(1-\alpha)\right\rceil.
\]

D5 gives the exact finite-\(B\) order-statistic form of the plus-one event and
quantifies the discrepancy between the exact and regular boundaries for the
D4 paired policy contrast.

---

# 2. Exact plus-one boundary

Define

\[
C_B(\alpha)
=
\left\lceil(B+1)\alpha\right\rceil.
\]

## Lemma D5.1. Exact order-statistic equivalence

If \(C_B(\alpha)=1\), then
\(\widehat p_B^+(x)<\alpha\) is impossible.

If \(C_B(\alpha)\ge2\), define

\[
k_B^+(\alpha)
=
B+2-C_B(\alpha).
\]

Then, for arbitrary real reference scores, including ties,

\[
\boxed{
\widehat p_B^+(x)<\alpha
\iff
x>X_{(k_B^+(\alpha))}.
}
\]

### Proof

Write

\[
N_{\ge}(x)
=
\sum_{b=1}^B I(X_b\ge x).
\]

Because \(1+N_{\ge}(x)\) is integer,

\[
1+N_{\ge}(x)<(B+1)\alpha
\iff
1+N_{\ge}(x)\le C_B(\alpha)-1.
\]

Thus,

\[
\widehat p_B^+(x)<\alpha
\iff
N_{\ge}(x)\le C_B(\alpha)-2.
\]

If \(C_B(\alpha)=1\), the right side requires \(N_{\ge}(x)\le-1\), which is
impossible.

Suppose \(C_B(\alpha)\ge2\). The inequality
\(N_{\ge}(x)\le C_B(\alpha)-2\) is equivalent to at least

\[
B-\{C_B(\alpha)-2\}
=
B+2-C_B(\alpha)
\]

reference observations being strictly smaller than \(x\). This is equivalent
to

\[
X_{(B+2-C_B(\alpha))}<x.
\]

No continuity assumption is used. The strict comparison is exactly what
preserves the declared \(\ge\) count in the presence of ties. \(\square\)

---

# 3. Exact finite-bank rejection probabilities

For an independent continuous evaluation score from the same distribution as
the reference scores,

\[
P\{X_{\mathrm{eval}}>X_{(k)}\}
=
\frac{B+1-k}{B+1}.
\]

Therefore,

\[
\tau_B^+(\alpha)
=
\frac{C_B(\alpha)-1}{B+1}
\]

and

\[
\tau_B^Q(\alpha)
=
\frac{B+1-k_B^Q(\alpha)}{B+1}.
\]

The first quantity is the largest attainable plus-one p-value grid point
strictly below \(\alpha\).

## Lemma D5.2. Adjacent-boundary identity

Whenever the plus-one rejection event is attainable,

\[
\boxed{
k_B^+(\alpha)-k_B^Q(\alpha)\in\{0,1\}.
}
\]

Consequently,

\[
\boxed{
\tau_B^Q(\alpha)-\tau_B^+(\alpha)
\in
\left\{0,\frac1{B+1}\right\}.
}
\]

### Proof

Let \(t=(B+1)\alpha\). Using
\(\lceil m-z\rceil=m-\lfloor z\rfloor\) for integer \(m\),

\[
k_B^Q(\alpha)
=
\left\lceil B-B\alpha\right\rceil
=
B-\lfloor B\alpha\rfloor.
\]

Also,

\[
k_B^+(\alpha)
=
B+2-\lceil(B+1)\alpha\rceil.
\]

Hence

\[
k_B^+(\alpha)-k_B^Q(\alpha)
=
2+\lfloor B\alpha\rfloor-\lceil(B+1)\alpha\rceil.
\]

Because \((B+1)\alpha-B\alpha=\alpha\in(0,1)\), the two integer roundings can
differ only in the two configurations that make the displayed quantity zero
or one. The tail-probability result follows from
\(\tau=(B+1-k)/(B+1)\). \(\square\)

For every D4 design point
\(B\in\{500,1000,3000\}\) and
\(\alpha\in\{0.01,0.05,0.10\}\), the index gap equals one.

---

# 4. D4 paired policy contrast

For one evaluation observation, write

\[
R_0(q_0)=I(X_0>q_0),
\qquad
A(c)=I(U>c),
\]

and

\[
M(q_0,q_1)
=
I(X_0\le q_0,\ X_1>q_1).
\]

The adaptive rejection indicator is

\[
H_A(q_0,q_1,c)
=
R_0(q_0)+A(c)M(q_0,q_1).
\]

The budget-matched comparator rejection probability is estimated by

\[
\widehat\pi_C
=
\widehat e_0
+
\widehat r\,\widehat\mu,
\]

where

\[
\widehat e_0=\mathbb P_nR_0,
\qquad
\widehat r=\mathbb P_nA,
\qquad
\widehat\mu=\mathbb P_nM.
\]

The paired rejection contrast is

\[
\widehat\Delta_\pi
=
\mathbb P_nH_A
-
\{\widehat e_0+\widehat r\,\widehat\mu\}.
\]

D5 compares this functional at the quantile thresholds
\((q_0^Q,q_1^Q)\) and the plus-one thresholds
\((q_0^+,q_1^+)\), using the same activation threshold, reference bank,
evaluation bank, and policy-state realizations.

---

# 5. Shrinking adjacent-order-statistic intervals

Suppose the candidate distributions have continuous densities that are
positive and finite near their target quantiles. When the two boundary indices
are adjacent, define the random interval

\[
I_{j,B}
=
(q_j^Q,q_j^+],
\qquad j\in\{0,1\}.
\]

Conditional on the reference bank, every candidate rejection indicator that
differs between the two modes is supported on \(I_{0,B}\), \(I_{1,B}\), or
their finite union together with bounded policy-state factors.

Standard adjacent-spacing behavior gives

\[
P(X_j\in I_{j,B}\mid\mathcal R_B)
=
O_p(B^{-1}).
\]

For an independent evaluation bank,

\[
\mathbb P_n I(X_j\in I_{j,B})
=
P(X_j\in I_{j,B}\mid\mathcal R_B)
+
O_p\left(
\sqrt{
\frac{
P(X_j\in I_{j,B}\mid\mathcal R_B)
}{n}
}
\right).
\]

Therefore,

\[
\mathbb P_n I(X_j\in I_{j,B})
=
O_p\left(
\frac1B+\frac1{\sqrt{Bn}}
\right).
\]

This rate is sharper than treating the two estimated quantiles separately,
because the bridge depends on their adjacent spacing rather than their
individual \(B^{-1/2}\) estimation errors.

---

# 6. Rejection-scale bridge theorem

## Theorem D5.3. Paired adjacent-boundary rate

Assume:

1. the reference and evaluation banks are independent complete-replication
   banks;
2. candidate marginal densities are continuous, positive, and finite in
   neighborhoods of the relevant quantiles;
3. the conditional policy-increment probabilities are locally bounded and
   sufficiently regular in the candidate thresholds;
4. the activation threshold and activation realization are common across the
   two boundary modes;
5. \(\alpha\) lies in a compact subinterval of \((0,1)\).

Then

\[
\boxed{
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
=
O_p\left(
\frac1B+\frac1{\sqrt{Bn}}
\right).
}
\]

If \(B\to\infty\) and \(n\to\infty\), then

\[
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
=
o_p(B^{-1/2}+n^{-1/2}).
\]

### Proof sketch

The difference in base rejection is supported on \(I_{0,B}\). The difference
in the incremental-rejection indicator is supported on the union of
\(I_{0,B}\) and \(I_{1,B}\). Multiplication by the common bounded activation
indicator does not change the order.

The comparator difference is

\[
\widehat r
\left(
\widehat\mu^+-\widehat\mu^Q
\right),
\]

because the activation rate is identical across modes. Since
\(0\le\widehat r\le1\), this has the same order as the incremental-rate
difference. The adaptive difference is an empirical average of a bounded
indicator supported on the same shrinking union. Applying the rate in Section
5 to the finite collection of terms proves the first display.

Finally,

\[
\frac{B^{-1}+(Bn)^{-1/2}}
{B^{-1/2}+n^{-1/2}}
\longrightarrow0
\]

when both banks diverge. \(\square\)

The theorem is an upper bound. Dependence structure and the paired policy
contrast may create additional cancellation, but no such cancellation is
required for the bridge.

---

# 7. Nominal-alpha TESS bridge

Define the locked nominal-alpha TESS map

\[
g_\alpha(\pi)
=
\frac{\log(1-\pi)}{\log(1-\alpha)}.
\]

Both D5 boundary modes retain the nominal scientific threshold \(\alpha\) in
the denominator.

## Theorem D5.4. Fixed-alpha TESS bridge

Suppose the assumptions of Theorem D5.3 hold, \(\alpha\) is bounded away from
zero, and the adaptive and comparator rejection probabilities are bounded
away from one. Then

\[
\boxed{
\widehat\Delta_S^+
-
\widehat\Delta_S^Q
=
O_p\left(
\frac1B+\frac1{\sqrt{Bn}}
\right)
=
o_p(B^{-1/2}+n^{-1/2}).
}
\]

### Proof

On the declared domain,

\[
g_\alpha'(\pi)
=
-\frac1{(1-\pi)\log(1-\alpha)}
\]

is uniformly bounded. Apply the mean-value theorem separately to the adaptive
and comparator rejection probabilities, then use Theorem D5.3. \(\square\)

---

# 8. Small-alpha and non-negligible regimes

For small \(\alpha\),

\[
|\log(1-\alpha)|
\sim\alpha.
\]

Thus a rejection-scale bridge discrepancy of order

\[
B^{-1}+(Bn)^{-1/2}
\]

can become

\[
O_p\left(
\frac1{B\alpha}
+
\frac1{\alpha\sqrt{Bn}}
\right)
\]

on the TESS scale.

Consequently, a uniform first-order bridge may fail or require stronger growth
conditions when:

- \(B\) is fixed;
- \(B\alpha=O(1)\);
- \(\alpha\) approaches a plus-one p-value grid boundary;
- \(\sqrt n/(B\alpha)\) does not vanish;
- \(1/(\alpha\sqrt B)\) does not vanish;
- rejection probabilities approach one.

These are scope conditions, not defects in the finite-sample plus-one rule.

---

# 9. Ties

Lemma D5.1 is exact with ties because it retains the original
\(I(X_b\ge x)\) count and the strict rejection rule
\(\widehat p_B^+(x)<\alpha\).

The adjacent-spacing rate theorem uses continuous candidate laws. Discrete or
mixed candidate laws can place positive mass between or at neighboring order
statistics, so the \(B^{-1}\) shrinking-mass argument need not apply without
additional assumptions or randomized tie handling.

---

# 10. Numerical implication

The D5 numerical validation regenerates the exact 108,000 D4 outer datasets
and computes both boundary modes on identical banks.

The primary numerical outcomes are

\[
D_{\pi,B,n}
=
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
\]

and

\[
D_{S,B,n}
=
\widehat\Delta_S^+
-
\widehat\Delta_S^Q.
\]

The scientific comparison is the RMS bridge discrepancy relative to the
frozen D4 empirical standard deviation of the corresponding quantile-mode
contrast. Magnitude labels are descriptive and do not determine
implementation PASS or FAIL.

---

# 11. Scope boundary

D5 establishes only the one-candidate-per-branch exact plus-one bridge for the
regular D4 paired contrast. It does not establish:

- finite multiple-candidate winner selection;
- a base trigger defined by a maximum score;
- winner ties or deterministic tie randomization;
- failed-fit fallback rules;
- simultaneous threshold-process inference.

Those remain later extensions in the D0 ladder.
