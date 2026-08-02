# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package B: threshold coherence, simultaneous optimality, and curve crossings

**Theory memo v3 - 2 August 2026**  
**Status:** Work Package B completed; top-tier theory phase continues  
**Starting point:** Theory memo v1 and Work Package A on sharp fixed-rate policy envelopes

---

## Executive assessment

Work Package B is successful.

Work Package A gave a pointwise-in-threshold sharp envelope for one-stage adaptive expansion. Work Package B determines when one policy can remain optimal over an interval of thresholds and shows that no such coherence exists in general.

The main results are:

1. The threshold-indexed conditional incremental effects
   \[
   m_\alpha(S)=E\{D_\alpha\mid S\}
   \]
   admit one common ordering exactly when they are comonotone, under continuous marginal distributions.
2. Under a common monotone index, one top-score activation rule is simultaneously optimal at every threshold in the interval and every activation rate.
3. First-order stochastic dominance of the activation-score distribution provides a general sufficient condition for one policy to dominate another over the full TESS curve.
4. Without rank coherence, policy ordering can reverse with the inferential threshold. In fact, exact-uniform fixed branches and identical candidate-count budgets can generate any prescribed finite pattern of policy-curve crossings.
5. Thus threshold-dependent policy ordering is an additional adaptive-policy phenomenon. It need not be inherited from the marginal p-value laws, fixed-branch TESS curves, or candidate-count budget.
6. When no policy is uniformly optimal, a weighted rejection-curve objective reduces to a top-score rule based on an integrated conditional incremental-effect field.

The mathematics of comonotonicity, stochastic ordering, and monotone comparative statics is established. The candidate new contribution is the application of those ideas to the threshold-indexed incremental-rejection process of an adaptive statistical policy, together with the exact curve-crossing impossibility result.

The top-tier feasibility decision remains **Go**.

---

# 1. Setup and curve-level policy order

Let \(I\subset(0,1)\) be an interval of local inferential thresholds. On one global-null data state, let

\[
R_0(\alpha),R_1(\alpha)\in\{0,1\},\qquad \alpha\in I,
\]

be the counterfactual rejection indicators under fixed base and fixed expanded searches. Define

\[
D_\alpha=R_1(\alpha)-R_0(\alpha)\in\{-1,0,1\}.
\]

Let \(S\) contain all information available at the activation decision. A randomized activation kernel is

\[
a(S)\in[0,1],
\]

with realized activation \(A=I\{V\le a(S)\}\) for an independent \(V\sim\mathrm{Uniform}(0,1)\). At activation rate \(r\),

\[
\mathcal A_r=\left\{a:0\le a(S)\le1,\ E\{a(S)\}=r\right\}.
\]

For every \(\alpha\in I\), define the conditional incremental-rejection field

\[
m_\alpha(S)=E(D_\alpha\mid S).
\]

The policy rejection curve is

\[
\pi_a(\alpha)
=
\pi_0(\alpha)+E\{a(S)m_\alpha(S)\}.
\]

For two rate-matched policies \(a,b\in\mathcal A_r\),

\[
\Delta_{a,b}(\alpha)
:=
\pi_a(\alpha)-\pi_b(\alpha)
=
E\left[\{a(S)-b(S)\}m_\alpha(S)\right].
\]

Because TESS is strictly increasing in the rejection probability at a common \(\alpha\),

\[
\operatorname{sign}\{S_a(\alpha)-S_b(\alpha)\}
=
\operatorname{sign}\{\Delta_{a,b}(\alpha)\}.
\]

We say that \(a\) **curve-dominates** \(b\) on \(I\), written \(a\succeq_I b\), if

\[
\Delta_{a,b}(\alpha)\ge0
\qquad\text{for every }\alpha\in I.
\]

This is generally a partial order: without additional structure, two policy curves may cross.

---

# 2. Threshold rank coherence

## Definition B1. Rank coherence

The family \(\{m_\alpha(S):\alpha\in I\}\) is **rank coherent** if, for independent copies \(S,S'\),

\[
\{m_\alpha(S)-m_\alpha(S')\}
\{m_\beta(S)-m_\beta(S')\}
\ge0
\]

almost surely for every \(\alpha,\beta\in I\).

Thus every pair of states is ordered in the same direction at every threshold. This is precisely comonotonicity of the threshold-indexed family.

## Theorem B1. Common-rank characterization

Assume that the distribution function \(F_\alpha\) of \(m_\alpha(S)\) is continuous for every \(\alpha\in I\). The following are equivalent.

1. The family \(\{m_\alpha(S):\alpha\in I\}\) is rank coherent.
2. There exists a common \(U\sim\mathrm{Uniform}(0,1)\) such that
   \[
   m_\alpha(S)=Q_\alpha(U)
   \qquad\text{a.s. for every }\alpha\in I,
   \]
   where \(Q_\alpha\) is the quantile function of \(m_\alpha(S)\).
3. There exists a nested collection of activation sets \(\{B_r:0<r<1\}\), with \(P(B_r)=r\), such that \(I(B_r)\) maximizes \(\pi_a(\alpha)\) over \(a\in\mathcal A_r\), simultaneously for every \(\alpha\in I\).

### Proof

The equivalence of statements 1 and 2 is the standard common-factor characterization of comonotonic random variables. Under continuous marginal distributions, one may take

\[
U=F_\alpha\{m_\alpha(S)\},
\]

which is the same rank variable for every \(\alpha\) under comonotonicity, and then

\[
m_\alpha(S)=Q_\alpha(U).
\]

Suppose statement 2 holds. Because each \(Q_\alpha\) is nondecreasing, the top-rate set

\[
B_r=\{U>1-r\}
\]

contains the largest values of \(m_\alpha(S)\) for every \(\alpha\). The sharp envelope theorem from Work Package A therefore shows that \(I(B_r)\) is simultaneously optimal at every threshold. The sets are nested in \(r\).

Conversely, suppose statement 3 holds. For continuous \(F_\alpha\), the top-rate maximizing set is unique up to null sets and equals

\[
\left\{F_\alpha\{m_\alpha(S)\}>1-r\right\}.
\]

If the same set is optimal for every \(\alpha\) and every rational \(r\in(0,1)\), the rank variables

\[
U_\alpha=F_\alpha\{m_\alpha(S)\}
\]

have identical upper level sets at all rational cutpoints and hence are equal almost surely. Calling the common rank \(U\) yields statement 2. \(\square\)

## Remarks

1. Continuity is used to avoid nonunique top-rate sets. With atoms, the result extends using one common tie-breaking uniform variable and boundary randomization.
2. A common optimum at one activation rate does not imply full rank coherence. The equivalence requires common optimal sets over all rates.
3. The comonotonic representation is classical. Its policy-level implication - one activation ordering that is simultaneously optimal across the entire inferential threshold interval - is the relevant result here.

## Corollary B1. Common monotone index

Suppose there is a scalar score \(T=T(S)\) and nondecreasing functions \(h_\alpha\) such that

\[
m_\alpha(S)=h_\alpha\{T(S)\}
\qquad\text{for every }\alpha\in I.
\]

Then the top-\(r\) rule based on \(T\) is simultaneously optimal over \(I\), and the bottom-\(r\) rule is simultaneously minimal.

A particularly transparent sufficient form is

\[
m_\alpha(S)=b_\alpha+c_\alpha\psi\{T(S)\},
\qquad c_\alpha\ge0,
\]

with \(\psi\) nondecreasing.

---

# 3. Uniform policy dominance through stochastic ordering

The common-index result can compare policies that are not exactly top- and bottom-tail rules.

Fix a common score \(T\) and a rate \(r>0\). For a policy \(a\in\mathcal A_r\), define the probability law of the score among activated states by

\[
\nu_a(B)
=
\frac{E\left[a(S)I\{T(S)\in B\}\right]}{r}.
\]

## Theorem B2. Activation-score stochastic dominance

Suppose

\[
m_\alpha(S)=h_\alpha\{T(S)\}
\]

with every \(h_\alpha\) nondecreasing. Let \(a,b\in\mathcal A_r\). If

\[
\nu_a\succeq_{\mathrm{FOSD}}\nu_b,
\]

then

\[
\pi_a(\alpha)\ge\pi_b(\alpha)
\quad\text{and}\quad
S_a(\alpha)\ge S_b(\alpha)
\qquad\text{for every }\alpha\in I.
\]

### Proof

By the policy representation,

\[
\pi_a(\alpha)-\pi_b(\alpha)
=
r\left\{
\int h_\alpha(t)\,d\nu_a(t)
-
\int h_\alpha(t)\,d\nu_b(t)
\right\}.
\]

First-order stochastic dominance makes this difference nonnegative for every nondecreasing function \(h_\alpha\). Monotonicity of the TESS transform gives the second conclusion. \(\square\)

## Corollary B2. Promising-random-rescue ordering

Let \(a_r^\uparrow\) activate the top \(r\) fraction of \(T\), let \(a_r^0(S)=r\) be random activation independent of \(T\), and let \(a_r^\downarrow\) activate the bottom \(r\) fraction. Then

\[
\nu_{a_r^\uparrow}
\succeq_{\mathrm{FOSD}}
\nu_{a_r^0}
\succeq_{\mathrm{FOSD}}
\nu_{a_r^\downarrow},
\]

and therefore

\[
\pi_{a_r^\uparrow}(\alpha)
\ge
\pi_{a_r^0}(\alpha)
\ge
\pi_{a_r^\downarrow}(\alpha)
\]

and

\[
S_{a_r^\uparrow}(\alpha)
\ge
S_{a_r^0}(\alpha)
\ge
S_{a_r^\downarrow}(\alpha)
\]

throughout \(I\).

This is the curve-level theoretical analogue of the promising-random-rescue ordering observed in the locked confirmatory study. Empirical absence of crossings is consistent with approximate common-index coherence, although it does not prove it.

---

# 4. Crossing criterion and simultaneous regret

## Proposition B1. Exact crossing criterion

For two rate-matched policies \(a,b\), define

\[
\Delta_{a,b}(\alpha)
=
E\left[\{a(S)-b(S)\}m_\alpha(S)\right].
\]

At every threshold,

\[
\operatorname{sign}\{S_a(\alpha)-S_b(\alpha)\}
=
\operatorname{sign}\{\Delta_{a,b}(\alpha)\}.
\]

If \(\Delta_{a,b}\) is continuous and has opposite signs at two thresholds, the rejection and TESS curves cross between them.

Thus threshold crossings are caused by a change in the alignment between the fixed policy contrast \(a-b\) and the threshold-indexed conditional field \(m_\alpha\).

## Simultaneous regret

Let

\[
\pi_r^U(\alpha)
=
\max_{a\in\mathcal A_r}\pi_a(\alpha)
\]

be the pointwise sharp upper envelope from Work Package A. Define the uniform rejection-curve regret

\[
\mathcal R_I(a;r)
=
\max_{\alpha\in I}
\left\{
\pi_r^U(\alpha)-\pi_a(\alpha)
\right\}.
\]

Assume throughout this paragraph that the relevant curves are continuous on the compact interval \(I\), so the displayed maxima exist. Under rank coherence, the common top-score rule has \(\mathcal R_I=0\). If the pointwise optimal state ordering reverses across thresholds, no single policy can have zero regret over the interval. Without continuity, the same statements hold with maxima replaced by suprema.

---

# 5. Exact threshold reversal with exact-uniform fixed branches

The next construction shows that curve crossing does not require threshold-dependent marginal validity or different candidate budgets.

Let \(h:[0,1]\to\mathbb R\) be continuously differentiable with

\[
h(0)=h(1)=0.
\]

Choose \(\varepsilon>0\) such that

\[
\varepsilon\|h'\|_\infty<1.
\]

Then

\[
F(x)=x+\varepsilon h(x),
\qquad
G(x)=x-\varepsilon h(x)
\]

are continuous distribution functions on \([0,1]\).

Let \(S\in\{-1,+1\}\) with equal probabilities. Conditional on \(S=+1\), let the base-branch p-value have distribution \(G\) and the optional-branch p-value distribution \(F\). Conditional on \(S=-1\), swap these distributions. Conditional dependence between the two p-values may be chosen arbitrarily and held fixed.

Unconditionally, both branch p-values are exactly uniform because

\[
\tfrac12F(x)+\tfrac12G(x)=x.
\]

Let the target activation rate be \(r\in(0,1)\), and choose

\[
0<d\le\min(r,1-r).
\]

Define two activation kernels

\[
a_H(S)=r+dS,
\qquad
a_L(S)=r-dS.
\]

We call these the high-alignment and low-alignment policies, respectively.

Both policies have activation probability \(r\), the same binary candidate-count distribution, and the same expected candidate-count budget.

## Theorem B3. Arbitrary smooth policy-curve difference

For every \(\alpha\in(0,1)\),

\[
\pi_H(\alpha)
=
\alpha+2d\varepsilon h(\alpha),
\]

\[
\pi_L(\alpha)
=
\alpha-2d\varepsilon h(\alpha),
\]

and hence

\[
\pi_H(\alpha)-\pi_L(\alpha)
=
4d\varepsilon h(\alpha).
\]

Consequently, the rejection and TESS curves cross at every interior zero of \(h\), with ordering determined by the sign of \(h\).

### Proof

The unconditional base rejection probability is \(\alpha\). The conditional incremental-rejection field is

\[
m_\alpha(S)=2\varepsilon S h(\alpha).
\]

Therefore

\[
E\{a_H(S)m_\alpha(S)\}
=
2\varepsilon h(\alpha)
E\{(r+dS)S\}
=
2d\varepsilon h(\alpha),
\]

because \(E(S)=0\) and \(E(S^2)=1\). The calculation for \(a_L\) has the opposite sign. Substitution into the policy representation gives the result. \(\square\)

## Corollary B3. A reversal at any prescribed threshold

For any \(\tau\in(0,1)\), take

\[
h_\tau(\alpha)
=
\alpha(1-\alpha)(\tau-\alpha).
\]

With sufficiently small \(\varepsilon\), the construction is valid and

- high-alignment policy has the larger rejection probability for \(0<\alpha<\tau\);
- the policies tie at \(\alpha=\tau\);
- low-alignment policy has the larger rejection probability for \(\tau<\alpha<1\).

At \(r=d=1/2\), the policies are deterministic state rules. Both fixed branches have TESS 1 at every threshold, yet the adaptive policies cross at the arbitrarily chosen threshold \(\tau\).

## Corollary B4. Any finite crossing pattern

For prescribed thresholds

\[
0<\tau_1<\cdots<\tau_J<1,
\]

choose

\[
h(\alpha)
=
\alpha(1-\alpha)
\prod_{j=1}^J(\alpha-\tau_j).
\]

After multiplying by a sufficiently small positive constant, the construction in Theorem B3 is valid. The two same-budget policy curves cross at every \(\tau_j\) and alternate their ordering between successive crossings.

Thus no ordering of adaptive policies over the complete TESS curve can be inferred from:

- exact validity of each fixed branch;
- the joint fixed branch law;
- common activation probability;
- candidate-count distribution;
- expected candidate-count budget.

The missing object is the threshold-indexed coupling between activation and conditional incremental rejection.

---

# 6. Threshold dependence beyond fixed-family copulas

For two fixed counterfactual branch p-values \(P_0,P_1\),

\[
m_\alpha(S)
=
P(P_1<\alpha\mid S)
-
P(P_0<\alpha\mid S).
\]

Hence threshold coherence is a statement about the ordering of conditional CDF differences across states. Fixed marginal distributions and the unconditional copula do not determine this conditional ordering.

The construction in Theorem B3 is deliberately strong:

- both fixed branch p-values are exactly uniform;
- both fixed branch TESS curves equal 1;
- the full joint law of the state and both branch outputs is held fixed;
- only the activation kernel changes;
- nevertheless adaptive policy curves can cross once, many times, or according to any prescribed finite smooth pattern.

Fixed-family copula geometry can itself create threshold-dependent TESS, as established in theory memo v1. Work Package B shows a second and logically separate source of threshold dependence: **policy-state coupling can create curve crossings even when fixed branch TESS curves are threshold invariant.**

---

# 7. A weighted compromise when coherence fails

If the family \(m_\alpha(S)\) is not rank coherent, no policy need be pointwise optimal at every threshold. A scientifically declared weighting of thresholds provides one compromise criterion.

Let \(W\) be a finite nonnegative measure on \(I\), and define the weighted rejection-curve objective

\[
J_W(a)
=
\int_I \pi_a(\alpha)\,W(d\alpha).
\]

Define the integrated incremental-effect score

\[
\bar m_W(S)
=
\int_I m_\alpha(S)\,W(d\alpha).
\]

## Theorem B4. Weighted-curve optimal policy

Among all \(a\in\mathcal A_r\), the objective \(J_W(a)\) is maximized by activating in states with the largest values of \(\bar m_W(S)\), with boundary randomization if needed. It is minimized by activating in states with the smallest values.

### Proof

By Fubini's theorem,

\[
J_W(a)
=
\int_I\pi_0(\alpha)\,W(d\alpha)
+
E\left[
 a(S)
 \int_I m_\alpha(S)\,W(d\alpha)
\right].
\]

The first term is policy independent. The second is \(E\{a(S)\bar m_W(S)\}\), so the sharp rearrangement result from Work Package A applies. \(\square\)

## Remark on a weighted TESS objective

The exact weighted objective

\[
\int_I S_a(\alpha)\,W(d\alpha)
\]

is nonlinear in \(a\) and does not reduce to one fixed score in general. Around a reference policy, a first-order approximation weights \(m_\alpha(S)\) additionally by the derivative of the TESS transform. Thus the appropriate compromise score depends on whether the scientific objective is rejection probability, TESS, or another curve functional.

---

# 8. Numerical verification

Three machine-readable examples accompany this memo.

## 8.1 Coherent common-index family

For \(T\sim\mathrm{Uniform}(0,1)\), let

\[
m_\alpha(T)
=
0.8\alpha(1-\alpha)(2T-1).
\]

At activation rate \(1/2\), the top-score, random, and bottom-score policies satisfy

\[
S_{\mathrm{top}}(\alpha)
>
S_{\mathrm{random}}(\alpha)
>
S_{\mathrm{bottom}}(\alpha)
\]

throughout the displayed interval.

![](WORK_PACKAGE_B_COHERENT_POLICY_TESS_CURVES.png){width=92%}

**Figure B1.** Under a common monotone index, one ordering holds over the full TESS curve.

## 8.2 Exact-uniform single crossing

The exact-uniform construction used

\[
\tau=0.05,
\qquad
\varepsilon=0.90,
\qquad
r=d=0.50.
\]

Both fixed branches have TESS 1, whereas the adaptive policies reverse ordering at \(\alpha=0.05\).

![](WORK_PACKAGE_B_SINGLE_CROSSING_TESS_CURVES.png){width=92%}

**Figure B2.** Threshold-dependent policy reversal despite exact fixed branch p-values and identical candidate-count budgets.

A Monte Carlo check with 600,000 states gave maximum absolute rejection-probability error 0.000433 across the evaluated thresholds.

## 8.3 Multiple prescribed crossings

A polynomial perturbation with roots at \(0.025\) and \(0.10\) generated two policy-curve crossings while preserving exact uniform marginal branch p-values.

![](WORK_PACKAGE_B_ARBITRARY_CROSSING_PREMIUM.png){width=92%}

**Figure B3.** Any finite set of crossing thresholds can be embedded by choosing a smooth perturbation with those roots.

---

# 9. Implications for the locked empirical study

The locked confirmatory and SUPPORT2-anchored analyses reported the same qualitative ordering over the declared threshold grid:

\[
\text{promising}
\;>\;
\text{random}
\;>\;
\text{rescue}.
\]

Work Package B gives a possible structural explanation: the base-stage score may act as an approximately common monotone index for \(m_\alpha(S)\) over the studied range. This interpretation is consistent with the positive covariance curves and score-decile mechanism plots, but it is not implied by them.

A direct frozen-output diagnostic would require no refitting:

1. estimate \(m_\alpha(S)\) on a common score-bin grid for every declared \(\alpha\);
2. compare rank orderings of those estimated fields across thresholds;
3. check first-order stochastic ordering of the trigger score among promising, random, and rescue activations;
4. report whether empirical policy curves cross and compute simultaneous regret relative to the pointwise envelope;
5. retain signed gain and loss transitions separately.

This diagnostic is useful for the top-tier manuscript but is not required to validate the already locked primary result.

---

# 10. Prior-art boundary

## Established mathematics

- Comonotonicity is a classical dependence concept; comonotonic variables are nondecreasing functions of a common factor.
- First-order stochastic dominance characterizes expectation ordering for increasing functions.
- Monotone comparative statics and single-crossing conditions study when optimizers move coherently with a parameter.
- Rearrangement principles yield top-score optimal allocation under a scalar budget.

These tools must be cited rather than claimed as new.

## Candidate new content

Subject to a broader literature audit, the strongest potentially new results are:

1. the equivalence between threshold-rank coherence of \(m_\alpha(S)\) and simultaneous same-budget optimality of one policy across the TESS curve;
2. the stochastic-order criterion for full-curve policy dominance;
3. the exact-uniform construction showing arbitrary finite policy-curve crossing patterns at identical candidate law and budget;
4. the separation of fixed-family threshold dependence from adaptive policy-state threshold dependence;
5. the use of integrated incremental-rejection fields to define scientifically weighted compromise policies when no uniform optimum exists.

The mathematical ingredients are standard. The novelty candidate is their synthesis around the policy-level rejection functional of adaptive statistical search.

---

# 11. Consequences for top-tier feasibility

The theory package now contains:

1. an axiomatic characterization of the logarithmic search-size scale;
2. a fixed-family copula and extremal-coefficient bridge;
3. general sharp same-budget policy envelopes;
4. an exact identifiability criterion;
5. an unbounded expected-budget mismatch theorem;
6. cost-weighted allocation theory;
7. common-rank simultaneous optimality;
8. full-curve stochastic policy dominance;
9. arbitrary same-budget policy-curve crossing constructions;
10. conditional TESS-curve estimation and finite-sample bands.

This is substantially stronger than an applied effective-number paper. The central theoretical message is now:

> **Adaptive-policy multiplicity is a threshold-indexed coupling problem. A common scalar trigger is uniformly optimal only under rank coherence of conditional incremental rejection. Without that coherence, fixed candidate laws and equal budgets permit arbitrary policy-curve reversals.**

The result supports continuing the top-tier theory phase.

---

# 12. Next decision

Work Package B resolves the threshold-coherence question. The remaining high-value theoretical problem is two-bank process inference when the reference bank estimates candidate-specific p-value maps and the activation trigger.

The recommended next step is a deliberately simplified Work Package D:

1. continuous branch scores;
2. unique winner almost surely;
3. a smooth or fixed activation threshold in the first theorem;
4. joint reference/evaluation empirical processes;
5. weak convergence and bootstrap validity for a TESS-curve contrast.

In parallel, the top-tier manuscript architecture can now be drafted because the conceptual theorem sequence is stable. Work Package D should be stopped if it requires assumptions so restrictive that they no longer illuminate the locked pipeline.

---

# References added or emphasized for Work Package B

1. Dhaene J, Denuit M, Goovaerts MJ, Kaas R, Vyncke D. The concept of comonotonicity in actuarial science and finance: theory. *Insurance: Mathematics and Economics*. 2002;31(1):3-33. doi:10.1016/S0167-6687(02)00134-8.
2. Shaked M, Shanthikumar JG. *Stochastic Orders*. Springer Series in Statistics. Springer; 2007. doi:10.1007/978-0-387-34675-5.
3. Milgrom P, Shannon C. Monotone comparative statics. *Econometrica*. 1994;62(1):157-180. doi:10.2307/2951479.
4. Hardy GH, Littlewood JE, Polya G. *Inequalities*. 2nd ed. Cambridge University Press; 1952.
5. Lieb EH, Loss M. *Analysis*. 2nd ed. Graduate Studies in Mathematics, Vol 14. American Mathematical Society; 2001.
6. Fréchet M. Généralisation du théorème des probabilités totales. *Fundamenta Mathematicae*. 1935;25(1):379-387.
7. Steffen N, Dickhaus T. Optimizing effective numbers of tests by vine copula modeling. *Dependence Modeling*. 2020;8(1):172-185. doi:10.1515/demo-2020-0010.
8. White H. A reality check for data snooping. *Econometrica*. 2000;68(5):1097-1126. doi:10.1111/1468-0262.00152.
