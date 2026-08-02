# Adaptive policy mechanism summary

## Decomposition at alpha=0.05

```text
                  library  local_alpha  pi_base  pi_full  pi_promising_observed  pi_random_observed  pi_rescue_observed  mean_incremental_effect_E_D  cov_activation_increment  mean_D_given_promising  mean_D_given_rescue  gain_count_promising  gain_count_rescue  loss_count_promising  loss_count_rescue
high_dependency_linear_20         0.05   0.0916   0.1034                 0.1034              0.0976              0.0916                       0.0118                  0.006030                0.024131             0.000000                    59                  0                     0                  0
       mixed_realistic_20         0.05   0.1988   0.3192                 0.2890              0.2582              0.2290                       0.1204                  0.029591                0.179182             0.060814                   458                151                     7                  0
```

## Bootstrap covariance intervals

```text
                  library  local_alpha  cov_activation_increment  bootstrap_mean  bootstrap_se  ci_low_95  ci_high_95  bootstrap_probability_gt_zero  bootstrap_probability_lt_zero  bootstrap_repetitions
high_dependency_linear_20         0.05                  0.006030        0.006028      0.000775   0.004543    0.007592                            1.0                            0.0                  20000
       mixed_realistic_20         0.05                  0.029591        0.029581      0.002279   0.025116    0.034030                            1.0                            0.0                  20000
```

Positive covariance means the promising trigger preferentially activates
the extra search in replications where full search has a more positive
incremental rejection effect than base search.