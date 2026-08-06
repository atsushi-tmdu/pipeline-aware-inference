# D8-A Manuscript Identity and Architecture v1

## 1. Scientific identity

This manuscript is a theory-and-validation paper on finite-reference and finite-evaluation bias in estimated threshold-adaptive policy functionals.

It is not primarily:

- an empirical comparison of promising, rescue, and matched-random search policies;
- a paper about candidate-count budgets or policy-allocation covariance;
- a general post-selection-inference or multiplicity-correction paper;
- a paper whose main novelty is the TESS transformation itself.

Its central object is the plug-in estimator of a policy contrast obtained from an independent reference bank and an independent evaluation sample.

The main theoretical target is

\[
E(\widehat{\Delta}_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}
+
o(B^{-1}+n^{-1}),
\]

where \(C_{\Delta,B}^{\mathrm{gen}}\) is a generalized second-order reference-bias coefficient that retains threshold-coincidence contributions.

TESS is treated as a nonlinear corollary of this policy-probability expansion rather than as the primary scientific object.

---

## 2. Recommended title

### Preferred

**Second-Order Finite-Sample Bias in Threshold-Adaptive Statistical Policies**

### Strong alternatives

1. **Generalized Second-Order Bias Expansions for Threshold-Adaptive Policies**
2. **Finite-Reference and Evaluation Bias in Adaptive Statistical Policy Functionals**
3. **Threshold Coincidence and Second-Order Bias in Adaptive Policy Estimation**

The preferred title is broad enough to include both the \(B^{-1}\) and \(n^{-1}\) contributions, while retaining the policy-level setting and avoiding overemphasis on TESS.

---

## 3. One-sentence claim

For the declared finite-candidate threshold-adaptive policy class, plug-in estimation from independent reference and evaluation banks admits a generalized second-order bias expansion that retains threshold-coincidence terms, includes an exact finite-\(n\) correction and its \(B^{-1}n^{-1}\) interaction, propagates to TESS, and is supported by prospectively locked numerical validation.

---

## 4. Short contribution statement

The manuscript makes four linked contributions.

1. **Generalized reference-bias expansion.**  
   It derives a second-order \(B^{-1}\) correction for policy contrasts estimated through reference-calibrated thresholds.

2. **Threshold-coincidence geometry.**  
   It shows that candidate-threshold coincidences contribute positive-part-square terms rather than being handled by an ordinary smooth Hessian alone.

3. **Exact evaluation-sample correction.**  
   It establishes the exact conditional identity
   \[
   E_E(\widehat{\Delta}_\pi\mid\widehat{\theta}_R)
   =
   \left(1-\frac1n\right)
   \Delta_\pi(\widehat{\theta}_R),
   \]
   yielding the \(-\Delta_\pi/n\) term and the combined \(B^{-1}n^{-1}\) interaction.

4. **Nonlinear TESS propagation and locked validation.**  
   It propagates the expansion through the TESS transformation and evaluates the resulting approximations in 17 prospectively specified primary equivalence classes across 75 locked simulation jobs.

---

## 5. Explicit non-claims

The manuscript should not claim:

- validity for arbitrary adaptive machine-learning pipelines;
- growing candidate dimension;
- discrete winner ties or failed-fit fallback rules unless separately proved;
- universal second-order validity for all nonsmooth policy maps;
- strong raw TESS accuracy when the evidence is MCSE-resolution limited;
- that TESS itself corrects multiplicity;
- that the current numerical validation proves a general process-level result.

The validated scope should be stated using the exact assumptions in the final theorem and protocol.

---

## 6. Main-text architecture

### 1. Introduction

1. Estimated thresholds create finite-reference bias in adaptive policy functionals.
2. Ordinary first-order theory does not quantify the \(B^{-1}\) centering error.
3. Threshold coincidences make the second-order geometry nonstandard.
4. Independent evaluation introduces a separate, exactly characterizable finite-\(n\) effect.
5. State the generalized expansion, TESS corollary, and locked validation.

### 2. Policy functional and two-bank estimation

#### 2.1 Declared policy class
- finite candidate pool;
- reference-calibrated candidate and trigger thresholds;
- policy contrast \(\Delta_\pi\);
- independent reference and evaluation banks.

#### 2.2 Plug-in estimator
- define \(\widehat{\theta}_R\);
- define \(\widehat{\Delta}_\pi\);
- distinguish reference randomness from evaluation randomness.

#### 2.3 TESS transformation
- define \(g_\alpha(\pi)\);
- identify TESS as a smooth transformation away from its boundary.

### 3. Generalized second-order theory

#### 3.1 Smooth reference-threshold expansion
- gradient contribution;
- Hessian–covariance contraction;
- reference-threshold centering bias.

#### 3.2 Threshold-coincidence geometry
- active coincidence set;
- positive-part-square contribution;
- generalized coefficient \(C_{\Delta,B}^{\mathrm{gen}}\).

#### 3.3 Exact finite-\(n\) evaluation identity
- conditional expectation identity;
- exact \(-\Delta_\pi/n\) term.

#### 3.4 Combined \(B,n\) expansion
- \(B^{-1}\);
- \(n^{-1}\);
- \(B^{-1}n^{-1}\);
- remainder and assumptions.

#### 3.5 TESS corollary
- transformed centering contribution;
- transformation curvature contribution;
- boundary-status qualification.

### 4. Prospectively locked numerical validation

#### 4.1 Validation design
- 17 primary and 8 diagnostic equivalence classes;
- three simulation families;
- five reference sizes and five evaluation sizes;
- two TESS levels;
- locked stopping and acceptance rules.

#### 4.2 Reference-only validation
- Figure 2;
- generalized prediction versus observed bias;
- comparison with simpler baselines.

#### 4.3 TESS finite-sample validation
- Figure 3;
- alpha-specific agreement;
- MCSE-resolution interpretation.

#### 4.4 Combined-policy and exact-identity validation
- Figure 4;
- joint \(B,n\) approximation;
- 85 simultaneous exact-identity checks.

### 5. Discussion

1. Main theoretical implication.
2. Why threshold coincidences matter.
3. Separation of reference and evaluation effects.
4. Interpretation of strong policy-level support versus MCSE-limited TESS evidence.
5. Scope limitations.
6. Relationship to the companion policy-level search-size paper.
7. Extensions: ties, failed fits, growing dimension, process-level inference.

---

## 7. Main figures and tables

### Figure 1
**Threshold geometry and generalized second-order expansion**

Role: theoretical roadmap.

### Figure 2
**Reference-only numerical validation**

Role: evidence for the generalized \(B^{-1}\) correction.

### Figure 3
**Alpha-specific TESS-bias agreement and Monte Carlo resolution**

Role: nonlinear propagation and the qualification of the formal pass.

### Figure 4
**Combined-policy approximation and exact finite-\(n\) identity**

Role: joint \(B,n\) validation and fatal implementation check.

### Table 1
**Prospectively locked validation design**

Role: confirmatory contract.

### Table 2
**Formal and auxiliary validation results**

Role: concise adjudication and evidential interpretation.

### Supplementary Table S1
**Detailed validation design**

Role: complete operational specification.

---

## 8. Separation from the former empirical version 2

### Former empirical version 2 retains

- same-budget policy non-identifiability;
- promising, rescue, and matched-random policy comparisons;
- high-dependency and mixed-realistic candidate libraries;
- policy-level rejection curves and TESS contrasts;
- \(\operatorname{Cov}(A,D_\alpha)\) and gain/loss capture;
- SUPPORT2 illustration.

### D8-A retains

- finite-reference threshold estimation;
- generalized second-order bias;
- threshold-coincidence geometry;
- exact finite-\(n\) evaluation identity;
- combined \(B,n\) expansion;
- TESS bias propagation;
- D8-A locked numerical validation.

### Shared material permitted in both papers

Only minimal common definitions and a short relationship statement. The papers should not reuse the same principal figures, tables, empirical results, or central claims.

---

## 9. Recommended abstract spine

### Background
Adaptive policy functionals are often evaluated using thresholds estimated from a finite reference sample. The resulting \(B^{-1}\) bias is not described by ordinary first-order theory, and threshold coincidences can make a standard smooth second-order expansion incomplete.

### Methods
Develop a generalized second-order expansion for a finite-candidate threshold-adaptive policy contrast estimated from independent reference and evaluation banks. Derive the exact finite-\(n\) evaluation identity, the combined \(B,n\) expansion, and the TESS corollary. Validate the results under a prospectively locked design.

### Results
Report strong raw numerical support for the reference and combined-policy expansions, exact agreement in all 85 finite-\(n\) identity checks, and a formal TESS pass whose raw finite-sample accuracy remained limited by Monte Carlo resolution.

### Conclusions
Finite-reference and finite-evaluation effects can be separated and combined analytically, but threshold coincidences require generalized second-order terms. The resulting expansion provides a principled finite-sample approximation for the declared adaptive policy class.

---

## 10. Immediate drafting order

1. Freeze the exact theorem statements and assumptions.
2. Finalize Figure 1–4 captions.
3. Draft Section 4 (Numerical validation) and Results first.
4. Draft Sections 2–3 from the final theorem package.
5. Write Introduction and Discussion after the theorem spine is stable.
6. Perform an explicit overlap audit against the former empirical version 2.
