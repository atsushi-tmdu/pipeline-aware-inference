# D7 Runtime-Only Preflight Adjudication

**Status: PASS**

This is mathematical and implementation debugging only. It is not scientific
evidence and does not lock the D7 numerical design.

## Unit tests

- Tests run: 21
- Result: PASS

## Regular benchmark

- Minimum candidate/trigger threshold separation:
  `0.77740657`
- Rejection contrast:
  `-0.00570626`
- Candidate 0 finite difference / boundary:
  `0.01142517` / `0.01163593`
- Candidate 1 finite difference / boundary:
  `0.00500156` / `0.00488945`
- Candidate 2 finite difference / boundary:
  `0.01205010` / `0.01121617`
- Trigger finite difference / boundary:
  `-0.00815848` / `-0.00855146`

## Maximum-density identity

- Winner-region decomposition:
  `0.47476782`
- CDF finite difference:
  `0.47475026`
- Result: PASS

## Coincidence kink

- Empirical nonadditivity:
  `0.02881981`
- Boundary coefficient:
  `0.02886472`
- Result: PASS

## Interpretation

The preflight supports the regular maximum-trigger boundary derivative and the
explicit positive-part nonregularity at candidate/trigger threshold
coincidence.

It does not validate discrete AUROC trigger atoms, deterministic trigger-tie
randomization, failed-fit handling, or the full scientific numerical design.
