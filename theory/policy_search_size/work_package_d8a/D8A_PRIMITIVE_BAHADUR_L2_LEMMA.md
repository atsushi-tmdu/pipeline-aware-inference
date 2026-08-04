# Lemma D8-A.2e: Primitive \(L^2\) Bahadur Remainder

## Statement

Under the assumptions of Lemma D8-A.2d, additionally suppose \(f\) is
continuous at \(q_p\). Define

\[
\psi_p(Y)
=
\frac{
p-I(Y\le q_p)
}{
f(q_p)
}
\]

and

\[
r_{p,B}
=
\widehat q_{p,B}-q_p
-
\frac1B\sum_{i=1}^B\psi_p(Y_i).
\]

Then

\[
\sqrt B\,r_{p,B}
\overset{p}\longrightarrow0
\]

and

\[
B\,E(r_{p,B}^2)
\longrightarrow0.
\]

## Proof

### Asymptotic linearity in probability

Let \(F_B\) be the empirical distribution function and
\(k_B=\lceil Bp\rceil\). Continuity implies no sample ties almost surely, so

\[
F_B(\widehat q_{p,B})
=
\frac{k_B}{B}.
\]

Write

\[
G_B=F_B-F.
\]

Then

\[
F(\widehat q)-p
=
-G_B(q_p)
+
\{G_B(q_p)-G_B(\widehat q)\}
+
\left(\frac{k_B}{B}-p\right).
\]

Lemma D8-A.2d implies

\[
\widehat q-q_p
=
O_p(B^{-1/2}).
\]

Continuity and positivity of \(f(q_p)\) give

\[
F(\widehat q)-p
=
f(q_p)(\widehat q-q_p)
+
o_p(B^{-1/2}).
\]

The empirical process indexed by intervals is stochastically equicontinuous,
hence

\[
G_B(\widehat q)-G_B(q_p)
=
o_p(B^{-1/2}).
\]

Finally,

\[
\sqrt B
\left|
\frac{k_B}{B}-p
\right|
\le
B^{-1/2}
\longrightarrow0.
\]

Therefore,

\[
\sqrt B
\left[
\widehat q-q_p
-
\frac{
p-F_B(q_p)
}{
f(q_p)
}
\right]
\overset{p}\longrightarrow0.
\]

The quantity in square brackets is \(r_{p,B}\).

### Upgrade to \(L^2\)

The leading term is an average of bounded variables divided by the positive
constant \(f(q_p)\). It therefore has uniformly bounded moments of every
fixed order after multiplication by \(\sqrt B\).

Lemma D8-A.2d gives a uniformly bounded \(r\)-th moment, for some \(r>2\), of
\(\sqrt B(\widehat q-q_p)\). Hence

\[
\left\{
|\sqrt B\,r_{p,B}|^2
\right\}
\]

is uniformly integrable.

Since \(\sqrt B\,r_{p,B}\to0\) in probability, uniform integrability implies

\[
E|\sqrt B\,r_{p,B}|^2\to0.
\]

Equivalently,

\[
B\,E(r_{p,B}^2)\to0.
\]

## Primitive status

The only empirical-process input is stochastic equicontinuity for the VC
class of intervals. All moment and tail control is supplied by
Lemma D8-A.2d.
