# D7 Final Scientific Adjudication

**Formal status: FAIL**

## Immutable decision

The prospectively locked D7 validation formally failed.
No criterion was changed and the scientific simulation was not repeated.

- Failed fatal checks: []
- Failed scientific checks: ['bootstrap_coverage_delta_pi', 'bootstrap_coverage_delta_s', 'both_trigger_ordering_strata', 'delta_pi_bias_per_cell', 'delta_pi_variance_ratio_per_cell', 'delta_s_bias_per_cell', 'delta_s_normal_coverage_per_cell', 'delta_s_variance_ratio_per_cell', 'plus_one_bridge_delta_pi', 'plus_one_bridge_delta_s', 'plus_one_sign_reversals']

## What was supported

- All implementation and fatal checks passed.
- Delta_pi normal coverage passed in 72 of 72 regular cells.
- Delta_S normal coverage passed in 71 of 72 regular cells.
- Delta_pi influence-variance criteria passed in 71 of 72 regular cells.
- Delta_S influence-variance criteria passed in 71 of 72 regular cells.
- Complete-replication bootstrap SD divided by empirical SD ranged from 0.975 to 1.126 for Delta_pi and from 0.973 to 1.128 for Delta_S.
- The maximum trigger-CDF discrepancy was 1.663 benchmark Monte Carlo standard errors.

## What was not supported under the locked finite design

- Per-cell Delta_pi bias criterion failed in 8 of 72 cells.
- Per-cell Delta_S bias criterion failed in 9 of 72 cells.
- Delta_pi plus-one bridge criterion failed in 27 of 72 cells.
- Delta_S plus-one bridge criterion failed in 29 of 72 cells.
- Delta_pi plus-one sign criterion failed in 14 of 72 cells.
- Delta_S plus-one sign criterion failed in 14 of 72 cells.
- Bootstrap normal coverage failed in 1 of 18 Delta_pi cells and 1 of 18 Delta_S cells.

## Qualified scientific interpretation

The results provide strong but incomplete support for the continuous, unique-winner, strictly separated first-order D7 theory.
The dominant limitations are finite-reference centering bias, especially at alpha=0.01, and slow finite-sample convergence of the paired plus-one bridge.
The post-hoc rate audit is exploratory and does not rescue the formal FAIL.

## Scope boundary

D7 does not validate discrete winner ties, deterministic tie rules, trigger-tie allocation, failed-fit fallback, growing candidate dimension, or the current empirical pipeline without an exact bank bridge.

## Next work package

D8 should prospectively study second-order finite-reference bias and the convergence rate of the plus-one bridge. D9 may then address positive-probability discrete winner ties.
