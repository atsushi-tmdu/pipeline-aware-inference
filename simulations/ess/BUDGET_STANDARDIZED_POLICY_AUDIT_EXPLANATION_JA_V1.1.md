# Budget-standardized adaptive-policy effects and reconstruction audit v1.1

## Purpose

The Phase 3C adaptive-policy reconstruction showed that promising-triggered
expansion produced a larger TESS than rescue-triggered expansion. However,
the observed expansion rates were not exactly identical because the trigger
was calibrated in the frozen reference bank and then applied to a finite
evaluation bank.

This analysis separates:

1. **Search budget** — how often the extra candidate family is activated.
2. **Policy allocation effect** — whether activation is concentrated in data
   states with a high incremental rejection opportunity.

It also audits the small p-value discrepancies between reconstructed fixed
policies and the original Phase 3C inference table.

---

## 1. Budget-matched random benchmark

Let

\[
D_\alpha=R_{\mathrm{full}}(\alpha)-R_{\mathrm{base}}(\alpha)
\]

and let \(A\) denote promising activation with rate \(r=E(A)\).

A random expansion policy with the same activation rate \(r\) has rejection
probability

\[
\pi_{\mathrm{rand},r}
=
\pi_{\mathrm{base}}+rE(D_\alpha).
\]

The promising policy satisfies

\[
\pi_{\mathrm{promising}}
-
\pi_{\mathrm{rand},r}
=
\operatorname{Cov}(A,D_\alpha).
\]

The rescue policy uses \(1-A\), with activation rate \(1-r\), and satisfies

\[
\pi_{\mathrm{rescue}}
-
\pi_{\mathrm{rand},1-r}
=
-\operatorname{Cov}(A,D_\alpha).
\]

Thus the covariance gives an exact budget-standardized policy effect on the
rejection-probability scale.

Because TESS is nonlinear in \(\pi\), the TESS-scale policy effects are
computed by transforming each budget-matched rejection probability.

---

## 2. Gain capture

For each alpha, the analysis also reports:

- number of \(D_\alpha=1\) replications
- proportion of those gains activated by the promising policy
- number and allocation of \(D_\alpha=-1\) losses

This quantifies how efficiently the trigger targets incremental rejection
opportunities.

---

## 3. Reconstruction audit

For fixed K=7 and fixed K=20, reconstructed outputs are compared against the
original Phase 3C `independent_inference_results.csv` with respect to:

- winner model
- winner selection ROC AUC
- naive empirical p-value
- rejection decision at every alpha in the TESS grid

Small p-value differences are acceptable only if their origin is understood
and they do not materially alter the reported rejection probabilities.

---

## 4. Interpretation

A positive budget-standardized promising effect means:

> At the same expected number of evaluated models, the promising trigger
> allocates the extra model family to replications with greater incremental
> rejection opportunity than random allocation.

This is the policy-level component of search multiplicity, distinct from the
computational budget itself.
