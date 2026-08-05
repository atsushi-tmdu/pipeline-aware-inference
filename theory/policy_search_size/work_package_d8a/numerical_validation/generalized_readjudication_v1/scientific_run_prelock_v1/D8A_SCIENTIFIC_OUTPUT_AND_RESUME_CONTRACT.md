# D8-A Scientific Output and Resume Contract

## Output root

The locked output root is specified in
`D8A_SCIENTIFIC_RUN_CONFIG.json`.

It must not exist before the final scientific run begins.

## Directory structure

Each family job receives an immutable directory:

```text
<output-root>/
  RUN_METADATA.json
  jobs/
    <job-id>/
      JOB_CONFIG.json
      batches/
        batch_<first>_<last>.jsonl
      JOB_STATUS.json
      SUMMARY.json
```

## Atomic writes

Every batch is written to a sibling temporary file and committed with
`os.replace`.

A batch is valid only if:

- its final filename matches its replicate interval;
- its JSONL rows parse;
- every row has the expected job ID;
- replicate indices are contiguous and unique;
- its SHA-256 digest is recorded in `JOB_STATUS.json`.

## Resume

A resumed run must:

1. verify the implementation, run-package, and job hashes;
2. scan only committed batch files;
3. reject overlapping or noncontiguous replicate intervals;
4. continue at the first missing replicate index;
5. regenerate no completed replicate;
6. preserve the original seed namespace;
7. leave acceptance criteria unchanged.

Temporary files are never treated as completed output.

## Completion

The top-level `COMPLETE` marker may be written only after all 75 family jobs
have valid summaries and the final scientific adjudication package has been
created.
