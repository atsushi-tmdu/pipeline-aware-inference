# TESS Final Figure Legends v1

## Figure-numbering decision

- **Figure 1:** Single conceptual figure.
- **Figure 2:** One figure with two stacked panels: upper, high-dependency library; lower, mixed-realistic library. Cite as “Figure 2” unless A/B labels are added to the artwork.
- **Figure 3:** Single forest plot.
- **Figure 4:** One figure with panels A and B.
- **Figure S1:** Single SUPPORT2-anchored supplementary figure.
- **Figure S2:** One supplementary figure with panels A–C.
- **Figure S3:** One supplementary figure with panels A and B.

## Final legends

### Figure 1. Adaptive development policy and inferential search size.

The base candidate family (K = 7) is evaluated first. Base-stage evidence determines whether an optional family of 13 additional candidates is activated or no expansion occurs. The complete development policy 𝒜 returns a final winner and its naive p-value, P𝒜. Under the global null, the policy-level rejection curve is π𝒜(α) = P₀{P𝒜 < α}. Tail-equivalent search size (TESS) expresses this rejection probability as the number of independent searches that would yield the same rejection probability at threshold α: TESS𝒜(α) = log{1 − π𝒜(α)}/log(1 − α). Relative to random expansion at the same activation rate, the policy allocation effect is characterized by πA − πrandom,r = Cov(A, Rfull − Rbase).

### Figure 2. Fixed-search TESS curves in the locked confirmatory simulation.

The upper panel shows the high-dependency candidate library and the lower panel shows the mixed-realistic candidate library. Curves compare fixed searches with K = 7 and K = 20 candidates. Points denote TESS estimates and shaded bands denote pointwise 95% paired-bootstrap confidence intervals, conditional on the frozen null-reference bank. Smaller local α values represent deeper inferential tails.

### Figure 3. Budget-standardized adaptive-policy effects across simulated and clinical-data structures.

Points show the difference in TESS at α = 0.05 between each adaptive expansion policy and random expansion at the same expected candidate budget; error bars show paired-bootstrap 95% confidence intervals. Positive values indicate greater inferential search burden than budget-matched random expansion, whereas negative values indicate lower burden. The square denotes the locked primary confirmatory comparison in the mixed-realistic library. Diamonds denote the supplementary SUPPORT2-anchored global-null validation; circles denote other confirmatory secondary comparisons. The vertical line at zero denotes no policy-allocation effect.

### Figure 4. Mechanism of the adaptive-policy effect.

(A) Proportion of evaluation replications activated by the promising policy and proportion of incremental rejection opportunities captured by that policy in the high-dependency, mixed-realistic, and SUPPORT2-anchored structures. Incremental rejection opportunities were replications in which full search changed base-search nonrejection into rejection. Direct labels show the observed percentages; the horizontal reference line marks 50% activation. (B) Covariance between promising-policy activation and the incremental rejection effect, Cov(A, Dα), across local α, where Dα = Rfull(α) − Rbase(α). Positive covariance indicates that expansion was preferentially activated in replications in which the optional candidate family increased rejection. Points denote estimates and error bars denote paired-bootstrap 95% confidence intervals. The vertical dashed line marks the prespecified primary threshold, α = 0.05. SUPPORT2 results are supplementary real-data-anchored global-null validation results.

### Figure S1. Adaptive-policy TESS curves in the SUPPORT2-anchored supplementary validation.

TESS curves are shown for fixed base search, rescue-triggered expansion, random expansion, promising-triggered expansion, and fixed full search while preserving the observed SUPPORT2 covariate and missing-data structure under outcome permutation. Points denote TESS estimates and error bars denote pointwise 95% paired-bootstrap confidence intervals. The vertical dashed line marks α = 0.05. Smaller local α values represent deeper inferential tails.

### Figure S2. Incremental rejection effects across base-stage evidence deciles.

Panels show (A) the high-dependency confirmatory structure, (B) the mixed-realistic confirmatory structure, and (C) the SUPPORT2-anchored validation structure. The horizontal axis gives the mean base-stage maximum ROC AUC within each decile. The blue series is the conditional probability that base search did not reject but full search rejected; the orange series is the conditional probability of the reverse transition; and the green series is their difference, the mean incremental rejection effect. The gray dashed line marks zero net incremental effect.

### Figure S3. Confirmatory adaptive-policy TESS curves displayed separately by policy.

Panels show (A) the high-dependency library and (B) the mixed-realistic library. Fixed base search, rescue-triggered expansion, random expansion, promising-triggered expansion, and fixed full search are displayed in separate rows to prevent overlapping uncertainty intervals from obscuring the policy-specific curves. Points denote TESS estimates and error bars denote pointwise 95% paired-bootstrap confidence intervals. The vertical dashed line marks the prespecified primary threshold, α = 0.05. Smaller local α values represent deeper inferential tails.

## Recommended file names

- `Figure1_policy_framework.*`
- `Figure2_fixed_search_TESS_curves.*`
- `Figure3_policy_effects_with_SUPPORT2.*`
- `Figure4A_activation_and_gain_capture.*`
- `Figure4B_activation_increment_covariance.*`
- `FigureS1_SUPPORT2_TESS_curves.*`
- `FigureS2A_high_dependency_score_deciles.*`
- `FigureS2B_mixed_realistic_score_deciles.*`
- `FigureS2C_SUPPORT2_score_deciles.*`
- `FigureS3A_high_dependency_adaptive_policy_TESS_curves.*`
- `FigureS3B_mixed_realistic_adaptive_policy_TESS_curves.*`

## Freeze note

**Figure 2 is one two-panel figure.** Rename the current file containing `Figure2A` to `Figure2_fixed_search_TESS_curves` before freezing the final manuscript archive.