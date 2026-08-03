# D6 Numerical Validation Adjudication

**Status: FAIL**

This is the locked scientific numerical validation adjudication.

## Execution

- Full-grid replication rows: 72000
- Bootstrap outer-dataset rows: 6000
- Elapsed seconds: 2042.590

## Fatal implementation checks

- all_dgp_covariances_positive_definite: PASS
- full_grid_row_count: PASS
- bootstrap_row_count: PASS
- covariance_identity: PASS
- plus_one_support: PASS
- plus_one_index_gap: PASS
- finite_full_grid: PASS
- finite_bootstrap: PASS
- zero_bootstrap_failures: PASS
- nonempty_required_outputs: PASS

## Scientific checks

- delta_pi_bias_per_cell: PASS
- delta_pi_median_bias: PASS
- delta_pi_variance_ratio_per_cell: PASS
- delta_pi_median_variance_ratio: PASS
- delta_pi_coverage_per_cell: PASS
- delta_pi_mean_coverage: PASS
- delta_s_bias_per_cell: FAIL
- delta_s_median_bias: PASS
- delta_s_variance_ratio_per_cell: PASS
- delta_s_median_variance_ratio: PASS
- delta_s_coverage_per_cell: PASS
- delta_s_mean_coverage: PASS
- delta_pi_bootstrap_sd_cells: PASS
- delta_pi_bootstrap_sd_median: PASS
- delta_pi_bootstrap_coverage_cells: PASS
- delta_pi_bootstrap_coverage_mean: PASS
- delta_s_bootstrap_sd_cells: PASS
- delta_s_bootstrap_sd_median: PASS
- delta_s_bootstrap_coverage_cells: PASS
- delta_s_bootstrap_coverage_mean: PASS
- plus_one_sequences: PASS

## Scope

This validation concerns fixed finite candidate pools, continuous unique winners, candidate-specific calibration, and a separate scalar activation trigger.

It is not direct evidence for maximum-score activation, deterministic tie rules, failed-fit fallback, growing candidate dimension, or simultaneous alpha-process inference.
