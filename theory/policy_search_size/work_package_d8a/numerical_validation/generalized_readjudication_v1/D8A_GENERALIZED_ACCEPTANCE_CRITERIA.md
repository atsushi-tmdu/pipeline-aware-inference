# D8-A Generalized Acceptance Criteria

## Acceptance unit

Scientific summaries use the 25 latent equivalence classes.

The 50 nonidentity transformed rows are invariance audits and cannot increase
the denominator of a scientific pass fraction.

## Fatal checks

The run is invalid if any of the following occurs:

- a historical registry row is deleted;
- an equivalence class lacks exactly three transformed members;
- a nonidentity member produces a different Boolean policy outcome;
- a generalized coefficient differs across transformations beyond tolerance;
- either active coincidence hyperplane is omitted;
- a contrast variance is nonpositive;
- the smooth-only/generalized coefficient difference does not equal the
  locked kink correction;
- reference and evaluation streams are not independent;
- the empirical quantile convention is not \(k_B=\lceil Bp\rceil\);
- a registered scientific class is omitted;
- an acceptance threshold is changed after scientific output is inspected.

## Exact evaluation identity

The finite-\(n\) covariance identity remains a fatal implementation check and
is tested with Bonferroni simultaneous Monte Carlo intervals at familywise
level \(0.01\).

## Reference approximation

Replace the historical ordinary-Hessian coefficient by
\(C_{\Delta,B}^{\mathrm{gen}}\).

At \(B=10{,}000\), over the 17 primary equivalence classes:

- median normalized residual at most \(0.15\);
- 90th percentile at most \(0.40\);
- median improvement from \(B=500\) to \(B=10{,}000\) at least 40%.

## Combined policy approximation

At \((B,n)=(10{,}000,10{,}000)\), over the 17 primary classes:

- median normalized residual at most \(0.15\);
- 90th percentile at most \(0.40\).

The approximation is

\[
\frac{C_{\Delta,B}^{\mathrm{gen}}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}^{\mathrm{gen}}}{Bn}.
\]

## TESS approximation

Use \(C_{S,R,B}^{\mathrm{gen}}\) and the unchanged \(C_{S,E}\).

At the largest pair:

- median normalized residual at most \(0.25\);
- 90th percentile at most \(0.60\).

## Improvement reporting

The generalized approximation is compared with:

1. no reference correction;
2. the superseded smooth-only correction;
3. the generalized correction.

The historical requirement that at least 75% of primary scientific units
improve over the first-order-only baseline is retained.

Generalized-versus-smooth-only improvement is reported for every class but is
not a standalone fatal criterion, because the locked kink contribution may
be smaller than Monte Carlo resolution in some cells.

## Precision limitation

No more than 10% of the 17 primary equivalence classes may reach the maximum
replicate count without meeting the locked MCSE target.
