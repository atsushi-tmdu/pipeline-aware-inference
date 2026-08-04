# Theorem D8-A.2: Joint Empirical-Quantile Moment Expansion

## Statement

For fixed \(d<\infty\), let the complete reference vector generate component
variables

\[
Y_\ell=g_\ell(W),
\qquad
\ell=1,\ldots,d.
\]

Assume every component satisfies the assumptions of Lemmas D8-A.2a,
D8-A.2d, and D8-A.2e, with a common moment exponent \(r>2\).

Then

\[
E(\widehat\theta-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

and

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
\frac{
P(Y_\ell\le\theta_\ell,\,
Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)f_m(\theta_m)
}.
\]

Moreover, for some \(\eta>0\),

\[
\sup_B
E\left\|
\sqrt B(\widehat\theta-\theta)
\right\|^{2+\eta}
<
\infty.
\]

## Proof

The mean expansion holds componentwise by Lemma D8-A.2a.

Lemma D8-A.2e gives the component \(L^2\) Bahadur remainders. Since the
dimension is fixed,

\[
B\,E\|r_B\|^2
=
B\sum_{\ell=1}^dE(r_{B,\ell}^2)
\longrightarrow0.
\]

Lemma D8-A.2b then yields the joint second-moment expansion and the
complete-vector covariance formula.

Finally, Proposition D8-A.2c reduces the vector \(2+\eta\) moment bound to the
component bounds supplied by Lemma D8-A.2d.

## Consequence

The joint empirical-quantile moment theorem required by the D8-A
expectation-level delta expansion is now complete under the stated
assumptions.

The general policy-map \(C^2\) theorem remains open.
