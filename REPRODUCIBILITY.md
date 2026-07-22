# Reproducibility and data-safety guide

Archived software release: version 1.0.0, DOI: `10.5281/zenodo.21482699`.

## Scope

This repository supports three distinct forms of reproducibility:

1. **Figure reproduction** from frozen aggregate outputs.
2. **Functional simulation checks** using smoke or quick presets.
3. **Local reconstruction of the public SUPPORT2 workflow** without
   redistributing participant-level records.

The full Monte Carlo analyses reported in the manuscript used the seeds,
repetition counts, and software environment documented in the supplementary
material. Smoke presets verify execution but do not reproduce the precision of
the full runs.

## Frozen environment

The principal frozen environment is specified in `requirements.txt`:

```bash
python3.13 --version
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Python 3.13 was used for the principal frozen analyses.

## Figure reproduction

```bash
bash figures/scripts/run_all.sh
```

The figure scripts read the aggregate archive
`figures/frozen_results/phase5a_master_results.zip`. They do not fit models,
load participant-level data, or evaluate the SUPPORT2 test set.

## Safe automated checks

Run simulations and figure checks:

```bash
bash tools/run_release_smoke_tests.sh
```

Add the locally reconstructed SUPPORT2 workflow:

```bash
bash tools/run_release_smoke_tests.sh --with-support2
```

The SUPPORT2 option performs only:

- Phase 4A acquisition and audit;
- Phase 4B split reconstruction;
- a sealed Phase 4C smoke search;
- Phase 4D lock verification with `--dry-run`;
- a five-repetition restricted-permutation functional check.

It does **not** invoke `--open-test CONFIRM` and does not calculate test-set
predictions or performance.

## Manual simulation checks

From the repository root:

```bash
python simulations/phase1/pipeline_null_pilot_v2.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase1

python simulations/phase2/pipeline_signal_phase2.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase2a

python simulations/phase2/pipeline_event_prevalence_phase2b.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase2b

python simulations/phase2/pipeline_metric_phase2c.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase2c

python simulations/phase2/pipeline_target_ap_phase2d.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase2d

python simulations/phase3/pipeline_independent_null_phase3.py \
  --preset smoke --n-jobs 2 --output-root /tmp/pipeline_phase3

python simulations/phase3b/pipeline_model_library_phase3b.py \
  --library similar_linear_7 \
  --signal-structure single_linear \
  --preset smoke \
  --n-jobs 2 \
  --output-root /tmp/pipeline_phase3b
```

## SUPPORT2 source and local files

Phase 4A retrieves UCI dataset ID 880 using `ucimlrepo`. Phase 4A and Phase 4B
archives contain participant-level information and must remain outside the Git
repository. The smoke-test helper uses a temporary directory and removes it by
default.

The original source is:

- UCI SUPPORT2: <https://archive.ics.uci.edu/dataset/880/support2>
- DOI: <https://doi.org/10.3886/ICPSR02957.v2>

## Untouched-test safeguard

`support2_phase4d_open_test.py` requires either:

- `--dry-run`, which verifies the locks without evaluating the test set; or
- an explicit confirmation value for actual test opening.

For installation checks and repository validation, use `--dry-run` only. The
untouched-test analysis reported in the manuscript has already been completed.

## Restricted-permutation provenance

The committed restricted-permutation results are aggregate outputs. Their
manifest and provenance files are in `support2/restricted_sensitivity/`.
`script_provenance.json` distinguishes the internal generating script from the
path-independent repository implementation rather than claiming byte-identical
provenance after portability refactoring.

## Release audit

Current tracked files and archive members can be checked with:

```bash
python tools/release_audit.py --current-tree-only
```

Before a public release, also scan reachable Git history:

```bash
python tools/release_audit.py --include-history
```

A public release should not be created until both commands pass from a fresh
clone of the final default branch.
