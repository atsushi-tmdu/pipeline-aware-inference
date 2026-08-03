# D4 Full Numerical Validation: Results Freeze

## Identity

- Validation version: full_v1
- Validation status: PASS
- Validation cells: 36
- Raw output files: 7
- Validation elapsed time: 3734.079 seconds
- Freeze generated: 2026-08-03 12:13:19 +0900
- Git repository: /Users/sendaatsushi/Documents/pipeline-aware/pipeline-aware-inference-clean-20260803
- Git branch at freeze creation: tess-top-tier-theory
- Git HEAD before freeze commit: cb39203719730bf9a0e0a887c6ecc67ed9f7c7d7

## Scientific scope

This freeze concerns the regular Work Package D4 paired
budget-matched policy contrast.

It is not direct evidence for the exact 20-candidate empirical
pipeline.

## Prespecified design

- DGPs: independent_normal, gaussian_factor, nonlinear_smooth
- Outer repetitions per cell: 3000
- Paired bootstrap repetitions per outer dataset: 999
- Alpha grid: 0.01, 0.05, 0.10
- Master seed: 20261117
- Primary interval: centered paired complete-replication
  two-bank bootstrap-normal interval

## Adjudication

- Overall status: PASS
- Failed primary/main checks: None
- Empty output files: None
- All 36 planned validation cells completed

## Integrity

SHA-256 digest of `D4_OUTPUTS_SHA256.txt`:

`84deeaaec34a6cdd6fb89bf1bfccd9610cbae7787304a03cbf79c1ade907e9f5`

The raw numerical outputs remain under the intentionally ignored
directory:

`theory/policy_search_size/work_package_d4/outputs/full_v1/`

Compact validation evidence, an output inventory, and cryptographic
fingerprints are stored in this tracked freeze directory.
