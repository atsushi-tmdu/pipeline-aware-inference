# D8-A Generalized Implementation Lock

**Implementation locked:** yes
**Scientific execution authorized:** yes
**Scientific simulation run:** no

## Locked implementation

The implementation lock contains:

- the empirical-order convention \(k_B=\lceil Bp\rceil\);
- deterministic and independent reference/evaluation random streams;
- canonical simulation of 25 latent scientific equivalence classes;
- exact transformation audits for the 50 nonidentity registry rows;
- analytic smooth-stratum gradients and Hessians;
- both active candidate-coincidence corrections;
- deterministic Gaussian probability calculations;
- generalized policy and TESS coefficients;
- engineering smoke tests and all-class oracle audits.

## Gaussian backend adjudication

A fixed-RNG Genz evaluator was reproducible but introduced a small
directional value bias in the most sensitive registered cell.

An independent deterministic nested-quadrature audit found:

- Genz apparent one-sided gradient gap:
  \(3.9050\times10^{-7}\);
- independent quadrature gradient gap:
  \(4.0874\times10^{-9}\);
- independent quadrature normalized directional error:
  \(1.9328\times10^{-5}\).

The locked source therefore uses deterministic Gaussian quadrature together
with analytic boundary derivatives. The Genz implementation is retained only
as a named legacy diagnostic.

## Final engineering evidence

- engineering unit tests: 55/55 PASS;
- scientific equivalence classes audited: 25/25;
- maximum analytic directional normalized error at radius 0.002:
  \(4.4624\times10^{-5}\);
- maximum full-oracle directional normalized error:
  \(2.2298\times10^{-5}\);
- maximum kink-identity error:
  \(2.2205\times10^{-16}\);
- maximum derivative-step discrepancy: \(0\);
- maximum covariance negative part: \(0\);
- transformation-invariance audit: PASS.

## Authorization boundary

This lock authorizes execution of the already locked scientific design.

It does not change the registered design or its acceptance criteria, and it
does not constitute a scientific simulation run.
