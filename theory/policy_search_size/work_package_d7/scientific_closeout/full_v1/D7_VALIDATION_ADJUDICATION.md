# D7 Scientific Validation Adjudication

**Status: FAIL**

## Fatal checks

- covariance_positive_definite_all_dgps: PASS
- fixed_finite_nested_pools: PASS
- continuous_dgp_observed_winner_ties: PASS
- main_cell_count: PASS
- main_replication_rows: PASS
- bootstrap_cell_count: PASS
- bootstrap_outer_rows: PASS
- near_coincidence_cell_count: PASS
- exact_coincidence_cell_count: PASS
- minimum_standardized_main_threshold_separation: PASS
- exact_main_threshold_coincidences: PASS
- covariance_identity_absolute_error_max: PASS
- nonfinite_scientific_outputs: PASS
- bootstrap_failures: PASS
- plus_one_support_violations: PASS
- benchmark_mcse_to_smallest_main_standard_error_max: PASS
- required_output_files_present: PASS

## Scientific checks

- delta_pi_bias_per_cell: FAIL
- delta_pi_bias_median: PASS
- delta_s_bias_per_cell: FAIL
- delta_s_bias_median: PASS
- delta_pi_variance_ratio_per_cell: FAIL
- delta_pi_variance_ratio_median: PASS
- delta_s_variance_ratio_per_cell: FAIL
- delta_s_variance_ratio_median: PASS
- delta_pi_normal_coverage_per_cell: PASS
- delta_pi_normal_coverage_median: PASS
- delta_s_normal_coverage_per_cell: FAIL
- delta_s_normal_coverage_median: PASS
- bootstrap_sd_delta_pi: PASS
- bootstrap_sd_delta_s: PASS
- bootstrap_coverage_delta_pi: FAIL
- bootstrap_coverage_delta_s: FAIL
- plus_one_bridge_delta_pi: FAIL
- plus_one_bridge_delta_s: FAIL
- plus_one_sign_reversals: FAIL
- both_trigger_ordering_strata: FAIL

## Main-grid ranges

- standardized Delta_pi bias: -0.3437 to 0.0447
- standardized Delta_S bias: -0.3508 to 0.0408
- Delta_pi variance ratio: 0.9200 to 1.2737
- Delta_S variance ratio: 0.9272 to 1.2862

## Bootstrap ranges

- Delta_pi SD ratio: 0.9745 to 1.1265
- Delta_S SD ratio: 0.9734 to 1.1276
