# D8-A Generalized-Theory Repair Checkpoint

**Generalized theory status:** proved under stated assumptions
**Historical numerical design re-adjudicated:** no
**Scientific execution:** blocked
**Scientific simulation run:** no

## Repaired local structure

At candidate-threshold coincidence, ordinary \(C^2\) differentiability is
replaced by a continuous degree-two piecewise quadratic expansion over the
finite threshold-order cone arrangement.

For the three-candidate policy, the only active candidate coincidence
hyperplanes are

\[
q_0=q_2
\qquad\text{and}\qquad
q_1=q_2.
\]

The policy expansion is

\[
\begin{aligned}
\Delta_\pi(\theta+u)
&=
\Delta_\pi(\theta)
+
g_\Delta^\top u
+
\frac12u^\top H_\Delta^{\mathrm{sm}}u
\\
&\quad+
\sum_{a:q_a=q_2}
\lambda_a(u_a-u_2)_+^2
+
o(\|u\|^2).
\end{aligned}
\]

## Repaired expectation coefficient

For the centered Gaussian threshold limit
\(Z\sim N(0,\Sigma_\theta)\),

\[
E(d_a^\top Z)_+^2
=
\frac12d_a^\top\Sigma_\theta d_a.
\]

Therefore,

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12\operatorname{tr}
\{H_\Delta^{\mathrm{sm}}\Sigma_\theta\}
\\
&\quad+
\frac12
\sum_{a:q_a=q_2}
\lambda_a
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

## Repaired finite-sample conclusions

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

The TESS reference coefficient is repaired using the generalized smooth
composition rule. The evaluation-bank coefficient is unchanged.

## Current boundary

The generalized theory is complete under its stated assumptions. The locked
75-cell numerical design has not yet been re-adjudicated, and scientific
simulation remains blocked.
