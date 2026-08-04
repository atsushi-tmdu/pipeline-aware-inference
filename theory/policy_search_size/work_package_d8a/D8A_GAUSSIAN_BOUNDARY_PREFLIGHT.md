# D8-A Correlated-Gaussian Boundary-Derivative Preflight

**Status:** runtime-only mathematical diagnostic; not scientific evidence

Let

\[
M_q=I(X>q),
\qquad
A_c=I(Y>c),
\]

where \((X,Y)\) is standard bivariate normal with correlation \(r\). Define

\[
\Delta(q,c)
=
\operatorname{Cov}(A_c,M_q).
\]

For the candidate boundary, increasing \(q\) turns \(M_q\) off, so the jump is
\(D=-1\). Therefore,

\[
\beta_q
=
P(Y>c)-P(Y>c\mid X=q)
\]

and

\[
\partial_q\Delta
=
\phi(q)\beta_q.
\]

For the trigger boundary,

\[
\beta_c
=
P(X>q)-P(X>q\mid Y=c)
\]

and

\[
\partial_c\Delta
=
\phi(c)\beta_c.
\]

The mixed derivative is

\[
\partial_{qc}^2\Delta
=
\phi(q)
\left[
f_{Y\mid X=q}(c)-\phi(c)
\right],
\]

which is generally nonzero when \(r\ne0\).

The covariance itself is evaluated by deterministic one-dimensional Gaussian quadrature,
rather than the randomized multivariate-normal CDF integrator. The preflight then
verifies these identities by finite differences. It does not prove the D8-A
winner-cell smoothness theorem.
