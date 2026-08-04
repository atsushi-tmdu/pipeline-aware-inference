# D8-A Gaussian Hessian Preflight

**Status:** runtime-only mathematical diagnostic; not scientific evidence

For the correlated-Gaussian indicator model

\[
\Delta(q,c)
=
\operatorname{Cov}\{I(Y>c),I(X>q)\},
\]

the preflight compares analytic and finite-difference values of

\[
\partial_{qq}^2\Delta,
\qquad
\partial_{qc}^2\Delta,
\qquad
\partial_{cc}^2\Delta.
\]

The underlying covariance is evaluated using deterministic
one-dimensional Gaussian quadrature.

The test also checks:

- symmetry of the analytic Hessian;
- equality of the two mixed-partial finite differences;
- zero mixed curvature under independence;
- positive local threshold-ordering radius under separation.

This is a consistency check for the proof architecture, not a proof of the
general winner-cell theorem.
