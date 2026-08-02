# D2 numerical validation

This directory contains the regular D2 theory, runtime preflight, and the separately locked scientific numerical validation.

## Dependencies

Python 3.10 or later with NumPy, pandas, SciPy, and matplotlib available.

## Runtime-only preflight

```bash
bash theory/policy_search_size/work_package_d2/run_preflight.sh
```

## Smoke test

```bash
bash theory/policy_search_size/work_package_d2/run_d2_validation_smoke.sh
```

## Create and verify the lock manifest

```bash
python3 theory/policy_search_size/work_package_d2/make_d2_lock_manifest.py
python3 theory/policy_search_size/work_package_d2/verify_d2_lock_manifest.py
```

## Full scientific run

Run only after the D2 lock commit and tag have been pushed:

```bash
bash theory/policy_search_size/work_package_d2/run_d2_validation_full.sh
```

The full-run script requires the lock tag to be an ancestor of HEAD and the tracked working tree to be clean.
