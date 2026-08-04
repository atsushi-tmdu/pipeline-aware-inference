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

## Scalar quantile mean lemma

Lemma D8-A.2a is now established under explicit local smoothness,
third-derivative, and tail-integrability assumptions.

It proves the scalar \(B^{-1}\) mean expansion with the exact lattice term.
The full joint quantile lemma remains incomplete.

## Joint quantile second-moment lifting

Lemma D8-A.2b is established conditional on a joint \(L^2\) Bahadur
remainder. It yields the complete-vector covariance matrix
\(\Sigma_\theta\).

Proposition D8-A.2c reduces the vector \(2+\eta\) moment condition to scalar
component bounds in fixed dimension.

The primitive Bahadur-remainder and scalar-tail proofs remain open, so the
full joint quantile lemma is not yet closed.

## Primitive Bahadur and full joint quantile theorem

Lemma D8-A.2d establishes a scalar uniform \(2+\eta\) quantile moment bound
from a local density lower bound and a finite higher moment.

Lemma D8-A.2e upgrades scalar asymptotic linearity to an \(L^2\) Bahadur
remainder.

Theorem D8-A.2 combines these results with the scalar mean lemma and joint
lifting lemma. The full joint empirical-quantile moment theorem is now
established under the stated assumptions.

The remaining central gap is the general policy-map \(C^2\) theorem.

## Regular policy-map \(C^2\) theorem

Lemma D8-A.3a proves coordinate moving-face differentiation under explicit
one- and two-face trace regularity.

Theorem D8-A.3 proves that the separated continuous policy contrast is
twice continuously differentiable under fixed finite pools, continuous
unique winners, strict threshold separation, and those trace assumptions.

The remaining tasks are the final policy-bias theorem and the TESS
second-order corollary.

## Final second-order theory

Lemma D8-A.4a establishes the expectation-level second-order delta method.

Theorem D8-A.4 combines the full joint quantile theorem, the regular
policy-map \(C^2\) theorem, and the exact evaluation identity.

Corollary D8-A.5 gives the TESS second-order bias decomposition into
reference centering, reference curvature, exact comparator-product
centering, and evaluation curvature.

D8-A theory is complete under its stated assumptions. Numerical validation
has not yet been designed or run.
