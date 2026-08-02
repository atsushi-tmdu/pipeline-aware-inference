# Work Package D1 Numerical Validation Protocol v1

## Status

**Locked before the scientific numerical run.**

This protocol validates the regular D1 theorem for a fixed local threshold and a known activation trigger. It does not modify the locked empirical TESS study and does not constitute evidence about the SUPPORT2 or mixed-realistic model libraries.

## Parent theory

- Parent protocol: `tess-theory-work-package-d0-v1-lock-20260802`
- Planned D1 lock tag: `tess-theory-work-package-d1-v1-lock-20260802`
- Planned D1 final tag: `tess-theory-work-package-d1-v1-final-20260802`

## Scientific question

Does the finite-sample behavior of the D1 estimator agree with the derived two-bank asymptotic linear expansion, asymptotic variance, TESS delta-method result, and complete-replication two-bank bootstrap under an exact benchmark law?

## Exact benchmark law

For every design cell,

\[
U,X_0,X_1 \stackrel{\mathrm{ind}}{\sim} N(0,1).
\]

The activation rate is fixed at

\[
r=0.5,
\]

and the activation trigger is the known population threshold

\[
c=\Phi^{-1}(1-r)=0.
\]

Candidate thresholds are estimated from the reference bank by the declared empirical generalized-inverse quantile convention. The evaluation bank is independent of the reference bank.

For local threshold \(\alpha\), the exact population quantities are

\[
\pi(\alpha)=\alpha+(1-\alpha)r\alpha,
\]

with the analytic evaluation- and reference-bank influence variances defined in the D1 theory memo. These exact values are the sole numerical source of truth.

## Locked design grid

Local thresholds:

\[
\alpha\in\{0.01,0.05,0.10\}.
\]

Reference/evaluation sizes:

\[
(B,n)\in\{(500,500),(1000,1000),(3000,3000),(3000,5000)\}.
\]

This gives 12 validation cells.

Per cell:

- outer Monte Carlo repetitions: **3,000**;
- complete-replication two-bank bootstrap repetitions per outer dataset: **999**;
- master seed: **20260921**;
- default worker processes: **24**;
- deterministic seeds are derived from the master seed, cell index, and outer-replication index, so results do not depend on scheduling order.

The settings were chosen from the runtime-only preflight. Debug estimates from the preflight were not used to choose scientific cells, success thresholds, or conclusions.

## Intervals and quantities

For rejection probability and TESS, the validation records:

1. empirical bias;
2. empirical variance versus the exact asymptotic variance;
3. mean two-bank bootstrap standard deviation versus empirical Monte Carlo standard deviation;
4. exact-oracle asymptotic-normal 95% coverage;
5. **basic 95% interval from the centered two-bank bootstrap** — the primary bootstrap interval;
6. percentile and bootstrap-normal intervals — secondary descriptions;
7. evaluation-only oracle-normal coverage — a diagnostic showing the consequence of ignoring reference-bank variation.

The ordinary bootstrap resamples complete reference vectors and complete evaluation vectors independently. Candidate quantiles are recomputed inside every reference bootstrap draw.

## Prespecified primary cells

The stricter criteria apply to:

- \((B,n,\alpha)=(1000,1000,0.05)\);
- \((3000,3000,0.05)\);
- \((3000,5000,0.05)\).

## Success criteria

### Primary cells

For both rejection probability and TESS:

- absolute standardized bias \(\le 0.12\);
- empirical/exact variance ratio in \([0.88,1.12]\);
- mean bootstrap-SD/empirical-SD ratio in \([0.88,1.12]\);
- oracle-normal and basic-bootstrap 95% coverage in \([0.93,0.97]\).

### All declared cells

For both rejection probability and TESS:

- absolute standardized bias \(\le 0.20\);
- empirical/exact variance ratio in \([0.80,1.20]\);
- mean bootstrap-SD/empirical-SD ratio in \([0.80,1.20]\);
- oracle-normal and basic-bootstrap 95% coverage in \([0.91,0.99]\).

### Evaluation-only diagnostic

The evaluation-only interval is not part of the scientific PASS rule. The protocol records whether:

- evaluation-only coverage falls below 0.93 in at least one cell; and
- the two-bank basic interval improves coverage by at least 0.01 in at least four cells.

## Adjudication

- **PASS:** every prespecified scientific agreement check passes.
- **REVIEW:** at least one scientific agreement check fails and must be inspected transparently. REVIEW does not by itself invalidate the analytic theorem; finite-sample behavior, Monte Carlo variability, implementation, and criteria must be separated.

The full run must not be repeated with changed settings after inspecting results. Any revised design requires a new versioned protocol.

## Output

The full run writes:

- `D1_VALIDATION_REPLICATIONS.csv.gz`;
- `D1_VALIDATION_CELL_SUMMARY.csv`;
- `D1_VALIDATION_CHECKS.json`;
- `D1_VALIDATION_SUMMARY.json`;
- `D1_VALIDATION_ADJUDICATION.md`;
- `D1_VALIDATION_MANIFEST.json`.

The manifest records source commit/tag, config hash, software environment, file sizes, and SHA-256 hashes.

## Runtime preflight correction

The first runtime preflight labeled peak resident memory as MB using Linux units. On macOS, `resource.getrusage(...).ru_maxrss` is returned in bytes rather than KiB. The reported `28788.0 MB` therefore corresponds to approximately **28.1 MiB**, not 28.8 GB. The corrected preflight script records both the raw value and platform-aware MiB conversion.
