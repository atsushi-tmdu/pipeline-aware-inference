# Pipeline-aware max-statistic inference after clinical machine-learning model search

This repository contains the code and frozen aggregate outputs for a study of
pipeline-aware max-statistic calibration after adaptive clinical machine-learning
model search. The method repeats the complete declared analytical pipeline under
the declared null mechanism and calibrates the maximum performance returned by
the search, rather than treating the selected model as though it had been fixed
in advance.

## Repository contents

- `simulations/`: Phase 1–3B programs evaluating type I error, power, event
  prevalence, metric choice, feature selection, candidate-library dependence,
  and signal representation.
- `support2/`: acquisition audit, frozen split construction, locked model search,
  untouched-test lock verification, and a diagnostic-group-restricted
  permutation sensitivity analysis for the public SUPPORT2 dataset.
- `figures/`: scripts and a frozen aggregate archive used to generate manuscript
  Figures 1–5.
- `supplementary/`: machine-readable and formatted Supplementary Tables S1–S6.
- `tools/`: release audit and smoke-test helpers.

## Environment

The principal frozen analyses used Python 3.13 and the exact package versions in
`requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce Figures 1–5

From the repository root:

```bash
bash figures/scripts/run_all.sh
```

Generated files are written to `figures/scripts/output/`. Figure generation reads
only the frozen aggregate archive in `figures/frozen_results/`; it does not refit
models or reopen the SUPPORT2 test set.

## Run smoke tests

The release helper runs syntax checks, portable-import checks, figure generation,
and smoke presets for Phases 1–3B. Outputs are written outside the repository.

```bash
bash tools/run_release_smoke_tests.sh
```

The optional SUPPORT2 check downloads the public dataset, reconstructs the frozen
split, runs a sealed Phase 4C smoke search, verifies the Phase 4D lock in dry-run
mode, and runs a five-repetition restricted-permutation functional test:

```bash
bash tools/run_release_smoke_tests.sh --with-support2
```

**The helper never opens or evaluates the SUPPORT2 test set.**

## Simulation programs

Phase-specific programs can be run directly from the repository root or by
absolute path from outside the repository; no manual `PYTHONPATH` setting is
required.

```bash
python simulations/phase1/pipeline_null_pilot_v2.py --preset smoke --n-jobs 2
python simulations/phase2/pipeline_signal_phase2.py --preset smoke --n-jobs 2
python simulations/phase3/pipeline_independent_null_phase3.py --help
python simulations/phase3b/pipeline_model_library_phase3b.py --help
```

The smoke and quick presets are functional checks and do not reproduce the full
Monte Carlo precision reported in the manuscript. Frozen aggregate results used
for the manuscript figures and tables are included separately.

## SUPPORT2 data source and workflow

The study uses the public SUPPORT2 dataset from the UCI Machine Learning
Repository:

- UCI dataset ID: 880
- Dataset page: <https://archive.ics.uci.edu/dataset/880/support2>
- Dataset DOI: <https://doi.org/10.3886/ICPSR02957.v2>

Participant-level SUPPORT2 records are **not** distributed in this repository.
The scripts obtain and process the public dataset locally:

1. `support2/support2_phase4a_audit.py` downloads and audits the source data.
2. `support2/support2_phase4b_freeze.py` reconstructs the prespecified split.
3. `support2/support2_phase4c_locked_search.py` performs model search while
   keeping the test split sealed.
4. `support2/support2_phase4d_open_test.py` verifies the locked analysis and can
   evaluate the untouched test set only after an explicit confirmation.

For routine reproducibility checks, use Phase 4D in **dry-run mode only**:

```bash
python support2/support2_phase4d_open_test.py \
  --frozen-zip path/to/support2_phase4b_frozen.zip \
  --phase4c-zip path/to/support2_phase4c_full.zip \
  --dry-run \
  --output-root path/to/phase4d_dry_run
```

The final untouched-test analysis reported in the manuscript has already been
performed. It should not be repeated merely to verify installation.

For a low-memory Phase 4C smoke run:

```bash
python support2/support2_phase4c_locked_search.py \
  --frozen-zip path/to/support2_phase4b_frozen.zip \
  --preset smoke \
  --parallel-backend threading \
  --n-jobs 2 \
  --output-root path/to/phase4c_smoke
```

## Restricted-permutation sensitivity analysis

The post hoc sensitivity analysis permutes outcomes within diagnostic group,
separately in the frozen training and model-selection splits:

```bash
python support2/restricted_sensitivity/run_restricted_sensitivity.py \
  --frozen-zip path/to/support2_phase4b_frozen.zip \
  --phase4c-zip path/to/support2_phase4c_full.zip \
  --n 1000 \
  --jobs 8 \
  --output-dir path/to/restricted_sensitivity
```

The committed CSV and JSON files in `support2/restricted_sensitivity/` are
aggregate outputs only.

## Data-safety boundary

The repository contains source code, configuration information, aggregate
outputs, figure/table inputs, and provenance metadata. It does **not** contain:

- participant-level SUPPORT2 records;
- frozen participant-level split archives;
- test-set prediction files;
- fitted participant-level model objects;
- credentials, private keys, or restricted-use data.

Run the current-tree audit with:

```bash
python tools/release_audit.py --current-tree-only
```

Additional details are provided in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Citation

The target software release is version 1.0.0. A permanent Zenodo DOI will be
added after archival. Citation metadata are provided in `CITATION.cff`.

When using the clinical example, also cite the SUPPORT2 dataset and its original
study.

## Manuscript status

The accompanying manuscript is being prepared for submission to the *Journal of
the American Medical Informatics Association* as a Research and Applications
article.

## Author

Atsushi Senda, MD, PhD  
ORCID: <https://orcid.org/0000-0002-0128-6800>

## License

MIT License. See [`LICENSE`](LICENSE).
