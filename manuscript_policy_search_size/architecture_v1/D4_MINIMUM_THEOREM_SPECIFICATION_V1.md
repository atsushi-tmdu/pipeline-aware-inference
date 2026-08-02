# Work Package D4: Minimum Theorem Specification v1

**Status:** Architecture-stage specification; not locked.
**Purpose:** Define the smallest paired two-bank theorem that directly matches the budget-matched promising-versus-random TESS contrast.

## 1. Population objects

At fixed `alpha`, on one null data state define:

- `R_0` - base-policy rejection indicator;
- `R_1` - expanded-policy rejection indicator;
- `D = R_1 - R_0`;
- `A` - adaptive activation indicator.

Let

- `e_0 = E(R_0)`;
- `r = E(A)`;
- `mu = E(D)`;
- `nu = E(AD)`.

Then

- `pi_A = e_0 + nu`;
- `pi_C = e_0 + r mu`, where `C` is random activation at the same population rate;
- `delta = pi_A - pi_C = nu - r mu = Cov(A,D)`;
- `Delta_S = g_alpha(pi_A) - g_alpha(pi_C)`.

## 2. Plug-in estimator

Use one complete-vector reference bank to estimate all candidate and activation thresholds. Use one independent evaluation bank to compute

- `e_0_hat = P_n R_0_hat`;
- `r_hat = P_n A_hat`;
- `mu_hat = P_n D_hat`;
- `nu_hat = P_n(A_hat D_hat)`.

Define

- `pi_A_hat = e_0_hat + nu_hat`;
- `pi_C_hat = e_0_hat + r_hat mu_hat`;
- `Delta_S_hat = g_alpha(pi_A_hat) - g_alpha(pi_C_hat)`.

This exactly mirrors a budget-matched benchmark using the realized evaluation-bank activation rate.

## 3. Evaluation influence function

For the population functional,

`IF(pi_A) = R_0 + AD - pi_A`,

`IF(pi_C) = (R_0-e_0) + mu(A-r) + r(D-mu)`.

Therefore

`phi_E^Delta = g_alpha'(pi_A){R_0 + AD - pi_A}`

`              - g_alpha'(pi_C){(R_0-e_0) + mu(A-r) + r(D-mu)}`.

This term automatically preserves the covariance among base rejection, activation, and incremental rejection.

## 4. Reference influence function

Let `theta` collect every reference-calibrated candidate and trigger threshold. Under the regular D2 model,

`theta_hat - theta = P_B psi_theta + o_p(B^-1/2)`.

The paired contrast reference influence is

`phi_R^Delta = {nabla_theta Delta_S(theta)}^T psi_theta`.

For one candidate per branch, the gradient can be written from the boundary-flux derivatives already established in D2. For multiple candidates with unique winners, a later extension may replace the scalar boundaries by winner-region boundary terms.

## 5. Core theorem target

Under D2-type smoothness, no-boundary-mass, complete-vector reference sampling, independent evaluation sampling, and `n/B -> lambda in (0,infinity)`, prove

`Delta_S_hat - Delta_S`

`= n^-1 sum phi_E^Delta(Y_i)`

`+ B^-1 sum phi_R^Delta(Z_b)`

`+ o_p(n^-1/2 + B^-1/2)`.

Consequently,

`sqrt(n)(Delta_S_hat - Delta_S)`

converges to a centered normal law with variance

`Var(phi_E^Delta) + lambda Var(phi_R^Delta)`.

## 6. Paired complete-replication bootstrap

In every bootstrap replication:

1. resample complete reference vectors;
2. recompute all candidate and trigger thresholds;
3. resample complete evaluation vectors;
4. use identical reference and evaluation bootstrap indices for both policies;
5. recompute `r_hat`, both rejection probabilities, and the TESS contrast.

Prove conditional consistency for the centered paired statistic.

## 7. First numerical validation

Use the same three regular DGP families as D2. Primary validation should focus on `B >= 3000` and `alpha = 0.05`, with smaller banks and `alpha = 0.01` retained as stress diagnostics.

Primary interval: paired two-bank bootstrap-normal.
Secondary: percentile.
Diagnostic: basic interval and evaluation-only interval.

## 8. Empirical bridge

After the regular theorem passes, map the locked empirical quantities to the D4 notation:

- `R_0` = fixed-base rejection;
- `R_1` = fixed-full rejection;
- `A` = promising activation;
- `D` = full minus base rejection;
- `pi_C` = budget-matched random benchmark at the observed activation rate.

The exact 20-candidate implementation remains subject to the plus-one and unique-winner bridge.

## 9. Stop rule

D4 is successful if the regular paired theorem and paired bootstrap are rigorous and the locked numerical validation passes in the main regime. Do not expand D4 into a general policy DAG or simultaneous alpha process before the unified manuscript is drafted.
