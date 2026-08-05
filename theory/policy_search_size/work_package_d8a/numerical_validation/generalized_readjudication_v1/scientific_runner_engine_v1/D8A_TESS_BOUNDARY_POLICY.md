# D8-A TESS Boundary Policy

For

\[
\operatorname{TESS}(p;\alpha)
=
\frac{\log(1-p)}{\log(1-\alpha)},
\]

the value is finite for \(0\le p<1\) and equals \(+\infty\) at \(p=1\).

JSON output must not contain nonstandard `Infinity` values. Every TESS value
and contrast is therefore represented as a structured record.

Value statuses:

- `finite`;
- `positive_infinity`.

Contrast statuses:

- `finite`;
- `positive_infinity`;
- `negative_infinity`;
- `indeterminate_both_one`.

Boundary records are never discarded, clipped, or silently converted to
missing values. Scientific summaries must report all status counts and
summarize finite values only within the `finite` stratum.
