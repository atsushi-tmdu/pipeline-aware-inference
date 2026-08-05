# D8-A Scientific Runner-Engine Lock

## Lock identity

- lock ID: `TESS_D8A_SCIENTIFIC_RUNNER_ENGINE_LOCK_V1`
- annotated tag: `d8a-scientific-runner-engine-lock-v1`
- parent scientific-run package:
  `d8a-scientific-run-package-prelock-v1`
- parent generalized implementation:
  `d8a-generalized-implementation-lock-v1`

## Locked scope

The lock covers the complete scientific runner engine, including:

- 75 registered family jobs;
- immutable seed namespaces;
- reference-only, evaluation-only, and combined engines;
- role-aware minimum, batch, and maximum replicate schedules;
- natural-oracle-scale Monte Carlo stopping;
- structured TESS boundary handling;
- atomic JSONL batches;
- interruption and deterministic resume;
- scientific summary and acceptance evaluators;
- job-level parallel executor;
- final execution gate.

The SHA-256 manifest excludes only the manifest, lock record, verifier, and
this lock document. Those four files are anchored by the annotated Git tag
and by the verifier requirement that `HEAD` equal the tag commit.

## Scientific status at lock

- scientific execution authorized: yes, only after tag verification;
- scientific output root touched: no;
- scientific simulation run: no.

Before the annotated tag exists at the current commit, the verifier fails and
the final execution gate remains closed.

## Historical precision amendments

The lock retains the full prospective audit trail:

1. the studentized \(R^{-1/2}\) proposal was superseded;
2. the bias-rate stopping proposal was superseded;
3. natural-oracle-scale stopping was adopted before scientific output;
4. bias-rate scales remain reserved for final MCSE-adjusted acceptance.

## Execution discipline

Scientific execution must be launched through

`run_d8a_scientific_validation_gate.py --execute`

from the exact lock-tag commit. The executor independently re-runs the lock
verifier before creating or resuming the scientific output root.
