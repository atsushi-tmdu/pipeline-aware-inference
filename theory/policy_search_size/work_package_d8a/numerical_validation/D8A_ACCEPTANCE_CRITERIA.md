# D8-A Numerical Acceptance Criteria

## Fatal implementation checks

The run is invalid if any of the following occurs:

- an admissible registered cell is omitted;
- a cell is deleted after results are viewed;
- the empirical quantile convention differs from
  \(k_B=\lceil Bp\rceil\);
- a deterministic oracle fails;
- a correlation matrix is not positive definite;
- a locked separation condition is violated;
- Hessian symmetry error exceeds \(10^{-8}\);
- independent Hessian implementations disagree beyond \(10^{-5}\) relative;
- reference and evaluation random streams are not independent.

## Exact evaluation identity

The exact policy covariance mean identity is checked using simultaneous
Bonferroni-adjusted Monte Carlo intervals with familywise level \(0.01\).

This is an implementation check, not an asymptotic check.

## Reference approximation

For each primary cell, define

\[
E_{R,B}
=
\frac{
\left[
|B\{\widehat{\operatorname{Bias}}_R-C_B/B\}|
-
z_\star B\,\operatorname{MCSE}
\right]_+
}{
1+|C_B|
}.
\]

At \(B=10{,}000\):

- median \(E_{R,B}\le0.15\);
- 90th percentile \(E_{R,B}\le0.40\).

The median must improve by at least 40% from \(B=500\) to \(B=10{,}000\).

## Combined policy approximation

The MCSE-adjusted absolute residual is divided by

\[
(B^{-1}+n^{-1})
(1+|C_{\Delta,B}|+|\Delta_\pi|).
\]

At \((B,n)=(10{,}000,10{,}000)\):

- median at most \(0.15\);
- 90th percentile at most \(0.40\).

## TESS approximation

The corresponding TESS residual is divided by

\[
(B^{-1}+n^{-1})
(1+|C_{S,R,B}|+|C_{S,E}|).
\]

At the largest pair:

- median at most \(0.25\);
- 90th percentile at most \(0.60\).

## Improvement criterion

At least 75% of primary cells must have a smaller absolute residual under the
second-order approximation than under the prespecified first-order-only
baseline.

## Precision limitation

No more than 10% of primary cells may reach the maximum replicate count
without meeting the locked MCSE target.
