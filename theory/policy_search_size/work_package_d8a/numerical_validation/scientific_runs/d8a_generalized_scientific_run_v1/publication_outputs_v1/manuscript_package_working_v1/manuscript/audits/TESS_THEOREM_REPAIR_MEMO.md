# D8-A TESS Theorem Repair Memo v1

## Problem

For the raw transform

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)},
\]

the event \(\widehat\pi=1\) gives \(g_\alpha(\widehat\pi)=+\infty\). A
population margin away from 1 does not eliminate this finite-sample event.
Therefore the current unconditional expectation theorem is not valid.

## Repaired target

Let

\[
\mathcal F_{B,n}
=
\{
\widehat\pi_A<1,\,
\widehat\pi_C<1
\}.
\]

The repaired inferential target is the finite-status mean

\[
E(
\widehat\Delta_S
\mid
\mathcal F_{B,n}
).
\]

Boundary-status probabilities are reported separately.

## Additional assumptions

There exist a compact neighborhood \(\mathcal N\) of \(\theta\) and
\(\varepsilon>0\) such that

\[
\sup_{\vartheta\in\mathcal N}
\max\{
\pi_A(\vartheta),
\pi_C(\vartheta)
\}
\le
1-2\varepsilon.
\]

The reference empirical quantiles localize exponentially:

\[
P(\widehat\theta_R\notin\mathcal N)
\le
C e^{-cB}.
\]

The probability maps, their generalized quadratic components, evaluation
variance functions, and the finite-\(n\) centering function are locally
Lipschitz on \(\mathcal N\).

## Boundary probability

On \(\widehat\theta_R\in\mathcal N\),

\[
P(
\widehat\pi_A=1
\mid
\widehat\theta_R
)
=
\pi_A(\widehat\theta_R)^n
\le
(1-2\varepsilon)^n.
\]

Also,

\[
0\le
\widehat\pi_C
=
\bar R_0+\bar A\bar M
\le
\bar R_0+\bar M
\le1.
\]

If \(\widehat\pi_C=1\), then it differs from
\(\pi_C(\widehat\theta_R)\le1-2\varepsilon\) by at least
\(2\varepsilon\). Hoeffding bounds for the three bounded sample means imply

\[
P(
\widehat\pi_C=1
\mid
\widehat\theta_R
)
\le
C e^{-cn}.
\]

Consequently,

\[
P(\mathcal F_{B,n}^c)
\le
C\{
e^{-cB}+e^{-cn}
\}.
\]

## Smooth-extension device

Choose a bounded \(C^3\) function
\(\widetilde g_{\alpha,\varepsilon}\) such that

\[
\widetilde g_{\alpha,\varepsilon}(x)
=
g_\alpha(x)
\]

for \(x\le1-\varepsilon\). Apply the generalized reference and evaluation
expectation expansions to

\[
\widetilde\Delta_S
=
\widetilde g_{\alpha,\varepsilon}(\widehat\pi_A)
-
\widetilde g_{\alpha,\varepsilon}(\widehat\pi_C).
\]

Because the population probabilities lie below \(1-2\varepsilon\), the
derivatives of the extension at the target equal those of \(g_\alpha\). Hence
the coefficients remain

\[
\begin{aligned}
C_{S,R,B}^{\mathrm{gen}}
&=
g_\alpha'(\pi_A)
C_{A,B}^{\mathrm{gen}}
+
\frac12g_\alpha''(\pi_A)V_{R,A}
\\
&\quad-
g_\alpha'(\pi_C)
C_{C,B}^{\mathrm{gen}}
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

## Raw finite values versus the extension

On the finite event,

\[
\widehat\pi_A=\frac{k}{n}
\]

and

\[
\widehat\pi_C
=
\frac{n k_0+k_Ak_M}{n^2}.
\]

If either value is strictly below 1, its distance from 1 is at least
\(n^{-2}\). Thus the magnitude of the raw finite TESS contrast is
\(O(\log n)\).

The raw finite transform and the bounded extension can differ only when an
estimated probability enters the upper boundary neighborhood. That event has
exponentially small probability, so

\[
E\left[
|\widehat\Delta_S-\widetilde\Delta_S|
I(\mathcal F_{B,n})
\right]
=
o(B^{-1}+n^{-1}).
\]

Since \(P(\mathcal F_{B,n})=1-o(B^{-1}+n^{-1})\), conditioning on
\(\mathcal F_{B,n}\) changes the mean by the same negligible order.

## Corrected corollary

\[
E(
\widehat\Delta_S
\mid
\mathcal F_{B,n}
)
-
\Delta_S
=
\frac{
C_{S,R,B}^{\mathrm{gen}}
}{B}
+
\frac{
C_{S,E}
}{n}
+
o(B^{-1}+n^{-1}).
\]

Moreover,

\[
P(\mathcal F_{B,n}^c)
\le
C\{
e^{-cB}+e^{-cn}
\}.
\]

## Component probability expansions to add

At candidate coincidence,

\[
\pi_A(\theta+u)
=
\pi_A
+
g_A^\top u
+
\frac12u^\top H_A^{\mathrm{sm}}u
+
\sum_{a\in\mathcal A_0}
s_a\kappa_a(d_a^\top u)_+^2
+
o(\|u\|^2),
\]

whereas

\[
\pi_C(\theta+u)
=
\pi_C
+
g_C^\top u
+
\frac12u^\top H_C^{\mathrm{sm}}u
+
\sum_{a\in\mathcal A_0}
\rho(\theta)\kappa_a(d_a^\top u)_+^2
+
o(\|u\|^2).
\]

Their difference recovers

\[
\lambda_a
=
\{s_a-\rho(\theta)\}\kappa_a.
\]

## Cross-term repair

When replacing a random evaluation coefficient
\(D(\widehat\theta_R)\) by \(D(\theta)\), use

\[
E|
D(\widehat\theta_R)-D(\theta)
|
\le
L E\|\widehat\theta_R-\theta\|
=
O(B^{-1/2}),
\]

not merely an \(O_p(B^{-1/2})\) statement. Therefore the induced term is

\[
O(B^{-1/2}n^{-1})
=
o(B^{-1}+n^{-1}).
\]

## Numerical alignment

The locked runner already:

1. leaves boundary records unclipped;
2. records finite, positive-infinite, negative-infinite, and indeterminate
   statuses;
3. computes the scalar mean only from finite records; and
4. treats any nonfinite primary record at the largest pair as formal failure.

Thus the repaired theorem matches the intended finite-status numerical
summary. A deterministic post-run audit should document this alignment before
the repaired manuscript is frozen.
