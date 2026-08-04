# D8-A Generalized Design Re-adjudication

## Historical design

The historical design lock contains 75 registered rows:

- three dependence structures;
- three common monotone transformations;
- three candidate probabilities;
- three trigger probabilities;
- a prespecified candidate-trigger separation rule.

The registry itself is retained unchanged.

## Exact transformation equivalence

Let \(h\) be any strictly increasing transformation used in the registry.
For every reference and evaluation observation,

\[
\arg\max_j h(Z_j)
=
\arg\max_j Z_j.
\]

For the declared generalized-inverse empirical quantile,

\[
\widehat q_{h(Z),p}
=
h(\widehat q_{Z,p}).
\]

Therefore,

\[
h(Z_j)>\widehat q_{h(Z_j),p}
\iff
Z_j>\widehat q_{Z_j,p}.
\]

The complete adaptive policy, comparator estimator, policy contrast, and TESS
contrast are exactly invariant under the common transformation.

Thus identity, exponential, and hyperbolic-sine rows with the same latent
dependence and probabilities belong to one scientific equivalence class.

## Re-adjudicated unit

Acceptance criteria are aggregated over 25 latent equivalence classes rather
than 75 transformed rows.

The original row-level primary designation induces:

- 17 primary scientific classes;
- 8 diagnostic scientific classes.

The 50 nonidentity rows are deterministic reparameterization audits and are
not counted as independent evidence.

## Candidate coincidence

Within every class,

\[
q_0=q_1=q_2.
\]

The active policy coincidence hyperplanes are

\[
q_0=q_2,
\qquad
q_1=q_2.
\]

The ordinary Hessian coefficient is replaced by the generalized coefficient

\[
\begin{aligned}
C_{\Delta,B}^{\mathrm{gen}}
&=
g_\Delta^\top b_{\theta,B}
+
\frac12
\operatorname{tr}
\{H_\Delta^{\mathrm{sm}}\Sigma_\theta\}
\\
&\quad+
\frac12
\sum_{a=0}^1
\lambda_a
d_a^\top\Sigma_\theta d_a.
\end{aligned}
\]

## Execution status

The design is prospectively re-adjudicated, but scientific execution remains
blocked until the generalized oracle and simulation implementation pass an
independent implementation lock.
