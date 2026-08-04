# Theorem D8-A.R4: Generalized Coincidence Policy Expansion

## Assumptions

1. The base and full candidate pools are fixed as
   \(\{0,1\}\subset\{0,1,2\}\).
2. Winners are almost surely unique.
3. Candidate-trigger thresholds are strictly separated.
4. For each incremental winner cell \((a,2)\), the integrated tail kernel
   \(H_a(w,s)\) satisfies the assumptions of Lemma D8-A.R2.
5. All smooth activation and separated-boundary terms are twice continuously
   differentiable with dominated derivatives.

## Cell representations

Define

\[
U_a(x,y)
=
\int_{-\infty}^{x}
H_a\{w,\max(w,y)\}\,dw.
\]

Then

\[
P_M(\theta)
=
\sum_{a=0}^1
U_a(q_a,q_2).
\]

Let

\[
s_a=I(c<q_a),
\]

which is locally constant by strict separation. Then

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

The activation probability \(P_A(\theta)\) is smooth.

## Generalized expansion

There exist a gradient \(g_\Delta\), a symmetric smooth-stratum Hessian
\(H_\Delta^{\mathrm{sm}}\), and branch coefficients

\[
\lambda_a
=
\{s_a-P_A(\theta)\}\kappa_a,
\qquad
\kappa_a
=
\frac12
\partial_sH_a(q_a,q_2),
\]

evaluated on each active coincidence \(q_a=q_2\), such that

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
\sum_{a:\,q_a=q_2}
\lambda_a
(u_a-u_2)_+^2
+
o(\|u\|^2).
\end{aligned}
\]

## Proof

Lemma D8-A.R2 gives the generalized expansion of every coincident
\(U_a(q_a,q_2)\). The terms \(U_a(c,q_2)\) are ordinary smooth terms because
\(c\ne q_2\) locally under the declared separation.

Hence

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

with kink coefficients \(\kappa_a\) and \(s_a\kappa_a\), respectively.

For

\[
\Delta_\pi=P_{AM}-P_AP_M,
\]

ordinary multiplication of the smooth expansion of \(P_A\) and the
generalized expansion of \(P_M\) shows that the policy kink coefficient is

\[
s_a\kappa_a-P_A\kappa_a
=
(s_a-P_A)\kappa_a.
\]

All remaining second-order terms combine into the symmetric
smooth-stratum Hessian \(H_\Delta^{\mathrm{sm}}\). The finite cone
arrangement gives a uniform remainder by taking the maximum over its finitely
many cone-wise remainder bounds.
