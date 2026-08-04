# D8-A Run Contract

## Before scientific execution

The implementation must be tagged after:

- all numerical code is complete;
- engineering tests pass;
- the locked cell registry is unchanged;
- no scientific output has been inspected.

A small engineering smoke test may execute at most two diagnostic cells with
at most 20 replicates each. Its output must be clearly labeled
`NON_SCIENTIFIC_ENGINEERING_ONLY` and must not be used to alter cells,
criteria, or formulas.

## During execution

- use the locked master seed;
- derive cell seeds from canonical cell keys;
- keep reference and evaluation streams independent;
- write results atomically by batch;
- preserve every failed numerical attempt in the log;
- do not overwrite completed batches silently.

## After execution

The formal result must report:

- every fatal check;
- every acceptance criterion;
- every precision-limited cell;
- the full cell count and replicate count;
- both successful and failed criteria.

No criterion may be reclassified after results are viewed.
