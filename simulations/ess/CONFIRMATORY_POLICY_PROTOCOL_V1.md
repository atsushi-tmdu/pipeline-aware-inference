# TESS Confirmatory Adaptive-Policy Study v1

**Status:** LOCKED BEFORE CONFIRMATORY RUN  
**Configuration SHA-256:** `ae58b6080bc4ae27a6e89e2545ebf7a0c8b9e12d96f3bc99012f3df03ccac1e8`

## 1. Purpose

The exploratory Phase 3C reanalysis suggested that adaptive expansion of an
ML candidate library creates a policy-level multiplicity effect that cannot be
explained by maximum candidate count or expected search budget alone.

This confirmatory study uses:

- fresh data-generation seeds,
- a new independent null-reference bank,
- a separate global-null evaluation bank,
- prespecified candidate libraries,
- prespecified activation rules,
- prespecified estimands and success criteria.

No Phase 3C exploratory result is used to tune this configuration.

---

## 2. Candidate libraries

Two prespecified 20-model libraries are used.

1. `high_dependency_linear_20`
2. `mixed_realistic_20`

The first 7 candidates form the base library. The remaining 13 candidates form
the optional expansion family.

---

## 3. Simulation size

Per library:

- null-reference replications: **5,000**
- independent global-null evaluation replications: **5,000**
- target AUROC: **0.50 only**
- selection-event count: **100**
- feature selection: **none**
- metric: **ROC AUC**

The fresh master seed is `20260817`.

---

## 4. Adaptive policies

The base-stage statistic is the maximum selection ROC AUC among the first
7 candidates.

The expansion threshold is calibrated in the independent reference bank so
that promising expansion occurs with probability 0.50, using a deterministic
tie randomization rule.

Policies:

1. fixed base, K=7
2. fixed full, K=20
3. random expansion
4. promising-triggered expansion
5. rescue-triggered expansion

The budget-matched random benchmarks use the observed activation rate of the
corresponding data-dependent policy.

---

## 5. Primary estimand

Primary library: `mixed_realistic_20`  
Primary alpha: **0.05**

\[
\Delta_{\mathrm{primary}}
=
\mathrm{TESS}_{\mathrm{promising}}(0.05)
-
\mathrm{TESS}_{\mathrm{random,\ matched\ budget}}(0.05).
\]

### Confirmatory success rule

The primary result is confirmed if the two-sided paired-bootstrap 95% confidence
interval has a lower bound greater than zero.

Bootstrap replications: **20,000**.

---

## 6. Key secondary estimands

1. The matched-budget promising effect on the rejection-probability scale.
2. The covariance
   \[
   \operatorname{Cov}\left(
   A,\,
   R_{\mathrm{full}}(0.05)-R_{\mathrm{base}}(0.05)
   \right).
   \]
3. The rescue-minus-matched-random TESS effect in the mixed library.
4. The difference in promising policy effects:
   \[
   \Delta_{\mathrm{mixed}}(0.05)
   -
   \Delta_{\mathrm{high}}(0.05).
   \]
5. Secondary TESS curves at alpha 0.10, 0.025, and 0.01.

Secondary findings are interpreted descriptively unless their paired-bootstrap
95% intervals exclude zero.

---

## 7. Reconstruction requirements

For fixed K=7 and K=20, reconstructed winner p-values must be audited against
the native Phase 3 inference output.

The confirmatory analysis requires:

- zero rejection-decision mismatches at all declared alpha values,
- all discrepancies to be reported,
- tie-related winner-name differences to be documented.

---

## 8. Analysis hierarchy

### Primary evidence

The fresh locked confirmatory simulation.

### Motivating evidence

The prior Phase 3C reanalysis.

### Theory and validation

- complete dependence and independence boundaries,
- Gaussian exact integration,
- t-copula and max-stable comparisons,
- analytic adaptive-branching examples.

---

## 9. Prohibited changes after locking

After committing this protocol and configuration, do not change:

- seeds,
- repetition counts,
- candidate order,
- base/extra split,
- primary library,
- primary alpha,
- primary estimand,
- success criterion,
- bootstrap count.

Any unavoidable software correction must be documented in a changelog and must
not depend on the observed confirmatory result.

---

## 10. Output locations

Simulation banks:

```text
results_ess_confirmatory/policy_v1_seed20260817/
```

Processed analysis:

```text
simulations/ess/outputs/confirmatory_policy_v1/
```

Final adjudication:

```text
simulations/ess/outputs/confirmatory_policy_v1/CONFIRMATORY_ADJUDICATION.md
```
