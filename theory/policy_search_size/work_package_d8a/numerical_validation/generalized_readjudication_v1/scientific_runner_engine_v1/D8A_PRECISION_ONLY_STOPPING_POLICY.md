# D8-A Role-Aware Precision-Only Stopping Policy

The original Monte Carlo contract is preserved verbatim in
`D8A_LOCKED_MONTE_CARLO_CONTRACT.json`.

The contract contains separate schedules for primary and diagnostic
scientific classes:

- `primary_minimum_replicates`;
- `primary_maximum_replicates`;
- `diagnostic_minimum_replicates`;
- `diagnostic_maximum_replicates`;
- one shared `batch_size`.

For each role:

1. continue until its minimum replicate count;
2. at or beyond that minimum, stop only when the external locked precision
   assessment passes;
3. otherwise continue by the shared locked batch size;
4. stop at that role's maximum replicate count;
5. distinguish `precision_target_met` from
   `maximum_replicates_reached`.

The runner engine does not reinterpret the locked precision targets.
