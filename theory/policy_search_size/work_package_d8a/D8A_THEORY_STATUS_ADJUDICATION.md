# D8-A Theory Status Adjudication

## Established

- The exact conditional evaluation identity

\[
E_E(\widehat\Delta_\pi\mid\widehat\theta)
=
(1-n^{-1})\Delta_\pi(\widehat\theta)
\]

is exact.

- The scalar order-statistic lattice coefficient follows from the beta
  distribution of the transformed order statistic, subject to the stated
  inverse-CDF remainder conditions.

- The candidate-trigger covariance formula is the covariance of the joint
  first-order quantile influence vector.

## Prospective, not yet proved

- The full joint quantile mean expansion with a uniform remainder.
- The required \(2+\eta\) moment bound.
- Twice continuous differentiability of the D7 policy map.
- The final \(C_{R,B}/B\) policy-bias theorem.
- The TESS second-order corollary.

## Correction to the initial scaffold

D8-A no longer assumes a deterministic second-order stochastic expansion.
It uses weaker expectation and covariance expansions plus Taylor-remainder
control.

## Numerical status

- scientific design locked: no;
- scientific simulation run: no;
- D7 formal status changed: no.

## Regular-regime gradient link

Under the stated boundary-differentiation conditions, the D7 coefficients
satisfy

\[
\partial_{q_j}\Delta_\pi=f_j(q_j)\beta_j^\Delta,
\qquad
\partial_c\Delta_\pi=f_T(c)\beta_c^\Delta.
\]

This establishes consistency between the D7 reference influence function and
the gradient entering D8-A.

The full twice-continuous-differentiability theorem remains prospective.

## Winner-cell and second-derivative scaffold

The D8-A regular policy map has now been represented as a finite sum of
winner-cell integrals with locally fixed threshold ordering.

Proposed sufficient conditions D8A-S1--S7 identify the regularity needed for
twice continuous differentiability.

The correlated-Gaussian Hessian preflight verifies all three Hessian entries
and mixed-partial symmetry, but the general moving-boundary proof remains
prospective.
