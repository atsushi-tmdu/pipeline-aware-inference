# D8-A Joint Empirical-Quantile Expansion Memo

## Status

Prospective derivation memo. No D8-A theory lock has been created.

## Exact convention

D7 and D8-A use

\[
\widehat q_{p,B}=Y_{(k_B)},
\qquad
k_B=\lceil Bp\rceil.
\]

Let \(q_p=F^{-1}(p)\) and define

\[
a_{p,B}=k_B-(B+1)p.
\]

Because

\[
F\{Y_{(k_B)}\}
\sim
\operatorname{Beta}(k_B,B+1-k_B),
\]

an inverse-CDF Taylor expansion yields

\[
E(\widehat q_{p,B})-q_p
=
\frac{b_{p,B}}{B}
+
o(B^{-1}),
\]

where

\[
b_{p,B}
=
\frac{a_{p,B}}{f(q_p)}
-
\frac{p(1-p)f'(q_p)}
{2f(q_p)^3}.
\]

## Lattice nonconvergence

The bounded offset \(a_{p,B}\) need not converge. For example,

\[
a_{0.37,100}=-0.37,
\qquad
a_{0.37,101}=0.26.
\]

Therefore, without an extra subsequence or quantile-convention assumption,
the correct unrestricted coefficient is \(B\)-dependent.

For the D7 candidate grid,

\[
p\in\{0.99,0.95,0.90\},
\qquad
B\in\{1000,3000,5000\},
\]

every \(Bp\) is an integer, so

\[
a_{p,B}=-p
\]

throughout the locked candidate-threshold grid. Trigger probabilities need
not share this alignment.

## Joint first-order covariance

For threshold components based on complete-vector functions \(Y_\ell\),

\[
\psi_\ell(Y)
=
\frac{p_\ell-I(Y_\ell\le\theta_\ell)}
{f_\ell(\theta_\ell)}.
\]

Hence,

\[
\Sigma_{\theta,\ell m}
=
\frac{
P(Y_\ell\le\theta_\ell,\,
  Y_m\le\theta_m)-p_\ell p_m
}{
f_\ell(\theta_\ell)f_m(\theta_m)
}.
\]

This retains candidate-candidate and candidate-trigger dependence within each
complete reference vector.

## Policy-map expansion

Let

\[
b_{\theta,B}
=
(b_{1,B},\ldots,b_{K+1,B})^\top.
\]

Then the prospective regular-policy expansion is

\[
E_R\{\Delta(\widehat\theta)\}
=
\Delta(\theta)
+
\frac{C_{R,B}}{B}
+
o(B^{-1}),
\]

with

\[
C_{R,B}
=
\nabla\Delta(\theta)^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{H_\Delta(\theta)\Sigma_\theta\}.
\]

Combining this with the exact evaluation identity gives

\[
E(\widehat\Delta)-\Delta
=
\frac{C_{R,B}}{B}
-
\frac{\Delta}{n}
-
\frac{C_{R,B}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

## Proof obligations

Before the joint quantile lemma is called proved, D8-A must supply:

1. inverse-CDF remainder control;
2. a joint complete-vector quantile expansion;
3. moment control sufficient for taking expectations;
4. the base-maximum density and density derivative;
5. an explicit lattice-stabilized corollary when a constant coefficient is
   desired.
