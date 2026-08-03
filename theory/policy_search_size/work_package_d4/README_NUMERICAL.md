# D4 numerical validation

The locked scientific target is the paired adaptive-versus-budget-matched-random contrast on both rejection-probability and TESS scales.

## Interval hierarchy

1. paired complete-replication two-bank bootstrap-normal interval - primary;
2. paired percentile interval - secondary;
3. paired basic interval - diagnostic;
4. oracle influence-function normal interval - diagnostic;
5. evaluation-only oracle interval - misspecification diagnostic.

A deliberately unpaired bootstrap is run only on a prespecified subset of outer datasets. It is diagnostic and is expected to lose the covariance benefit of the paired comparison.

## Smoke test

```bash
bash theory/policy_search_size/work_package_d4/run_d4_validation_smoke.sh
```

Smoke outputs are not scientific evidence.

## Full run

The full run is permitted only after the lock commit and tag exist:

```bash
bash theory/policy_search_size/work_package_d4/run_d4_validation_full.sh
```

Required tag:

```text
tess-theory-work-package-d4-v1-lock-20260802
```
