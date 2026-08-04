# Lemma D8-A.R2: Generic Moving-Max Cell Expansion

## Setup

Let

\[
U(a,q)
=
\int_{-\infty}^{a}
H\{w,\max(w,q)\}\,dw,
\]

where \(H(w,s)\) is twice continuously differentiable near \((t,t)\), its
required derivatives are locally dominated, and the integrals below are
finite.

This form is obtained from a base-winner/full-winner cell after integrating
out the losing base coordinate and the added-candidate upper tail.

Define

\[
A_s(t)
=
\int_{-\infty}^{t}
\partial_s H(w,t)\,dw
\]

and

\[
A_{ss}(t)
=
\int_{-\infty}^{t}
\partial_{ss} H(w,t)\,dw.
\]

## Result

At the coincidence point \(a=q=t\), for local increments \(u,v\),

\[
\begin{aligned}
U(t+u,t+v)
&=
U(t,t)
+
H(t,t)u
+
A_s(t)v
\\
&\quad
+
\frac12
\left[
H_w(t,t)u^2
+
2H_s(t,t)uv
+
A_{ss}(t)v^2
\right]
\\
&\quad
+
\frac12H_s(t,t)(u-v)_+^2
+
o(u^2+v^2).
\end{aligned}
\]

## Proof

On the cone \(u\le v\),

\[
U(t+u,t+v)
=
\int_{-\infty}^{t+u}
H(w,t+v)\,dw.
\]

Ordinary two-variable Taylor expansion under the integral gives the displayed
formula without the positive-part term.

On the cone \(u>v\),

\[
\begin{aligned}
U(t+u,t+v)
&=
\int_{-\infty}^{t+v}
H(w,t+v)\,dw
\\
&\quad+
\int_{t+v}^{t+u}
H(w,w)\,dw.
\end{aligned}
\]

Taylor expansion of both integrals gives the same base polynomial plus

\[
\frac12H_s(t,t)(u-v)^2.
\]

Combining the two cones yields the positive-part-square representation.
Continuity on \(u=v\) is immediate. The dominated derivative assumptions give
a remainder uniform over directions in compact sets.

## Consequence

Ordinary \(C^2\) differentiability is replaced by a continuous,
degree-two, piecewise quadratic second-order map.
