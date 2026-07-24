# Phase 3C full simulation release package

This package contains the frozen Phase 3C full analysis.

## Authoritative design

- Null-reference repetitions: 10,000 per library
- Evaluation repetitions: 2,000 per target AUROC and library
- Candidate pools: K=7 and K=20
- Target AUROCs: 0.5, 0.6, 0.65
- Selection events: 100
- Feature selection: none
- Primary metric: AUROC

## Directory naming note

The raw engine-generated run directories retain the word `quick` because the validated Phase 3 engine was reused. This label is an internal preset name only. The full configuration and row counts above define the analysis stage.

## Contents

- `compact_summary/`: GitHub-suitable derived summaries and manifests.
- `frozen_raw_sanitized/`: frozen raw outputs with numerical CSVs unchanged; absolute local paths removed from text metadata.
- `phase3c_full_status.json` and `phase3c_full_report.md`: final status labels.
- `SHA256SUMS.txt`: checksums for all files in this package except itself.
