# D2 Numerical Validation v1: Adjudication

**Status: PASS**

This validation concerns the regular Work Package D2 model with reference-estimated candidate and activation thresholds. It is not evidence for the empirical TESS application.

## Locked design

- DGPs: ['independent_normal', 'gaussian_factor', 'nonlinear_smooth']
- Outer repetitions per cell: 3000
- Bootstrap repetitions per outer dataset: 999
- Alpha grid: [0.01, 0.05, 0.1]
- Designs: [{'B': 500, 'n': 500}, {'B': 1000, 'n': 1000}, {'B': 3000, 'n': 3000}, {'B': 3000, 'n': 5000}]
- Master seed: 20261017
- Primary interval: centered complete-replication two-bank bootstrap-normal interval
- Elapsed seconds: 1917.194

## Cell summary

| DGP | B | n | alpha | pi var ratio | pi boot-normal cov | TESS var ratio | TESS boot-normal cov | trigger var ratio | eval-only pi cov |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| independent_normal | 500 | 500 | 0.010 | 1.203 | 0.963 | 1.217 | 0.965 | 10.614 | 0.800 |
| independent_normal | 500 | 500 | 0.050 | 1.038 | 0.958 | 1.049 | 0.959 | 2.707 | 0.849 |
| independent_normal | 500 | 500 | 0.100 | 0.987 | 0.953 | 0.996 | 0.956 | 1.878 | 0.846 |
| independent_normal | 1000 | 1000 | 0.010 | 1.095 | 0.955 | 1.101 | 0.956 | 6.477 | 0.838 |
| independent_normal | 1000 | 1000 | 0.050 | 0.989 | 0.958 | 0.995 | 0.958 | 2.313 | 0.851 |
| independent_normal | 1000 | 1000 | 0.100 | 1.006 | 0.950 | 1.012 | 0.952 | 1.530 | 0.852 |
| independent_normal | 3000 | 3000 | 0.010 | 0.964 | 0.962 | 0.965 | 0.961 | 4.314 | 0.857 |
| independent_normal | 3000 | 3000 | 0.050 | 1.022 | 0.947 | 1.025 | 0.948 | 1.517 | 0.846 |
| independent_normal | 3000 | 3000 | 0.100 | 1.017 | 0.950 | 1.019 | 0.948 | 1.348 | 0.851 |
| independent_normal | 3000 | 5000 | 0.010 | 1.049 | 0.951 | 1.051 | 0.952 | 2.743 | 0.793 |
| independent_normal | 3000 | 5000 | 0.050 | 0.999 | 0.949 | 1.001 | 0.949 | 1.383 | 0.795 |
| independent_normal | 3000 | 5000 | 0.100 | 0.966 | 0.954 | 0.967 | 0.954 | 1.208 | 0.801 |
| gaussian_factor | 500 | 500 | 0.010 | 1.203 | 0.958 | 1.219 | 0.960 | 449.436 | 0.813 |
| gaussian_factor | 500 | 500 | 0.050 | 1.028 | 0.953 | 1.040 | 0.955 | 12.162 | 0.837 |
| gaussian_factor | 500 | 500 | 0.100 | 1.026 | 0.949 | 1.038 | 0.952 | 3.999 | 0.845 |
| gaussian_factor | 1000 | 1000 | 0.010 | 1.125 | 0.957 | 1.132 | 0.957 | 393.810 | 0.818 |
| gaussian_factor | 1000 | 1000 | 0.050 | 0.985 | 0.958 | 0.991 | 0.959 | 10.022 | 0.848 |
| gaussian_factor | 1000 | 1000 | 0.100 | 1.010 | 0.954 | 1.015 | 0.955 | 2.969 | 0.829 |
| gaussian_factor | 3000 | 3000 | 0.010 | 1.014 | 0.956 | 1.017 | 0.956 | 131.270 | 0.838 |
| gaussian_factor | 3000 | 3000 | 0.050 | 1.022 | 0.950 | 1.025 | 0.950 | 6.851 | 0.838 |
| gaussian_factor | 3000 | 3000 | 0.100 | 0.965 | 0.951 | 0.967 | 0.951 | 2.175 | 0.852 |
| gaussian_factor | 3000 | 5000 | 0.010 | 1.028 | 0.954 | 1.030 | 0.954 | 101.235 | 0.769 |
| gaussian_factor | 3000 | 5000 | 0.050 | 1.030 | 0.945 | 1.032 | 0.945 | 3.701 | 0.776 |
| gaussian_factor | 3000 | 5000 | 0.100 | 1.004 | 0.949 | 1.007 | 0.950 | 1.714 | 0.782 |
| nonlinear_smooth | 500 | 500 | 0.010 | 1.178 | 0.967 | 1.192 | 0.967 | 4.087 | 0.790 |
| nonlinear_smooth | 500 | 500 | 0.050 | 0.981 | 0.959 | 0.993 | 0.960 | 1.572 | 0.846 |
| nonlinear_smooth | 500 | 500 | 0.100 | 1.028 | 0.953 | 1.042 | 0.955 | 1.287 | 0.830 |
| nonlinear_smooth | 1000 | 1000 | 0.010 | 1.127 | 0.956 | 1.134 | 0.958 | 2.655 | 0.828 |
| nonlinear_smooth | 1000 | 1000 | 0.050 | 0.987 | 0.952 | 0.993 | 0.954 | 1.371 | 0.845 |
| nonlinear_smooth | 1000 | 1000 | 0.100 | 0.971 | 0.955 | 0.977 | 0.956 | 1.244 | 0.842 |
| nonlinear_smooth | 3000 | 3000 | 0.010 | 1.076 | 0.947 | 1.078 | 0.947 | 1.892 | 0.833 |
| nonlinear_smooth | 3000 | 3000 | 0.050 | 0.993 | 0.955 | 0.995 | 0.955 | 1.170 | 0.837 |
| nonlinear_smooth | 3000 | 3000 | 0.100 | 1.041 | 0.948 | 1.043 | 0.949 | 1.112 | 0.818 |
| nonlinear_smooth | 3000 | 5000 | 0.010 | 1.037 | 0.957 | 1.039 | 0.958 | 1.602 | 0.780 |
| nonlinear_smooth | 3000 | 5000 | 0.050 | 1.000 | 0.951 | 1.002 | 0.951 | 1.131 | 0.778 |
| nonlinear_smooth | 3000 | 5000 | 0.100 | 1.007 | 0.949 | 1.009 | 0.949 | 1.005 | 0.763 |

## Failed primary/main checks

None.

## Interpretation

PASS requires all prespecified primary and main-regime checks to pass. Stress cells are reported diagnostically. REVIEW preserves every result and triggers transparent inspection without automatically invalidating the D2 theorem.
