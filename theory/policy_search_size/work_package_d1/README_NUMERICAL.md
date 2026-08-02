# D1 Numerical Validation

## Apply before the scientific run

1. Run the corrected runtime preflight if desired.
2. Run the smoke test.
3. Generate `D1_LOCK_MANIFEST.json`.
4. Commit all D1 theory and numerical-protocol source files.
5. Tag the commit `tess-theory-work-package-d1-v1-lock-20260802`.
6. Push the branch and lock tag.
7. Run the full validation exactly once under the locked configuration.

## Corrected runtime preflight

```bash
bash theory/policy_search_size/work_package_d1/run_preflight.sh
```

On macOS the corrected output reports `peak_resident_memory_mib`. The earlier `28788.0 MB` value was a platform-unit conversion error and corresponds to about 28.1 MiB.

## Smoke test

```bash
bash theory/policy_search_size/work_package_d1/run_d1_validation_smoke.sh
```

The smoke test is computational debugging only and is not scientific evidence.

## Create the lock manifest

```bash
python3 theory/policy_search_size/work_package_d1/make_d1_lock_manifest.py
python3 theory/policy_search_size/work_package_d1/verify_d1_lock_manifest.py
```

## Full run after commit/tag

```bash
caffeinate -dimsu \
  bash theory/policy_search_size/work_package_d1/run_d1_validation_full.sh \
  2>&1 | tee "$HOME/Documents/pipeline-aware-confirmatory-logs/d1_numerical_validation_v1_20260802.log"
```

Full outputs are written below `outputs/full_v1/` and are ignored until selected processed outputs are explicitly added after review.
