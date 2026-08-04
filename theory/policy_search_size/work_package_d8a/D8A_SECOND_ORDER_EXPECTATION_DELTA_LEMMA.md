# Lemma D8-A.4a: Second-Order Expectation Delta Method

## Statement

Let \(U_B=\widehat\theta_B-\theta\in\mathbb R^d\), with fixed
\(d<\infty\). Suppose

\[
E(U_B)
=
\frac{b_B}{B}
+
o(B^{-1}),
\]

\[
B\,E(U_BU_B^\top)
=
\Sigma+o(1),
\]

and, for some \(\eta>0\),

\[
\sup_B
E\|\sqrt B\,U_B\|^{2+\eta}
<
\infty.
\]

Let \(h\) be twice continuously differentiable in a neighborhood of
\(\theta\). Then

\[
E\{h(\widehat\theta_B)\}
=
h(\theta)
+
\frac1B
\left[
\nabla h(\theta)^\top b_B
+
\frac12
\operatorname{tr}
\{H_h(\theta)\Sigma\}
\right]
+
o(B^{-1}).
\]

The vector \(b_B\) may be bounded and \(B\)-dependent.

## Proof

Taylor's theorem gives

\[
h(\theta+U_B)
=
h(\theta)
+
\nabla h(\theta)^\top U_B
+
\frac12
U_B^\top H_h(\theta)U_B
+
R_B,
\]

where

\[
|R_B|
\le
\|U_B\|^2
\omega(\|U_B\|)
\]

for a deterministic modulus \(\omega(t)\to0\).

The first two expectation terms give

\[
E\{\nabla h(\theta)^\top U_B\}
=
\frac{\nabla h(\theta)^\top b_B}{B}
+
o(B^{-1})
\]

and

\[
E\{U_B^\top H_h(\theta)U_B\}
=
\frac{
\operatorname{tr}
\{H_h(\theta)\Sigma\}
}{B}
+
o(B^{-1}).
\]

It remains to show

\[
B\,E|R_B|\to0.
\]

The higher-moment condition implies that
\(\{B\|U_B\|^2\}\) is uniformly integrable. Also \(U_B\to0\) in probability,
so \(\omega(\|U_B\|)\to0\) in probability. Uniform integrability and bounded
local continuity of the Hessian therefore yield

\[
B\,E[
\|U_B\|^2\omega(\|U_B\|)
]
\to0.
\]

This proves the result.
