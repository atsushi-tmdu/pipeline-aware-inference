# D8-A Precision-Contract Gap Adjudication

## Formal status

**Status:** `ACCEPTANCE_SCALES_PARTIALLY_RECOVERED_STOPPING_CONTRACT_INCOMPLETE`
**Runner engine locked:** no
**Scientific output root touched:** no
**Scientific simulation run:** no

## Audit correction

The historical precision-scaling reconstruction reported
`PARTIAL_SCALING_EVIDENCE_FOUND`, but its Python candidates are bias and
asymptotic-approximation formulas rather than MCSE definitions.

Every candidate in that audit has `has_se_token=false`.

Consequently, the candidate counts for the reference-only and combined
families are not evidence that a Monte Carlo stopping statistic was defined.

## What is historically recoverable

### Reference approximation

The committed acceptance document defines the MCSE-adjusted normalized
residual

\[
\frac{
\left[
\left|B\{\widehat{\operatorname{Bias}}_R-C_B/B\}\right|
-z_\star B\,\operatorname{MCSE}
\right]_+
}{
1+|C_B|
}.
\]

This identifies the reference-family MCSE scale

\[
\frac{B\,\operatorname{MCSE}}{1+|C_B|}.
\]

### Combined policy approximation

The committed design specifies the normalization denominator

\[
(B^{-1}+n^{-1})
(1+|C_{\Delta,B}|+|\Delta_\pi|).
\]

### Combined TESS approximation

The committed design specifies the normalization denominator

\[
(B^{-1}+n^{-1})
(1+|C_{S,R,B}|+|C_{S,E}|).
\]

These are acceptance-metric scales. They do not by themselves define the
full sequential stopping contract.

## What remains undefined

The committed sources do not uniquely specify:

1. the Monte Carlo variance estimator and degrees-of-freedom convention;
2. the evaluation-only scaled-MCSE denominator;
3. whether the 0.03 target is applied pointwise, by maximum, or by another
   aggregation over sample sizes and estimands;
4. which policy and TESS outputs enter the stopping maximum;
5. a diagnostic-class precision target or an alternative fixed diagnostic
   replicate rule;
6. how nonfinite TESS boundary records participate in precision stopping;
7. the exact simultaneous critical value \(z_\star\) outside the final
   acceptance calculation.

## Consequence

The runner engine may not be locked and the scientific run may not begin
until a prospective precision-contract amendment resolves these points.

The amendment must be completed before any scientific output is generated.
