# D8-A Expectation-Level Joint Quantile Expansion

## Status

Prospective proof memo. No D8-A theory lock has been created.

## 1. Why the moment formulation is preferable

A representation of the form

\[
\widehat\theta-\theta
=
B^{-1/2}Z_B+B^{-1}b_{\theta,B}+o_p(B^{-1})
\]

is stronger than D8-A needs and may suppress random second-order terms.

For the expectation of a smooth policy map, it is sufficient to establish

\[
E(\widehat\theta-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

and

\[
B\,E\left[
(\widehat\theta-\theta)
(\widehat\theta-\theta)^\top
\right]
=
\Sigma_\theta+o(1),
\]

together with a uniform-integrability or higher-moment condition controlling
the Taylor remainder.

## 2. Expectation-level delta theorem target

Let \(h\) be twice continuously differentiable in a neighborhood of
\(\theta\), with locally uniformly continuous Hessian. Suppose

\[
E\|\widehat\theta-\theta\|^{2+\eta}
=
O\left(B^{-1-\eta/2}\right)
\]

for some \(\eta>0\). Then the prospective theorem is

\[
E\{h(\widehat\theta)\}
=
h(\theta)
+
\frac1B
\left[
\nabla h(\theta)^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{H_h(\theta)\Sigma_\theta\}
\right]
+
o(B^{-1}).
\]

This result requires only moment expansions, not a deterministic
second-order stochastic remainder.

## 3. Joint quantile covariance

Let \(Y_\ell\) denote the complete-vector function defining threshold
component \(\ell\). Candidate components use candidate scores; the trigger
component uses the base maximum.

The first-order quantile influence functions are

\[
\psi_\ell(Y)
=
\frac{
p_\ell-I(Y_\ell\le\theta_\ell)
}{
f_\ell(\theta_\ell)
}.
\]

Therefore,

\[
\Sigma_{\theta,\ell m}
=
E\{\psi_\ell(Y)\psi_m(Y)\}
=
\frac{
P(Y_\ell\le\theta_\ell,\,
  Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)f_m(\theta_m)
}.
\]

Because all components are evaluated on the same complete reference vector,
candidate-trigger dependence is retained automatically.

## 4. Reference coefficient

For the policy contrast \(h=\Delta_\pi\), define

\[
C_{R,B}
=
\nabla\Delta_\pi(\theta)^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{H_{\Delta_\pi}(\theta)\Sigma_\theta\}.
\]

Partitioning candidate thresholds and the trigger threshold gives

\[
\frac12\operatorname{tr}(H_{qq}\Sigma_{qq})
+
H_{qc}^\top\Sigma_{qc}
+
\frac12H_{cc}\Sigma_{cc}.
\]

The middle term is the candidate-trigger contribution.

## 5. Combined reference and evaluation result

Using the exact conditional covariance identity,

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{R,B}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{R,B}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

## 6. Proof obligations

The remaining work is to prove:

1. the componentwise \(B^{-1}\) quantile mean expansion with the exact lattice
   term;
2. the joint first-order covariance limit;
3. a \(2+\eta\) moment bound for the joint quantile vector;
4. twice differentiability of the separated continuous policy map;
5. interchange of differentiation and integration for its gradient and
   Hessian.
