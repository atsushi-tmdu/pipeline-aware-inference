# Pipeline-aware max-statistic inference after clinical machine-learning model search

This repository implements pipeline-aware max-statistic calibration for
inference after adaptive clinical machine-learning model search. The central
idea is to repeat the complete declared analytical pipeline under the declared
null mechanism and calibrate the maximum performance returned by the search.

## Repository contents

- `simulations/`: Phase 1–3B simulation programs for type I error, power,
  metric dependence, event prevalence, candidate-library dependence, and
  signal representation.
- `support2/`: audit, frozen split construction, locked model search,
  untouched-test evaluation, and a diagnostic-group-restricted permutation
  sensitivity analysis for the public SUPPORT2 data.
- `figures/`: scripts and frozen aggregate results used to generate manuscript
  Figures 1–5.
- `supplementary/`: Supplementary Tables S1–S9 in DOCX, XLSX, and CSV formats.

## Environment

Python 3.13 was used for the frozen analyses. Install the principal frozen
software versions with:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce the figures

```bash
bash figures/scripts/run_all.sh
```

The figure scripts read only the frozen aggregate archive in
`figures/frozen_results/`. They do not refit models or reopen the SUPPORT2 test
set.

## Simulation programs

The phase-specific scripts can be run directly from the repository root. Shared
modules are resolved from the repository layout, so the scripts do not need to
be copied into one directory.

Examples:

```bash
python simulations/phase1/pipeline_null_pilot_v2.py --preset smoke
python simulations/phase3/pipeline_independent_null_phase3.py --help
python simulations/phase3b/pipeline_model_library_phase3b.py --help
```

## SUPPORT2 workflow

Participant-level SUPPORT2 data are not distributed in this repository. Obtain
the public dataset from the UCI Machine Learning Repository (dataset ID 880)
and follow the phase scripts in order:

1. `support2_phase4a_audit.py`
2. `support2_phase4b_freeze.py`
3. `support2_phase4c_locked_search.py`
4. `support2_phase4d_open_test.py`

Phase 4C keeps the test split sealed. Phase 4D should be run only after the
winning algorithm and hyperparameters have been locked.

For a low-memory Phase 4C smoke run, the threading backend can be selected
explicitly:

```bash
python support2/support2_phase4c_locked_search.py \
  --frozen-zip path/to/support2_phase4b_frozen.zip \
  --preset smoke \
  --parallel-backend threading \
  --n-jobs 4
```

## Restricted-permutation sensitivity analysis

The post hoc sensitivity analysis permutes outcomes within diagnostic group,
separately in the frozen training and model-selection splits:

```bash
python support2/restricted_sensitivity/run_restricted_sensitivity.py \
  --frozen-zip path/to/support2_phase4b_frozen.zip \
  --phase4c-zip path/to/support2_phase4c_full.zip \
  --n 1000 \
  --jobs 8
```

Frozen aggregate sensitivity results are included in
`support2/restricted_sensitivity/`. They contain no participant-level records.

## Data-safety boundary

The repository contains code, configuration information, aggregate outputs,
and figure/table inputs. It does **not** contain participant-level SUPPORT2
records, frozen participant-level splits, credentials, or restricted-use data.

## Manuscript status

The accompanying manuscript is being prepared for submission to the *Journal
of the American Medical Informatics Association* as a Research and
Applications article. Repository release metadata and a permanent archive DOI
will be finalized separately.

## Author

Atsushi Senda, MD, PhD  
ORCID: https://orcid.org/0000-0002-0128-6800

## License

MIT License.
