# D6 Runtime Decision Before Numerical Lock

**Decision:** retain the prospective full scientific design without reducing
the declared repetition counts.

## Runtime-only evidence

- Smoke status: `PASS`
- Full-grid rows: `288`
- Bootstrap outer rows: `48`
- Elapsed time: `1.990` seconds
- Scientific evidence: no

The smoke used 8 outer repetitions per full-grid cell, 4 bootstrap outer
datasets per bootstrap cell, and 19 bootstrap resamples per outer dataset.

## Locked scientific counts

- Full-grid outer repetitions: **2,000 per cell**
- Full-grid cells: **36**
- Bootstrap outer datasets: **500 per bootstrap cell**
- Bootstrap cells: **12**
- Bootstrap resamples: **249 per outer dataset**
- Unconditional benchmark draws per DGP-alpha cell: **4,194,304**
- Conditional draws per candidate or activation boundary: **524,288**

## Rationale

The smoke completed without fatal checks, nonfinite results, support
violations, tie events, bootstrap failures, or memory problems. Its elapsed
time provided no runtime-based reason to weaken the prospective design.

The full run will be materially longer because the scientific benchmark and
bootstrap counts are much larger. The counts are nevertheless retained because
the smoke demonstrated a lightweight, stable implementation. This decision is
based only on runtime and implementation feasibility, not on scientific
estimates from the smoke.

After this lock, changing any scientific count, DGP, seed, success criterion,
or bootstrap cell requires a new D6 numerical-protocol version.
