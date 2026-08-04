# Work Package D7

Maximum-score activation-trigger extension of the D6 finite-candidate theory.

D7 replaces the separate scalar activation score with

\[
T=\max_{j\in\mathcal J_0}X_j.
\]

The first theorem studies the regular regime in which the maximum-trigger
threshold differs from every base candidate rejection threshold.

At exact threshold coincidence, the directional derivative contains a
positive-part term and ordinary bootstrap validity is not presumed.

No D7 scientific computation has been run.

## Initial implementation scaffold

`d7_core.py` implements the maximum-trigger policy state, generalized-inverse
maximum quantile, regular threshold-separation audit, inherited D6 candidate
jump field, exact coincidence-relevance field, and the positive-part
directional term.

The initial tests are algebra and implementation checks only. They are not
scientific numerical validation.

## Runtime-only derivative preflight

The preflight compares common-random-number finite differences against:

- candidate winner-region boundary derivatives;
- the maximum-trigger boundary decomposition;
- the maximum-density winner-region identity;
- the exact-coincidence positive-part kink.

Its outputs are ignored and are not scientific evidence.

## Theory completion

`D7_THEORY_MEMO.md` now contains the formal maximum-density decomposition,
regular maximum-trigger two-bank theorem, TESS expansion,
complete-replication bootstrap theorem, candidate plus-one bridge, and the
candidate/trigger threshold-coincidence nonregularity theorem.

The next step is the frozen empirical trigger-separation and trigger-tie audit,
followed by a prospective scientific numerical protocol.

## Empirical historical-surrogate audit

A read-only audit found two complete historical 20-candidate raw banks. Across
the declared alpha grid, neither library exhibited candidate/trigger threshold
coincidence or a gap within one local score spacing.

The banks did exhibit discrete base-winner ties (`12/10000` and `4/10000`).
No raw bank matched the hashes in the current confirmatory manifests, so this
is a descriptive historical-surrogate audit rather than a formal bridge to the
current frozen empirical policy.

See `D7_EMPIRICAL_AUDIT_ADJUDICATION.md` and
`empirical_audit/historical_surrogates_v1/`.
