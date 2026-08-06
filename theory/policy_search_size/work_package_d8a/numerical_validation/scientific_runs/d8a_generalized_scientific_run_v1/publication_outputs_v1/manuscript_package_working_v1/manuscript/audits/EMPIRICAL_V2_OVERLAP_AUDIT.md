# Cross-Manuscript Overlap Audit v1

## Manuscripts compared

1. **Finite-sample paper:** *Second-Order Finite-Sample Bias in Threshold-Adaptive Statistical Policies* — D8-A Main Manuscript Draft v3.
2. **Frozen empirical paper:** *Inferential Search Size Is a Property of the Adaptive Development Policy: Quantifying Multiplicity in Machine-Learning Pipelines* — empirical manuscript draft v2.

## Executive judgment

**Overall overlap risk after the v4 repair: LOW.**

The manuscripts share a small mathematical vocabulary—adaptive rejection, a marginal-rate-matched comparator, the TESS transformation, and an activation–increment covariance identity—but differ in scientific question, policy class, main theorem, simulation design, evidence, figures, tables, and conclusions.

## Quantitative prose comparison

Declarations and reference lists were excluded.

- Shared exact 10-word sequences: **0**
- Shared exact 8-word sequences: **0**
- Shared exact 7-word sequences: **0**
- Shared exact 6-word sequences: **1**
- Maximum TF–IDF cosine similarity between any pair of core prose paragraphs: **0.207**

The shared six-word sequence was:

> conditional on the reference bank the

No shared prose passage of seven or more consecutive normalized words was detected.

## Scientific boundary

| Dimension | D8-A finite-sample paper | Frozen empirical paper | Assessment |
|---|---|---|---|
| Primary question | Bias of a plug-in policy contrast with finite reference and evaluation samples | Effect of state-dependent search allocation on global-null rejection and TESS | Distinct |
| Policy class | Three continuous candidates; monotone gain-only augmentation; unique winners | Twenty fitted candidates; plus-one empirical p-values; gain and loss states possible | Distinct |
| Main result | Generalized \(B^{-1}\), \(n^{-1}\), coincidence, and TESS expectation expansions | Same-budget allocation covariance and empirical TESS contrasts | Distinct |
| Reference bank | Object of empirical-quantile bias theory | Candidate-wise empirical-null calibration and post hoc bootstrap sensitivity | Distinct |
| Validation | 25 equivalence classes, 75 jobs, 126,000 Monte Carlo replicates | Two 20-model libraries and SUPPORT2-anchored permutation experiment | No reused evidence |
| Figures and tables | Theory geometry and approximation diagnostics | Policy diagram, TESS curves, forest plot, mechanism | No reuse |
| Principal conclusion | Separate reference and evaluation centering mechanisms | Search burden depends on allocation across data states | Distinct |

## Necessary shared definitions

### TESS

Both use

\[
g_lpha(x)=rac{\log(1-x)}{\log(1-lpha)}.
\]

In the empirical paper TESS is the principal diagnostic outcome. In D8-A it is only a smooth transformation used to propagate finite-sample bias.

### Matched comparator

Both use independent activation at the same marginal rate. In the empirical paper this isolates policy allocation. In D8-A it defines a fixed scalar functional with an exact finite-\(n\) identity.

### Increment identity

The increments differ materially:

- empirical paper:
  \[
  D_lpha=R_{m full}-R_{m base}\in\{-1,0,1\};
  \]
- D8-A:
  \[
  M=(1-R_0)R_1\in\{0,1\}.
  \]

D8-A is therefore a continuous monotone-augmentation model and does not claim direct validity for the empirical selected-winner pipeline.

## Repairs incorporated in D8-A v4

1. Identified the policy as a **continuous monotone augmentation**.
2. Distinguished gain-only \(M\) from the signed empirical full-minus-base increment.
3. Limited the matched comparator to a finite-sample plug-in estimand.
4. Added a subsection separating finite-sample estimation from promising/rescue allocation questions.
5. Stated that the D8-A validation uses no fitted-model library, clinical dataset, or policy-allocation simulation output.
6. Clarified that TESS itself is not the claimed methodological contribution.
7. Aligned the Proof Supplement with the same boundary.

## Publication workflow

The distinct-paper boundary is scientifically defensible. Once either paper is public, the other should cite it for the shared definitions. If the manuscripts are under review concurrently, the related manuscript should be disclosed to both editors, with an explicit statement that no simulations, fitted-model results, clinical-data results, principal figures, or tables are shared.

## Final adjudication

**PASS — distinct-paper boundary established.**

Use D8-A Main Manuscript Draft v4 and Proof Supplement Draft v3 as the working versions.
