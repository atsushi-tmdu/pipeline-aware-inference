# D8-A TESS Finite-Status Alignment Audit v1

## Status

**Source-level alignment: PASS**  
**Raw scientific-output reinspection: pending execution of the accompanying verifier**

## Repaired theoretical estimand

The repaired theorem concerns

\[
E(
\widehat\Delta_S^{\mathrm{fin}}
\mid
\mathcal F_{B,n}
),
\qquad
\mathcal F_{B,n}
=
\{
\widehat\pi_A<1,\,
\widehat\pi_C<1
\}.
\]

Boundary statuses are reported separately.

## Locked runner behavior

The locked runner was designed before the scientific run to:

1. retain four TESS statuses:
   - finite;
   - positive infinity;
   - negative infinity;
   - indeterminate when both empirical probabilities equal 1;
2. leave boundary observations unclipped;
3. calculate the scalar mean only from records with status `finite`;
4. record the count and fraction of every boundary status; and
5. fail the primary largest-pair TESS criterion if any record is nonfinite.

This behavior matches the repaired theoretical decomposition into a finite-status mean and a complementary boundary-status probability.

## Frozen numerical result

The frozen validation reports zero nonfinite records in the 17 primary classes at both \(\alpha=0.01\) and \(0.05\) for \(B=n=10{,}000\). Consequently, in those acceptance cells,

\[
\text{finite-status mean}
=
\text{mean over all simulated records}.
\]

The already reported observed biases and residuals therefore require no numerical alteration if raw-output reinspection confirms the frozen summary.

## What the verifier checks

The accompanying script performs three deterministic checks without rerunning a simulation:

1. imports the locked runner summary code and verifies on synthetic records that nonfinite observations are excluded from the finite-value mean but retained in status counts;
2. searches the frozen publication outputs for the reported zero-nonfinite primary result; and
3. inspects primary combined-job summaries, when their schema permits, for finite-summary and nonfinite-count records.

The verifier does not alter the repository, output files, acceptance criteria, seeds, or scientific conclusions.

## Reuse decision

- Policy-probability simulation: **no rerun required**
- Exact finite-\(n\) simulation: **no rerun required**
- TESS simulation: **no rerun expected**
- Remaining gate: deterministic finite-status/raw-output alignment verification

The historical checkpoint and scientific-run locks remain unchanged.
