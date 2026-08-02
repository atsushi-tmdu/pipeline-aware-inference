# Phase 3C adaptive ML policy summary

All results are conditional on the frozen null-reference bank.

## Expansion metadata

```text
                  library  trigger_threshold  trigger_tie_probability  target_expansion_probability  reference_base_repetitions  evaluation_repetitions  base_candidate_count  extra_candidate_count  maximum_candidate_count
high_dependency_linear_20           0.512533                      1.0                           0.5                        5000                    5000                     7                     13                       20
       mixed_realistic_20           0.528544                      1.0                           0.5                        5000                    5000                     7                     13                       20
```

## TESS at alpha=0.05

```text
                  library          policy_label     tess  expansion_rate  mean_evaluated_candidate_count
high_dependency_linear_20      Fixed base (K=7) 1.872964          0.0000                          7.0000
high_dependency_linear_20     Expand for rescue 1.872964          0.5110                         13.6430
high_dependency_linear_20      Random expansion 2.002160          0.5008                         13.5104
high_dependency_linear_20     Fixed full (K=20) 2.127870          1.0000                         20.0000
high_dependency_linear_20 Expand when promising 2.127870          0.4890                         13.3570
       mixed_realistic_20      Fixed base (K=7) 4.321124          0.0000                          7.0000
       mixed_realistic_20     Expand for rescue 5.070193          0.4966                         13.4558
       mixed_realistic_20      Random expansion 5.822898          0.5008                         13.5104
       mixed_realistic_20 Expand when promising 6.649658          0.5034                         13.5442
       mixed_realistic_20     Fixed full (K=20) 7.495847          1.0000                         20.0000
```

## Fixed-policy reconstruction validation

```text
                  library     policy  pool_size  rows_compared  maximum_absolute_p_value_difference  mean_absolute_p_value_difference
high_dependency_linear_20 fixed_base          7           5000                             0.014997                      6.838632e-06
high_dependency_linear_20 fixed_full         20           5000                             0.007598                      2.039592e-06
       mixed_realistic_20 fixed_base          7           5000                             0.000600                      8.398320e-07
       mixed_realistic_20 fixed_full         20           5000                             0.000200                      2.799440e-07
```