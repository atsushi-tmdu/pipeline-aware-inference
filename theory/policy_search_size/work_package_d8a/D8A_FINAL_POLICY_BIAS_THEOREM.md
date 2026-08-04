# Theorem D8-A.4: Second-Order Finite-Reference Policy Bias

## Statement

Assume the joint empirical-quantile moment theorem D8-A.2 and the regular
policy-map \(C^2\) theorem D8-A.3.

Let

\[
\theta=(q_1,\ldots,q_K,c)
\]

and define

\[
C_{\Delta,B}
=
\nabla\Delta_\pi(\theta)^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{
H_{\Delta_\pi}(\theta)
\Sigma_\theta
\}.
\]

Let the evaluation estimator be

\[
\widehat\Delta_\pi
=
\overline{AM}
-
\bar A\bar M.
\]

As \(B,n\to\infty\),

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

In particular,

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}}{B}
-
\frac{\Delta_\pi}{n}
+
o(B^{-1}+n^{-1}).
\]

## Proof

Lemma D8-A.4a applied to
\(h=\Delta_\pi\) gives

\[
E_R\{
\Delta_\pi(\widehat\theta_R)
\}
=
\Delta_\pi(\theta)
+
\frac{C_{\Delta,B}}{B}
+
o(B^{-1}).
\]

Conditional on the reference bank, the exact evaluation identity is

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

Taking reference expectation,

\[
\begin{aligned}
E(\widehat\Delta_\pi)
&=
\left(1-\frac1n\right)
\left[
\Delta_\pi
+
\frac{C_{\Delta,B}}{B}
+
o(B^{-1})
\right].
\end{aligned}
\]

Subtracting \(\Delta_\pi\) yields the stated expansion.

## Interpretation

The \(B^{-1}\) term is reference-threshold centering and curvature bias. The
\(-\Delta_\pi/n\) term is the exact divisor-\(n\) covariance bias. The
\(B^{-1}n^{-1}\) term is an explicit interaction.
