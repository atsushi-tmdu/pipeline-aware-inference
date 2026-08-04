# Lemma D8-A.2b: Joint Quantile Second-Moment Lifting

## Statement

Let \(W_1,\ldots,W_B\) be iid complete reference vectors. For fixed
\(d<\infty\), let

\[
Y_{i\ell}=g_\ell(W_i),
\qquad
\ell=1,\ldots,d,
\]

with marginal probability \(p_\ell\), quantile

\[
\theta_\ell
=
F_\ell^{-1}(p_\ell),
\]

and positive density \(f_\ell(\theta_\ell)\).

Define

\[
\psi_\ell(W)
=
\frac{
p_\ell-I(Y_\ell\le\theta_\ell)
}{
f_\ell(\theta_\ell)
},
\qquad
\psi(W)
=
(\psi_1(W),\ldots,\psi_d(W))^\top.
\]

Assume the component quantiles use the declared generalized-inverse
order-statistic convention and satisfy the joint \(L^2\) Bahadur
representation

\[
\widehat\theta-\theta
=
\frac1B\sum_{i=1}^B\psi(W_i)
+
r_B,
\]

with

\[
B\,E\|r_B\|^2
\longrightarrow0.
\]

Then

\[
B\,E\left[
(\widehat\theta-\theta)
(\widehat\theta-\theta)^\top
\right]
=
\Sigma_\theta+o(1),
\]

where

\[
\Sigma_{\theta,\ell m}
=
E\{\psi_\ell(W)\psi_m(W)\}
=
\frac{
P(Y_\ell\le\theta_\ell,\,
  Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)f_m(\theta_m)
}.
\]

Together with the scalar mean expansions from Lemma D8-A.2a,

\[
E(\widehat\theta-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1})
\]

componentwise.

## Proof

Write

\[
L_B
=
\frac1B\sum_{i=1}^B\psi(W_i).
\]

Because \(E\{\psi(W)\}=0\),

\[
E(L_B)=0
\]

and independence gives

\[
B\,E(L_BL_B^\top)
=
E\{\psi(W)\psi(W)^\top\}
=
\Sigma_\theta.
\]

Now,

\[
\widehat\theta-\theta
=
L_B+r_B.
\]

For components \(\ell,m\),

\[
\begin{aligned}
&B\left|
E\left[
(\widehat\theta_\ell-\theta_\ell)
(\widehat\theta_m-\theta_m)
\right]
-
E(L_{B,\ell}L_{B,m})
\right|
\\
&\le
B|E(L_{B,\ell}r_{B,m})|
+
B|E(L_{B,m}r_{B,\ell})|
+
B|E(r_{B,\ell}r_{B,m})|.
\end{aligned}
\]

By Cauchy--Schwarz,

\[
B|E(L_{B,\ell}r_{B,m})|
\le
\sqrt{\Sigma_{\theta,\ell\ell}}
\sqrt{B\,E(r_{B,m}^2)}
\longrightarrow0.
\]

The symmetric cross term is identical, and

\[
B|E(r_{B,\ell}r_{B,m})|
\le
\sqrt{B\,E(r_{B,\ell}^2)}
\sqrt{B\,E(r_{B,m}^2)}
\longrightarrow0.
\]

Hence every matrix entry converges to the corresponding entry of
\(\Sigma_\theta\). Since \(d\) is fixed, entrywise and matrix convergence are
equivalent.

The componentwise mean expansion is supplied by Lemma D8-A.2a.

## Complete-vector dependence

The covariance is generally nonzero because all threshold components are
calculated from the same complete reference vectors. In D8-A, the component
functions include candidate scores and the base maximum, so the formula
retains candidate-trigger dependence.

## Scope

This lemma is conditional on the joint \(L^2\) Bahadur remainder. Establishing
that remainder under the final primitive smoothness and tail assumptions is a
separate proof obligation.
