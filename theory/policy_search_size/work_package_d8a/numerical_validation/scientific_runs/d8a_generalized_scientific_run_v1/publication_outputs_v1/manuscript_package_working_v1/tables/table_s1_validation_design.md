# Supplementary Table S1. Detailed prospectively specified numerical-validation design

| Domain | Prospectively specified design | Purpose |
|---|---|---|
| Scientific units | 25 latent equivalence classes: 17 primary and 8 diagnostic. | Primary classes determine formal acceptance; diagnostic classes probe boundary and implementation behavior. |
| Transformation audit | 50 deterministic common-monotone-transform audit rows; transformed rows do not count as independent evidence. | Checks invariance while preserving the 17-class formal denominator. |
| Simulation families | Reference-only, evaluation-only, and combined; 25 jobs per family and 75 jobs total. | Separates reference-threshold error, finite-n evaluation error, and their joint contribution. |
| Reference-bank sizes | B=250, 500, 1,000, 3,000, and 10,000. | Evaluates the generalized reference-bias expansion across the full grid; the locked improvement criterion compares B=500 with B=10,000. |
| Evaluation-sample sizes | n=250, 500, 1,000, 3,000, and 10,000. | Evaluates the exact finite-n identity and combined expansion. |
| TESS levels | alpha=0.01 and 0.05. | Assesses nonlinear propagation to TESS separately by alpha. |
| Random-number contract | Master seed 20260804; independent reference and evaluation streams; nested prefixes within each family. | Ensures deterministic replay, common random numbers, and interruption-safe resumption. |
| Replication schedule | Primary: minimum 2,000 and maximum 20,000; diagnostic: minimum 1,000 and maximum 5,000; batch size 250. | Implements role-aware precision-only stopping. |
| Stopping criterion | MCSE/(1+\|tau\|) <=0.03, where tau was the locked population target; TESS status proportions used unit scale. | Controls Monte Carlo resolution without using the observed Monte Carlo mean in the stopping scale. |
| Reference acceptance | At B=10,000: median normalized residual <=0.15; 90th percentile <=0.40; median improvement from B=500 >=40%; improved-class fraction >=75%. | Formal primary-class assessment of the generalized reference correction. |
| Combined-policy acceptance | At (B,n)=(10,000,10,000): median normalized residual <=0.15 and 90th percentile <=0.40. | Tests the joint reference/evaluation bias prediction, including the B-by-n interaction term. |
| Combined-TESS acceptance | At (B,n)=(10,000,10,000), separately by alpha: median normalized residual <=0.25; 90th percentile <=0.60; any nonfinite primary record was a formal failure. | Tests the nonlinear TESS corollary with explicit boundary-status accounting. |
| Exact identity check | 85 two-sided Bonferroni comparisons at familywise alpha=0.01; z*=3.85098; target E(delta_hat)=(1-1/n)Delta_pi. | Prespecified fatal implementation check for the finite-n evaluation identity. |
| Precision-limited allowance | No more than 10% of primary classes could reach the maximum replicate count without meeting precision; with 17 primary classes, the operational maximum was one class. | Prevents formal acceptance from relying on widespread precision-limited primary classes. |
| Formal decision rule | PASS required every scientific criterion and every fatal check to pass; post-hoc class dropping was prohibited. | Preserves the predeclared 17-class confirmatory denominator. |

## Notes

1. Only the identity member of each latent equivalence class was simulated. Common monotone transformations were deterministic invariance audits and did not enlarge the scientific denominator.
2. The design was specified and computationally locked before the scientific run. Completed-run results and evidential interpretation are reported separately.
3. The 10% precision-limited rule corresponds operationally to at most one of 17 primary classes, because two classes would exceed the locked fraction.
