# D8-A Runner Engine Protocol

## Family semantics

### Reference-only

For each reference-bank replicate, generate one bank at the largest
registered \(B\). Every smaller \(B\) uses a prefix of that same bank.

For each prefix:

1. calculate the empirical candidate and trigger thresholds;
2. evaluate the exact population policy probabilities at those thresholds;
3. record adaptive, comparator, and policy-contrast values;
4. record TESS contrasts for each locked \(\alpha\).

### Evaluation-only

Use the population threshold vector and generate one evaluation bank at the
largest registered \(n\). Every smaller \(n\) uses a prefix.

For each prefix, record the adaptive estimator, product-of-means comparator,
policy contrast, finite-\(n\) target, and TESS contrast.

### Combined

Generate independent reference and evaluation banks from their distinct
prelocked streams. Each registered \((B,n)\) pair uses prefixes of the same
two banks.

## Engineering boundary

The engineering smoke test uses:

- two diagnostic classes;
- three family jobs per class;
- 20 replicates per job;
- one size point per family;
- output labeled `NON_SCIENTIFIC_ENGINEERING_ONLY`.

It does not use the locked scientific output root and cannot count as
scientific evidence.
