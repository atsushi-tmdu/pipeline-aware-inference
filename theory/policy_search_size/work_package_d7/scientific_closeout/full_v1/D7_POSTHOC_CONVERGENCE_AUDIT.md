# D7 Post-hoc Convergence-Rate Audit

**Status:** exploratory, nonadjudicative, existing outputs only

This audit was specified after the locked D7 scientific result was known.
It does not alter the formal FAIL decision and is not confirmatory evidence.

## Formal result retained

- Delta_pi bias failures: 8 of 72
- Delta_S bias failures: 9 of 72
- Delta_pi variance failures: 1 of 72
- Delta_S variance failures: 1 of 72
- Delta_pi normal-coverage failures: 0 of 72
- Delta_S normal-coverage failures: 1 of 72
- Delta_pi plus-one bridge failures: 27 of 72
- Delta_S plus-one bridge failures: 29 of 72

## Trigger calibration

The largest absolute discrepancy between the deterministic maximum-CDF calibration and the independent benchmark was 1.663 benchmark Monte Carlo standard errors.
This does not support trigger-CDF numerical integration as the main cause of failure.

## Finite-reference bias pattern

Across alpha=0.01 series, the median descriptive slope of log absolute bias versus log B was -1.031; the second-order reference-bias benchmark is -1.
At fixed B=3000, changing n from 3000 to 5000 produced a median relative bias change of 0.114 across alpha=0.01 series.
The fitted 1/B and 1/B+1/n models are descriptive because each series has only four design points.

## Plus-one bridge pattern

Across alpha=0.01 series, the median descriptive slope of log bridge ratio versus log B was -0.502; the relative first-order benchmark is -0.5.
Under a purely descriptive 1/sqrt(B) extrapolation, the median reference size predicted to cross the locked 0.15 bridge threshold was 5676.

## Interpretation boundary

- The formal D7 status remains FAIL.
- The audit does not justify changing any locked threshold.
- The audit is a motivation for prospective second-order theory and a new work package.
- Discrete winner ties remain outside D7.
