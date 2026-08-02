# Budget-standardized policy effect summary

## Point estimates at alpha=0.05

```text
                  library  local_alpha    n  promising_activation_rate  rescue_activation_rate  pi_base  pi_full  pi_promising  pi_rescue  pi_random_matched_promising_budget  pi_random_matched_rescue_budget  cov_activation_increment  pi_promising_minus_matched_random  pi_rescue_minus_matched_random  tess_promising  tess_rescue  tess_random_matched_promising_budget  tess_random_matched_rescue_budget  tess_promising_minus_matched_random  tess_rescue_minus_matched_random  incremental_gain_count  incremental_loss_count  gain_count_activated_promising  gain_count_allocated_rescue  loss_count_activated_promising  loss_count_allocated_rescue  promising_gain_capture_fraction
high_dependency_linear_20         0.05 5000                     0.4890                  0.5110   0.0916   0.1034        0.1034     0.0916                            0.097370                         0.097630                  0.006030                           0.006030                       -0.006030        2.127870     1.872964                              1.997196                           2.002804                             0.130673                         -0.129841                      59                       0                              59                            0                               0                            0                         1.000000
       mixed_realistic_20         0.05 5000                     0.5034                  0.4966   0.1988   0.3192        0.2890     0.2290                            0.259409                         0.258591                  0.029591                           0.029591                       -0.029591        6.649658     5.070193                              5.854708                           5.833167                             0.794950                         -0.762974                     609                       7                             458                          151                               7                            0                         0.752053
```

## Bootstrap TESS effects

```text
                  library  local_alpha                              metric  bootstrap_mean  bootstrap_se  ci_low_95  ci_high_95  bootstrap_probability_gt_zero  bootstrap_probability_lt_zero  bootstrap_repetitions
high_dependency_linear_20         0.05 tess_promising_minus_matched_random        0.130657      0.016911   0.098254    0.164909                            1.0                            0.0                  20000
high_dependency_linear_20         0.05    tess_rescue_minus_matched_random       -0.129811      0.016695  -0.163581   -0.097796                            0.0                            1.0                  20000
       mixed_realistic_20         0.05 tess_promising_minus_matched_random        0.794711      0.062147   0.672615    0.916738                            1.0                            0.0                  20000
       mixed_realistic_20         0.05    tess_rescue_minus_matched_random       -0.762564      0.057214  -0.874610   -0.649701                            0.0                            1.0                  20000
```

## Fixed-policy reconstruction audit

```text
                  library     policy  pool_size  rows_compared  model_mismatch_count  score_difference_count_gt_1e12  p_difference_count_gt_1e12  p_difference_count_gt_1e4  maximum_absolute_p_value_difference  mean_absolute_p_value_difference  decision_mismatch_count_across_all_alphas
high_dependency_linear_20 fixed_base          7           5000                     2                               0                          86                         86                             0.014997                      6.838632e-06                                          0
high_dependency_linear_20 fixed_full         20           5000                    14                               0                           8                          8                             0.007598                      2.039592e-06                                          0
       mixed_realistic_20 fixed_base          7           5000                     0                               0                          19                         19                             0.000600                      8.398320e-07                                          0
       mixed_realistic_20 fixed_full         20           5000                     0                               0                           7                          7                             0.000200                      2.799440e-07                                          0
```