# D8-A Coincidence-Gap Checkpoint

**Gap status:** confirmed
**Scientific execution:** blocked
**Scientific simulation run:** no

## Confirmed counterexample

For the independent-Gaussian winner-cell contribution

\[
U(a,q)
=
\int_{-\infty}^{a}
\phi(w)\Phi(w)
\overline\Phi\{\max(w,q)\}\,dw,
\]

the one-sided mixed derivatives at \(a=q=t\) are

\[
\partial_q^-\partial_a U(t,t)=0
\]

and

\[
\partial_q^+\partial_a U(t,t)
=
-\phi(t)^2\Phi(t).
\]

Thus ordinary twice continuous differentiability fails at the candidate
winner/threshold coincidence.

## Proven repair component

The same cell admits the local expansion

\[
\begin{aligned}
U(t+u,t+v)
&=
U(t,t)
+
F(t)G(t)u
+
A(t)G'(t)v
\\
&\quad
+
\frac12
\left[
G(t)F'(t)u^2
+
2F(t)G'(t)uv
+
A(t)G''(t)v^2
\right]
\\
&\quad
+
\frac12F(t)G'(t)(u-v)_+^2
+
o(u^2+v^2).
\end{aligned}
\]

The positive-part-square term is the missing second-order correction.

## Current adjudication

- `d8a-theory-complete-v1` is retained as an immutable historical checkpoint.
- Its completeness claim is superseded at candidate-threshold coincidence.
- `d8a-numerical-design-lock-v1` is retained as an immutable design record.
- Scientific execution under that design is blocked.
- The smooth-stratum quantile and policy results remain valid.
- The full finite-cone generalized policy theorem is not yet proved.

## Next proof target

Construct a continuous degree-two piecewise quadratic map \(Q_\theta\) over
the finite threshold-order cone arrangement and prove

\[
\Delta_\pi(\theta+u)
=
\Delta_\pi(\theta)
+
g^\top u
+
Q_\theta(u)
+
o(\|u\|^2).
\]
