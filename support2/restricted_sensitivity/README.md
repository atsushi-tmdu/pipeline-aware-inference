# Diagnostic-group-restricted SUPPORT2 null sensitivity

`run_restricted_sensitivity.py` repeats the seven-algorithm SUPPORT2 search
while permuting the outcome within diagnostic group, separately in the frozen
training and model-selection splits.

This is a post hoc sensitivity analysis for a different conditional null from
the primary within-split permutation analysis. It preserves diagnostic-group
outcome prevalence while retaining the frozen data-role assignment and
predictor matrices.

## Inputs

The script requires locally reconstructed Phase 4B and Phase 4C archives. These
archives can contain participant-level data and therefore are not distributed
with this repository.

## Example

```bash
python run_restricted_sensitivity.py \
  --frozen-zip /path/to/support2_phase4b_frozen.zip \
  --phase4c-zip /path/to/support2_phase4c_full.zip \
  --n 1000 \
  --jobs 8 \
  --output-dir restricted_sensitivity_output
```

Use `--parallel-backend threading` for a low-memory smoke run. The committed
CSV and JSON files are aggregate outputs only.

## Frozen-result provenance

The 1,000-repetition aggregate results were generated before the portable
repository script was assembled. `script_provenance.json` records the SHA-256
of that internal generating script and the current path-independent repository
script. `frozen_output_manifest_sha256.csv` verifies the committed aggregate
outputs without incorrectly claiming that the portability refactor was the
byte-identical generating script.
