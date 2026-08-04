# D8-A Protocol: Second-Order Finite-Reference Bias

**Status:** prospective theory scaffold; not locked
**Parent result:** `d7-continuous-validation-full-v1`
**Parent formal status:** FAIL

## Objective

D8-A studies finite-reference bias in the regular continuous
maximum-trigger estimator developed in D7.

For fixed reference thresholds,

\[
\widehat\Delta_\pi
=
\overline{AM}-\bar A\bar M
\]

satisfies the exact identity

\[
E_E(\widehat\Delta_\pi\mid\widehat\theta_R)
=
\left(1-\frac1n\right)
\Delta_\pi(\widehat\theta_R).
\]

For the joint empirical-quantile vector, D8-A will establish the weaker and
sufficient moment expansions

\[
E(\widehat\theta_R-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

and

\[
B\,E\left[
(\widehat\theta_R-\theta)
(\widehat\theta_R-\theta)^\top
\right]
=
\Sigma_\theta+o(1).
\]

For a twice differentiable regular policy map,

\[
C_{R,B}
=
\nabla\Delta_\pi(\theta)^\top b_{\theta,B}
+
\frac12\operatorname{tr}
\{H_{\Delta_\pi}(\theta)\Sigma_\theta\}.
\]

The prospective combined expansion is

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

## TESS extension

For

\[
g_\alpha(x)=
\frac{\log(1-x)}{\log(1-\alpha)},
\]

D8-A will retain both transformed centering bias and curvature bias.

## Scope

- continuous candidate scores;
- fixed finite candidate pools;
- almost-surely unique winners;
- strict candidate-trigger threshold separation;
- independent reference and evaluation banks;
- positive differentiable candidate and maximum densities.

## Exclusions

- plus-one bridge rates, assigned to D8-B;
- discrete winner ties;
- exact threshold coincidence;
- trigger-tie allocation;
- failed-fit fallback;
- growing candidate dimension;
- any change to the D7 formal decision.

## Sequence

1. Prove the exact evaluation identity.
2. Derive the joint second-order empirical-quantile expansion under the exact
   order-statistic convention.
3. Establish twice differentiability of the separated policy map.
4. Identify \(C_{R,B}\), including lattice and candidate-trigger cross terms.
5. Derive the TESS second-order corollary.
6. Lock a new numerical design only after the theory and criteria are fixed.
