# D8-A Generalized Implementation Protocol

## Oracle

The canonical identity parameterization is used for all scientific
calculations. Generalized coefficients include both active kink directions:

\[
d_0=(1,0,-1,0)^\top,
\qquad
d_1=(0,1,-1,0)^\top.
\]

The smooth-stratum Hessian is evaluated after subtracting the two locked
positive-part-square terms. Central differences are Richardson-extrapolated.

## Random streams

Each scientific equivalence class has deterministic independent streams for:

- reference generation;
- evaluation generation;
- engineering-only checks.

Streams use `PCG64DXSM` and SHA-256-derived spawn keys.

## Transformation audit

Every engineering bank is transformed by the locked exponential and
hyperbolic-sine maps. Winner identities, empirical-quantile decisions, policy
fields, and estimators must agree exactly with the identity representation.

## Engineering smoke test

The smoke test is limited to:

- two diagnostic classes;
- 20 replicates per class;
- \(B=n=64\).

All outputs are labeled `NON_SCIENTIFIC_ENGINEERING_ONLY`.

## Current gate

Passing this package does not itself authorize scientific execution. A
separate implementation checkpoint and tag are required.
