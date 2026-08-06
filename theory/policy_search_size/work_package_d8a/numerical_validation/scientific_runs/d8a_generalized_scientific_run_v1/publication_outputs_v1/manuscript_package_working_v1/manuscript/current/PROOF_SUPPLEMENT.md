# Supplementary Appendix

## Second-Order Finite-Sample Bias in Threshold-Adaptive Statistical Policies

**Draft status:** Proof Supplement v4 — mathematical repair  
**Companion main manuscript:** D8A Main Manuscript Draft v5 — mathematical repair  
**Purpose:** Provide the primitive assumptions, complete theorem dependency chain, and proofs underlying Theorems 1–3, Proposition 1, and Corollaries 1–2 of the main manuscript.

---

# S1. Notation and assumptions

## S1.1 Reference-bank quantiles

Let \(W_1,\ldots,W_B\) be independent copies of a complete reference vector \(W\). For fixed \(d<\infty\), define component variables

\[
Y_\ell=g_\ell(W),
\qquad
\ell=1,\ldots,d,
\]

with distribution functions \(F_\ell\), densities \(f_\ell\), target probabilities \(p_\ell\in(0,1)\), and population quantiles

\[
\theta_\ell
=
F_\ell^{-1}(p_\ell).
\]

The empirical quantiles use the exact generalized-inverse order-statistic convention

\[
\widehat\theta_{\ell,R}
=
Y_{\ell,(k_{B,\ell})},
\qquad
k_{B,\ell}
=
\lceil Bp_\ell\rceil.
\]

Write

\[
\theta=(\theta_1,\ldots,\theta_d)^\top,
\qquad
\widehat\theta_R
=
(\widehat\theta_{1,R},\ldots,\widehat\theta_{d,R})^\top.
\]

For each coordinate, define the lattice offset

\[
a_{\ell,B}
=
k_{B,\ell}-(B+1)p_\ell.
\]

Because \(k_{B,\ell}=\lceil Bp_\ell\rceil\), the sequence
\(\{a_{\ell,B}\}_B\) is bounded but need not converge.

We impose the following reference-quantile conditions.

**Assumption Q.**

For every coordinate \(\ell\):

1. \(F_\ell\) is strictly increasing in a neighborhood of \(\theta_\ell\).
2. \(f_\ell\) is positive and twice continuously differentiable in that neighborhood.
3. The inverse distribution function \(Q_\ell=F_\ell^{-1}\) has a bounded third derivative on \([p_\ell-\delta_\ell,p_\ell+\delta_\ell]\) for some \(\delta_\ell>0\).
4. For some common \(r=2+\eta>2\), there exists \(s>r\) such that
   \[
   E|Y_\ell|^s<\infty.
   \]
5. The dimension \(d\) is fixed as \(B\to\infty\).

The local positivity in Assumption Q implies a density lower bound near each target quantile. The moment condition, together with exponential concentration of a central order statistic, controls the complementary tail contribution required by the inverse-cdf Taylor expansion.

Define the component influence functions

\[
\psi_\ell(W)
=
\frac{
p_\ell-I(Y_\ell\le\theta_\ell)
}{
f_\ell(\theta_\ell)
},
\]

and let

\[
\psi(W)
=
(\psi_1(W),\ldots,\psi_d(W))^\top.
\]

The complete-vector covariance matrix is

\[
\Sigma_\theta
=
E\{\psi(W)\psi(W)^\top\},
\]

whose entries are

\[
\Sigma_{\theta,\ell m}
=
\frac{
P(Y_\ell\le\theta_\ell,\,
Y_m\le\theta_m)
-
p_\ell p_m
}{
f_\ell(\theta_\ell)
f_m(\theta_m)
}.
\]

No independence among coordinates of \(W\) is assumed.

## S1.2 Policy class

The base candidate pool is \(\{0,1\}\), and the full candidate pool is \(\{0,1,2\}\). Candidate scores are continuous. Define the almost-surely unique winners

\[
J_0
=
\arg\max_{j\in\{0,1\}}X_j,
\qquad
J_1
=
\arg\max_{j\in\{0,1,2\}}X_j.
\]

Candidate-specific rejection thresholds are \(q_0,q_1,q_2\). Define

\[
R_0
=
I(X_{J_0}>q_{J_0}),
\qquad
R_1
=
I(X_{J_1}>q_{J_1}).
\]

Let

\[
T=\max(X_0,X_1),
\qquad
A=I(T>c),
\]

where \(c\) is the activation threshold. In the declared model,

\[
\theta=(q_0,q_1,q_2,c)^\top.
\]

The present policy is a monotone augmentation: activation can add a rejection but cannot revoke a base rejection. Define

\[
M=(1-R_0)R_1,
\]

so that \(M\in\{0,1\}\) records a gain-only incremental rejection opportunity. This excludes the loss state \(R_1-R_0=-1\) that can occur in selected-winner pipelines with candidate-specific discrete calibration. The adaptive rejection indicator is

\[
R_A=R_0+AM.
\]

Write

\[
e_0(\theta)=E_\theta(R_0),
\qquad
\rho(\theta)=E_\theta(A),
\qquad
\mu(\theta)=E_\theta(M),
\qquad
\nu(\theta)=E_\theta(AM).
\]

The adaptive and comparator probabilities are

\[
\pi_A(\theta)=e_0(\theta)+\nu(\theta),
\]

\[
\pi_C(\theta)=e_0(\theta)+\rho(\theta)\mu(\theta),
\]

and the policy contrast is

\[
\Delta_\pi(\theta)
=
\nu(\theta)-\rho(\theta)\mu(\theta).
\]

We impose the following policy regularity.

**Assumption P.**

1. The base and full candidate pools remain fixed.
2. Winners are almost surely unique.
3. Candidate and activation thresholds are strictly separated:
   \[
   \min_{j\in\{0,1,2\}}|c-q_j|>0.
   \]
4. For every incremental winner cell \((a,2)\), \(a\in\{0,1\}\), its probability admits the representation
   \[
   U_a(x,y)
   =
   \int_{-\infty}^{x}
   K_a\{w,\max(w,y)\}\,dw.
   \]
   There is a neighborhood of every relevant coincidence \((q_a,q_2)\) on which \(K_a\), \(\partial_wK_a\), and \(\partial_sK_a\) are continuous at the moving upper boundary, and the functions \(\partial_sK_a(w,s)\) and \(\partial_{ss}K_a(w,s)\) admit parameter-uniform integrable envelopes over the complete lower integration range.
5. The corresponding differentiated integral maps have continuous second derivatives in each threshold-order cone. Their second derivatives extend continuously to the cone boundaries from within each cone.
6. All activation terms and all moving-boundary terms whose boundaries remain separated are twice continuously differentiable, with the differentiation-under-the-integral conditions in item 4.
7. The probability maps \(e_0,\rho,\mu,\nu,\pi_A,\pi_C\), and \(\Delta_\pi\) are bounded. The primitive continuity and domination conditions above hold on one common local neighborhood.

Candidate-threshold coincidence is permitted at \(q_0=q_2\) and \(q_1=q_2\). Candidate–trigger coincidence is excluded by Assumption P.3.

## S1.3 Evaluation bank

Let \((R_{0i},A_i,M_i)_{i=1}^n\) be independent evaluation observations under the policy fixed by the reference bank. The evaluation bank is independent of the reference bank. Conditional on \(\widehat\theta_R\), define

\[
\widehat\pi_A
=
\overline{R_A},
\]

\[
\widehat\pi_C
=
\overline{R_0}+\bar A\bar M,
\]

and

\[
\widehat\Delta_\pi
=
\widehat\pi_A-\widehat\pi_C
=
\overline{AM}-\bar A\bar M.
\]

Because \(R_0M=0\),

\[
0\le
\widehat\pi_C
=
\overline{R_0}+\bar A\bar M
\le
\overline{R_0}+\bar M
\le1.
\]

For the TESS result, define

\[
\mathcal F_{B,n}
=
\{
\widehat\pi_A<1,\,
\widehat\pi_C<1
\}.
\]

The strengthened TESS assumptions are stated in Section S6.

---

# S2. Empirical-quantile expansions

## Lemma S1. Scalar empirical-quantile mean expansion

Let \(Y_1,\ldots,Y_B\) be iid with distribution function \(F\), density \(f\), and target quantile

\[
q_p=F^{-1}(p),
\qquad
0<p<1.
\]

Let

\[
\widehat q_{p,B}
=
Y_{(k_B)},
\qquad
k_B=\lceil Bp\rceil,
\]

and define

\[
a_{p,B}
=
k_B-(B+1)p.
\]

Under the scalar version of Assumption Q,

\[
E(\widehat q_{p,B})-q_p
=
\frac{b_{p,B}}{B}
+
o(B^{-1}),
\]

where

\[
b_{p,B}
=
\frac{a_{p,B}}{f(q_p)}
-
\frac{
p(1-p)f'(q_p)
}{
2f(q_p)^3
}.
\]

The coefficient \(b_{p,B}\) is bounded but may depend on \(B\).

### Proof

By the probability-integral transform,

\[
F\{Y_{(k_B)}\}
\overset{d}=
U_{(k_B)},
\]

where

\[
U_{(k_B)}
\sim
\operatorname{Beta}(k_B,B+1-k_B).
\]

Let

\[
H_B=U_{(k_B)}-p.
\]

The exact first moment is

\[
E(H_B)
=
\frac{k_B}{B+1}-p
=
\frac{a_{p,B}}{B+1}.
\]

The exact variance is

\[
\operatorname{Var}(U_{(k_B)})
=
\frac{
k_B(B+1-k_B)
}{
(B+1)^2(B+2)
}.
\]

Since \(a_{p,B}=O(1)\),

\[
E(H_B^2)
=
\frac{p(1-p)}{B}
+
O(B^{-2}).
\]

On \(\{|H_B|\le\delta\}\), Taylor expansion of \(Q=F^{-1}\) gives

\[
Q(p+H_B)
=
Q(p)
+
Q'(p)H_B
+
\frac12Q''(p)H_B^2
+
R_B,
\]

with

\[
|R_B|
\le
C|H_B|^3.
\]

For a central beta order statistic,

\[
E|H_B|^3=O(B^{-3/2}),
\]

so the local remainder is \(o(B^{-1})\).

For the complementary event, central-order-statistic concentration gives

\[
P(|H_B|>\delta)\le C_1e^{-C_2B}.
\]

The finite \(s\)-th moment in Assumption Q and Hölder's inequality imply

\[
E\left[
|Q(U_{(k_B)})|
I(|H_B|>\delta)
\right]
=
o(B^{-1}).
\]

Finally,

\[
Q'(p)=\frac1{f(q_p)}
\]

and

\[
Q''(p)
=
-\frac{f'(q_p)}{f(q_p)^3}.
\]

Substitution of the first two moments of \(H_B\) proves the result. \(\square\)

## Lemma S2. Scalar quantile moment bound

Under the scalar version of Assumption Q,

\[
\sup_{B\ge B_0}
E\left|
\sqrt B(\widehat q_{p,B}-q_p)
\right|^r
<
\infty
\]

for sufficiently large \(B_0\). Consequently,

\[
\left\{
B(\widehat q_{p,B}-q_p)^2
\right\}_{B\ge B_0}
\]

is uniformly integrable.

### Proof

Choose \(\delta>0\) such that

\[
\inf_{|x-q_p|\le\delta}f(x)\ge m>0.
\]

For \(0<t\le\delta\),

\[
F(q_p+t)-p\ge mt,
\qquad
p-F(q_p-t)\ge mt.
\]

Because

\[
0\le \frac{\lceil Bp\rceil}{B}-p\le \frac1B,
\]

the upper and lower order-statistic deviations are binomial deviations with probability gap at least

\[
(mt-B^{-1})_+.
\]

Hoeffding's inequality (Hoeffding, 1963) therefore gives

\[
P(
|\widehat q_{p,B}-q_p|>t
)
\le
2\exp\left[
-2B(mt-B^{-1})_+^2
\right].
\]

Integrating this tail bound after the change of variable \(u=\sqrt B\,t\) yields a uniform \(r\)-th moment bound on
\(\{|\widehat q_{p,B}-q_p|\le\delta\}\).

On the complementary event,

\[
|\widehat q_{p,B}-q_p|
\le
\max_{1\le i\le B}|Y_i|+|q_p|.
\]

For \(s>r\), Hölder's inequality gives an upper bound consisting of a polynomial moment factor and an exponentially decreasing deviation probability. Since

\[
E\max_{i\le B}|Y_i|^s
\le
B E|Y|^s,
\]

the exponential factor dominates. This proves the uniform \(r\)-th moment bound.

For any \(K>0\),

\[
\begin{aligned}
&E\left[
B(\widehat q_{p,B}-q_p)^2
I\{
\sqrt B|\widehat q_{p,B}-q_p|>K
\}
\right]
\\
&\qquad\le
\frac{
E|\sqrt B(\widehat q_{p,B}-q_p)|^r
}{
K^{r-2}
}.
\end{aligned}
\]

The right-hand side tends to zero uniformly as \(K\to\infty\), proving uniform integrability. \(\square\)

## Lemma S3. Primitive \(L^2\) Bahadur remainder

Under the assumptions of Lemma S2, suppose additionally that \(f\) is continuous at \(q_p\). Define

\[
\psi_p(Y)
=
\frac{
p-I(Y\le q_p)
}{
f(q_p)
}
\]

and

\[
r_{p,B}
=
\widehat q_{p,B}-q_p
-
\frac1B
\sum_{i=1}^B
\psi_p(Y_i).
\]

Then

\[
\sqrt B\,r_{p,B}
\overset{p}\longrightarrow0
\]

and

\[
B E(r_{p,B}^2)
\longrightarrow0.
\]

### Proof

Let \(F_B\) be the empirical distribution function and \(k_B=\lceil Bp\rceil\). Continuity of \(F\) implies no sample ties almost surely, so

\[
F_B(\widehat q_{p,B})
=
\frac{k_B}{B}.
\]

Writing \(G_B=F_B-F\),

\[
F(\widehat q)-p
=
-G_B(q_p)
+
\{G_B(q_p)-G_B(\widehat q)\}
+
\left(\frac{k_B}{B}-p\right).
\]

Lemma S2 implies

\[
\widehat q-q_p=O_p(B^{-1/2}).
\]

Continuity and positivity of \(f(q_p)\) give

\[
F(\widehat q)-p
=
f(q_p)(\widehat q-q_p)
+
o_p(B^{-1/2}).
\]

Standard stochastic equicontinuity of the empirical process indexed by the VC class of half-lines gives

\[
G_B(\widehat q)-G_B(q_p)
=
o_p(B^{-1/2}).
\]

Also,

\[
\sqrt B
\left|
\frac{k_B}{B}-p
\right|
\le
B^{-1/2}
\longrightarrow0.
\]

Therefore,

\[
\sqrt B
\left[
\widehat q-q_p
-
\frac{
p-F_B(q_p)
}{
f(q_p)
}
\right]
\overset{p}\longrightarrow0.
\]

The expression in square brackets is \(r_{p,B}\).

The leading empirical-process term has uniformly bounded moments of every fixed order after multiplication by \(\sqrt B\). Lemma S2 supplies a uniformly bounded \(r\)-th moment, for some \(r>2\), for
\(\sqrt B(\widehat q-q_p)\). Hence

\[
\{
|\sqrt B r_{p,B}|^2
\}_B
\]

is uniformly integrable. Convergence in probability to zero therefore implies

\[
E|\sqrt B r_{p,B}|^2\to0,
\]

which is equivalent to the stated \(L^2\) remainder. \(\square\)

## Theorem S1. Joint empirical-quantile moment expansion

Under Assumption Q,

\[
E_R(\widehat\theta_R-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

where the \(\ell\)-th coordinate of \(b_{\theta,B}\) is

\[
b_{\ell,B}
=
\frac{a_{\ell,B}}{f_\ell(\theta_\ell)}
-
\frac{
p_\ell(1-p_\ell)f_\ell'(\theta_\ell)
}{
2f_\ell(\theta_\ell)^3
}.
\]

Moreover,

\[
\sqrt B(\widehat\theta_R-\theta)
\Rightarrow
Z\sim N(0,\Sigma_\theta),
\]

\[
B E_R[
(\widehat\theta_R-\theta)
(\widehat\theta_R-\theta)^\top
]
=
\Sigma_\theta+o(1),
\]

and, for the \(\eta>0\) in Assumption Q,

\[
\sup_B
E_R
\left\|
\sqrt B(\widehat\theta_R-\theta)
\right\|^{2+\eta}
<
\infty.
\]

### Proof

Lemma S1 gives the mean expansion componentwise.

By Lemma S3,

\[
\widehat\theta_R-\theta
=
\frac1B
\sum_{i=1}^B
\psi(W_i)
+
r_B,
\]

with

\[
B E\|r_B\|^2
=
B\sum_{\ell=1}^d
E(r_{B,\ell}^2)
\longrightarrow0.
\]

In particular,

\[
\sqrt B\,r_B\to0
\]

in probability. The multivariate central limit theorem applied to the iid vectors \(\psi(W_i)\), followed by Slutsky's theorem, yields

\[
\sqrt B(\widehat\theta_R-\theta)
\Rightarrow
N(0,\Sigma_\theta).
\]

Let

\[
L_B
=
\frac1B\sum_{i=1}^B\psi(W_i).
\]

Then

\[
B E(L_BL_B^\top)
=
\Sigma_\theta.
\]

For coordinates \(\ell,m\),

\[
\begin{aligned}
&B\left|
E[
(\widehat\theta_\ell-\theta_\ell)
(\widehat\theta_m-\theta_m)
]
-
E(L_{B,\ell}L_{B,m})
\right|
\\
&\quad\le
B|E(L_{B,\ell}r_{B,m})|
+
B|E(L_{B,m}r_{B,\ell})|
+
B|E(r_{B,\ell}r_{B,m})|.
\end{aligned}
\]

Each term tends to zero by Cauchy--Schwarz and the \(L^2\) remainder. Hence the joint second-moment expansion follows.

Finally, for \(r=2+\eta\),

\[
\|x\|_2^r
\le
d^{r/2-1}
\sum_{\ell=1}^d|x_\ell|^r.
\]

The fixed-dimensional vector moment bound therefore follows from the component bounds in Lemma S2. \(\square\)

**Main-text correspondence.** Theorem S1 proves Theorem 1 of the main manuscript.

---

# S3. Threshold-coincidence geometry

## Lemma S4. Generic moving-maximum cell expansion

Let

\[
U(a,q)
=
\int_{-\infty}^{a}
K\{w,\max(w,q)\}\,dw,
\]

where \(K(w,s)\) satisfies Assumption P near \((t,t)\). Define

\[
J_s(t)
=
\int_{-\infty}^{t}
\partial_sK(w,t)\,dw
\]

and

\[
J_{ss}(t)
=
\int_{-\infty}^{t}
\partial_{ss}K(w,t)\,dw.
\]

At the coincidence point \(a=q=t\), for local increments \(u,v\),

\[
\begin{aligned}
U(t+u,t+v)
&=
U(t,t)
+
K(t,t)u
+
J_s(t)v
\\
&\quad
+
\frac12
\left[
K_w(t,t)u^2
+
2K_s(t,t)uv
+
J_{ss}(t)v^2
\right]
\\
&\quad
+
\frac12K_s(t,t)(u-v)_+^2
+
o(u^2+v^2),
\end{aligned}
\]

uniformly over directions in compact sets.

### Proof

On the cone \(u\le v\),

\[
U(t+u,t+v)
=
\int_{-\infty}^{t+u}
K(w,t+v)\,dw.
\]

Differentiation under the integral and an ordinary two-variable Taylor expansion give

\[
\begin{aligned}
U(t+u,t+v)
&=
U(t,t)
+
K(t,t)u
+
J_s(t)v
\\
&\quad
+
\frac12
\left[
K_w(t,t)u^2
+
2K_s(t,t)uv
+
J_{ss}(t)v^2
\right]
+
o(u^2+v^2).
\end{aligned}
\]

Because \((u-v)_+=0\) on this cone, this is the claimed formula.

On the cone \(u>v\),

\[
\begin{aligned}
U(t+u,t+v)
&=
\int_{-\infty}^{t+v}
K(w,t+v)\,dw
\\
&\quad+
\int_{t+v}^{t+u}
K(w,w)\,dw.
\end{aligned}
\]

Expanding the first integral as a function of \(v\) and the second integral about \(t\) gives the same base polynomial plus

\[
\frac12K_s(t,t)(u-v)^2.
\]

Since \((u-v)_+=u-v\) on this cone, the two cone-wise expressions combine into the stated positive-part-square representation. Dominated derivatives provide a remainder uniform over compact direction sets. \(\square\)

## Lemma S5. Winner-cell and coincidence inventory

The only nonempty base/full winner pairs are

\[
(0,0),\quad(0,2),\quad(1,1),\quad(1,2).
\]

On cells \((a,a)\),

\[
M=0.
\]

On cells \((a,2)\),

\[
M
=
I(X_a\le q_a)
I\{X_2>\max(X_a,q_2)\}.
\]

Consequently, the only candidate-threshold coincidence hyperplanes relevant to \(M\) are

\[
q_0=q_2
\qquad\text{and}\qquad
q_1=q_2.
\]

Under strict candidate–trigger separation, no additional coincidence hyperplane contributes to \(AM\).

### Proof

If candidate \(a\in\{0,1\}\) wins the base pool, the full-pool winner is either the same candidate \(a\) or the newly added candidate 2. The other base candidate cannot become the full winner because it was already below \(a\).

When the winner remains \(a\), adding candidate 2 does not create a rejection unavailable to the base pool, so \(M=0\). When candidate 2 becomes the full winner, incremental rejection requires that the base winner fail its own threshold and candidate 2 exceed both the base-winner score and its own threshold, giving the displayed expression.

On base-winner cell \(a\),

\[
A=I(X_a>c).
\]

If \(c<q_a\),

\[
AM
=
I(c<X_a\le q_a)
I\{X_2>\max(X_a,q_2)\};
\]

if \(c>q_a\), then \(AM=0\). Because the ordering between \(c\) and every \(q_j\) is locally fixed, only the hyperplanes \(q_a=q_2\) remain active. \(\square\)

## Theorem S2. Generalized local policy expansion

Define

\[
\mathcal A_0
=
\{a\in\{0,1\}:q_a=q_2\},
\]

\[
d_a=e_a-e_2,
\]

and

\[
s_a=I(c<q_a).
\]

For the incremental winner-cell kernel \(K_a\), define

\[
\kappa_a
=
\frac12
\partial_sK_a(q_a,q_2)
\]

and

\[
\lambda_a
=
\{s_a-\rho(\theta)\}\kappa_a.
\]

Under Assumption P, there exist gradients \(g_A,g_C,g_\Delta\) and symmetric smooth-stratum Hessians \(H_A^{\mathrm{sm}},H_C^{\mathrm{sm}},H_\Delta^{\mathrm{sm}}\) such that

\[
\begin{aligned}
\pi_A(\theta+u)
&=
\pi_A(\theta)
+
g_A^\top u
+
\frac12u^\top H_A^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
s_a\kappa_a(d_a^\top u)_+^2
+
o(\|u\|^2),
\end{aligned}
\]

\[
\begin{aligned}
\pi_C(\theta+u)
&=
\pi_C(\theta)
+
g_C^\top u
+
\frac12u^\top H_C^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
\rho(\theta)\kappa_a(d_a^\top u)_+^2
+
o(\|u\|^2),
\end{aligned}
\]

and

\[
\begin{aligned}
\Delta_\pi(\theta+u)
&=
\Delta_\pi(\theta)
+
g_\Delta^\top u
+
\frac12
u^\top H_\Delta^{\mathrm{sm}}u
\\
&\quad
+
\sum_{a\in\mathcal A_0}
\lambda_a(d_a^\top u)_+^2
+
o(\|u\|^2).
\end{aligned}
\]

All three remainders are uniform over directions in compact sets.

### Proof

For \(a\in\{0,1\}\), define

\[
U_a(x,y)
=
\int_{-\infty}^{x}
K_a\{w,\max(w,y)\}\,dw.
\]

The incremental-rejection probability is

\[
P_M(\theta)
=
\sum_{a=0}^1
U_a(q_a,q_2).
\]

Because \(s_a\) is locally constant,

\[
P_{AM}(\theta)
=
\sum_{a=0}^1
s_a
\left[
U_a(q_a,q_2)
-
U_a(c,q_2)
\right].
\]

The activation probability \(P_A(\theta)=\rho(\theta)\) is smooth under Assumption P.

For every active coincidence \(q_a=q_2\), Lemma S4 gives a positive-part-square coefficient \(\kappa_a\) in the expansion of \(P_M\) and \(s_a\kappa_a\) in the expansion of \(P_{AM}\). The terms \(U_a(c,q_2)\) are ordinary smooth terms because \(c\ne q_2\) locally. Thus

\[
P_M(\theta+u)
=
P_M
+
g_M^\top u
+
Q_M(u)
+
o(\|u\|^2)
\]

and

\[
P_{AM}(\theta+u)
=
P_{AM}
+
g_{AM}^\top u
+
Q_{AM}(u)
+
o(\|u\|^2),
\]

where \(Q_M\) and \(Q_{AM}\) are continuous piecewise-quadratic maps.

Since

\[
\pi_A=e_0+P_{AM},
\]

the coincidence coefficient of \(\pi_A\) is \(s_a\kappa_a\). Since

\[
\pi_C=e_0+P_AP_M,
\]

the coincidence coefficient of \(\pi_C\) is \(P_A\kappa_a=\rho(\theta)\kappa_a\). The base probability \(e_0\) and activation probability \(P_A\) contribute only ordinary smooth terms under Assumption P.

Finally, since

\[
\Delta_\pi
=
P_{AM}-P_AP_M,
\]

multiplying the smooth expansion of \(P_A\) by the generalized expansion of \(P_M\) shows that the coincidence coefficient in \(P_AP_M\) is \(P_A\kappa_a\). Hence the coefficient in \(\Delta_\pi\) is

\[
s_a\kappa_a-P_A\kappa_a
=
(s_a-P_A)\kappa_a
=
\lambda_a.
\]

All remaining second-order terms are ordinary quadratic terms and combine into
\(H_\Delta^{\mathrm{sm}}\). The two active hyperplanes divide the local parameter space into at most four cones. Taking the maximum of the finitely many cone-wise remainder bounds gives the uniform \(o(\|u\|^2)\) remainder. \(\square\)

**Main-text correspondence.** Theorem S2 proves Theorem 2 of the main manuscript.

---

# S4. Generalized expectation expansion

## Lemma S6. Expectation delta method for a finite piecewise-quadratic map

This lemma is an expectation-level specialization. It is related to extended delta methods for directionally differentiable maps (Shapiro, 1991; Dümbgen, 1993; Fang and Santos, 2019) and to second-order analysis of nondifferentiable functionals under first-order degeneracy (Chen and Fang, 2019), but it targets a nondegenerate first-order term together with an order-\(B^{-1}\) mean expansion.

Let \(U_B=\widehat\theta_R-\theta\in\mathbb R^d\), where \(d\) is fixed. Suppose

\[
E(U_B)
=
\frac{b_B}{B}
+
o(B^{-1}),
\]

\[
\sqrt B\,U_B
\Rightarrow
Z,
\]

and, for some \(\eta>0\),

\[
\sup_B
E\|\sqrt B\,U_B\|^{2+\eta}
<
\infty.
\]

Suppose a bounded functional \(h\) has the local expansion

\[
h(\theta+u)
=
h(\theta)
+
g^\top u
+
Q(u)
+
r(u),
\]

where \(Q\) is continuous, homogeneous of degree two, piecewise quadratic over a finite cone arrangement, satisfies

\[
|Q(u)|\le C\|u\|^2,
\]

and

\[
r(u)=o(\|u\|^2)
\]

uniformly over directions. Then

\[
E\{h(\theta+U_B)\}
=
h(\theta)
+
\frac{
g^\top b_B+E\{Q(Z)\}
}{B}
+
o(B^{-1}).
\]

### Proof

The linear term satisfies

\[
E(g^\top U_B)
=
\frac{g^\top b_B}{B}
+
o(B^{-1}).
\]

By homogeneity,

\[
B Q(U_B)
=
Q(\sqrt B\,U_B).
\]

The moment bound and \(|Q(x)|\le C\|x\|^2\) imply uniform integrability of
\(\{Q(\sqrt B\,U_B)\}_B\). Continuity of \(Q\), weak convergence, and uniform integrability therefore give

\[
B E\{Q(U_B)\}
\longrightarrow
E\{Q(Z)\}.
\]

For the remainder, fix a neighborhood on which

\[
|r(u)|\le \varepsilon\|u\|^2
\]

for sufficiently small \(\|u\|\). The local contribution is at most

\[
\varepsilon B E\|U_B\|^2=O(\varepsilon).
\]

On the complementary event \(\{\|U_B\|>\delta\}\), define the remainder globally by

\[
r(U_B)
=
h(\theta+U_B)-h(\theta)-g^\top U_B-Q(U_B).
\]

Because \(h\) is bounded and \(|Q(u)|\le C\|u\|^2\),

\[
|r(U_B)|
\le
C_0+C_1\|U_B\|+C_2\|U_B\|^2.
\]

The \(2+\eta\) moment bound implies

\[
B P(\|U_B\|>\delta)=O(B^{-\eta/2}),
\]

\[
B E[
\|U_B\|
I\{\|U_B\|>\delta\}
]
=
O(B^{-\eta/2}),
\]

and

\[
B E[
\|U_B\|^2
I\{\|U_B\|>\delta\}
]
=
O(B^{-\eta/2}).
\]

Thus the tail contribution is \(o(B^{-1})\). Letting \(\varepsilon\downarrow0\) proves the result. \(\square\)

## Theorem S3. Generalized second-order reference bias

Under Assumptions Q and P,

\[
E_R\{
\Delta_\pi(\widehat\theta_R)
\}
=
\Delta_\pi(\theta)
+
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{B}
+
o(B^{-1}),
\]

where

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\left(
H_\Delta^{\mathrm{sm}}\Sigma_\theta
\right)
\\
&\quad
+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_a
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

### Proof

Theorem S2 has the quadratic map

\[
Q_\Delta(u)
=
\frac12u^\top H_\Delta^{\mathrm{sm}}u
+
\sum_{a\in\mathcal A_0}
\lambda_a(d_a^\top u)_+^2.
\]

Apply Lemma S6 with the joint reference expansion in Theorem S1. For
\(Z\sim N(0,\Sigma_\theta)\),

\[
E\left(
\frac12 Z^\top H_\Delta^{\mathrm{sm}}Z
\right)
=
\frac12
\operatorname{tr}
(
H_\Delta^{\mathrm{sm}}\Sigma_\theta
).
\]

For each \(a\), \(d_a^\top Z\) is a centered Gaussian random variable with variance

\[
d_a^\top\Sigma_\theta d_a.
\]

Symmetry of a centered Gaussian law gives

\[
E(d_a^\top Z)_+^2
=
\frac12
E(d_a^\top Z)^2
=
\frac12
d_a^\top\Sigma_\theta d_a.
\]

Substituting these expectations into Lemma S6 yields the result. \(\square\)

**Main-text correspondence.** Theorem S3 proves Theorem 3 of the main manuscript.

---

# S5. Exact evaluation identity and combined policy bias

## Proposition S1. Exact conditional evaluation identity

Conditional on the reference bank,

\[
E_E(
\widehat\Delta_\pi
\mid
\widehat\theta_R
)
=
\left(1-\frac1n\right)
\Delta_\pi(\widehat\theta_R).
\]

### Proof

Suppress the conditioning notation and write

\[
\rho=E(A),
\qquad
\mu=E(M),
\qquad
\nu=E(AM),
\qquad
\Delta_\pi=\nu-\rho\mu.
\]

Because the evaluation observations are iid,

\[
E(\overline{AM})=\nu.
\]

Moreover,

\[
\begin{aligned}
E(\bar A\bar M)
&=
\frac1{n^2}
\sum_{i=1}^n
\sum_{j=1}^n
E(A_iM_j)
\\
&=
\frac1{n^2}
\left[
n\nu+n(n-1)\rho\mu
\right]
\\
&=
\rho\mu
+
\frac{\nu-\rho\mu}{n}
\\
&=
\rho\mu+\frac{\Delta_\pi}{n}.
\end{aligned}
\]

Therefore,

\[
\begin{aligned}
E(\widehat\Delta_\pi)
&=
E(\overline{AM}-\bar A\bar M)
\\
&=
\nu-\rho\mu-\frac{\Delta_\pi}{n}
\\
&=
\left(1-\frac1n\right)\Delta_\pi.
\end{aligned}
\]

Restoring conditioning on \(\widehat\theta_R\) proves the proposition. \(\square\)

**Main-text correspondence.** Proposition S1 proves Proposition 1 of the main manuscript.

## Corollary S1. Combined finite-reference and finite-evaluation bias

Under Assumptions Q, P, and the evaluation-bank conditions,

\[
\begin{aligned}
E(\widehat\Delta_\pi)-\Delta_\pi
&=
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{Bn}
\\
&\quad
+
o(B^{-1}+n^{-1}).
\end{aligned}
\]

### Proof

By Proposition S1,

\[
E(\widehat\Delta_\pi)
=
\left(1-\frac1n\right)
E_R\{
\Delta_\pi(\widehat\theta_R)
\}.
\]

Theorem S3 gives

\[
E_R\{
\Delta_\pi(\widehat\theta_R)
\}
=
\Delta_\pi
+
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{B}
+
o(B^{-1}).
\]

Hence

\[
\begin{aligned}
E(\widehat\Delta_\pi)
&=
\left(1-\frac1n\right)
\left[
\Delta_\pi
+
\frac{
C_{\Delta,B}^{\mathrm{gen}}
}{B}
+
o(B^{-1})
\right].
\end{aligned}
\]

Subtracting \(\Delta_\pi\) yields the displayed formula. Because

\[
\left(1-\frac1n\right)o(B^{-1})
=
o(B^{-1}),
\]

the remainder is also \(o(B^{-1}+n^{-1})\).

The \(B^{-1}n^{-1}\) term is retained because its coefficient is algebraically determined by the exact factor \(1-1/n\). Under the stated remainder, it is not claimed to be separately identified as an asymptotic order. \(\square\)

**Main-text correspondence.** Corollary S1 proves Corollary 1 of the main manuscript.

---

# S6. Finite-status nonlinear propagation to TESS

## Lemma S7. Smooth composition of a generalized reference expansion

Suppose a scalar probability map \(\pi(\theta)\) has local expansion

\[
\pi(\theta+u)
=
\pi(\theta)
+
g_\pi^\top u
+
Q_\pi(u)
+
o(\|u\|^2),
\]

where \(Q_\pi\) is continuous, homogeneous of degree two, and satisfies the conditions of Lemma S6. Let

\[
C_{\pi,B}^{\mathrm{gen}}
=
g_\pi^\top b_{\theta,B}
+
E\{Q_\pi(Z)\}.
\]

For a scalar \(C^3\) transform \(h\) with bounded derivatives on a neighborhood of the probability range,

\[
C_{h\circ\pi,B}^{\mathrm{gen}}
=
h'(\pi)
C_{\pi,B}^{\mathrm{gen}}
+
\frac12
h''(\pi)
g_\pi^\top\Sigma_\theta g_\pi.
\]

### Proof

Write

\[
\delta_\pi(u)
=
g_\pi^\top u
+
Q_\pi(u)
+
o(\|u\|^2).
\]

A scalar Taylor expansion gives

\[
\begin{aligned}
h\{\pi(\theta+u)\}
&=
h(\pi)
+
h'(\pi)\delta_\pi(u)
+
\frac12h''(\pi)\delta_\pi(u)^2
+
o(\|u\|^2)
\\
&=
h(\pi)
+
h'(\pi)g_\pi^\top u
+
h'(\pi)Q_\pi(u)
\\
&\quad
+
\frac12h''(\pi)(g_\pi^\top u)^2
+
o(\|u\|^2),
\end{aligned}
\]

because products involving \(Q_\pi(u)\) are of order higher than two. Apply Lemma S6 and use

\[
E(g_\pi^\top Z)^2
=
g_\pi^\top\Sigma_\theta g_\pi.
\]

This yields the claimed coefficient. \(\square\)

## Lemma S8. Evaluation-bank expansion for a bounded smooth transform

Conditional on a fixed reference parameter \(\vartheta\), let

\[
\pi_A(\vartheta)=E_\vartheta(R_A),
\qquad
\pi_C(\vartheta)
=
E_\vartheta(R_0)
+
E_\vartheta(A)E_\vartheta(M).
\]

Define

\[
\zeta_A
=
R_A-\pi_A
\]

and

\[
\zeta_C
=
(R_0-e_0)
+
\mu(A-\rho)
+
\rho(M-\mu),
\]

with variances

\[
V_{E,A}=E(\zeta_A^2),
\qquad
V_{E,C}=E(\zeta_C^2).
\]

Let \(h\) be \(C^3\) with bounded derivatives on an open interval containing \([0,1]\). Uniformly for \(\vartheta\) in a sufficiently small compact neighborhood of \(\theta\),

\[
E_E\{h(\widehat\pi_A)\mid\vartheta\}
=
h(\pi_A)
+
\frac{
h''(\pi_A)V_{E,A}
}{2n}
+
o(n^{-1}),
\]

and

\[
\begin{aligned}
E_E\{h(\widehat\pi_C)\mid\vartheta\}
&=
h(\pi_C)
+
\frac{
h'(\pi_C)\Delta_\pi
}{n}
\\
&\quad
+
\frac{
h''(\pi_C)V_{E,C}
}{2n}
+
o(n^{-1}).
\end{aligned}
\]

### Proof

The adaptive estimator is the bounded sample mean

\[
\widehat\pi_A
=
\frac1n\sum_{i=1}^nR_{A,i}.
\]

It is unbiased and has first-order influence function \(\zeta_A\). A third-order Taylor expansion with bounded derivatives and bounded observations gives the first result uniformly.

For the comparator, define

\[
T_n
=
(\overline{R_0},\bar A,\bar M)^\top
\]

and

\[
\varphi(r,a,m)=r+am.
\]

Then

\[
\widehat\pi_C=\varphi(T_n),
\qquad
\pi_C=\varphi(e_0,\rho,\mu).
\]

The gradient of \(\varphi\) is

\[
\nabla\varphi=(1,\mu,\rho)^\top,
\]

so its first-order influence function is \(\zeta_C\). Its only nonzero second derivative is the \(a,m\) cross derivative. Consequently,

\[
E(\widehat\pi_C)-\pi_C
=
\frac{\operatorname{Cov}(A,M)}{n}
=
\frac{\Delta_\pi}{n},
\]

which is also exact by Proposition S1. Applying the bounded smooth expectation expansion to \(h\circ\varphi\) gives the second result. Uniformity follows from bounded observations and uniform continuity of the derivatives on the compact reference neighborhood. \(\square\)

## Assumption T. TESS interiority and localization

There exist a compact neighborhood \(\mathcal N\) of \(\theta\), constants \(\varepsilon,c_0,C_0>0\), and locally Lipschitz versions of the probability, variance, and evaluation-centering maps such that:

1. 
   \[
   \sup_{\vartheta\in\mathcal N}
   \max\{
   \pi_A(\vartheta),
   \pi_C(\vartheta)
   \}
   \le
   1-2\varepsilon;
   \]
2.
   \[
   P(\widehat\theta_R\notin\mathcal N)
   \le
   C_0e^{-c_0B};
   \]
3. the component expansions of Theorem S2 hold on \(\mathcal N\);
4. the conditional remainder in Lemma S8 is uniform on \(\mathcal N\); and
5. the joint sequence satisfies the mild relative-growth condition
   \[
   \log n\,e^{-c_0B}
   =
   o(B^{-1}+n^{-1}).
   \]

The last condition includes the usual polynomially comparable and ordinary simulation regimes.

## Lemma S9. Boundary-status probability and finite-grid bound

Under Assumption T, there exist constants \(C,c>0\) such that

\[
P(\mathcal F_{B,n}^c)
\le
C\{
e^{-cB}+e^{-cn}
\}.
\]

Moreover, on \(\mathcal F_{B,n}\),

\[
|
g_\alpha(\widehat\pi_A)
|
+
|
g_\alpha(\widehat\pi_C)
|
\le
C_\alpha(1+\log n).
\]

### Proof

On \(\{\widehat\theta_R\in\mathcal N\}\),

\[
P(
\widehat\pi_A=1
\mid
\widehat\theta_R
)
=
\pi_A(\widehat\theta_R)^n
\le
(1-2\varepsilon)^n.
\]

For the comparator,

\[
\widehat\pi_C
=
\varphi(
\overline{R_0},
\bar A,
\bar M
),
\qquad
\varphi(r,a,m)=r+am.
\]

If \(\widehat\pi_C=1\), then

\[
|
\widehat\pi_C
-
\pi_C(\widehat\theta_R)
|
\ge
2\varepsilon.
\]

The map \(\varphi\) is Lipschitz on \([0,1]^3\). Hoeffding bounds for the three bounded sample means and a union bound therefore give

\[
P(
\widehat\pi_C=1
\mid
\widehat\theta_R
)
\le
C_1e^{-c_1n}.
\]

Adding the reference-localization probability proves the first result.

On the finite event,

\[
\widehat\pi_A
\le
1-\frac1n.
\]

Also,

\[
\widehat\pi_C
=
\frac{
n k_0+k_Ak_M
}{n^2}
\]

for integers \(k_0,k_A,k_M\). Hence, when \(\widehat\pi_C<1\),

\[
\widehat\pi_C
\le
1-\frac1{n^2}.
\]

Substitution in the logarithmic transform gives the \(O(1+\log n)\) bound. \(\square\)

## Corollary S2. Finite-status second-order TESS bias

Let

\[
g_\alpha(x)
=
\frac{\log(1-x)}{\log(1-\alpha)},
\qquad
0<\alpha<1.
\]

For \(r\in\{A,C\}\), define

\[
\lambda_{A,a}=s_a\kappa_a,
\qquad
\lambda_{C,a}=\rho(\theta)\kappa_a,
\]

and

\[
\begin{aligned}
C_{r,B}^{\mathrm{gen}}
&=
g_r^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
(
H_r^{\mathrm{sm}}\Sigma_\theta
)
\\
&\quad
+
\frac12
\sum_{a\in\mathcal A_0}
\lambda_{r,a}
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

Let

\[
V_{R,r}
=
g_r^\top
\Sigma_\theta
g_r.
\]

Define

\[
\begin{aligned}
C_{S,R,B}^{\mathrm{gen}}
&=
g_\alpha'(\pi_A)
C_{A,B}^{\mathrm{gen}}
+
\frac12
g_\alpha''(\pi_A)
V_{R,A}
\\
&\quad
-
g_\alpha'(\pi_C)
C_{C,B}^{\mathrm{gen}}
-
\frac12
g_\alpha''(\pi_C)
V_{R,C}
\end{aligned}
\]

and

\[
C_{S,E}
=
\frac12
g_\alpha''(\pi_A)V_{E,A}
-
g_\alpha'(\pi_C)\Delta_\pi
-
\frac12
g_\alpha''(\pi_C)V_{E,C}.
\]

Under Assumptions Q, P, and T,

\[
E(
\widehat\Delta_S^{\mathrm{fin}}
\mid
\mathcal F_{B,n}
)
-
\Delta_S
=
\frac{
C_{S,R,B}^{\mathrm{gen}}
}{B}
+
\frac{
C_{S,E}
}{n}
+
o(B^{-1}+n^{-1}),
\]

and

\[
P(\mathcal F_{B,n}^c)
\le
C\{
e^{-cB}+e^{-cn}
\}.
\]

### Proof

Choose a bounded \(C^3\) extension
\(\widetilde g_{\alpha,\varepsilon}\) that equals \(g_\alpha\) on
\([0,1-\varepsilon]\). Because the population probabilities are at most
\(1-2\varepsilon\) on \(\mathcal N\), the extension and the raw TESS transform
have the same derivatives at the population targets.

Apply Lemma S7 to
\(\widetilde g_{\alpha,\varepsilon}\circ\pi_A\) and
\(\widetilde g_{\alpha,\varepsilon}\circ\pi_C\). The component expansions in
Theorem S2 yield the reference coefficient
\(C_{S,R,B}^{\mathrm{gen}}\).

Conditional on the reference bank, Lemma S8 gives the evaluation coefficient
\(C_{S,E}(\widehat\theta_R)\). Local Lipschitz continuity and Theorem S1 imply

\[
\begin{aligned}
E_R|
C_{S,E}(\widehat\theta_R)
-
C_{S,E}(\theta)
|
&\le
L E_R\|
\widehat\theta_R-\theta
\|
+
o(1)
\\
&=
O(B^{-1/2}).
\end{aligned}
\]

Therefore the induced reference–evaluation cross term is

\[
O(B^{-1/2}n^{-1})
=
o(B^{-1}+n^{-1}).
\]

This proves the expansion for the bounded extension.

It remains to compare the bounded extension with the raw finite transform.
They agree when both empirical probabilities are at most \(1-\varepsilon\).
On the remaining finite boundary-neighborhood event, Lemma S9 gives an
\(O(1+\log n)\) magnitude bound, while Hoeffding concentration and reference
localization give exponentially decreasing probability. Assumption T.5 makes
the resulting expectation
\(o(B^{-1}+n^{-1})\).

Finally,

\[
P(\mathcal F_{B,n})
=
1-o(B^{-1}+n^{-1}),
\]

so dividing the finite-event numerator by
\(P(\mathcal F_{B,n})\) does not alter the displayed expansion. \(\square\)

**Main-text correspondence.** Corollary S2 proves the finite-status Corollary 2 of the main manuscript.

# S7. Proof dependency map and scope

The proof chain is

\[
\text{Lemma S1}
+
\text{Lemmas S2--S3}
\Longrightarrow
\text{Theorem S1},
\]

\[
\text{Lemmas S4--S5}
\Longrightarrow
\text{Theorem S2},
\]

\[
\text{Theorems S1--S2}
+
\text{Lemma S6}
\Longrightarrow
\text{Theorem S3},
\]

\[
\text{Theorem S3}
+
\text{Proposition S1}
\Longrightarrow
\text{Corollary S1},
\]

and

\[
\text{Lemma S7}
+
\text{Lemma S8}
+
\text{Lemma S9}
\Longrightarrow
\text{Corollary S2}.
\]

The theoretical scope is restricted to:

- fixed finite candidate pools;
- continuous candidate scores;
- almost-surely unique winners;
- fixed-dimensional empirical-quantile calibration;
- strict separation between activation and candidate thresholds;
- candidate-threshold coincidences at \(q_0=q_2\) or \(q_1=q_2\);
- independent reference and evaluation banks; and
- the finite-status TESS assumptions in Assumption T.

The supplement contains no fitted-model, clinical-data, or policy-allocation result. The proofs do not establish results for:

- discrete plus-one empirical \(p\)-values;
- discrete winner or trigger ties;
- candidate–trigger threshold coincidence;
- failed-fit fallback rules;
- growing candidate dimension;
- arbitrary nonsmooth policy maps; or
- uniform process-level inference over \(\alpha\); or
- a finite unconditional expectation for the raw logarithmic TESS estimator.

---

# S8. Manuscript theorem crosswalk

| Main manuscript | Supplement | Role |
|---|---|---|
| Theorem 1 | Theorem S1 | Joint empirical-quantile mean, Gaussian, second-moment, and moment expansion |
| Theorem 2 | Theorem S2 | Generalized local policy expansion at candidate-threshold coincidence |
| Theorem 3 | Theorem S3 | Generalized \(B^{-1}\) reference-bias coefficient |
| Proposition 1 | Proposition S1 | Exact conditional finite-\(n\) identity |
| Corollary 1 | Corollary S1 | Combined policy-probability bias |
| Corollary 2 | Corollary S2 | Finite-status TESS bias expansion and boundary-probability bound |

---

# S9. Items to complete before submission

1. Reformat the verified references below to the target journal's style.
2. Convert internal proof notation to the target journal's theorem and appendix style.
3. Verify every strengthened derivative, domination, interiority, and localization condition against the final data-generating class statement.
4. Add the complete numerical protocol, equivalence-class registry, and simultaneous-factor derivations as separate supplementary sections.
5. Obtain an independent mathematical review of Lemma S4, Theorem S2, and Lemma S6.


---

# S10. References

Bahadur RR. A note on quantiles in large samples. *Annals of Mathematical Statistics*. 1966;37(3):577–580. doi:10.1214/aoms/1177699450.

Chen Q, Fang Z. Inference on functionals under first order degeneracy. *Journal of Econometrics*. 2019;210(2):459–481. doi:10.1016/j.jeconom.2019.01.011.

Dümbgen L. On nondifferentiable functions and the bootstrap. *Probability Theory and Related Fields*. 1993;95(1):125–140. doi:10.1007/BF01197342.

Fang Z, Santos A. Inference on directionally differentiable functions. *Review of Economic Studies*. 2019;86(1):377–412. doi:10.1093/restud/rdy049.

Hoeffding W. Probability inequalities for sums of bounded random variables. *Journal of the American Statistical Association*. 1963;58(301):13–30. doi:10.1080/01621459.1963.10500830.

Kiefer J. On Bahadur's representation of sample quantiles. *Annals of Mathematical Statistics*. 1967;38(5):1323–1342. doi:10.1214/aoms/1177698690.

Oehlert GW. A note on the delta method. *American Statistician*. 1992;46(1):27–29. doi:10.1080/00031305.1992.10475842.

Shapiro A. Asymptotic analysis of stochastic programs. *Annals of Operations Research*. 1991;30(1):169–186. doi:10.1007/BF02204815.
