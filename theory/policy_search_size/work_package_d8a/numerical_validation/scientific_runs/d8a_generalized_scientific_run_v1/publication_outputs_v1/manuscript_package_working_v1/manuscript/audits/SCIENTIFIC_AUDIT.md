# Scientific and Structural Audit of Main Manuscript Draft v1

## Overall verdict

**Status: scientifically coherent after repair; not yet submission-ready.**

No fatal contradiction was found between the central policy expansion, the
generalized coincidence theorem, the exact finite-\(n\) identity, the TESS
corollary, and the locked numerical results. Draft v1 nevertheless contained
several material omissions or notation problems that could have triggered
reviewer objections. These have been corrected in Draft v2.

## Major findings corrected in v2

### 1. Gaussian limit omitted from Theorem 1

Draft v1 stated the reference mean, second moment, and \(2+\eta\) bound, but did
not state

\[
\sqrt B(\widehat\theta_R-\theta)\Rightarrow N(0,\Sigma_\theta).
\]

That limit is needed to justify

\[
E(d_a^\top Z)_+^2
=
\frac12d_a^\top\Sigma_\theta d_a
\]

in the generalized expectation coefficient. The Gaussian limit is now explicit.

### 2. Collision of the symbol \(H\)

Draft v1 used \(H\) both for the adaptive rejection indicator and for the
moving-\(\max\) winner-cell kernel. The kernel has been renamed \(K\), with
integrated derivatives \(J_s\) and \(J_{ss}\); the adaptive rejection indicator
is now \(R_A\).

### 3. Incremental rejection and comparator were underdefined

The manuscript now defines

\[
M=(1-R_0)R_1,
\qquad
R_A=R_0+AM,
\]

which establishes that \(R_A\) is binary and avoids double counting. The
matched comparator is formally defined through an independent
\(A^\circ\sim\mathrm{Bernoulli}(\rho)\), with
\(R_C=R_0+A^\circ M\).

### 4. Probability notation was inconsistent

Draft v1 alternated among \(\rho\), \(P_A\), and \(P_A(\theta)\) without
explicit identification. Draft v2 defines
\(P_A=\rho\), \(P_M=\mu\), and \(P_{AM}=\nu\), and uses
\(\rho(\theta)\) in the branch coefficient.

### 5. Formal residual scales were missing

The acceptance decision cannot be reconstructed from \(R_{\mathrm{adj}}\)
without its denominator. Draft v2 restores the locked reference, combined, and
TESS scales.

### 6. The \(B^{-1}n^{-1}\) term needed qualification

The product term is algebraically determined by multiplying the reference
expansion by the exact factor \(1-1/n\). With remainder
\(o(B^{-1}+n^{-1})\), however, it is not separately resolved as an asymptotic
order. Draft v2 retains the term but states this limitation explicitly.

## Additional corrections

- Defined the target law and identified the global-null application.
- Defined standard basis vectors \(e_j\).
- Clarified strict candidate–trigger separation.
- Added the main simulation-class construction: three dependence structures,
  probability settings, common candidate thresholds, and transformation audits.
- Replaced internal wording “committed replicates” with “Monte Carlo replicates.”
- Defined the locked zero-denominator rule for the median-improvement statistic.
- Removed the unsupported implication that structural results are already
  available as a citable companion paper.
- Corrected the code-availability statement: Figure 1 currently has a locked
  raster reference but no deterministic editable source.

## Items still unresolved

### A. Literature and novelty audit

All `[REF]` placeholders and the reference list remain incomplete. No priority
claim should be made before a focused search of second-order quantile bias,
nonsmooth delta methods, and piecewise-quadratic functionals.

### B. Complete proof supplement

The main theorem statements are coherent, but submission requires a unified
supplement containing primitive assumptions, proof dependencies, and the
generalized coincidence repair in final notation.

### C. Figure 1 production status

The approved Figure 1 is a locked raster visual reference. It should not be
represented as a deterministic source figure. Before submission it should be
manually rebuilt as an editable vector or otherwise handled in accordance with
the target journal's image and generative-AI policy.

### D. Numerical-design exposition

Draft v2 is adequate for a main-text overview, but the exact class registry,
probability values, dependence matrices, scale definitions, simultaneous-factor
derivations, and stopping implementation must remain available in the
Supplement and repository.

### E. Overlap audit

A line-by-line comparison with the frozen empirical version 2 is still needed.
Definitions may overlap, but principal claims, figures, tables, and numerical
evidence must remain distinct.

## Recommendation

Use Draft v2 as the next working manuscript. Do not commit it as a final
manuscript checkpoint until the proof supplement and literature audit have
been completed.
