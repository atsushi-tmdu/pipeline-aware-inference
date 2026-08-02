# Policy-Level Search Size for Adaptive Statistical Pipelines

## Work Package A: sharp policy envelopes, general non-identifiability, and cost-weighted allocation

**Theory memo v2 - 2 August 2026**  
**Status:** Work Package A completed; top-tier feasibility assessment continues  
**Starting point:** Theory memo v1, locked confirmatory study, SUPPORT2-anchored validation, and two-bank uncertainty sensitivity

---

## Executive assessment

Work Package A is successful.

The two-candidate counterexample in theory memo v1 can be replaced by a general representation and sharp envelope theory for one-stage adaptive expansion. At a fixed threshold, the inferential effect of every policy with the same activation rate is completely determined by how its activation rule couples to the conditional incremental rejection effect

$$
m_\alpha(S)=E\{D_\alpha\mid S\},
\qquad
D_\alpha=R_1(\alpha)-R_0(\alpha).
$$

The attainable rejection probabilities form an explicit interval whose endpoints are upper and lower quantile integrals of $m_\alpha(S)$. Consequently:

1. candidate-count distribution and expected candidate count identify policy-level rejection only when $m_\alpha(S)$ is constant almost surely;
2. whenever $m_\alpha(S)$ is nonconstant, every nontrivial activation rate admits same-budget policies with different rejection probabilities and different TESS values;
3. the earlier two-candidate construction extends to every activation rate $r\in(0,1)$ with two fixed policies that attain the pointwise envelopes simultaneously over the whole range $0<\alpha<1/2$;
4. with $K$ optional candidates, the deep-tail TESS can approach $K+1$ or 1 under policies with the same activation rate and the same candidate-count distribution;
5. expected candidate count alone does not even upper-bound deep-tail policy search size: at a fixed expected candidate count, the high-allocation TESS limit can be made arbitrarily large;
6. when branch costs vary by state, the optimal policy orders states by conditional incremental rejection per unit cost.

The optimization mathematics is an application of the Hardy-Littlewood rearrangement or bathtub principle and, in the cost-weighted case, the Neyman-Pearson/fractional-knapsack principle. That mathematical tool is not new. The potential foundational contribution is the policy-level representation, the identifiability criterion, and the curve-level impossibility results for adaptive search.

---

# 1. Setup

Fix a local threshold $\alpha\in(0,1)$. On one global-null data state, let

$$
R_0(\alpha),R_1(\alpha)\in\{0,1\}
$$

be the counterfactual rejection indicators under a fixed base search and a fixed full search. Define

$$
D_\alpha=R_1(\alpha)-R_0(\alpha)\in\{-1,0,1\}.
$$

Let $S$ denote all information available when the optional branch decision is made. A randomized activation kernel is a measurable function

$$
a(S)\in[0,1].
$$

Using an independent $V\sim\mathrm{Uniform}(0,1)$, the realized activation indicator may be written

$$
A=I\{V\le a(S)\}.
$$

Thus $P(A=1\mid S)=a(S)$. Define

$$
m_\alpha(S)=E(D_\alpha\mid S),
$$

and write

$$
\pi_0(\alpha)=E\{R_0(\alpha)\}.
$$

For a target activation rate $r\in[0,1]$, define the feasible class

$$
\mathcal A_r
=
\left\{a:0\le a(S)\le1,\ E\{a(S)\}=r\right\}.
$$

The optional family is assumed to be activated jointly. If the base and full searches evaluate $K_0$ and $K_1$ candidates, respectively, every $a\in\mathcal A_r$ has

$$
P(N=K_1)=r,
\qquad
P(N=K_0)=1-r,
$$

and therefore

$$
E(N)=K_0+r(K_1-K_0).
$$

Every optional candidate also has marginal inclusion probability $r$. If activating the branch has a fixed additional cost $c$, all policies in $\mathcal A_r$ have the same expected cost.

---

# 2. Policy representation

## Theorem A1. Representation at fixed activation information

For every activation kernel $a\in\mathcal A_r$, the policy rejection probability is

$$
\pi_a(\alpha)
=
\pi_0(\alpha)+E\{a(S)m_\alpha(S)\}.
$$

### Proof

The realized policy rejection indicator is

$$
R_a(\alpha)
=
R_0(\alpha)+A D_\alpha.
$$

Because $V$ is independent of the data state conditional on $S$,

$$
E(A\mid S,D_\alpha)=a(S).
$$

Therefore

$$
E(AD_\alpha)
=
E\left[E\{AD_\alpha\mid S,D_\alpha\}\right]
=
E\{a(S)D_\alpha\}
=
E\left[a(S)E(D_\alpha\mid S)\right].
$$

Substitution gives the result. $\square$

## Interpretation

The full candidate law determines $R_0$, $R_1$, and hence $D_\alpha$. The activation-time information determines the conditional field $m_\alpha(S)$. The policy contributes the allocation kernel $a(S)$. Candidate-count budget imposes only the scalar constraint $E(a)=r$; it does not specify the coupling $E(am_\alpha)$.

This representation is the basic reason that fixed-family summaries cannot generally identify adaptive-policy multiplicity.

---

# 3. Sharp fixed-rate policy envelope

Let $F_{m,\alpha}$ be the distribution function of $m_\alpha(S)$ and define its left-continuous generalized quantile

$$
Q_\alpha(u)
=
\inf\{x:F_{m,\alpha}(x)\ge u\},
\qquad 0<u<1.
$$

For $r\in[0,1]$, define the lower and upper integrated quantiles

$$
L_\alpha(r)=\int_0^r Q_\alpha(u)\,du,
$$

$$
U_\alpha(r)=\int_{1-r}^1 Q_\alpha(u)\,du.
$$

## Theorem A2. Sharp attainable interval at a fixed activation rate

For $0<r<1$,

$$
\left\{\pi_a(\alpha):a\in\mathcal A_r\right\}
=
\left[
\pi_0(\alpha)+L_\alpha(r),
\ \pi_0(\alpha)+U_\alpha(r)
\right].
$$

The upper endpoint is attained by activating in states with the largest values of $m_\alpha(S)$, with boundary randomization if necessary. The lower endpoint is attained by activating in states with the smallest values.

### Proof

Choose a threshold $\lambda_U$ and $q_U\in[0,1]$ such that

$$
a_U(S)
=
I\{m_\alpha(S)>\lambda_U\}
+q_U I\{m_\alpha(S)=\lambda_U\}
$$

satisfies $E(a_U)=r$. For any feasible $a$,

$$
E\left[(a-a_U)(m_\alpha-\lambda_U)\right]\le0.
$$

Indeed, where $m_\alpha>\lambda_U$, one has $a-a_U\le0$; where $m_\alpha<\lambda_U$, one has $a-a_U\ge0$; and the product is zero on the boundary. Since $E(a-a_U)=0$,

$$
E(am_\alpha)-E(a_Um_\alpha)
=
E\left[(a-a_U)(m_\alpha-\lambda_U)\right]
\le0.
$$

Thus $a_U$ is optimal. Its value is the upper integrated quantile $U_\alpha(r)$ by the standard quantile representation of a top-$r$ rearrangement.

The lower endpoint follows by applying the same argument to $-m_\alpha$, yielding a bottom-$r$ threshold rule $a_L$. Finally, every value between the endpoints is attained by the randomized mixture

$$
a_t=(1-t)a_L+t a_U,
\qquad 0\le t\le1,
$$

which remains in $\mathcal A_r$ and varies the expectation linearly. $\square$

## Mathematical prior-art status

The sharp optimization step is a form of the Hardy-Littlewood rearrangement or bathtub principle. It is also analogous to the Neyman-Pearson principle: under a scalar budget constraint, allocate mass where the relevant conditional benefit is largest. The candidate novelty is not the rearrangement inequality itself, but its interpretation as a complete sharp envelope for adaptive-policy rejection burden.

---

# 4. Identifiability, the random benchmark, and TESS envelopes

Let

$$
\mu_\alpha=E\{m_\alpha(S)\}=E(D_\alpha).
$$

A rate-$r$ random expansion independent of the data state has

$$
\pi_{\mathrm{rand},r}(\alpha)
=
\pi_0(\alpha)+r\mu_\alpha.
$$

Because the overall mean lies between the bottom- and top-tail averages,

$$
L_\alpha(r)
\le
r\mu_\alpha
\le
U_\alpha(r).
$$

## Corollary A1. Sharp allocation-premium interval

For all $a\in\mathcal A_r$,

$$
L_\alpha(r)-r\mu_\alpha
\le
\pi_a(\alpha)-\pi_{\mathrm{rand},r}(\alpha)
\le
U_\alpha(r)-r\mu_\alpha.
$$

Equivalently, the maximal positive allocation premium is

$$
r\left\{
\frac{1}{r}\int_{1-r}^1Q_\alpha(u)\,du
-
E(m_\alpha)
\right\},
$$

and the maximal negative premium is the analogous bottom-$r$ deviation.

## Corollary A2. Exact identifiability criterion

The following are equivalent:

1. every activation policy with a common rate $r\in(0,1)$ has the same rejection probability;
2. $L_\alpha(r)=U_\alpha(r)$;
3. $m_\alpha(S)$ is constant almost surely.

If $m_\alpha(S)$ is nonconstant, then for every $r\in(0,1)$ there exist two policies with:

- the same full candidate law;
- the same activation probability;
- the same marginal inclusion probability for every optional candidate;
- the same candidate-count distribution;
- the same expected candidate count and fixed branch cost;

but different policy-level rejection probabilities.

### Proof

If $m_\alpha$ is constant, Theorem A1 makes $E(am_\alpha)=rE(m_\alpha)$ for every feasible policy. Conversely, if $m_\alpha$ is nonconstant, its quantile function is nonconstant. For $0<r<1$,

$$
U_\alpha(r)-L_\alpha(r)
=
\int_0^r
\left\{
Q_\alpha(1-r+u)-Q_\alpha(u)
\right\}du
>0.
$$

Theorem A2 then supplies distinct same-rate policies. $\square$

## Corollary A3. Pointwise TESS envelope

Let

$$
g_\alpha(\pi)
=
\frac{\log(1-\pi)}{\log(1-\alpha)}.
$$

Because $g_\alpha$ is increasing, the pointwise attainable TESS interval is

$$
\left[
 g_\alpha\{\pi_0+L_\alpha(r)\},
 \ g_\alpha\{\pi_0+U_\alpha(r)\}
\right],
$$

with the upper endpoint interpreted as $+\infty$ if its rejection probability is 1.

The envelope is pointwise in $\alpha$: in a general problem, the policy maximizing rejection at one threshold need not maximize it at another. The constructions in Section 6 are stronger because the same fixed policies attain the envelopes over an interval of thresholds.

---

# 5. Perfect-information signed transition envelope

Suppose the activation information reveals $D_\alpha$ itself. Define

$$
g_\alpha=P(D_\alpha=1),
\qquad
\ell_\alpha=P(D_\alpha=-1),
\qquad
z_\alpha=1-g_\alpha-\ell_\alpha.
$$

The optimal high-rejection policy activates gain states first, then neutral states, then loss states. The optimal low-rejection policy reverses that order.

## Corollary A4. Explicit gain-loss envelope

At activation rate $r$, define the upper and lower incremental contributions by

$$
M_\alpha^{U}(r)
=
\min(r,g_\alpha)
-
\max\{0,r-(1-\ell_\alpha)\},
$$

and

$$
M_\alpha^{L}(r)
=
-\min(r,\ell_\alpha)
+
\max\{0,r-(1-g_\alpha)\}.
$$

These are respectively the maximum and minimum of $E(aD_\alpha)$ over $a\in\mathcal A_r$.

Thus the exact attainable rejection interval is obtained by adding $\pi_0(\alpha)$ to these expressions.

This result makes clear why complete signed mechanism reporting matters. Gain counts alone do not determine the policy effect when reverse transitions are possible.

---

# 6. Arbitrary-rate two-candidate curve-level non-identifiability

The next theorem generalizes the two-candidate example in theory memo v1 from activation rate $1/2$ to every $r\in(0,1)$.

## Theorem A3. Two fixed same-rate policies attaining opposite envelopes

Let

$$
U\sim\mathrm{Uniform}(0,1),
\qquad
P_1=U,
\qquad
P_2=1-U.
$$

Candidate 1 is always evaluated and candidate 2 is optional. For a fixed activation rate $r\in(0,1)$, define

$$
A_L=I(U\le r),
\qquad
A_H=I(U>1-r).
$$

Both policies activate candidate 2 with probability $r$, have the same candidate-count distribution, and have expected candidate count $1+r$. The reported p-value is the minimum among evaluated candidates.

For every $0<\alpha<1/2$,

$$
\pi_H(\alpha)
=
\alpha+\min(r,\alpha),
$$

whereas

$$
\pi_L(\alpha)
=
\alpha+\max(0,r+\alpha-1).
$$

These are the sharp upper and lower same-rate envelopes.

### Proof

The base candidate rejects on

$$
B_\alpha=\{U<\alpha\},
$$

and the optional candidate rejects on

$$
G_\alpha=\{U>1-\alpha\}.
$$

For $\alpha<1/2$, these events are disjoint. The policy rejection probability is

$$
\pi_A(\alpha)
=
\alpha+P(A=1,G_\alpha).
$$

For the high-tail policy,

$$
P(A_H=1,G_\alpha)
=
P\{U>\max(1-r,1-\alpha)\}
=
\min(r,\alpha).
$$

For the low-tail policy,

$$
P(A_L=1,G_\alpha)
=
P(1-\alpha<U\le r)
=
\max(0,r+\alpha-1).
$$

These are the Fréchet-Hoeffding upper and lower bounds for the intersection of an activation event of probability $r$ and an incremental-rejection event of probability $\alpha$, and hence are sharp. $\square$

## Deep-tail consequence

For every fixed $r\in(0,1)$ and every

$$
0<\alpha<\min(r,1-r),
$$

one has

$$
\pi_H(\alpha)=2\alpha,
\qquad
\pi_L(\alpha)=\alpha.
$$

Therefore the high-tail policy has the same rejection curve as fixed full search, while the low-tail policy has the same rejection curve as the base search. Moreover,

$$
\lim_{\alpha\downarrow0}S_H(\alpha)=2,
\qquad
\lim_{\alpha\downarrow0}S_L(\alpha)=1.
$$

This holds for every positive activation rate, however small. An optional candidate evaluated only rarely can reproduce the complete two-candidate deep-tail burden if activation is concentrated exactly where that candidate can reject.

---

# 7. Many optional candidates and an unbounded expected-budget mismatch

The previous effect is not limited to two candidates.

## Theorem A4. Same-rate policies with deep-tail limits 1 and $K+1$

Fix an integer $K\ge1$ and an activation rate $r\in(0,1)$. There exist $K+1$ exact marginally uniform p-values, one base candidate and $K$ jointly activated optional candidates, together with two fixed policies satisfying:

- the same full candidate joint law;
- the same activation probability $r$;
- the same marginal inclusion probability $r$ for every optional candidate;
- the same candidate-count distribution;
- expected candidate count $1+rK$;

such that

$$
\lim_{\alpha\downarrow0}S_H(\alpha)=K+1,
\qquad
\lim_{\alpha\downarrow0}S_L(\alpha)=1.
$$

### Construction and proof

Let $U$ be uniform on the unit circle and define

$$
a_j=\frac{j}{K+1},
\qquad
P_j=(U-a_j)\bmod1,
\qquad j=0,1,\ldots,K.
$$

Every $P_j$ is exactly uniform. For sufficiently small $\alpha$, the rejection events

$$
E_{j,\alpha}=\{P_j<\alpha\}
$$

are disjoint arcs of length $\alpha$ beginning at $a_j$.

Choose a measurable activation set $H$ of measure $r$ that contains a positive-length right-neighborhood of every optional anchor $a_1,\ldots,a_K$. Choose another activation set $L$ of measure $r$ whose closure avoids all optional anchors. Such sets exist because the circle is atomless and the anchor set is finite.

Hence there is an $\varepsilon>0$ such that, for all $0<\alpha<\varepsilon$,

- every optional rejection arc is contained in $H$;
- no optional rejection arc intersects $L$.

Under policy $H$, all $K+1$ disjoint rejection arcs are captured, so

$$
\pi_H(\alpha)=(K+1)\alpha.
$$

Under policy $L$, only the base arc is captured, so

$$
\pi_L(\alpha)=\alpha.
$$

Therefore

$$
S_H(\alpha)
=
\frac{\log\{1-(K+1)\alpha\}}{\log(1-\alpha)}
\longrightarrow K+1,
$$

while $S_L(\alpha)=1$. $\square$

## Corollary A5. Expected candidate count does not upper-bound deep-tail TESS

Fix any expected candidate-count budget $b>1$. For every integer $K>b-1$, set

$$
r_K=\frac{b-1}{K}.
$$

Then the construction in Theorem A4 has

$$
E(N)=1+r_KK=b,
$$

but

$$
\lim_{\alpha\downarrow0}S_H(\alpha)=K+1.
$$

As $K\to\infty$, the expected candidate count remains fixed at $b$ while the deep-tail TESS limit diverges.

Thus there is no universal upper bound on deep-tail policy search size that is a function only of expected candidate count.

This is a stronger impossibility statement than the original two-candidate example. It shows that an apparently mild average search budget can conceal arbitrarily large deep-tail multiplicity when a large optional family is activated selectively.

---

# 8. State-dependent branch cost

Candidate count is only one possible budget. Let $c(S)>0$ be the additional cost of activating the optional branch in state $S$, with

$$
0<E\{c(S)\}<\infty.
$$

For an expected optional-search budget $b\in(0,E c)$, define

$$
\mathcal A_b^c
=
\left\{a:0\le a\le1,\ E\{a(S)c(S)\}=b\right\}.
$$

Let

$$
C=E\{c(S)\},
\qquad
\beta=\frac{b}{C},
\qquad
\rho_\alpha(S)=\frac{m_\alpha(S)}{c(S)}.
$$

Define the cost-weighted probability measure

$$
d\nu(S)=\frac{c(S)}{C}\,dP(S),
$$

and let $Q_{\rho,\alpha}^{\nu}$ be the quantile function of $\rho_\alpha(S)$ under $\nu$.

## Theorem A5. Sharp cost-weighted envelope

Define the upper and lower incremental rejection contributions at expected cost $b$ by

$$
M_{\alpha,c}^{U}(b)
=
C\int_{1-\beta}^{1}Q_{\rho,\alpha}^{\nu}(u)\,du,
$$

and

$$
M_{\alpha,c}^{L}(b)
=
C\int_{0}^{\beta}Q_{\rho,\alpha}^{\nu}(u)\,du.
$$

These are respectively the maximum and minimum of $E\{a(S)m_\alpha(S)\}$ over $a\in\mathcal A_b^c$.

The upper endpoint is attained by activating where the benefit-cost ratio

$$
\rho_\alpha(S)=m_\alpha(S)/c(S)
$$

is largest, with boundary randomization if needed. The lower endpoint activates where the ratio is smallest.

### Proof

Under the cost-weighted measure $\nu$,

$$
E\{a(S)m_\alpha(S)\}
=
C E_\nu\{a(S)\rho_\alpha(S)\},
$$

and the budget constraint becomes

$$
E_\nu\{a(S)\}=\beta.
$$

Theorem A2 applied under $\nu$ gives the result. $\square$

## Interpretation

When optional branches have equal cost, ordering by $m_\alpha(S)$ is optimal. When costs vary, the optimal fixed-budget policy orders states by incremental rejection opportunity per unit cost. This is a policy-level analogue of a fractional-knapsack or Neyman-Pearson allocation rule.

---

# 9. Numerical verification

The exact two-candidate formulas were checked with $10^6$ Monte Carlo draws at $\alpha=0.05$ for activation rates

$$
r\in\{0.05,0.10,0.25,0.50,0.75,0.90,0.95\}.
$$

The maximum absolute Monte Carlo error in the rejection probabilities was 0.000813. The calculation is a numerical check only; the results above are exact.

![Sharp same-rate envelopes and fixed-budget divergence](/mnt/data/WORK_PACKAGE_A_SHARP_ENVELOPES.png){width=95%}

**Figure A1.** Left: sharp lower and upper policy rejection probabilities in the exact two-candidate construction at $\alpha=0.05$. Over a broad range of activation rates, the lower policy has base-search rejection probability while the upper policy has fixed-full rejection probability. Right: with expected candidate count fixed at 1.5, the low-allocation deep-tail TESS limit remains 1 while the high-allocation limit grows as $K+1$.

Machine-readable numerical checks accompany this memo.

---

# 10. What is standard and what may be new

## Standard mathematical ingredients

- the top- and bottom-quantile optimization in Theorem A2 is a rearrangement or bathtub principle;
- the arbitrary-rate two-event intersection bounds are Fréchet-Hoeffding bounds;
- the state-dependent cost rule is a Neyman-Pearson/fractional-knapsack threshold principle;
- monotone conversion from rejection probability to TESS is algebraic.

These should be cited and not presented as newly invented mathematical tools.

## Candidate foundational contributions

Subject to a broader literature audit, the strongest potentially new claims are:

1. **Policy representation:** at fixed activation information, the entire same-budget rejection class is generated by the coupling $E\{a(S)m_\alpha(S)\}$.
2. **Sharp policy identifiability criterion:** activation rate and fixed candidate law identify rejection burden if and only if $m_\alpha(S)$ is constant almost surely.
3. **Curve-level non-identifiability:** fixed policies with identical candidate law and budget descriptors can simultaneously attain opposite rejection envelopes across a threshold interval.
4. **Unbounded expected-budget mismatch:** expected candidate count alone cannot upper-bound deep-tail policy search size.
5. **Cost-weighted policy calculus:** the relevant allocation score is conditional incremental rejection per unit branch cost.

The precise literature novelty of items 1-5 remains provisional until a focused search of adaptive subset selection, selected-family multiple testing, data snooping, and randomized search-cost theory is complete.

---

# 11. Consequences for the top-tier paper

Work Package A provides more than a single adversarial counterexample. It yields a general sharp theory:

$$
\boxed{
\text{candidate law}
+
\text{activation information}
+
\text{activation kernel}
\ \longrightarrow\ 
\text{policy rejection law}
}
$$

and shows exactly which component is lost when one reports only candidate count, expected count, marginal inclusion rates, or the fixed-full copula.

A top-tier theory paper can now be organized around:

1. axiomatic characterization of the search-size scale;
2. fixed-family copula and extremal-coefficient bridge;
3. sharp policy envelope and identifiability theorem;
4. simultaneous arbitrary-rate and unbounded-budget counterexamples;
5. policy allocation calculus and cost-weighted extension;
6. conditional and two-bank inference for the TESS process;
7. the locked empirical study as evidence that the theoretical coupling occurs in realistic model libraries.

The results in this memo materially strengthen the **Go** decision for continuing the top-tier theory phase.

---

# 12. Next work package

## Work Package B: threshold coherence and policy ordering across the TESS curve

The sharp envelope is pointwise in $\alpha$. The next question is when one scalar activation score can order policies coherently over an interval of thresholds.

The immediate targets are:

1. characterize conditions under which
   $$
   m_{\alpha_1}(S)
   \quad\text{and}\quad
   m_{\alpha_2}(S)
   $$
   induce the same state ordering for all $\alpha$ in an interval;
2. prove that a common monotone index yields one policy that is simultaneously optimal over that interval;
3. construct a counterexample in which the optimal activation ordering reverses with $\alpha$;
4. determine whether policy curves can cross despite identical activation rate and fixed candidate law;
5. connect these results to threshold-dependent copula behavior and to the empirical promising/rescue curves.

After Work Package B, the project should decide whether to proceed first to two-bank process inference or to write the top-tier manuscript architecture.

---

# References added for Work Package A

1. Fréchet M. Généralisation du théorème des probabilités totales. *Fundamenta Mathematicae*. 1935;25(1):379-387.
2. Hardy GH, Littlewood JE, Pólya G. *Inequalities*. 2nd ed. Cambridge University Press; 1952.
3. Lieb EH, Loss M. *Analysis*. 2nd ed. Graduate Studies in Mathematics, Vol 14. American Mathematical Society; 2001.
4. Neyman J, Pearson ES. On the problem of the most efficient tests of statistical hypotheses. *Philosophical Transactions of the Royal Society A*. 1933;231:289-337. doi:10.1098/rsta.1933.0009.
5. Brascamp HJ, Lieb EH, Luttinger JM. A general rearrangement inequality for multiple integrals. *Journal of Functional Analysis*. 1974;17(2):227-237. doi:10.1016/0022-1236(74)90013-5.
6. Romano JP, Wolf M. Stepwise multiple testing as formalized data snooping. *Econometrica*. 2005;73(4):1237-1282. doi:10.1111/j.1468-0262.2005.00615.x.
7. Steffen N, Dickhaus T. Optimizing effective numbers of tests by vine copula modeling. *Dependence Modeling*. 2020;8(1):172-185. doi:10.1515/demo-2020-0010.
8. White H. A reality check for data snooping. *Econometrica*. 2000;68(5):1097-1126. doi:10.1111/1468-0262.00152.

