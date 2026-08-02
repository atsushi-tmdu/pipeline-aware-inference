# D1 Numerical Validation v1: Adjudication

**Status: REVIEW**

This validation concerns the regular Work Package D1 model with a known activation trigger and reference-estimated candidate quantiles. It is numerical validation of the theorem, not evidence for the empirical TESS application.

## Locked design

- Outer Monte Carlo repetitions per cell: 3000
- Two-bank bootstrap repetitions per outer dataset: 999
- Activation rate: 0.5
- Alpha grid: [0.01, 0.05, 0.1]
- Designs: [{'B': 500, 'n': 500}, {'B': 1000, 'n': 1000}, {'B': 3000, 'n': 3000}, {'B': 3000, 'n': 5000}]
- Master seed: 20260921
- Elapsed seconds: 560.743

## Cell summary

| B | n | alpha | pi variance ratio | pi bootstrap coverage | TESS variance ratio | TESS bootstrap coverage | eval-only pi coverage |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 500 | 500 | 0.010 | 1.205 | 0.885 | 1.220 | 0.885 | 0.795 |
| 500 | 500 | 0.050 | 1.052 | 0.920 | 1.065 | 0.912 | 0.847 |
| 500 | 500 | 0.100 | 1.036 | 0.924 | 1.049 | 0.925 | 0.840 |
| 1000 | 1000 | 0.010 | 1.075 | 0.915 | 1.081 | 0.923 | 0.833 |
| 1000 | 1000 | 0.050 | 1.062 | 0.916 | 1.067 | 0.917 | 0.833 |
| 1000 | 1000 | 0.100 | 0.985 | 0.935 | 0.989 | 0.935 | 0.854 |
| 3000 | 3000 | 0.010 | 1.028 | 0.920 | 1.030 | 0.921 | 0.844 |
| 3000 | 3000 | 0.050 | 1.012 | 0.939 | 1.014 | 0.939 | 0.850 |
| 3000 | 3000 | 0.100 | 1.016 | 0.938 | 1.019 | 0.937 | 0.849 |
| 3000 | 5000 | 0.010 | 1.046 | 0.917 | 1.048 | 0.918 | 0.789 |
| 3000 | 5000 | 0.050 | 1.017 | 0.934 | 1.018 | 0.932 | 0.789 |
| 3000 | 5000 | 0.100 | 0.993 | 0.939 | 0.995 | 0.940 | 0.803 |

## Failed checks

- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'pi_standardized_bias', 'value': 0.38925993265712616, 'lower': 0.0, 'upper': 0.2, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'tess_standardized_bias', 'value': 0.3943603605011471, 'lower': 0.0, 'upper': 0.2, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'pi_variance_ratio', 'value': 1.205449164766825, 'lower': 0.8, 'upper': 1.2, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'tess_variance_ratio', 'value': 1.219557487138849, 'lower': 0.8, 'upper': 1.2, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'pi_oracle_coverage', 'value': 0.907, 'lower': 0.91, 'upper': 0.99, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'tess_oracle_coverage', 'value': 0.907, 'lower': 0.91, 'upper': 0.99, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'pi_basic_bootstrap_coverage', 'value': 0.885, 'lower': 0.91, 'upper': 0.99, 'passed': False}
- {'cell': {'B': 500, 'n': 500, 'alpha': 0.01}, 'tier': 'all', 'metric': 'tess_basic_bootstrap_coverage', 'value': 0.885, 'lower': 0.91, 'upper': 0.99, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.01}, 'tier': 'all', 'metric': 'pi_standardized_bias', 'value': 0.2993253445014115, 'lower': 0.0, 'upper': 0.2, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.01}, 'tier': 'all', 'metric': 'tess_standardized_bias', 'value': 0.3024067022369408, 'lower': 0.0, 'upper': 0.2, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.05}, 'tier': 'primary', 'metric': 'pi_standardized_bias', 'value': 0.12243053411562918, 'lower': 0.0, 'upper': 0.12, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.05}, 'tier': 'primary', 'metric': 'tess_standardized_bias', 'value': 0.12893414722537205, 'lower': 0.0, 'upper': 0.12, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.05}, 'tier': 'primary', 'metric': 'pi_basic_bootstrap_coverage', 'value': 0.916, 'lower': 0.93, 'upper': 0.97, 'passed': False}
- {'cell': {'B': 1000, 'n': 1000, 'alpha': 0.05}, 'tier': 'primary', 'metric': 'tess_basic_bootstrap_coverage', 'value': 0.9166666666666666, 'lower': 0.93, 'upper': 0.97, 'passed': False}

## Interpretation

PASS means that the prespecified Monte Carlo agreement criteria for bias, asymptotic variance, bootstrap standard error, and 95% coverage were met in every declared validation cell. REVIEW means that one or more scientific agreement criteria require inspection; it does not by itself invalidate the analytic theorem.
