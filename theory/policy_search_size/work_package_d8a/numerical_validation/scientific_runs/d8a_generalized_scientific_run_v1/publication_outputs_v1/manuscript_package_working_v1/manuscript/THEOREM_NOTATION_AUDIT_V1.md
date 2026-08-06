# Theorem-notation audit for the finite-sample bias manuscript

## Canonical policy notation

The final manuscript should use the following notation consistently.

\[
\Delta_\pi(\theta)
=
P_{AM}(\theta)
-
P_A(\theta)P_M(\theta),
\]

with evaluation estimator

\[
\widehat{\Delta}_\pi
=
\overline{AM}
-
\bar A\bar M.
\]

Conditional on the reference bank,

\[
E_E(
\widehat{\Delta}_\pi
\mid
\widehat{\theta}_R
)
=
\left(1-\frac1n\right)
\Delta_\pi(\widehat{\theta}_R).
\]

This identity generates the exact \(-\Delta_\pi/n\) evaluation term.

---

## Canonical generalized local expansion

For the active coincidence set

\[
\mathcal A_0
=
\{a\in\{0,1\}:q_a=q_2\},
\]

the local expansion is

\[
\begin{aligned}
\Delta_\pi(\theta+u)
&=
\Delta_\pi(\theta)
+
g_\Delta^\top u
+
\frac12
u^\top H_\Delta^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
\lambda_a
(d_a^\top u)_+^2
+
o(\|u\|^2),
\end{aligned}
\]

where

\[
d_a=e_a-e_2,
\qquad
\lambda_a
=
\{s_a-P_A(\theta)\}\kappa_a,
\qquad
s_a=I(c<q_a).
\]

There is **no additional factor \(1/2\)** in front of the positive-part-square sum in the local expansion. The factor \(1/2\) appears after Gaussian expectation because

\[
E(d_a^\top Z)_+^2
=
\frac12 d_a^\top\Sigma_\theta d_a.
\]

---

## Canonical generalized reference coefficient

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\left(
H_\Delta^{\mathrm{sm}}\Sigma_\theta
\right)
\\
&\quad
+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

The combined policy-bias expansion is

\[
E(\widehat{\Delta}_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

The \(B^{-1}n^{-1}\) term is explicit and should not be silently dropped in the displayed principal expansion.

---

## Canonical TESS notation

Define

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)}
\]

and

\[
\Delta_S
=
g_\alpha(\pi_A)
-
g_\alpha(\pi_C).
\]

For \(r\in\{A,C\}\), let \(C_{r,B}^{\mathrm{gen}}\) denote the generalized reference coefficient for \(\pi_r\), and define

\[
V_{R,r}
=
g_{\pi_r}^\top
\Sigma_\theta
g_{\pi_r}.
\]

Then the generalized reference coefficient for the TESS contrast is

\[
\begin{aligned}
C_{S,R,B}^{\mathrm{gen}}
&=
g_\alpha'(\pi_A)
C_{A,B}^{\mathrm{gen}}
+
\frac12
g_\alpha''(\pi_A)
V_{R,A}
\\
&\quad
-
g_\alpha'(\pi_C)
C_{C,B}^{\mathrm{gen}}
-
\frac12
g_\alpha''(\pi_C)
V_{R,C}.
\end{aligned}
\]

The evaluation coefficient is

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

Thus,

\[
E(\widehat{\Delta}_S)-\Delta_S
=
\frac{C_{S,R,B}^{\mathrm{gen}}}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]

The manuscript should not use the generic labels
\(C_{\mathrm{TESS},R}\) and \(C_{\mathrm{TESS},E}\) once the theorem notation is introduced.

---

## Simultaneous constants

Two distinct simultaneous constants must not be conflated.

1. **Residual-adjustment constant**
   \[
   z_{\mathrm{sim}}
   =
   4.2372795825947795.
   \]

2. **Exact-identity Bonferroni boundary**
   \[
   z_{\mathrm{id}}
   =
   3.8509780194087373.
   \]

Use \(z_{\mathrm{sim}}\) in the MCSE-adjusted normalized residual and
\(z_{\mathrm{id}}\) in the 85 exact finite-\(n\) checks.

---

## Scope language required in the manuscript

The validated policy theorem assumes:

- fixed base and full candidate pools \(\{0,1\}\subset\{0,1,2\}\);
- almost-surely unique winners;
- strict candidate-trigger threshold separation;
- active candidate coincidences only at \(q_0=q_2\) and \(q_1=q_2\);
- twice differentiable smooth terms with dominated derivatives;
- fixed-dimensional reference-threshold estimation;
- independent reference and evaluation banks.

The manuscript should not silently broaden this to arbitrary adaptive machine-learning pipelines, growing candidate dimension, discrete ties, or failed-fit fallback rules.

---

## Corrections to draft v1

1. Keep the Figure 1 positive-part-square sum without an extra \(1/2\).
2. Define \(\mathcal A_0\) explicitly rather than only calling it an active set.
3. Replace generic TESS coefficient names by
   \(C_{S,R,B}^{\mathrm{gen}}\) and \(C_{S,E}\).
4. Define \(\Delta_\pi\), \(\widehat\Delta_\pi\), and \(\Delta_S\) before the validation section.
5. Distinguish \(z_{\mathrm{sim}}\) from \(z_{\mathrm{id}}\).
6. State the finite three-candidate theorem scope explicitly.
