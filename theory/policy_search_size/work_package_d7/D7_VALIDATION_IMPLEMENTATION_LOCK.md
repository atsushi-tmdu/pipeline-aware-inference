# D7 Validation Implementation Lock

**Implementation lock:** complete
**Scientific full run completed:** no

This lock freezes the code that will execute the already-locked D7 continuous
maximum-trigger scientific validation.

Before this lock was created:

- the D7 theory checkpoint verified PASS;
- the D7 numerical-design lock verified PASS;
- all 37 unit tests passed;
- the complete smoke path passed;
- smoke winner ties were zero;
- smoke plus-one support violations were zero;
- smoke bootstrap failures were zero;
- smoke covariance-identity error was at machine precision.

The smoke bias, variance-ratio, and bootstrap-ratio ranges are not scientific
evidence because smoke repetition counts are intentionally tiny.

No scientific full run had been executed when this lock was created.
