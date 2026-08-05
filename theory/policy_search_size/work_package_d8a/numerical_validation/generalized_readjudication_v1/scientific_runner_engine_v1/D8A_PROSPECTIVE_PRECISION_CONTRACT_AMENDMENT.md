# D8-A Prospective Natural-Scale Precision-Contract Amendment

## Status

**Amendment ID:** `TESS_D8A_PROSPECTIVE_NATURAL_SCALE_PRECISION_CONTRACT_AMENDMENT_V3`
**Adopted before scientific output:** yes
**Supersedes:** uncommitted studentized V1 and rate-aware V2
**Runner engine locked:** no
**Scientific output root touched:** no
**Scientific simulation run:** no

## Separation of purposes

Two distinct scales are required.

1. **Sequential stopping** asks whether the Monte Carlo estimate of each
   registered estimand is numerically precise.
2. **Final acceptance** asks whether an observed approximation residual is
   small relative to its theoretical \(B^{-1}\), \(n^{-1}\), or combined
   asymptotic rate.

The asymptotic bias-rate denominator is retained only for final acceptance.
Using it for stopping was prospectively rejected because it required
millions of replicates in engineering-only diagnostic cases.

## Monte Carlo variance estimator

For scalar replicate output \(Y_1,\ldots,Y_R\),

\[
\widehat{\operatorname{Var}}(Y)
=
\frac{1}{R-1}
\sum_{r=1}^{R}(Y_r-\bar Y)^2,
\qquad
\operatorname{MCSE}(\bar Y)
=
\frac{\widehat{\operatorname{SD}}(Y)}{\sqrt R}.
\]

The variance estimator uses `ddof=1`.

## Natural oracle scale for stopping

For a scalar estimand with locked population target \(\tau\),

\[
s_{\mathrm{nat}}(\tau)
=
1+|\tau|,
\]

and

\[
\operatorname{scaledMCSE}_{\mathrm{stop}}
=
\frac{\operatorname{MCSE}}{1+|\tau|}.
\]

The population target is calculated only from the locked DGP and locked
deterministic Gaussian oracle. It does not use observed Monte Carlo means,
biases, residuals, signs, or agreement with theory.

The scale is dimensionless after expressing each output on its registered
estimand scale.

## Stopping-driving outputs

The maximum stopping scaled MCSE is taken over every registered sample-size
point.

### Reference-only

- adaptive probability, target \(\pi_A\);
- comparator probability, target \(\pi_C\);
- policy contrast, target \(\Delta_\pi\);
- each TESS contrast, target \(S_\alpha(\pi_A)-S_\alpha(\pi_C)\).

### Evaluation-only and combined

- adaptive estimate, target \(\pi_A\);
- comparator estimate, target \(\pi_C\);
- policy contrast, target \(\Delta_\pi\);
- each TESS contrast, target \(S_\alpha(\pi_A)-S_\alpha(\pi_C)\).

The same locked population targets are used across registered \(B\) and
\(n\); each registered point is nevertheless assessed separately.

## TESS boundary records

For each TESS boundary status, its Bernoulli status proportion uses
denominator 1.

For finite TESS values:

- at least two finite records: use
  \(1+|S_\alpha(\pi_A)-S_\alpha(\pi_C)|\);
- one finite record: precision failure;
- zero finite records: finite-value mean not applicable.

Boundary records are never discarded or clipped.

Any nonfinite TESS record in a primary largest-pair acceptance cell is a
formal TESS-criterion failure and is reported by status.

## Aggregation and stopping

A family job passes precision only when the maximum stopping scaled MCSE
over all registered points and outputs is at most 0.03.

The same target applies to primary and diagnostic classes.

The locked role-specific minimum, batch, and maximum replicate counts remain
unchanged. A diagnostic job may reach its maximum without precision; this is
reported but does not enter the historical primary precision-limited
fraction. A primary job reaching its maximum without precision is
precision-limited.

## Final MCSE-adjusted acceptance

Final acceptance continues to use the historical rate-aware scales.

### Reference approximation

\[
\frac{B\,\operatorname{MCSE}}{1+|C_B|}.
\]

### Combined policy approximation

\[
\frac{\operatorname{MCSE}}
{(B^{-1}+n^{-1})(1+|C_{\Delta,B}|+|\Delta_\pi|)}.
\]

### Combined TESS approximation

\[
\frac{\operatorname{MCSE}}
{(B^{-1}+n^{-1})(1+|C_{S,R,B}|+|C_{S,E}|)}.
\]

These acceptance scales do not drive stopping.

## Simultaneous critical values

Final MCSE-adjusted acceptance uses two-sided Bonferroni critical values at
familywise level 0.01. Exact counts and values are stored in
`D8A_PROSPECTIVE_NATURAL_SCALE_PRECISION_CONTRACT.json`.
