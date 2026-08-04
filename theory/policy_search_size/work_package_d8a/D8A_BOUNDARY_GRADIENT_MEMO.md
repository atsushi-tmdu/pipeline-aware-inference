# D8-A Boundary Gradient and D7 Influence-Coefficient Link

## Status

Regular-regime first-derivative identity. The full twice-differentiable
policy-map theorem remains unproved.

## 1. Candidate-threshold derivative

Let \(D_j\) be the D7 candidate jump field. Under strict threshold separation,
unique winners, positive candidate density, and valid boundary
differentiation,

\[
\frac{\partial}{\partial q_j}
\Delta_\pi(\theta)
=
f_j(q_j)
E\left[
(A-\rho)D_j
\mid X_j=q_j
\right].
\]

Define

\[
\beta_j^\Delta
=
E\left[
(A-\rho)D_j
\mid X_j=q_j
\right].
\]

Then

\[
\partial_{q_j}\Delta_\pi
=
f_j(q_j)\beta_j^\Delta.
\]

Because the empirical-quantile influence function is

\[
\frac{p_j-I(X_j\le q_j)}
{f_j(q_j)},
\]

the reference influence contribution is

\[
\frac{\partial_{q_j}\Delta_\pi}
{f_j(q_j)}
\{p_j-I(X_j\le q_j)\}
=
\beta_j^\Delta
\{p_j-I(X_j\le q_j)\}.
\]

Thus the D7 candidate reference-IF coefficient is the policy gradient divided
by the candidate boundary density.

## 2. Trigger-threshold derivative

Since \(A=I(T>c)\) and \(M\) does not depend directly on \(c\),

\[
\frac{\partial}{\partial c}E(AM)
=
-f_T(c)E(M\mid T=c)
\]

and

\[
\frac{\partial\rho}{\partial c}
=
-f_T(c).
\]

Therefore,

\[
\frac{\partial}{\partial c}\Delta_\pi
=
f_T(c)
\left\{
\mu-E(M\mid T=c)
\right\}.
\]

With

\[
\beta_c^\Delta
=
\mu-E(M\mid T=c),
\]

we obtain

\[
\partial_c\Delta_\pi
=
f_T(c)\beta_c^\Delta.
\]

Again, the D7 reference-IF coefficient is the policy gradient divided by the
maximum boundary density.

## 3. Consequence for D8-A

Let

\[
g_\theta
=
\nabla\Delta_\pi(\theta).
\]

The gradient components in the second-order coefficient satisfy

\[
g_{\theta,\ell}
=
f_\ell(\theta_\ell)\beta_\ell^\Delta.
\]

Hence the linear second-order term can be written equivalently as

\[
\nabla\Delta_\pi(\theta)^\top b_{\theta,B}
=
\sum_\ell
f_\ell(\theta_\ell)
\beta_\ell^\Delta
b_{\ell,B}.
\]

This makes the connection between the D7 first-order theory and the D8-A
second-order bias explicit.

## 4. Candidate-trigger mixed curvature

The mixed derivative

\[
\partial_{q_jc}^2\Delta_\pi
\]

is generally nonzero because the trigger threshold changes the
activation-weighted candidate jump field and the candidate threshold changes
the incremental field along the trigger boundary.

Therefore the Hessian-covariance contraction must retain

\[
H_{qc}^\top\Sigma_{qc}.
\]

## 5. Remaining proof obligation

The formulas above require a justified boundary-differentiation theorem for
the actual winner-cell integrals. D8-A still needs:

- a local winner-cell integral representation;
- dominated first and second boundary derivatives;
- control of codimension-two boundary intersections;
- continuity of the resulting gradient and Hessian.

These tasks are not replaced by the numerical preflight.
