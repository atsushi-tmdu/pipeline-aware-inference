# D8-A Quantile-Convention Adjudication

## Decision

Replace the unrestricted constant \(C_R\) by a bounded
reference-size-dependent coefficient \(C_{R,B}\).

## Reason

Under

\[
k_B=\lceil Bp\rceil,
\]

the lattice offset

\[
a_{p,B}=k_B-(B+1)p
\]

need not converge. A constant second-order coefficient requires a stabilized
subsequence, a compatible grid, or a different interpolated or randomized
quantile convention.

## Consequences

- The exact finite-evaluation identity is unchanged.
- Candidate-trigger covariance and Hessian cross terms remain required.
- The unrestricted combined expansion uses \(C_{R,B}\).
- Constant-\(C_R\) statements become conditional corollaries.
- D7 remains formally FAIL.
- No D8-A scientific simulation has been designed or run.
