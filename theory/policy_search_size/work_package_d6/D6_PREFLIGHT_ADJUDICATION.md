# D6 Runtime-Only Preflight Adjudication

**Status: PASS**

This document records mathematical and implementation debugging only. It is
not scientific evidence and does not lock the D6 numerical design.

## Unit tests

- Tests run: 18
- Result: PASS

The tests cover nested pools, unique winners, winner-region representation,
the covariance identity, centered evaluation influence, all candidate-threshold
jump cases, complete-vector resampling, and the TESS derivative.

## Continuous Gaussian derivative benchmark

- Rejection-contrast benchmark:
  \(\Delta_\pi=0.01919700\)
- Candidate 0 finite difference / boundary:
  0.00464899 / 0.00503099
- Candidate 1 finite difference / boundary:
  0.00067270 / 0.00076317
- Candidate 2 finite difference / boundary:
  -0.03616680 / -0.03440965
- Activation finite difference / boundary:
  0.01191380 / 0.01126773

All prespecified runtime-only derivative checks passed.

## Interpretation

The preflight supports the algebra and implementation of the winner-region
boundary coefficients, including the negative optional-candidate contribution
and the exact zero-jump shared-winner case.

It does not establish finite-sample coverage, full two-bank bootstrap
performance, exact 20-candidate empirical-pipeline validity, tie handling,
failed-fit handling, or maximum-score-trigger validity.
