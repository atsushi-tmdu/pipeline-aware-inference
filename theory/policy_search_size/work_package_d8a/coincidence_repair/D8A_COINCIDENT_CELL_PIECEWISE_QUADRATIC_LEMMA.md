# Lemma D8-A.R1: Coincident Winner/Threshold Cell Expansion

## Cell

Consider the independent-Gaussian winner-cell contribution

\[
U(a,q)
=
\int_{-\infty}^{a}
\phi(w)\Phi(w)
\overline\Phi\{\max(w,q)\}\,dw.
\]

This term arises when a base winner is rejected at threshold \(a\), while an
added candidate must exceed both the winner score \(w\) and its own threshold
\(q\).

Let

\[
F(w)=\phi(w)\Phi(w),
\qquad
G(w)=\overline\Phi(w),
\qquad
A(t)=\int_{-\infty}^{t}F(w)\,dw.
\]

## Non-\(C^2\) point

At \(a=q=t\),

\[
\partial_a U(a,q)
=
F(a)G\{\max(a,q)\}.
\]

Therefore,

\[
\partial_q^-\partial_a U(t,t)=0,
\]

while

\[
\partial_q^+\partial_a U(t,t)
=
F(t)G'(t)
=
-\phi(t)^2\Phi(t).
\]

The ordinary mixed derivative is discontinuous.

## Piecewise quadratic expansion

For local increments \(u=a-t\) and \(v=q-t\),

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

The final term is the missing coincidence correction.

## Gaussian expectation

If

\[
\sqrt B
\begin{pmatrix}
\widehat a-a\\
\widehat q-q
\end{pmatrix}
\Rightarrow
\begin{pmatrix}Z_a\\Z_q\end{pmatrix}
\]

with centered Gaussian limit, then

\[
E(Z_a-Z_q)_+^2
=
\frac12
\operatorname{Var}(Z_a-Z_q).
\]

Hence this cell contributes

\[
\frac14
F(t)G'(t)
\operatorname{Var}(Z_a-Z_q)
\]

to the order-\(B^{-1}\) expectation coefficient.

## Scope

This proves the local expansion for one explicit coincident winner/threshold
cell. The full policy requires summing and reconciling all active coincidence
cones.
