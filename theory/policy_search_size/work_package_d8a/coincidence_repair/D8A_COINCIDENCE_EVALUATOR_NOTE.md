# D8-A Coincidence Evaluator Note

The winner-cell probability

\[
U(a,q)
=
\int_{-\infty}^{a}
\phi(w)\Phi(w)
\overline\Phi\{\max(w,q)\}\,dw
\]

is evaluated in closed form.

If \(a\le q\),

\[
U(a,q)
=
\frac12\Phi(a)^2\overline\Phi(q).
\]

If \(a>q\),

\[
U(a,q)
=
\frac12\Phi(q)^2\overline\Phi(q)
+
J\{\Phi(a)\}
-
J\{\Phi(q)\},
\]

where

\[
J(y)
=
\frac12y^2-\frac13y^3.
\]

This avoids adaptive-quadrature error when \(a-q\) is very small. The earlier
test failure was caused by numerical integration across the moving
\(\max(w,q)\) kink, not by the piecewise quadratic formula.
