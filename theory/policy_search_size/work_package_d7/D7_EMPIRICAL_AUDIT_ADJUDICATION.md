# D7 Empirical Audit Adjudication

## Formal status

**Exact bridge to the current frozen empirical policy: INCOMPLETE.**

No available raw candidate-score bank matched the SHA-256 recorded by the
current confirmatory or SUPPORT2 manifests. The two complete 20-candidate
banks are historical surrogates, and the available SUPPORT2 bank contains only
seven candidates and cannot be joined to the current 20-candidate manifest.

## Historical-surrogate findings

For `high_dependency_linear_20` and `mixed_realistic_20`:

- all six declared alpha values had strictly nonzero candidate/trigger
  threshold gaps;
- no candidate threshold equaled the maximum-trigger threshold;
- no candidate/trigger pair was within one local discrete score spacing;
- the smallest observed gap was `0.00045` in `mixed_realistic_20` at
  alpha `0.10`;
- base-winner score ties occurred in `12/10000` and `4/10000`
  replications, respectively;
- trigger-threshold tie mass was `1/10000` in each bank;
- the reconstructed strict activation rate was exactly `0.50`, so the
  historical banks required no probabilistic trigger-tie allocation.

## Interpretation

The audit gives descriptive support for threshold separation in the two
historical 20-candidate libraries. It does not establish the D7 regularity
conditions for the current frozen confirmatory banks because the hashes differ.

More importantly, the historical AUROC banks exhibit positive-probability
winner ties. Thus the continuous almost-sure unique-winner theorem is not an
exact empirical bridge even when candidate and trigger thresholds are
separated.

The remaining empirical gap is therefore not primarily threshold coincidence.
It is the discrete-score winner-tie rule, followed by exact reconstruction of
the current frozen raw banks and the SUPPORT2 20-candidate library.

## Consequence for the work-package ladder

D7 scientific validation may proceed in the continuous, unique-winner,
separated-threshold regime. A later work package must explicitly handle
discrete winner ties and the declared deterministic tie-breaking rule before
claiming an exact empirical-pipeline theorem.
