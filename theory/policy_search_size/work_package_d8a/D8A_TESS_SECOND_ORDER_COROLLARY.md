# Corollary D8-A.5: Second-Order TESS Bias

## Setup

Let

\[
g_\alpha(x)
=
\frac{\log(1-x)}
{\log(1-\alpha)}
\]

and

\[
\Delta_S
=
g_\alpha(\pi_A)
-
g_\alpha(\pi_C),
\]

where

\[
\pi_A=E(H)
\]

is the adaptive rejection probability and

\[
\pi_C=e_0+\rho\mu
\]

is the budget-matched comparator probability.

Assume \(\pi_A\) and \(\pi_C\) lie in a compact subset of \([0,1)\).

For \(r\in\{A,C\}\), define

\[
C_{r,B}
=
\nabla\pi_r(\theta)^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{
H_{\pi_r}(\theta)
\Sigma_\theta
\},
\]

and

\[
V_{R,r}
=
\nabla\pi_r(\theta)^\top
\Sigma_\theta
\nabla\pi_r(\theta).
\]

For the evaluation bank, define

\[
\zeta_A
=
H-\pi_A
\]

and

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

## Result

Let

\[
C_{S,R,B}
=
g_\alpha'(\pi_A)C_{A,B}
+
\frac12
g_\alpha''(\pi_A)V_{R,A}
-
g_\alpha'(\pi_C)C_{C,B}
-
\frac12
g_\alpha''(\pi_C)V_{R,C},
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

Then

\[
E(\widehat\Delta_S)-\Delta_S
=
\frac{C_{S,R,B}}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]

## Proof

### Reference contribution

Apply Lemma D8-A.4a to the smooth compositions

\[
g_\alpha\circ\pi_A
\]

and

\[
g_\alpha\circ\pi_C.
\]

The chain-rule Hessian gives, respectively,

\[
g_\alpha'(\pi_r)C_{r,B}
+
\frac12
g_\alpha''(\pi_r)V_{R,r}.
\]

Subtracting comparator from adaptive yields \(C_{S,R,B}\).

### Evaluation contribution

Conditional on the reference bank,

\[
E_E(\widehat\pi_A)
=
\pi_A(\widehat\theta_R).
\]

For the comparator estimator,

\[
\widehat\pi_C
=
\bar R_0+\bar A\bar M,
\]

and the exact conditional mean is

\[
E_E(\widehat\pi_C)
=
\pi_C(\widehat\theta_R)
+
\frac{
\Delta_\pi(\widehat\theta_R)
}{n}.
\]

The first-order evaluation influence functions are
\(\zeta_A\) and \(\zeta_C\). A scalar second-order delta expansion gives the
adaptive curvature term

\[
\frac12
g_\alpha''(\pi_A)V_{E,A}
\]

and the comparator contribution

\[
g_\alpha'(\pi_C)\Delta_\pi
+
\frac12
g_\alpha''(\pi_C)V_{E,C}.
\]

The comparator is subtracted, producing \(C_{S,E}\).

Reference-evaluation interaction terms are
\(o(B^{-1}+n^{-1})\).

## Scientific interpretation

The TESS bias separates into:

1. reference centering and reference curvature;
2. exact comparator-product centering at order \(n^{-1}\);
3. adaptive and comparator evaluation curvature.

This formalizes the centering-versus-Jensen decomposition observed in D7.
