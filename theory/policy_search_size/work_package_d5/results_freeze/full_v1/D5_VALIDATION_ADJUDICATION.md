# D5 Plus-One Bridge: Adjudication

**Status: PASS**

**Run label: SCIENTIFIC VALIDATION**

## Design

- Cells: 36
- Outer repetitions per cell: 3000
- Master seed: 20261117
- Elapsed seconds: 17.461

## Fatal checks

- PASS: d4_tag_commit
- PASS: d4_lock_manifest_files
- PASS: d4_frozen_raw_outputs
- PASS: expected_cell_count
- PASS: expected_replication_count
- PASS: unique_replication_identity
- PASS: all_quantile_mode_d4_reproduction
- PASS: common_activation_threshold
- PASS: common_activation_realization
- PASS: finite_replication_outputs
- PASS: finite_cell_summary
- PASS: d4_grid_index_gap_one

## Exact finite-bank boundaries

| B | alpha | count_ceiling | quantile_index | plus_one_index | plus_one_attainable | index_gap | tau_quantile | tau_plus_one | tail_probability_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 500 | 0.01 | 6 | 495 | 496 | true | 1 | 0.011976 | 0.00998004 | 0.00199601 |
| 500 | 0.05 | 26 | 475 | 476 | true | 1 | 0.0518962 | 0.0499002 | 0.00199601 |
| 500 | 0.1 | 51 | 450 | 451 | true | 1 | 0.101796 | 0.0998004 | 0.00199601 |
| 1000 | 0.01 | 11 | 990 | 991 | true | 1 | 0.010989 | 0.00999001 | 0.000999001 |
| 1000 | 0.05 | 51 | 950 | 951 | true | 1 | 0.0509491 | 0.04995 | 0.000999001 |
| 1000 | 0.1 | 101 | 900 | 901 | true | 1 | 0.100899 | 0.0999001 | 0.000999001 |
| 3000 | 0.01 | 31 | 2970 | 2971 | true | 1 | 0.0103299 | 0.00999667 | 0.000333222 |
| 3000 | 0.05 | 151 | 2850 | 2851 | true | 1 | 0.0503166 | 0.0499833 | 0.000333222 |
| 3000 | 0.1 | 301 | 2700 | 2701 | true | 1 | 0.1003 | 0.0999667 | 0.000333222 |

## Bridge summary

| dgp | B | n | alpha | delta_pi_bridge_rms | delta_pi_bridge_rms_to_d4_sd | delta_pi_bridge_label | delta_tess_bridge_rms | delta_tess_bridge_rms_to_d4_sd | delta_tess_bridge_label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| independent_normal | 500 | 500 | 0.01 | 0.000993769 | 0.418693 | material | 0.100854 | 0.418696 | material |
| independent_normal | 500 | 500 | 0.05 | 0.00101237 | 0.212099 | small | 0.0214102 | 0.212264 | small |
| independent_normal | 500 | 500 | 0.1 | 0.000989122 | 0.153559 | small | 0.0110393 | 0.153697 | small |
| independent_normal | 1000 | 1000 | 0.01 | 0.0004773 | 0.288906 | material | 0.0483229 | 0.288842 | material |
| independent_normal | 1000 | 1000 | 0.05 | 0.000514755 | 0.155053 | small | 0.0108557 | 0.155038 | small |
| independent_normal | 1000 | 1000 | 0.1 | 0.000498854 | 0.108512 | small | 0.00555449 | 0.108465 | small |
| independent_normal | 3000 | 3000 | 0.01 | 0.000170611 | 0.186548 | small | 0.0172383 | 0.186437 | small |
| independent_normal | 3000 | 3000 | 0.05 | 0.000165857 | 0.0863467 | negligible | 0.0034938 | 0.0863288 | negligible |
| independent_normal | 3000 | 3000 | 0.1 | 0.000163617 | 0.0634988 | negligible | 0.00181808 | 0.0635394 | negligible |
| independent_normal | 3000 | 5000 | 0.01 | 0.000133853 | 0.183848 | small | 0.0135337 | 0.183889 | small |
| independent_normal | 3000 | 5000 | 0.05 | 0.000127264 | 0.0847553 | negligible | 0.00267941 | 0.0847239 | negligible |
| independent_normal | 3000 | 5000 | 0.1 | 0.000125635 | 0.0610999 | negligible | 0.0013961 | 0.0611214 | negligible |
| gaussian_factor | 500 | 500 | 0.01 | 0.00157912 | 0.485224 | material | 0.162596 | 0.486049 | material |
| gaussian_factor | 500 | 500 | 0.05 | 0.0014093 | 0.247918 | small | 0.0312201 | 0.250705 | material |
| gaussian_factor | 500 | 500 | 0.1 | 0.00126867 | 0.187454 | small | 0.0151452 | 0.189725 | small |
| gaussian_factor | 1000 | 1000 | 0.01 | 0.000781907 | 0.356113 | material | 0.0801526 | 0.356721 | material |
| gaussian_factor | 1000 | 1000 | 0.05 | 0.0006733 | 0.167264 | small | 0.0148429 | 0.168782 | small |
| gaussian_factor | 1000 | 1000 | 0.1 | 0.000656487 | 0.134504 | small | 0.00782542 | 0.137171 | small |
| gaussian_factor | 3000 | 3000 | 0.01 | 0.000271415 | 0.221458 | small | 0.0277654 | 0.222041 | small |
| gaussian_factor | 3000 | 3000 | 0.05 | 0.000229637 | 0.0995924 | negligible | 0.00505997 | 0.100464 | small |
| gaussian_factor | 3000 | 3000 | 0.1 | 0.000209036 | 0.073992 | negligible | 0.00247896 | 0.0749814 | negligible |
| gaussian_factor | 3000 | 5000 | 0.01 | 0.000233592 | 0.21794 | small | 0.02391 | 0.218667 | small |
| gaussian_factor | 3000 | 5000 | 0.05 | 0.000212853 | 0.102835 | small | 0.00470041 | 0.103973 | small |
| gaussian_factor | 3000 | 5000 | 0.1 | 0.000177093 | 0.0731856 | negligible | 0.00212479 | 0.0752682 | negligible |
| nonlinear_smooth | 500 | 500 | 0.01 | 0.000984498 | 0.392646 | material | 0.0998934 | 0.392497 | material |
| nonlinear_smooth | 500 | 500 | 0.05 | 0.00102299 | 0.190956 | small | 0.0216754 | 0.191224 | small |
| nonlinear_smooth | 500 | 500 | 0.1 | 0.00104571 | 0.139704 | small | 0.011714 | 0.139894 | small |
| nonlinear_smooth | 1000 | 1000 | 0.01 | 0.000496094 | 0.28654 | material | 0.0502594 | 0.286688 | material |
| nonlinear_smooth | 1000 | 1000 | 0.05 | 0.000504499 | 0.135948 | small | 0.0106448 | 0.135935 | small |
| nonlinear_smooth | 1000 | 1000 | 0.1 | 0.000516205 | 0.0985681 | negligible | 0.00575453 | 0.0987176 | negligible |
| nonlinear_smooth | 3000 | 3000 | 0.01 | 0.000164953 | 0.173184 | small | 0.0166771 | 0.173171 | small |
| nonlinear_smooth | 3000 | 3000 | 0.05 | 0.000169952 | 0.0779879 | negligible | 0.00357963 | 0.0779573 | negligible |
| nonlinear_smooth | 3000 | 3000 | 0.1 | 0.000167974 | 0.0554927 | negligible | 0.00186666 | 0.0554654 | negligible |
| nonlinear_smooth | 3000 | 5000 | 0.01 | 0.000128563 | 0.171127 | small | 0.0129976 | 0.17112 | small |
| nonlinear_smooth | 3000 | 5000 | 0.05 | 0.000128986 | 0.0742034 | negligible | 0.00271879 | 0.0742065 | negligible |
| nonlinear_smooth | 3000 | 5000 | 0.1 | 0.000130955 | 0.0522457 | negligible | 0.00145649 | 0.0522867 | negligible |

## Interpretation

PASS concerns implementation integrity and complete reproduction of the frozen D4 quantile-mode results.

The negligible/small/material labels are descriptive and do not determine PASS or FAIL.

This result concerns the one-candidate-per-branch D4 contrast. It is not direct evidence for finite multiple-candidate winner selection.
