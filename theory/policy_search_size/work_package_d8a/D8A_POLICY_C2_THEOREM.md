# Theorem D8-A.3: Twice Differentiability of the Regular Policy Map

## Statement

Let the base and expanded candidate pools be fixed and finite. Suppose:

### P1. Continuous unique winners

The complete score vector has a joint density, and base/full winner ties have
probability zero.

### P2. Strict candidate-trigger separation

\[
\min_{j\in\mathcal J_0}|q_j-c|>0.
\]

### P3. Coordinate trace regularity

Every base/full winner cell satisfies the one- and two-face trace conditions
of Lemma D8-A.3a for all candidate and trigger coordinates appearing in the
policy.

Then there exists a neighborhood \(U\) of the population threshold vector
such that

\[
\theta\mapsto\Delta_\pi(\theta)
\]

is twice continuously differentiable on \(U\).

## Proof

### Step 1: fixed finite winner partition

Up to the null winner-tie set, score space is the finite disjoint union

\[
\mathcal W_{ab}
=
\{J_0=a,\ J_1=b\},
\qquad
a\in\mathcal J_0,\ b\in\mathcal J_1.
\]

The winner cells depend only on the score vector, not on \(\theta\).

### Step 2: stable local Boolean form

Strict separation provides

\[
r
<
\frac12
\min_{j\in\mathcal J_0}|q_j-c|.
\]

On the sup-norm threshold ball of radius \(r\), every sign of \(q_j-c\)
remains fixed.

Within \(\mathcal W_{ab}\),

\[
A=I(x_a>c).
\]

If \(a=b\), the incremental field

\[
M=(1-R_0)R_1
\]

is identically zero. If \(a\ne b\),

\[
M
=
I(x_a\le q_a)
I(x_b>q_b).
\]

Moreover, \(AM\) is either identically zero or, when \(c<q_a\),

\[
AM
=
I(c<x_a\le q_a)
I(x_b>q_b).
\]

Thus the local logical form is fixed throughout \(U\).

### Step 3: finite moving-face representation

Each of

\[
P_A(\theta)=E(A),\qquad
P_M(\theta)=E(M),\qquad
P_{AM}(\theta)=E(AM)
\]

is a finite sum over winner cells of integrals with at most two distinct
moving coordinate faces. Intervals such as

\[
I(c<x_a\le q_a)
\]

are differences of two one-face integrals.

Lemma D8-A.3a therefore gives

\[
P_A,\ P_M,\ P_{AM}\in C^2(U).
\]

### Step 4: policy contrast

Since

\[
\Delta_\pi(\theta)
=
P_{AM}(\theta)
-
P_A(\theta)P_M(\theta),
\]

the contrast belongs to \(C^2(U)\).

Its gradient is

\[
\nabla\Delta_\pi
=
\nabla P_{AM}
-
P_M\nabla P_A
-
P_A\nabla P_M.
\]

Its Hessian is

\[
\begin{aligned}
H_{\Delta_\pi}
&=
H_{AM}
-
P_MH_A
-
P_AH_M
\\
&\quad
-
\nabla P_A\nabla P_M^\top
-
\nabla P_M\nabla P_A^\top.
\end{aligned}
\]

### Step 5: connection to D7

The one-face derivative formulas reduce to

\[
\partial_{q_j}\Delta_\pi
=
f_j(q_j)\beta_j^\Delta
\]

and

\[
\partial_c\Delta_\pi
=
f_T(c)\beta_c^\Delta.
\]

Thus the gradient agrees with the D7 reference influence-function
coefficients.

## Scope

The theorem is deliberately stated under explicit trace regularity. It does
not cover threshold coincidence, positive-probability winner ties, or moving
candidate dimension.
