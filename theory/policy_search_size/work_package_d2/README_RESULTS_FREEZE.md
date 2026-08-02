# D2 results freeze

This post-lock package preserves the completed D2 scientific numerical validation without modifying the locked D2 protocol or code.

## Scientific status

- Locked automatic status: `PASS`
- Scientific interpretation: the estimated-trigger two-bank first-order theory and centered complete-replication bootstrap-normal inference were validated in every primary and main-regime cell.
- The scientific run must not be repeated to obtain a different classification.

## Build the freeze

From the repository root:

```bash
bash theory/policy_search_size/work_package_d2/run_d2_results_freeze.sh
```

The command will:

1. verify the locked run summary;
2. copy selected reviewable outputs into `frozen_results/v1/`;
3. construct a deterministic external archive containing the complete full-v1 output, full-run log, and review output;
4. write the archive SHA-256 into a tracked results manifest;
5. verify all tracked hashes and the external archive.

Default external archive location:

```text
~/Documents/policy-search-size-theory-archives/d2_v1/
```

## Tracked versus archived material

Tracked in Git:

- summary JSON;
- checks JSON;
- benchmark JSON;
- cell summary CSV;
- original automatic adjudication;
- validation manifest;
- post-run scientific adjudication;
- full-run log;
- results-freeze manifest.

Archived externally:

- the complete `outputs/full_v1/` directory, including replication-level data;
- full-run log;
- review-output text;
- post-run adjudication.

## After successful freeze

Remove the two temporary root-level text files:

```bash
rm -f   theory/policy_search_size/work_package_d2/D2_FULL_RUN_LOG.txt   theory/policy_search_size/work_package_d2/D2_REVIEW_OUTPUT.txt
```

The copies required for preservation will already exist in the frozen-results directory and external archive.
