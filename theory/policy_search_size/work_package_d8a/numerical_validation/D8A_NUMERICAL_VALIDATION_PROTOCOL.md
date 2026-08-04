# D8-A Prospective Numerical Validation Protocol

## Objective

Validate the implementation and finite-sample usefulness of

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}}{Bn}
+
o(B^{-1}+n^{-1})
\]

and

\[
E(\widehat\Delta_S)-\Delta_S
=
\frac{C_{S,R,B}}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]

Simulation is not used to establish the already proved theorem. It checks
implementation, coefficient calculation, and practical finite-sample
accuracy.

## Policy

The base pool is \(\{0,1\}\) and the full pool is \(\{0,1,2\}\).

\[
J_0=\arg\max_{j\in\{0,1\}}X_j,
\qquad
J_1=\arg\max_{j\in\{0,1,2\}}X_j.
\]

\[
R_0=I(X_{J_0}>q_{J_0}),
\qquad
R_1=I(X_{J_1}>q_{J_1}),
\]

\[
A=I\{\max(X_0,X_1)>c\},
\qquad
M=(1-R_0)R_1,
\]

\[
H=R_0+AM.
\]

The policy contrast is

\[
\Delta_\pi=\operatorname{Cov}(A,M).
\]

The budget-matched comparator estimator is

\[
\bar R_0+\bar A\bar M.
\]

## Data-generating family

A three-dimensional Gaussian copula is used with independent,
equicorrelated, and asymmetric dependence structures.

All coordinates receive the same strictly increasing transformation:

\[
h(z)=z,\qquad
h(z)=e^{0.35z},\qquad
h(z)=\sinh(0.5z).
\]

The common transformation preserves all winner identities while changing
marginal quantile density and curvature.

## Cell eligibility

Candidate probabilities are \(0.90,0.95,0.99\). Trigger probabilities for the
base maximum are \(0.50,0.70,0.85\).

A cell is included exactly when the latent candidate-trigger separation is at
least \(0.10\). The generated registry is immutable after lock.

## Three experiments

### Reference-only

Only the reference bank is random. Conditional evaluation expectations are
computed without evaluation Monte Carlo. This isolates the \(B^{-1}\)
centering and curvature terms.

### Evaluation-only

Population thresholds are fixed. This verifies the exact covariance identity

\[
E(\widehat\Delta_\pi)
=
(1-1/n)\Delta_\pi
\]

and the \(n^{-1}\) TESS expansion.

### Combined

Independent reference and evaluation banks are generated. This validates the
full policy expansion, its \(B^{-1}n^{-1}\) interaction, and the two-rate TESS
expansion.

## Monte Carlo precision

Stopping is based only on Monte Carlo precision. It may not depend on the
direction or apparent success of a scientific result.

Primary cells use 2,000 to 20,000 replicates. Diagnostic cells use 1,000 to
5,000. Banks are streamed and sample sizes are nested through common random
numbers.

## Adjudication

Exact identities, deterministic oracle agreement, cell completeness, and
seed independence are fatal checks.

Asymptotic approximation criteria measure finite-sample usefulness. Failure
of such a criterion does not by itself refute a theorem stated with an
unspecified little-o remainder.
