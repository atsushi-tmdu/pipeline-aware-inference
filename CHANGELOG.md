# Changelog

## 1.1.0 — 2026-07-25

Scalability and release-engineering update for the accompanying manuscript.

Zenodo concept DOI: `10.5281/zenodo.21482698`.

The version-specific DOI for v1.1.0 will be assigned after Zenodo
archives the GitHub release.

### Added

- Prospectively gated Phase 3C scalability extension comparing nested
  K=7 and K=20 candidate pools.
- High-dependence linear and mixed-realistic 20-candidate libraries.
- Frozen Phase 3C aggregate results, candidate manifests, dependence
  summaries, null-maximum summaries, winner frequencies, and paired
  power contrasts.
- Audited sanitized Phase 3C public-release package and internal
  checksum manifest.
- Phase 3C configuration files, runner scripts, library tests, and
  scientific audit report.

### Changed

- Generalized repository-path sanitization so public artifacts do not
  depend on a specific local username or operating system.
- Extended the reproducibility materials from Phase 3B through Phase 3C.

### Validation

- Candidate-library determinism and nested K=7/K=20 membership checks
  passed.
- Pipeline-aware global-null type I error ranged from 0.043 to 0.055
  across the four Phase 3C library-by-K conditions.
- The prespecified high-dependence K=20 power difference at oracle
  AUROC 0.60 was 0.245 (95% CI, 0.226-0.264).
- Public-release internal checksums, ZIP integrity, and personal-path
  audits passed.

## 1.0.0 — 2026-07-22

Initial public software release for the accompanying manuscript.

Archived release DOI: `10.5281/zenodo.21482699`.

### Included

- Phase 1–3B simulation programs.
- Public SUPPORT2 acquisition, split-freeze, locked-search, and dry-run lock
  verification workflow.
- Diagnostic-group-restricted permutation sensitivity implementation and frozen
  aggregate outputs.
- Figure 1–5 reproduction from a frozen aggregate archive.
- Supplementary Tables S1–S6 in formatted and machine-readable formats.
- Pinned principal software environment.
- Release smoke tests and privacy/secrets/path audit tooling.

### Data-safety boundary

Participant-level SUPPORT2 records, frozen participant-level splits, test-set
predictions, and fitted participant-level model objects are not distributed.
