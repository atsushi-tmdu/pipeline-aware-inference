# Manuscript figures

The `scripts/` directory contains the programs used to generate the five
manuscript figures.

The `frozen_results/` directory contains the frozen machine-readable result
archive used by the figure scripts. Figure generation does not refit models,
rerun null-reference analyses, or reevaluate the SUPPORT2 test set.

## Reproduction

From the repository root, run:

```bash
bash figures/scripts/run_all.sh
```

Generated figures are written to:

```text
figures/scripts/output/
```
