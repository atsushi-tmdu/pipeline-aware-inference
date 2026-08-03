# Work Package D5 Protocol

## Exact plus-one/order-statistic bridge for the D4 paired policy contrast

**Status:** locked before scientific run
**Parent branch:** `tess-top-tier-theory`
**Preceding frozen result:** `d4-validation-full-v1`

---

# 1. Purpose

Work Package D5 studies the exact finite-reference-bank boundary induced by the
plus-one Monte Carlo p-value rule and connects it to the empirical
generalized-inverse quantile representation used in Work Packages D1-D4.

D5 does not modify D4. The D4 theory, code, configuration, numerical results,
freeze record, commit, and tag remain immutable.

The primary question is whether replacing the exact plus-one candidate
boundary by the D1-D4 quantile boundary changes the paired adaptive-versus-
budget-matched-random policy contrast at first order.

---

# 2. Locked parent estimator

For a candidate score \(x\) and a reference bank
\(X_1,\ldots,X_B\), the empirical paper uses

\[
\widehat p_B^+(x)
=
\frac{1+\sum_{b=1}^B I(X_b\ge x)}{B+1}.
\]

The exact candidate-level rejection event is

\[
\widehat p_B^+(x)<\alpha.
\]

The D1-D4 regular representation instead uses the empirical
generalized-inverse threshold

\[
\widehat q_B^Q(\alpha)
=
X_{(k_B^Q(\alpha))},
\qquad
k_B^Q(\alpha)
=
\left\lceil B(1-\alpha)\right\rceil,
\]

with rejection event \(x>\widehat q_B^Q(\alpha)\).

The D4 activation threshold is not a Monte Carlo p-value boundary. D5 therefore
keeps the D4 activation threshold unchanged:

\[
\widehat c_B
=
\widehat F_{U,B}^{-1}(1-r).
\]

Only the candidate thresholds \(q_0\) and \(q_1\) differ between the two
boundary modes.

---

# 3. Exact finite-\(B\) boundary

Define

\[
C_B(\alpha)
=
\left\lceil (B+1)\alpha\right\rceil.
\]

If \(C_B(\alpha)=1\), the strict event
\(\widehat p_B^+(x)<\alpha\) is impossible.

If \(C_B(\alpha)\ge2\), define

\[
k_B^+(\alpha)
=
B+2-C_B(\alpha).
\]

D5 will prove, with the declared \(\ge\) count and strict \(<\alpha\) rule, that

\[
\widehat p_B^+(x)<\alpha
\iff
x>X_{(k_B^+(\alpha))}.
\]

For an independent continuous evaluation score,

\[
\tau_B^+(\alpha)
=
P\{X_{\mathrm{eval}}>X_{(k_B^+(\alpha))}\}
=
\frac{C_B(\alpha)-1}{B+1}.
\]

This is the largest attainable plus-one p-value grid point strictly below
\(\alpha\).

For the D1-D4 quantile convention, an independent continuous evaluation
score has finite-\(B\) rejection probability

\[
\tau_B^Q(\alpha)
=
\frac{B+1-k_B^Q(\alpha)}{B+1}.
\]

The adjacent-boundary identity to be proved is

\[
k_B^+(\alpha)-k_B^Q(\alpha)\in\{0,1\}
\]

whenever the plus-one rejection event is attainable. Consequently,

\[
\tau_B^Q(\alpha)-\tau_B^+(\alpha)
\in
\left\{0,\frac1{B+1}\right\}.
\]

This is an exact finite-\(B\) identity, not an asymptotic approximation.

---

# 4. D5 estimators

For every D4 outer dataset, D5 computes two versions of the same paired policy
contrast.

## 4.1 Quantile version

The quantile version is the unchanged D4 estimator:

\[
\widehat\Delta_\pi^Q
=
\widehat\pi_A^Q-\widehat\pi_C^Q,
\]

and

\[
\widehat\Delta_S^Q
=
g_\alpha(\widehat\pi_A^Q)
-
g_\alpha(\widehat\pi_C^Q),
\qquad
g_\alpha(\pi)
=
\frac{\log(1-\pi)}{\log(1-\alpha)}.
\]

## 4.2 Plus-one version

The plus-one version uses \(k_B^+(\alpha)\) for both candidate thresholds,
retains the D4 activation threshold, and evaluates the identical adaptive and
matched-comparator maps.

Both boundary modes use the **nominal scientific threshold \(\alpha\)** in the
TESS denominator. D5 does not replace \(\log(1-\alpha)\) by
\(\log(1-\tau_B^+)\). This convention is required to match the locked empirical
pipeline and the D4 estimand:

\[
\widehat\Delta_\pi^+
=
\widehat\pi_A^+-\widehat\pi_C^+,
\]

\[
\widehat\Delta_S^+
=
g_\alpha(\widehat\pi_A^+)
-
g_\alpha(\widehat\pi_C^+).
\]

## 4.3 Bridge discrepancies

The primary D5 numerical quantities are

\[
D_{\pi,B,n}
=
\widehat\Delta_\pi^+
-
\widehat\Delta_\pi^Q
\]

and

\[
D_{S,B,n}
=
\widehat\Delta_S^+
-
\widehat\Delta_S^Q.
\]

The two versions must use the same reference bank, evaluation bank,
activation threshold, policy-state realization, and comparator construction.

---

# 5. Theorem targets

## D5-T1. Exact order-statistic equivalence

Prove the exact finite-\(B\) equivalence in Section 3, including:

- the strict p-value inequality;
- the reference count using \(I(X_b\ge x)\);
- the unattainable region \(C_B(\alpha)=1\);
- the integer rounding convention;
- ties and the continuous-law specialization.

## D5-T2. Adjacent-boundary lemma

Prove that the exact plus-one threshold and D1-D4 generalized-inverse threshold
are identical or adjacent order statistics.

## D5-T3. Adjacent-random-boundary rate theorem

Under continuous densities that are positive and finite near the candidate
quantiles, suitable local regularity of the conditional policy increments,
and over a compact alpha interval bounded away from zero and one, establish
the sharper rate

\[
D_{\pi,B,n}
=
O_p\left(
\frac1B+\frac1{\sqrt{Bn}}
\right).
\]

The \(B^{-1}\) term is the probability mass between adjacent reference order
statistics. The \((Bn)^{-1/2}\) term is the evaluation empirical fluctuation
of that shrinking interval.

The theorem must then state explicitly that, when \(B\to\infty\) and
\(n\to\infty\),

\[
D_{\pi,B,n}
=
o_p(B^{-1/2}+n^{-1/2}).
\]

The proof must preserve the pairing of the two policies and identify any
additional cancellation specific to the D4 contrast without requiring that
cancellation for the general upper bound.

## D5-T4. Nominal-alpha TESS-scale bridge

Under an alpha interval bounded away from zero, and rejection probabilities
bounded away from one, transfer D5-T3 through the nominal-alpha TESS map:

\[
D_{S,B,n}
=
O_p\left(
\frac1B+\frac1{\sqrt{Bn}}
\right)
=
o_p(B^{-1/2}+n^{-1/2}).
\]

The role of

\[
g_\alpha'(\pi)
=
-\frac{1}{(1-\pi)\log(1-\alpha)}
\]

must be explicit. The proof must also explain why uniformity can fail when
\(\alpha\) approaches zero.

## D5-T5. Non-negligible regimes

Characterize regimes in which plus-one discreteness need not be negligible,
including:

- fixed \(B\);
- \(B\alpha=O(1)\);
- alpha near an attainable plus-one grid boundary;
- alpha approaching zero fast enough for the TESS derivative to amplify an
  order-\(B^{-1}\) rejection-scale discrepancy.

The small-alpha analysis should track the nominal leading scale

\[
O_p\left(
\frac1{B\alpha}
+
\frac1{\alpha\sqrt{Bn}}
\right)
\]

on the TESS scale, subject to the rejection probabilities remaining away from
one. In particular, comparison with an \(n^{-1/2}\) first-order scale should
make the conditions involving \(\sqrt n/(B\alpha)\) and
\(1/(\alpha\sqrt B)\) explicit.

A documented impossibility or non-equivalence result is acceptable if a
uniform first-order bridge cannot hold in such regimes.

---

# 6. Reuse of the frozen D4 datasets

D5 reuses the exact D4 outer datasets by deterministic regeneration.

For D4 outer replication \(o\) in DGP \(d\) and cell \(c\), the random generator
identity is

```python
np.random.SeedSequence(
    [20261117, dgp_index, cell_index, outer_index]
)
```

The reference bank is drawn first and the evaluation bank second from the same
generator, exactly as in D4.

A prospective unit-level reproduction test must verify one independently
regenerated outer dataset from every one of the 36 D4 cells against the frozen
D4 replication file with maximum absolute error at most \(10^{-12}\).

The completed pre-protocol audit reproduced all 36 cells with overall maximum
absolute error \(4.441\times10^{-16}\).

The full scientific D5 run must additionally verify **all 108,000 regenerated
quantile-mode estimates** against the corresponding frozen D4 replication
records to the same \(10^{-12}\) tolerance before using the paired plus-one
results for adjudication.

Before importing or executing D4 sampling and estimator code, D5 must verify:

- the annotated D4 results tag `d4-validation-full-v1`;
- the expected D4 results commit
  `9b0a2530bfb5e363f59bd7b290d1c064c82b5eaa`;
- the D4 lock manifest and its declared file hashes;
- the SHA-256 identity of the frozen D4 replication file.

A failed parent-integrity check is fatal.

---

# 7. Numerical design

D5 inherits the D4 scientific design without alteration:

- DGPs:
  - `independent_normal`;
  - `gaussian_factor` with D4 parameters;
  - `nonlinear_smooth` with D4 parameters.
- activation-rate target: \(r=0.50\);
- alpha grid: \(\{0.01,0.05,0.10\}\);
- designs:
  - \((B,n)=(500,500)\);
  - \((B,n)=(1000,1000)\);
  - \((B,n)=(3000,3000)\);
  - \((B,n)=(3000,5000)\);
- outer repetitions per cell: 3000;
- total cells: 36;
- total regenerated outer datasets: 108,000;
- master seed: 20261117.

D5 does not rerun the D4 bootstrap. Its numerical purpose is the fully paired
boundary discrepancy, not revalidation of D4 interval coverage.

---

# 8. Recorded quantities

For every outer dataset, D5 records:

## Identity

- `dgp_index`;
- `cell_index`;
- `outer_index`;
- `dgp`;
- `B`;
- `n`;
- `alpha`;
- target activation rate.

## Integer boundary

- \(C_B(\alpha)\);
- \(k_B^Q(\alpha)\);
- \(k_B^+(\alpha)\), or an unattainable-boundary flag;
- order-index gap;
- \(\tau_B^Q\);
- \(\tau_B^+\);
- marginal tail-probability gap.

## Thresholds

- quantile \(q_0^Q,q_1^Q\);
- plus-one \(q_0^+,q_1^+\);
- common activation threshold \(c\);
- threshold spacings \(q_j^+-q_j^Q\).

## Policy estimates

For both boundary modes:

- base rejection rate;
- activation rate;
- incremental-rejection rate;
- activated incremental-rejection rate;
- adaptive rejection probability;
- comparator rejection probability;
- rejection-probability contrast;
- adaptive TESS;
- comparator TESS;
- TESS contrast.

## Bridge outcomes

- \(D_{\pi,B,n}\);
- \(D_{S,B,n}\);
- absolute discrepancies;
- discrepancies scaled by \(\sqrt n\), \(\sqrt B\), and \(B\);
- strict sign reversals and zero-status changes in the paired policy contrast;
- relative discrepancy compared with the empirical D4 contrast standard
  deviation in the same cell.

---

# 9. Cell-level summaries

For every cell, report:

- mean, median, standard deviation, RMS, and selected quantiles of
  \(D_{\pi,B,n}\) and \(D_{S,B,n}\);
- Monte Carlo standard errors for means, RMS quantities, and reported
  frequencies;
- mean absolute discrepancy;
- maximum absolute discrepancy;
- frequency of exact equality;
- frequencies of strict sign reversal and zero-status change;
- \(B\)-scaled and first-order-scaled discrepancy summaries;
- comparison with the frozen D4 empirical contrast standard deviation;
- separate summaries for the main regime \(B=3000\) and stress regimes
  \(B\le1000\).

No direction or magnitude of the bridge discrepancy is assumed in advance.

---

# 10. Validation rules

## Fatal failure

D5 fails if any of the following occurs:

- the D4 lock or frozen-results identity cannot be verified;
- deterministic bank reproduction exceeds \(10^{-12}\);
- exact integer-boundary unit tests fail;
- regenerated quantile-mode D4 estimates differ from the frozen D4 estimates
  by more than \(10^{-12}\);
- a nonfinite output is produced;
- the plus-one and quantile estimators are not evaluated on identical banks;
- the activation threshold differs across boundary modes;
- a declared output or manifest file is missing.

## Scientific adjudication

Numerical magnitude is not allowed to determine whether the implementation
passes. The adjudication must report transparently whether the observed bridge
is negligible, small, or material relative to the frozen D4 first-order
uncertainty.

A favorable result must not be selected by changing DGPs, alpha values,
sample sizes, seeds, summary metrics, or interpretation thresholds after lock.

---

# 11. Interpretation scale

For each cell define

\[
R_\pi
=
\frac{\operatorname{RMS}(D_{\pi,B,n})}
{\operatorname{SD}(\widehat\Delta_\pi^Q)}
\]

and

\[
R_S
=
\frac{\operatorname{RMS}(D_{S,B,n})}
{\operatorname{SD}(\widehat\Delta_S^Q)}.
\]

The following labels are descriptive rather than pass/fail criteria:

- `negligible`: ratio below 0.10;
- `small`: ratio from 0.10 to below 0.25;
- `material`: ratio 0.25 or greater.

The exact ratios and unthresholded summaries remain primary. Labels may not
replace the numerical results. If a frozen D4 cell has zero empirical contrast
standard deviation, its ratio is reported as undefined rather than divided by
zero.

The labels are descriptive only and cannot determine PASS or FAIL.

---

# 12. Outputs

The locked D5 run will produce:

- `D5_BRIDGE_REPLICATIONS.csv.gz`;
- `D5_BRIDGE_CELL_SUMMARY.csv`;
- `D5_BOUNDARY_TABLE.csv`;
- `D5_VALIDATION_CHECKS.json`;
- `D5_VALIDATION_SUMMARY.json`;
- `D5_VALIDATION_ADJUDICATION.md`;
- `D5_VALIDATION_MANIFEST.json`.

Raw outputs will be ignored by Git. A compact results-freeze directory will
contain the adjudication, summary, boundary table, inventory, run log, and
SHA-256 manifest.

---

# 13. Locking sequence

Before any scientific D5 run:

1. review this protocol;
2. implement D5 in a separate `work_package_d5` directory;
3. add unit and deterministic-reproduction tests;
4. run runtime-only smoke checks;
5. freeze the scientific configuration;
6. generate and verify a lock manifest;
7. commit and create an annotated D5 protocol/implementation lock tag;
8. run the full paired bridge analysis;
9. adjudicate without changing the locked design;
10. freeze, commit, tag, and push the D5 results.

---

# 14. Scope boundary

D5 does not cover:

- multiple candidates within a branch;
- winner selection;
- a base trigger defined by a maximum score;
- winner ties or deterministic tie randomization;
- failed-fit fallback rules;
- simultaneous threshold-process inference.

Those extensions begin only after the exact plus-one bridge is completed or
its obstruction is documented.
