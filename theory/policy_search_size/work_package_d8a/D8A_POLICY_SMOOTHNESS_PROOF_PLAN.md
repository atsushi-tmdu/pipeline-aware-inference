# D8-A Policy-Map Smoothness Proof Plan

## Goal

Establish that

\[
\theta\mapsto\Delta_\pi(\theta)
\]

is twice continuously differentiable in a neighborhood of the population
threshold vector under the regular D7 regime.

## 1. Local ordering stability

Strict threshold separation gives

\[
\min_{j\in\mathcal J_0}|q_j-c|>0.
\]

Hence there is a positive neighborhood in which every ordering relation
between \(c\) and the base-candidate thresholds remains unchanged. The
activation and candidate-threshold logic therefore has a fixed local
combinatorial form.

A convenient radius is

\[
r_\theta
=
\frac12
\min_{j\in\mathcal J_0}|q_j-c|.
\]

## 2. Winner partition

Partition score space by the unique base and full winners. On each open
winner cell, the policy indicators reduce to inequalities involving fixed
coordinate functions and moving scalar thresholds.

Winner-tie surfaces have probability zero under a continuous joint density.
Intersections of winner boundaries with moving threshold surfaces are
codimension at least two and should not contribute first-order boundary mass.

## 3. Integral representation

Write each probability entering

\[
\Delta_\pi
=
E(AM)-E(A)E(M)
\]

as a finite sum of integrals over winner cells. Locally, each integration
region has fixed logical structure and boundaries moving with individual
components of \(\theta\).

## 4. First derivatives

Differentiate each integral using boundary differentiation. Candidate
derivatives are weighted integrals over \(X_j=q_j\); the trigger derivative is
a weighted integral over \(T=c\).

These boundary expressions must reproduce the D7 first-order coefficients.

## 5. Second derivatives

Differentiate the boundary integrals once more. Terms divide into:

- candidate-candidate boundary interactions;
- candidate-trigger interactions;
- trigger-trigger curvature;
- derivatives of conditional winner and rejection probabilities along each
  boundary.

The candidate-trigger terms are generally nonzero even when the threshold
estimators have simple marginal quantile forms.

## 6. Regularity conditions to state explicitly

A proof will require conditions such as:

- a joint density with two locally integrable derivatives;
- positive candidate and maximum densities at all thresholds;
- dominated boundary densities and their derivatives;
- no positive-probability winner ties;
- strict candidate-trigger separation;
- finite candidate pools.

## 7. Nonregular boundary

If \(q_j=c\), the local ordering is not stable and the D7 positive-part
directional term reappears. D8-A excludes this case.
