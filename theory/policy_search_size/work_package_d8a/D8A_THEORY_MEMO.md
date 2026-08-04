# D8-A Theory Memo

## 1. Exact finite-evaluation identity

Conditional on the reference bank, evaluation observations are iid. Therefore,

\[
E_E\left[
\overline{AM}-\bar A\bar M
\mid\widehat\theta
\right]
=
\left(1-\frac1n\right)
\operatorname{Cov}_{\widehat\theta}(A,M).
\]

This identity is finite-sample and exact.

## 2. Expectation-level second-order reference expansion

D8-A does not assume a deterministic second-order stochastic remainder.
Instead, it targets

\[
E(\widehat\theta-\theta)
=
\frac{b_{\theta,B}}{B}
+
o(B^{-1}),
\]

and

\[
B\,E\left[
(\widehat\theta-\theta)
(\widehat\theta-\theta)^\top
\right]
=
\Sigma_\theta+o(1),
\]

together with a \(2+\eta\) moment bound controlling the Taylor remainder.

For a twice continuously differentiable contrast \(\Delta(\theta)\),

\[
E_R\{\Delta(\widehat\theta)\}
=
\Delta(\theta)
+
\frac{C_{R,B}}{B}
+
o(B^{-1}),
\]

where

\[
C_{R,B}
=
\nabla\Delta(\theta)^\top b_{\theta,B}
+
\frac12\operatorname{tr}
\{H_\Delta(\theta)\Sigma_\theta\}.
\]

## 3. Candidate-trigger cross term

Partitioning the threshold vector into candidate thresholds \(q\) and the
trigger threshold \(c\), the curvature coefficient includes

\[
\frac12\operatorname{tr}(H_{qq}\Sigma_{qq})
+
H_{qc}^\top\Sigma_{qc}
+
\frac12H_{cc}\Sigma_{cc}.
\]

The cross term cannot be removed without an additional orthogonality result.

## 4. Combined expansion

Using the exact conditional identity,

\[
E(\widehat\Delta)-\Delta
=
\frac{C_{R,B}}{B}
-
\frac{\Delta}{n}
-
\frac{C_{R,B}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

## 5. Empirical-quantile convention

The coefficient \(b_{\theta,B}\) depends on the exact empirical-quantile index

\[
k_B=\lceil Bp\rceil.
\]

The bounded lattice term \(k_B-(B+1)p\), density derivatives, and dependence
among complete reference vectors must all be retained.

## 6. TESS derivatives

\[
g_\alpha'(x)
=
-\frac{1}{(1-x)\log(1-\alpha)}
\]

and

\[
g_\alpha''(x)
=
-\frac{1}{(1-x)^2\log(1-\alpha)}.
\]

The second-order TESS result must contain both mean-centering and curvature
components.

## 7. Prospective theorem targets

- Proposition D8-A.1: exact conditional evaluation identity.
- Lemma D8-A.2: joint second-order quantile expansion.
- Lemma D8-A.3: twice differentiability of the separated policy map.
- Theorem D8-A.4: combined \(B^{-1}\) and \(n^{-1}\) bias expansion with bounded \(C_{R,B}\); constant-coefficient corollaries require lattice stabilization.
- Corollary D8-A.5: second-order TESS expansion.

Only Proposition D8-A.1 is presently treated as established. The remaining
statements are proof targets.
