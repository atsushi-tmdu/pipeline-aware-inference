# Theorem D8-A.R5: Generalized Second-Order Expectation Expansion

Assume

\[
E(\widehat\theta-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

\[
\sqrt B(\widehat\theta-\theta)
\Rightarrow
Z\sim N(0,\Sigma_\theta),
\]

and the existing uniform \(2+\eta\) moment bound.

Suppose the policy has the generalized expansion of Theorem D8-A.R4. Then

\[
E\{\Delta_\pi(\widehat\theta)\}
=
\Delta_\pi(\theta)
+
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
+
o(B^{-1}),
\]

where

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{
H_\Delta^{\mathrm{sm}}\Sigma_\theta
\}
\\
&\quad
+
\frac12
\sum_{a:\,q_a=q_2}
\lambda_a
d_a^\top\Sigma_\theta d_a,
\end{aligned}
\]

and

\[
d_a=e_a-e_2.
\]

## Proof

Apply the generalized expansion to
\(u=\widehat\theta-\theta\), multiply by \(B\), and use the uniform
\(2+\eta\) moment bound to obtain uniform integrability of every degree-two
term.

The smooth quadratic expectation converges to the trace term. For each kink,

\[
E(d_a^\top Z)_+^2
=
\frac12
d_a^\top\Sigma_\theta d_a
\]

because \(d_a^\top Z\) is centered Gaussian.

The uniform cone-wise remainder is \(o(B^{-1})\) in expectation.
