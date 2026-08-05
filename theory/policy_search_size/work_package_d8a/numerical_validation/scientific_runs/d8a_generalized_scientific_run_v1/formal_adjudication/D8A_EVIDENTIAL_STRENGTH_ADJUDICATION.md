# D8-A Evidential-Strength Adjudication

- Formal contract status: **PASS**
- Overall interpretation: **FORMAL_PASS_WITH_QUALIFIED_NUMERICAL_SUPPORT**
- Policy expansion evidence: **STRONG_SUPPORT**
- TESS finite-sample evidence: **FORMAL_PASS_BUT_MCSE_RESOLUTION_LIMITED**

## Raw-threshold sensitivity

- Reference B=10,000: PASS
- Combined policy: PASS
- TESS alpha=0.01: FAIL
- TESS alpha=0.05: FAIL

## Improvement robustness

- Generalized versus no correction: 15/17
- Generalized versus gradient-only: 14/17
- Generalized versus smooth-only: 9/17 (reported, nonfatal)
- Fatal 75% conclusion robust to baseline ambiguity: YES

## Interpretation

All prospectively specified formal criteria were met. Policy-level numerical evidence is strong. The TESS criteria passed only after the locked simultaneous MCSE adjustment; the raw normalized TESS residuals did not meet the nominal thresholds. Accordingly, finite-sample TESS usefulness is classified as Monte Carlo-resolution limited rather than strongly confirmed.

No prospective criterion was changed, and no scientific simulation was rerun.
