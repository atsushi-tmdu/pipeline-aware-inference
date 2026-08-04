# Proposition D8-A.2c: Fixed-Dimension Moment Reduction

Let \(r=2+\eta\ge2\) and \(d<\infty\). For every \(x\in\mathbb R^d\),

\[
\|x\|_2^r
\le
d^{r/2-1}
\sum_{\ell=1}^d|x_\ell|^r.
\]

Consequently, if

\[
\sup_B
E\left|
\sqrt B
(\widehat\theta_\ell-\theta_\ell)
\right|^{2+\eta}
<\infty
\]

for each component \(\ell\), then

\[
\sup_B
E\left\|
\sqrt B
(\widehat\theta-\theta)
\right\|^{2+\eta}
<\infty.
\]

Thus the vector higher-moment requirement reduces to scalar empirical
quantile moment bounds when the threshold dimension is fixed.

This proposition does not itself prove the scalar bounds. Those bounds remain
to be derived from local quantile concentration and tail control.
