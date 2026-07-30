# Manuscript-ready theory draft: adaptive branching and inferential search size

## Setup

Let \(P_{01},\ldots,P_{0K_0}\) and
\(P_{11},\ldots,P_{1K_1}\) be mutually independent \(U(0,1)\)
variables under the global null. Define

\[
A=\min_{1\le j\le K_0}P_{0j},
\qquad
B=\min_{1\le j\le K_1}P_{1j},
\]

and select \(\tau=1-2^{-1/K_0}\), so that
\(P(A\le\tau)=P(A>\tau)=1/2\).

Consider three policies:

\[
W_P=
\begin{cases}
\min(A,B),&A\le\tau,\\
A,&A>\tau,
\end{cases}
\]

\[
W_R=
\begin{cases}
\min(A,B),&C=1,\\
A,&C=0,
\end{cases}
\qquad
C\sim\operatorname{Bernoulli}(1/2),
\]

and

\[
W_S=
\begin{cases}
A,&A\le\tau,\\
\min(A,B),&A>\tau.
\end{cases}
\]

The policies respectively expand the search when the initial result is
promising, independently of the initial result, or when the initial result
requires rescue.

For policy \(m\in\{P,R,S\}\), define

\[
Q_m(\alpha)=P(W_m\ge\alpha)
\]

and

\[
\operatorname{TESS}_m(\alpha)
=
\frac{\log Q_m(\alpha)}{\log(1-\alpha)}.
\]

## Proposition

All three policies evaluate \(K_0+K_1/2\) candidates on average and share the
same maximum candidate count \(K_0+K_1\). Nevertheless, for every
\(\alpha\in(0,1)\),

\[
\operatorname{TESS}_P(\alpha)
<
\operatorname{TESS}_R(\alpha)
<
\operatorname{TESS}_S(\alpha).
\]

Moreover,

\[
\lim_{\alpha\downarrow0}\operatorname{TESS}_m(\alpha)
=
K_0+\frac{K_1}{2}
\qquad
(m=P,R,S).
\]

If \(\alpha>\tau\), then

\[
\operatorname{TESS}_P(\alpha)=K_0
\quad\text{and}\quad
\operatorname{TESS}_S(\alpha)=K_0+K_1.
\]

## Proof

Write

\[
S_0(\alpha)=(1-\alpha)^{K_0},
\qquad
S_1(\alpha)=(1-\alpha)^{K_1}.
\]

For \(\alpha\le\tau\),

\[
Q_P(\alpha)
=
\frac12+
\left(S_0(\alpha)-\frac12\right)S_1(\alpha),
\]

\[
Q_R(\alpha)
=
S_0(\alpha)\frac{1+S_1(\alpha)}2,
\]

and

\[
Q_S(\alpha)
=
S_0(\alpha)-\frac12+\frac12S_1(\alpha).
\]

Therefore,

\[
Q_P(\alpha)-Q_R(\alpha)
=
Q_R(\alpha)-Q_S(\alpha)
=
\frac12\{1-S_0(\alpha)\}\{1-S_1(\alpha)\}>0.
\]

For \(\alpha>\tau\),

\[
Q_P(\alpha)=S_0(\alpha),
\qquad
Q_R(\alpha)=S_0(\alpha)\frac{1+S_1(\alpha)}2,
\qquad
Q_S(\alpha)=S_0(\alpha)S_1(\alpha),
\]

and hence

\[
Q_P(\alpha)-Q_R(\alpha)
=
Q_R(\alpha)-Q_S(\alpha)
=
\frac12S_0(\alpha)\{1-S_1(\alpha)\}>0.
\]

Because \(\log(1-\alpha)<0\), the ordering reverses after transformation to
TESS.

Finally,

\[
S_0(\alpha)=1-K_0\alpha+o(\alpha),
\qquad
S_1(\alpha)=1-K_1\alpha+o(\alpha),
\]

and substitution into any of the three expressions gives

\[
Q_m(\alpha)
=
1-\left(K_0+\frac{K_1}{2}\right)\alpha+o(\alpha).
\]

The stated limit follows from
\(\log(1-\alpha)=-\alpha+o(\alpha)\). \(\square\)

## Interpretation

The proposition shows that finite-threshold inferential multiplicity is not
determined by the maximum or expected number of evaluated candidates.
Instead, it depends on how candidate activation is coupled to the current
extremeness of the data. Search expansion that is concentrated in already
rejecting states adds relatively little new rejection opportunity, whereas
rescue expansion allocates new candidates preferentially to states that have
not yet rejected.
