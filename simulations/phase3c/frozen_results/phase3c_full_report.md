# Phase 3C full-analysis status

- Decision: **FULL SUCCESS**
- Scientific audit: **PASS**
- Maximum pipeline-aware Type I error across full null cells: `0.0550`
- Primary power difference (pipeline-aware minus Bonferroni): `0.2450`
- Paired 95% CI: `0.2260` to `0.2640`
- Prespecified GO threshold: `0.0500`

Primary cell: `high_dependency_linear_20`, K=20, oracle AUROC=0.60.

The internal engine directory name contains `quick` because Phase 3C reused the validated Phase 3 engine. The authoritative design is the full configuration: 10,000 null-reference repetitions and 2,000 evaluation repetitions per AUROC and library.
