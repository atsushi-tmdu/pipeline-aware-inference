# D1 results freeze

This post-lock package preserves the completed D1 scientific numerical validation without modifying the locked D1 protocol or code.

## Scientific status

- Locked automatic status: `REVIEW`
- Scientific interpretation: D1 first-order two-bank theory supported; basic bootstrap interval not uniformly validated.
- The scientific run must not be repeated to obtain a different locked classification.

## Build the freeze

From the repository root:

```bash
bash theory/policy_search_size/work_package_d1/run_d1_results_freeze.sh
```

The command will:

1. verify the locked run summary;
2. copy selected reviewable outputs into `frozen_results/v1/`;
3. construct a deterministic external archive containing the complete full-v1 output, full-run log, and review output;
4. write the archive SHA-256 into a tracked results manifest;
5. verify all tracked hashes and the external archive.

Default external archive location:

```text
~/Documents/policy-search-size-theory-archives/d1_v1/
```

## Tracked versus archived material

Tracked in Git:

- summary JSON;
- checks JSON;
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

Remove the two temporary untracked root-level text files:

```bash
rm -f \
  theory/policy_search_size/work_package_d1/D1_FULL_RUN_LOG.txt \
  theory/policy_search_size/work_package_d1/D1_REVIEW_OUTPUT.txt
```

The copies required for preservation will already exist in the frozen-results directory and external archive.
