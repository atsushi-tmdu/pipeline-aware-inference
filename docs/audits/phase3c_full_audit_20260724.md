# Phase 3C Full Simulation Audit

## Verdict

**Scientific audit: PASS.** The full Phase 3C results support inclusion in the next manuscript version without further simulation reruns.

## Frozen design verified

- Libraries: `high_dependency_linear_20`, `mixed_realistic_20`
- Candidate pools: K=7 and K=20, paired within each replication
- Oracle AUROCs: 0.50, 0.60, 0.65
- Selection events: 100
- Feature selection: none
- Primary metric: AUROC
- Null reference repetitions: 10,000 per library
- Evaluation repetitions: 2,000 per AUROC and library
- Master seed: 20260726

## Raw-data integrity

For each library:

- Null model rows: 200,000 = 10,000 × 20
- Evaluation model rows: 120,000 = 2,000 × 3 × 20
- Inference rows: 60,000 = 2,000 × 3 × 2 pools × 5 methods
- Duplicate analysis keys: 0
- Reference/evaluation seed overlap: 0
- Missing or nonfinite AUROC values: 0
- Candidate fit failures: 0
- Run completion flag: true
- Candidate manifest SHA-256: verified

The same dataset seed schedules were used across the two libraries, as intended for paired library comparisons, while independent seed namespaces separated the null-reference and evaluation banks.

## Main findings reproduced from raw inference files

### Type I error: pipeline-aware empirical method

- High-dependence K=7: 0.0550
- High-dependence K=20: 0.0530
- Mixed-realistic K=7: 0.0430
- Mixed-realistic K=20: 0.0465

### Primary power contrast

High-dependence library, K=20, oracle AUROC 0.60:

- Pipeline-aware power: 0.555
- Bonferroni power: 0.310
- Difference: +0.245
- Paired bootstrap 95% CI: +0.226 to +0.264
- Pipeline-only rejections: 490
- Bonferroni-only rejections: 0

### Confirmatory mixed-library contrast

Mixed-realistic library, K=20, oracle AUROC 0.60:

- Pipeline-aware power: 0.478
- Bonferroni power: 0.382
- Difference: +0.096
- Paired bootstrap 95% CI: +0.083 to +0.109

### Effective search size

- High-dependence: K_eff 1.199 at K=7; 1.215 at K=20
- Mixed-realistic: K_eff 3.091 at K=7; 3.581 at K=20

## Required packaging cleanup before public release

These are documentation/release issues, not reasons to rerun the simulations.

1. Replace pilot labels in the full summary:
   - `Phase 3C pilot go/no-go report`
   - `GO TO FULL`
   - `phase3c_pilot_master_summary.csv`
   with full-analysis labels such as `FULL SUCCESS` and `phase3c_full_master_summary.csv`.
2. Explain or replace the engine-generated `quick` label in full-run directory names. Preserve the frozen raw outputs; use a clear public-facing wrapper/README rather than altering numerical files.
3. Remove absolute local paths from public configs and logs.
4. Exclude `__pycache__` and `.pyc` files.
5. Add a reproducible `run_phase3c_full.sh` (or a stage-aware general runner); the supplied shell script is pilot-specific.
6. Add compact derived files from existing raw results, without rerunning:
   - candidate winner frequencies
   - K=7 versus K=20 power-preservation contrasts
7. Do not commit duplicate large raw CSVs and nested ZIPs directly into the Git tree. Keep code/config/compact summaries in GitHub and place the frozen raw archive in the release/Zenodo assets.

## Recommended next decision

The holdout/nested-CV comparison is not required before initial submission. Phase 3C already supplies a strong, coherent extension. Add a concise conceptual comparison in the manuscript. If an empirical holdout comparison is nevertheless pursued, it should be run now on a separate branch before the manuscript, GitHub release, and Zenodo version are updated—not afterward.
