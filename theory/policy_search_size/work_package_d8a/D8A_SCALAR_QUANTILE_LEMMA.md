# Lemma D8-A.2a: Scalar Empirical-Quantile Mean Expansion

## Statement

Let \(Y_1,\ldots,Y_B\) be iid with distribution function \(F\), and let

\[
q_p=F^{-1}(p),
\qquad
0<p<1.
\]

Use the generalized-inverse empirical quantile

\[
\widehat q_{p,B}
=
Y_{(k_B)},
\qquad
k_B=\lceil Bp\rceil.
\]

Assume:

1. \(F\) is strictly increasing in a neighborhood of \(q_p\);
2. its density \(f\) is positive and twice continuously differentiable in
   that neighborhood;
3. \(Q=F^{-1}\) has a bounded third derivative on
   \([p-\delta,p+\delta]\) for some \(\delta>0\);
4. the order-statistic tail contribution satisfies
   \[
   E\!\left[
   |Q(U_{(k_B)})|
   I\{|U_{(k_B)}-p|>\delta\}
   \right]
   =
   o(B^{-1}),
   \]
   where
   \[
   U_{(k_B)}\sim
   \operatorname{Beta}(k_B,B+1-k_B).
   \]

Define the lattice offset

\[
a_{p,B}
=
k_B-(B+1)p.
\]

Then

\[
E(\widehat q_{p,B})-q_p
=
\frac{b_{p,B}}{B}
+
o(B^{-1}),
\]

where

\[
b_{p,B}
=
\frac{a_{p,B}}{f(q_p)}
-
\frac{
p(1-p)f'(q_p)
}{
2f(q_p)^3
}.
\]

The coefficient \(b_{p,B}\) is bounded but need not converge with \(B\).

## Proof

By the probability-integral transform,

\[
F\{Y_{(k_B)}\}
\overset{d}=U_{(k_B)},
\]

with

\[
U_{(k_B)}
\sim
\operatorname{Beta}(k_B,B+1-k_B).
\]

Write

\[
H_B=U_{(k_B)}-p.
\]

The exact first moment is

\[
E(H_B)
=
\frac{k_B}{B+1}-p
=
\frac{a_{p,B}}{B+1}.
\]

The exact variance is

\[
\operatorname{Var}(U_{(k_B)})
=
\frac{
k_B(B+1-k_B)
}{
(B+1)^2(B+2)
}.
\]

Since \(a_{p,B}=O(1)\),

\[
E(H_B^2)
=
\frac{p(1-p)}{B}
+
O(B^{-2}).
\]

On the event \(|H_B|\le\delta\), Taylor expansion of \(Q=F^{-1}\) gives

\[
Q(p+H_B)
=
Q(p)
+
Q'(p)H_B
+
\frac12Q''(p)H_B^2
+
R_B,
\]

with

\[
|R_B|
\le
C|H_B|^3.
\]

For a beta order statistic with \(p\) fixed in \((0,1)\),

\[
E|H_B|^3
=
O(B^{-3/2}),
\]

so the local Taylor remainder is \(o(B^{-1})\). Assumption 4 controls the
complementary tail event.

The inverse-function identities are

\[
Q'(p)
=
\frac1{f(q_p)}
\]

and

\[
Q''(p)
=
-\frac{f'(q_p)}{f(q_p)^3}.
\]

Therefore,

\[
\begin{aligned}
E(\widehat q_{p,B})-q_p
&=
\frac1{f(q_p)}
\frac{a_{p,B}}{B+1}
\\
&\quad
-
\frac12
\frac{f'(q_p)}{f(q_p)^3}
\left\{
\frac{p(1-p)}{B}
+
O(B^{-2})
\right\}
+
o(B^{-1})
\\
&=
\frac1B
\left[
\frac{a_{p,B}}{f(q_p)}
-
\frac{
p(1-p)f'(q_p)
}{
2f(q_p)^3
}
\right]
+
o(B^{-1}).
\end{aligned}
\]

This proves the result.

## Remarks

### Lattice stabilization

A constant coefficient exists along any subsequence on which
\(a_{p,B}\) converges. It also exists on compatible grids for which
\(Bp\) has a fixed fractional pattern.

### Uniform distribution

If \(F\) is uniform, \(f'=0\), and the exact bias is

\[
E(\widehat q_{p,B})-p
=
\frac{a_{p,B}}{B+1}.
\]

### Scope

This lemma proves only the scalar mean expansion. The joint covariance,
higher-moment control, and policy-map Taylor theorem remain separate tasks.
