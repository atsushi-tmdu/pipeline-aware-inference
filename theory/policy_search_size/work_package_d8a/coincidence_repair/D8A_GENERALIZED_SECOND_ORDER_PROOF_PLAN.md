# D8-A Generalized Coincidence Repair Plan

## Target local form

For threshold increment \(u\),

\[
\Delta_\pi(\theta+u)
=
\Delta_\pi(\theta)
+
g^\top u
+
Q_\theta(u)
+
o(\|u\|^2),
\]

where \(Q_\theta\) is continuous, positively homogeneous of degree two, and
piecewise quadratic over the finite arrangement of threshold-order cones.

Away from coincidence,

\[
Q_\theta(u)
=
\frac12u^\top H_{\Delta_\pi}u.
\]

At coincidence, \(Q_\theta\) additionally contains terms such as

\[
\kappa_{jk}(u_j-u_k)_+^2.
\]

## Expectation theorem target

If

\[
\sqrt B(\widehat\theta-\theta)
\Rightarrow Z
\]

and the existing \(2+\eta\) moment bound holds, then

\[
E\{\Delta_\pi(\widehat\theta)\}
=
\Delta_\pi(\theta)
+
\frac{
g^\top b_{\theta,B}
+
E\{Q_\theta(Z)\}
}{B}
+
o(B^{-1}).
\]

For Gaussian \(Z\), each single positive-part-square term has a closed-form
expectation.

## Required proof steps

1. enumerate every winner-cell logical form;
2. identify all active threshold-order hyperplanes;
3. derive each cone-specific quadratic polynomial;
4. prove continuity and a uniform second-order remainder across cones;
5. combine cells into the policy contrast;
6. derive the generalized TESS composition rule;
7. repair the numerical oracle and acceptance coefficients.

## Current status

The explicit one-cell coincidence lemma is proved.

The complete finite-cone policy theorem is not yet proved.
