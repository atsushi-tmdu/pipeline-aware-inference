# D8-A Winner-Cell Integral Representation

## Status

Prospective proof scaffold. The full twice-differentiability theorem is not
yet declared proved.

## 1. Finite winner partition

Let

\[
J_0(x)
=
\arg\max_{j\in\mathcal J_0}x_j,
\qquad
J_1(x)
=
\arg\max_{j\in\mathcal J_1}x_j.
\]

Under almost-sure uniqueness, score space is partitioned, up to a null tie
set, into finitely many winner cells

\[
\mathcal W_{ab}
=
\{x:J_0(x)=a,\ J_1(x)=b\},
\qquad
a\in\mathcal J_0,\ b\in\mathcal J_1.
\]

Because both candidate pools are fixed and finite, there are at most

\[
|\mathcal J_0|\,|\mathcal J_1|
\]

such cells.

## 2. Local threshold-ordering stability

Strict separation gives

\[
d_\theta
=
\min_{j\in\mathcal J_0}|q_j-c|
>
0.
\]

For every threshold perturbation satisfying

\[
\|\widetilde\theta-\theta\|_\infty
<
\frac{d_\theta}{2},
\]

the sign of every \(q_j-c\) remains unchanged. Consequently, the local
Boolean form of activation and candidate rejection is fixed.

This eliminates the D7 positive-part kink from the D8-A regular
neighborhood.

## 3. Cellwise integral form

Every probability entering

\[
\Delta_\pi(\theta)
=
E_\theta(AM)
-
E_\theta(A)E_\theta(M)
\]

can be written as a finite sum

\[
P_r(\theta)
=
\sum_{a,b}
\int_{\mathcal W_{ab}}
I\{G_{r,ab}(x,\theta)>0\}
f_X(x)\,dx,
\]

where \(G_{r,ab}\) is a finite collection of coordinate-threshold
inequalities whose logical structure is constant in the stable
neighborhood.

Winner cells themselves do not move with \(\theta\); only candidate and
trigger threshold faces move.

## 4. First boundary derivatives

Differentiating a candidate threshold \(q_j\) produces a trace integral over

\[
\{x_j=q_j\}\cap\mathcal W_{ab}.
\]

Summing the affected cells gives

\[
\partial_{q_j}\Delta_\pi
=
f_j(q_j)
E\left[
(A-\rho)D_j
\mid X_j=q_j
\right].
\]

Differentiating the trigger threshold gives a trace over

\[
\{T=c\},
\]

and

\[
\partial_c\Delta_\pi
=
f_T(c)
\left\{
\mu-E(M\mid T=c)
\right\}.
\]

These reproduce the D7 reference influence coefficients after division by
the corresponding boundary density.

## 5. Second boundary derivatives

A second derivative acts either:

1. on the boundary density;
2. on the conditional policy trace along that boundary; or
3. on a second moving boundary.

This creates:

- candidate-candidate terms;
- candidate-trigger terms;
- trigger-trigger terms.

The mixed candidate-trigger term is generally nonzero.

## 6. Null intersections

The following sets require explicit treatment:

- winner ties;
- intersections of two candidate threshold faces;
- intersections of a candidate face with the trigger face;
- winner boundaries intersecting threshold faces.

Under a continuously differentiable joint density and suitable
transversality, these are codimension-two or null sets for first derivatives.
For second derivatives they contribute through iterated boundary traces,
not through positive-probability atoms.

## 7. Remaining task

A rigorous proof must convert this decomposition into a local
twice-continuous-differentiability theorem with dominated trace integrals.
