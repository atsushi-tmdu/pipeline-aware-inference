# D4 Numerical Validation v1: Adjudication

**Status: PASS**

This validation concerns the regular Work Package D4 paired budget-matched policy contrast. It is not direct evidence for the exact 20-candidate empirical pipeline.

## Locked design

- DGPs: ['independent_normal', 'gaussian_factor', 'nonlinear_smooth']
- Outer repetitions per cell: 3000
- Paired bootstrap repetitions per outer dataset: 999
- Alpha grid: [0.01, 0.05, 0.1]
- Designs: [{'B': 500, 'n': 500}, {'B': 1000, 'n': 1000}, {'B': 3000, 'n': 3000}, {'B': 3000, 'n': 5000}]
- Master seed: 20261117
- Primary interval: centered paired complete-replication two-bank bootstrap-normal interval
- Elapsed seconds: 3734.079

## Cell summary

| DGP | B | n | alpha | Delta TESS truth | var ratio | paired boot SD ratio | paired boot-normal cov | eval-only cov | unpaired/paired SD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| independent_normal | 500 | 500 | 0.010 | 0.000000 | 1.160 | 1.145 | 0.992 | 0.927 | 4.547 |
| independent_normal | 500 | 500 | 0.050 | 0.000000 | 1.015 | 1.087 | 0.973 | 0.951 | 4.407 |
| independent_normal | 500 | 500 | 0.100 | 0.000000 | 1.022 | 1.061 | 0.965 | 0.946 | 4.568 |
| independent_normal | 1000 | 1000 | 0.010 | 0.000000 | 1.119 | 1.085 | 0.979 | 0.934 | 4.395 |
| independent_normal | 1000 | 1000 | 0.050 | 0.000000 | 0.978 | 1.079 | 0.969 | 0.954 | 4.496 |
| independent_normal | 1000 | 1000 | 0.100 | 0.000000 | 1.039 | 1.031 | 0.952 | 0.942 | 4.452 |
| independent_normal | 3000 | 3000 | 0.010 | 0.000000 | 1.026 | 1.055 | 0.967 | 0.946 | 4.595 |
| independent_normal | 3000 | 3000 | 0.050 | 0.000000 | 0.981 | 1.046 | 0.965 | 0.953 | 4.530 |
| independent_normal | 3000 | 3000 | 0.100 | 0.000000 | 0.973 | 1.043 | 0.959 | 0.952 | 4.439 |
| independent_normal | 3000 | 5000 | 0.010 | 0.000000 | 1.083 | 1.034 | 0.959 | 0.942 | 5.198 |
| independent_normal | 3000 | 5000 | 0.050 | 0.000000 | 0.998 | 1.037 | 0.956 | 0.947 | 5.163 |
| independent_normal | 3000 | 5000 | 0.100 | 0.000000 | 1.034 | 1.011 | 0.953 | 0.943 | 5.153 |
| gaussian_factor | 500 | 500 | 0.010 | 0.450286 | 1.274 | 1.032 | 0.948 | 0.824 | 4.002 |
| gaussian_factor | 500 | 500 | 0.050 | 0.401077 | 1.029 | 1.048 | 0.953 | 0.858 | 4.025 |
| gaussian_factor | 500 | 500 | 0.100 | 0.359458 | 0.974 | 1.065 | 0.955 | 0.891 | 4.283 |
| gaussian_factor | 1000 | 1000 | 0.010 | 0.450286 | 1.149 | 1.044 | 0.951 | 0.823 | 3.760 |
| gaussian_factor | 1000 | 1000 | 0.050 | 0.401077 | 1.026 | 1.032 | 0.951 | 0.857 | 4.059 |
| gaussian_factor | 1000 | 1000 | 0.100 | 0.359458 | 0.995 | 1.045 | 0.956 | 0.894 | 4.297 |
| gaussian_factor | 3000 | 3000 | 0.010 | 0.450286 | 1.068 | 1.022 | 0.944 | 0.831 | 3.863 |
| gaussian_factor | 3000 | 3000 | 0.050 | 0.401077 | 1.010 | 1.017 | 0.949 | 0.856 | 4.042 |
| gaussian_factor | 3000 | 3000 | 0.100 | 0.359458 | 1.002 | 1.022 | 0.955 | 0.882 | 4.269 |
| gaussian_factor | 3000 | 5000 | 0.010 | 0.450286 | 1.030 | 1.031 | 0.951 | 0.778 | 3.705 |
| gaussian_factor | 3000 | 5000 | 0.050 | 0.401077 | 1.053 | 0.997 | 0.946 | 0.795 | 4.086 |
| gaussian_factor | 3000 | 5000 | 0.100 | 0.359458 | 0.982 | 1.028 | 0.956 | 0.840 | 4.469 |
| nonlinear_smooth | 500 | 500 | 0.010 | -0.000705 | 1.219 | 1.142 | 0.987 | 0.921 | 4.053 |
| nonlinear_smooth | 500 | 500 | 0.050 | -0.005603 | 1.055 | 1.080 | 0.964 | 0.916 | 4.276 |
| nonlinear_smooth | 500 | 500 | 0.100 | -0.013472 | 1.045 | 1.053 | 0.963 | 0.914 | 4.039 |
| nonlinear_smooth | 1000 | 1000 | 0.010 | -0.000705 | 1.156 | 1.091 | 0.975 | 0.924 | 4.217 |
| nonlinear_smooth | 1000 | 1000 | 0.050 | -0.005603 | 1.007 | 1.072 | 0.962 | 0.923 | 4.162 |
| nonlinear_smooth | 1000 | 1000 | 0.100 | -0.013472 | 1.013 | 1.049 | 0.959 | 0.915 | 4.079 |
| nonlinear_smooth | 3000 | 3000 | 0.010 | -0.000705 | 1.047 | 1.070 | 0.969 | 0.940 | 4.481 |
| nonlinear_smooth | 3000 | 3000 | 0.050 | -0.005603 | 1.038 | 1.024 | 0.949 | 0.919 | 4.196 |
| nonlinear_smooth | 3000 | 3000 | 0.100 | -0.013472 | 1.013 | 1.028 | 0.955 | 0.916 | 4.065 |
| nonlinear_smooth | 3000 | 5000 | 0.010 | -0.000705 | 1.049 | 1.065 | 0.968 | 0.934 | 4.850 |
| nonlinear_smooth | 3000 | 5000 | 0.050 | -0.005603 | 0.997 | 1.042 | 0.961 | 0.919 | 4.652 |
| nonlinear_smooth | 3000 | 5000 | 0.100 | -0.013472 | 1.007 | 1.025 | 0.951 | 0.886 | 4.385 |

## Failed primary/main checks

None.

## Interpretation

PASS requires every prespecified primary and main-regime check for both the rejection-probability premium and the TESS contrast to pass. Stress cells and the deliberately unpaired bootstrap are diagnostic. REVIEW preserves all results for transparent inspection without automatically invalidating the theorem.
