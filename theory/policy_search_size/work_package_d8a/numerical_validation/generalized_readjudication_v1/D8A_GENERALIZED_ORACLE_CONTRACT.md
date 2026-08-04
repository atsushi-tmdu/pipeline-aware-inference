# D8-A Generalized Oracle Contract

## Canonical parameterization

All oracle calculations use the latent Gaussian parameterization

\[
\theta_Z=(z_p,z_p,z_p,t_s),
\]

where

\[
z_p=\Phi^{-1}(p)
\]

and \(t_s\) is the \(s\)-quantile of the base maximum
\(\max(Z_0,Z_1)\).

The common monotone score transformations are treated as exact
reparameterizations, not separate stochastic data-generating mechanisms.

## Quantile moments

For each reference size \(B\), the oracle must calculate:

\[
E(\widehat\theta_Z-\theta_Z)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1})
\]

with the exact order index

\[
k_B=\lceil Bp\rceil.
\]

The joint covariance is

\[
\Sigma_{\ell m}
=
\frac{
P(Y_\ell\le\theta_\ell,Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)f_m(\theta_m)
}.
\]

## Generalized policy coefficient

The oracle must provide:

- population policy probabilities;
- the policy gradient;
- the smooth-stratum Hessian;
- both kink coefficients \(\lambda_0,\lambda_1\);
- both contrast variances
  \(d_a^\top\Sigma_\theta d_a\);
- \(C_{\Delta,B}^{\mathrm{gen}}\);
- the adaptive and comparator generalized reference coefficients;
- \(C_{S,R,B}^{\mathrm{gen}}\);
- the unchanged evaluation coefficient \(C_{S,E}\).

## Required independent audits

### Directional expansion

For each dependence/probability class, compare the exact deterministic policy
map with its generalized local approximation in directions from every active
threshold-order cone.

### Contrast variance

For \(a\in\{0,1\}\),

\[
d_a^\top\Sigma_\theta d_a>0.
\]

For equal candidate probabilities in latent Gaussian margins,

\[
d_a^\top\Sigma_\theta d_a
=
\frac{
2\{p-\Phi_2(z_p,z_p;\rho_{a2})\}
}{
\phi(z_p)^2
}.
\]

### Transformation invariance

Identity, exponential, and hyperbolic-sine representations must agree for:

- all Boolean policy decisions;
- all finite-sample estimators;
- every generalized oracle coefficient;
- all acceptance decisions.

### Smooth-only discrepancy

The difference between the generalized coefficient and the smooth-only
coefficient must equal the declared sum of positive-part-square expectation
corrections.

## Tolerances

- deterministic probability absolute tolerance: \(10^{-10}\);
- coefficient relative tolerance: \(10^{-8}\);
- transformation-invariance absolute tolerance: \(10^{-10}\);
- directional expansion normalized-error target: \(10^{-4}\);
- contrast variance positivity floor: \(10^{-12}\).
