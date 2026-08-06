# Table 2. Numerical-validation results and interpretability diagnostics

## Panel A. Approximation criteria

| Component | Prospectively specified criterion | MCSE-adjusted result | Raw diagnostic | Formal decision | Interpretation |
|---|---|---|---|---|---|
| Reference approximation, B=10,000 | Median <=0.15; 90th percentile <=0.40 | Median 0; 90th percentile 0 | Median 0.0355; 90th percentile 0.0958 | PASS | Strong support for approximation accuracy at B=10,000 |
| Combined policy, B=n=10,000 | Median <=0.15; 90th percentile <=0.40 | Median 0; 90th percentile 0 | Median 0.0495; 90th percentile 0.1474 | PASS | Strong numerical support |
| TESS, alpha=0.01, B=n=10,000 | Median <=0.25; 90th percentile <=0.60; no nonfinite primary record | Median 0; 90th percentile 0 | Median 0.5288; 90th percentile 1.4612; nonfinite records 0 | PASS under adjusted metric | Formal pass; finite-sample accuracy was MCSE-resolution limited |
| TESS, alpha=0.05, B=n=10,000 | Median <=0.25; 90th percentile <=0.60; no nonfinite primary record | Median 0; 90th percentile 0 | Median 0.4073; 90th percentile 0.8891; nonfinite records 0 | PASS under adjusted metric | Formal pass; finite-sample accuracy was MCSE-resolution limited |

## Panel B. Additional checks and sensitivity diagnostics

| Component | Prospectively specified criterion | Formal result | Raw or auxiliary diagnostic | Formal decision | Interpretation |
|---|---|---|---|---|---|
| Reference median-improvement criterion | At least 40% improvement from B=500 to B=10,000 | Formal statistic 1.00 because both adjusted medians were truncated to 0 | Raw normalized median increased from 0.0049 at B=500 to 0.0355 at B=10,000 | PASS under adjusted metric | Formal criterion was non-discriminating under complete MCSE flooring; the raw diagnostic did not show improvement |
| Improved primary-class fraction | At least 75% improved versus the prespecified baseline | 15/17 (88.2%) improved versus no reference correction | 14/17 (82.4%) versus gradient-only; 9/17 (52.9%) versus smooth-only (nonfatal) | PASS | Improvement conclusion was robust to the no-correction and gradient-only baselines |
| Exact finite-n evaluation identity | All 85 simultaneous Bonferroni checks pass at z*=3.85098 | 85/85 passed | \|difference\|/MCSE: median 0.6308; 90th percentile 1.705; maximum 2.997 | PASS | Strong implementation support |
| Precision-limited primary classes | No more than 1 of 17 primary classes | 0/17 | 75/75 simulation jobs met the precision target; 126,000 Monte Carlo replicates | PASS | Adequate Monte Carlo precision |

## Notes

1. The MCSE-adjusted normalized residual subtracts the prospectively specified simultaneous z* times MCSE allowance from the absolute raw residual, truncates at zero, and divides by the locked scale. Zero therefore denotes containment within the Monte Carlo uncertainty allowance, not a zero raw residual.
2. The B=500-to-10,000 median-improvement criterion became non-discriminating because both adjusted medians were truncated to zero. Its formal PASS is retained because the rule was prospectively specified; the raw diagnostic is shown separately and did not demonstrate improvement.
3. The prespecified improved-class baseline was no reference correction. Gradient-only and smooth-only comparisons are sensitivity diagnostics; the smooth-only comparison was not a standalone fatal criterion.
4. Raw diagnostics did not alter formal adjudication. No criterion was changed, no class was dropped, and the scientific simulation was not rerun.
