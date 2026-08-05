# D8-A Scientific Runner Engine

This package implements the scientific family-job engine beneath the
prelocked D8-A run infrastructure.

It supports:

- the 25 latent scientific equivalence classes;
- 75 prelocked family jobs;
- reference-only, evaluation-only, and combined families;
- exact prelocked seed namespaces;
- nested sample-size prefixes;
- deterministic Gaussian population targets;
- policy and TESS outputs;
- atomic JSONL batches;
- strict resume scans.

The package is not yet an engine lock. Its only executed output is an
engineering-only smoke test using two diagnostic classes and 20 replicates
per family job.

The scientific output root is not created or modified.
