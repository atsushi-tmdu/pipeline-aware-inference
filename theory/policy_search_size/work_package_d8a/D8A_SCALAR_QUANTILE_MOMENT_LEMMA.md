# Lemma D8-A.2d: Scalar Quantile Moment Bound

## Statement

Let \(Y_1,\ldots,Y_B\) be iid with distribution function \(F\), and let

\[
q_p=F^{-1}(p),
\qquad
0<p<1.
\]

Use

\[
\widehat q_{p,B}=Y_{(\lceil Bp\rceil)}.
\]

Assume:

1. \(F\) is continuous;
2. for some \(\delta>0\), \(F\) is differentiable on
   \([q_p-\delta,q_p+\delta]\);
3. its density satisfies
   \[
   \inf_{|x-q_p|\le\delta}f(x)\ge m>0;
   \]
4. for some \(r>2\), there exists \(s>r\) such that
   \[
   E|Y|^s<\infty.
   \]

Then

\[
\sup_{B\ge B_0}
E\left|
\sqrt B
(\widehat q_{p,B}-q_p)
\right|^r
<
\infty
\]

for sufficiently large \(B_0\). Consequently, the family

\[
\left\{
B(\widehat q_{p,B}-q_p)^2
\right\}_{B\ge B_0}
\]

is uniformly integrable.

## Proof

### Local concentration

For \(0<t\le\delta\), the density lower bound gives

\[
F(q_p+t)-p\ge mt
\]

and

\[
p-F(q_p-t)\ge mt.
\]

Let \(k_B=\lceil Bp\rceil\). Since

\[
0\le\frac{k_B}{B}-p\le\frac1B,
\]

the events \(\widehat q_{p,B}>q_p+t\) and
\(\widehat q_{p,B}<q_p-t\) are binomial deviations with effective probability
gap at least

\[
(mt-B^{-1})_+.
\]

Hoeffding's inequality yields

\[
P\left(
|\widehat q_{p,B}-q_p|>t
\right)
\le
2\exp\left[
-2B(mt-B^{-1})_+^2
\right].
\]

Using the tail-integral identity for moments and the change of variable
\(u=\sqrt B\,t\), this bound implies

\[
\sup_B
E\left[
\left|
\sqrt B
(\widehat q_{p,B}-q_p)
\right|^r
I\{|\widehat q_{p,B}-q_p|\le\delta\}
\right]
<
\infty.
\]

### Complementary tail event

The event
\(|\widehat q_{p,B}-q_p|>\delta\) has probability at most
\(C\exp(-cB)\).

Also,

\[
|\widehat q_{p,B}-q_p|
\le
\max_{1\le i\le B}|Y_i|+|q_p|.
\]

Choose \(s>r\). Hölder's inequality gives

\[
\begin{aligned}
&E\left[
B^{r/2}
|\widehat q_{p,B}-q_p|^r
I\{|\widehat q_{p,B}-q_p|>\delta\}
\right]
\\
&\le
B^{r/2}
\left[
E\left(
\max_i|Y_i|+|q_p|
\right)^s
\right]^{r/s}
P\{|\widehat q_{p,B}-q_p|>\delta\}^{1-r/s}.
\end{aligned}
\]

Since

\[
E\max_i|Y_i|^s
\le
B\,E|Y|^s,
\]

the polynomial factor is dominated by the exponential probability factor.
The complementary contribution therefore tends to zero.

Combining the local and complementary bounds proves the result.

## Uniform integrability

For any \(K>0\),

\[
E\left[
B(\widehat q-q)^2
I\{\sqrt B|\widehat q-q|>K\}
\right]
\le
\frac{
E|\sqrt B(\widehat q-q)|^r
}{
K^{r-2}
}.
\]

The right side tends to zero uniformly as \(K\to\infty\).
