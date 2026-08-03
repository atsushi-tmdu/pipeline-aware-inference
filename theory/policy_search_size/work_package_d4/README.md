# Work Package D4

Paired two-bank inference for the budget-matched adaptive-policy TESS contrast.

## Status before the scientific run

- theory derivation: complete in the declared regular one-candidate-per-branch model;
- runtime-only preflight: completed locally and not scientific evidence;
- numerical validation protocol: ready to be locked;
- scientific validation: not yet run.

## Required order

```bash
bash theory/policy_search_size/work_package_d4/run_d4_validation_smoke.sh
python3 theory/policy_search_size/work_package_d4/make_d4_lock_manifest.py
python3 theory/policy_search_size/work_package_d4/verify_d4_lock_manifest.py
```

Commit and tag the complete D4 directory before running the full validation.
