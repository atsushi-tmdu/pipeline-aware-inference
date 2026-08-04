# D8-A.R3: Winner-Cell and Coincidence Inventory

## Nonempty winner cells

The base pool is \(\{0,1\}\) and the full pool is \(\{0,1,2\}\).

If the base winner is \(a\in\{0,1\}\), the full winner can only be:

- the same candidate \(a\); or
- the added candidate \(2\).

The other base candidate cannot become the full winner because it was already
below \(a\) before candidate \(2\) was added.

Thus the only nonempty winner pairs are

\[
(0,0),\quad(0,2),\quad(1,1),\quad(1,2).
\]

## Incremental rejection

On cells \((a,a)\),

\[
M=(1-R_0)R_1=0.
\]

On cells \((a,2)\),

\[
M
=
I(X_a\le q_a)
I\{X_2>\max(X_a,q_2)\}.
\]

Therefore the only candidate-threshold coincidence hyperplanes relevant to
the incremental policy are

\[
q_0=q_2
\qquad\text{and}\qquad
q_1=q_2.
\]

## Activation

On base-winner cell \(a\),

\[
A=I(X_a>c).
\]

Under strict candidate-trigger separation, the ordering of \(c\) and \(q_a\)
is locally fixed.

If \(c<q_a\),

\[
AM
=
I(c<X_a\le q_a)
I\{X_2>\max(X_a,q_2)\}.
\]

If \(c>q_a\), \(AM=0\).

No additional coincidence hyperplane is active under the locked separation
condition.

## Finite cone arrangement

The generalized local expansion is therefore divided by the two hyperplanes

\[
u_0-u_2=0,
\qquad
u_1-u_2=0.
\]

There are at most four threshold-order cones.
