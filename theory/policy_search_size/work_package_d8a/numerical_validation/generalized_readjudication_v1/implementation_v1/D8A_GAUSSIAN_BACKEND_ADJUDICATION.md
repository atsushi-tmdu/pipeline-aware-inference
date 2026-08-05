# D8-A Gaussian-Probability Backend Adjudication

The fixed-RNG Genz evaluator was reproducible, but an independent
deterministic nested-quadrature audit found that it introduced a small
directional value bias in the worst registered cell.

Observed worst-case diagnostics:

- base-point backend difference:
  \(5.5804\times10^{-10}\);
- apparent Genz one-sided gradient discrepancy:
  \(3.9050\times10^{-7}\);
- independent quadrature gradient discrepancy:
  \(4.0874\times10^{-9}\);
- independent quadrature normalized directional error:
  at most \(1.9328\times10^{-5}\).

The deterministic candidate backend uses Plackett's correlation integral for
bivariate Gaussian probabilities and conditional deterministic integration
for trivariate probabilities.

No implementation lock is created by this file.
