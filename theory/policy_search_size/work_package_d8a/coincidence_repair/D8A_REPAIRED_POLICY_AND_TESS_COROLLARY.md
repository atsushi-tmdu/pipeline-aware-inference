# Corollary D8-A.R6: Repaired Policy and TESS Bias

## Policy

The exact conditional evaluation identity remains

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

Therefore,

\[
\begin{aligned}
E(\widehat\Delta_\pi)-\Delta_\pi
&=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{Bn}
\\
&\quad
+
o(B^{-1}+n^{-1}).
\end{aligned}
\]

## Smooth composition

If a probability map \(\pi(\theta)\) has generalized coefficient

\[
C_{\pi,B}^{\mathrm{gen}}
=
g_\pi^\top b_{\theta,B}
+
E\{Q_\pi(Z)\},
\]

then for a twice continuously differentiable scalar transform \(h\),

\[
C_{h\circ\pi,B}^{\mathrm{gen}}
=
h'(\pi)
C_{\pi,B}^{\mathrm{gen}}
+
\frac12
h''(\pi)
g_\pi^\top
\Sigma_\theta
g_\pi.
\]

## TESS

For

\[
g_\alpha(x)
=
\frac{\log(1-x)}
{\log(1-\alpha)},
\]

replace the earlier ordinary-Hessian reference coefficients by the
generalized coefficients for \(\pi_A\) and \(\pi_C\).

The evaluation-bank coefficient is unchanged. Thus

\[
E(\widehat\Delta_S)-\Delta_S
=
\frac{
C_{S,R,B}^{\mathrm{gen}}
}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]
