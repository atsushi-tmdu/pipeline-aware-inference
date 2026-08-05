# D8-A Scientific Run Package Protocol

## Status

**Run infrastructure prelocked:** yes
**Scientific runner engine locked:** no
**Scientific simulation run:** no

## Scientific units

The run contains 25 latent scientific equivalence classes:

- 17 primary classes;
- 8 diagnostic classes.

The 50 nonidentity transformation rows are exact deterministic audits and
are not independent scientific units.

## Job families

Each scientific class has three family jobs:

1. reference-only;
2. evaluation-only;
3. combined reference/evaluation.

This gives 75 family jobs. Sample-size points within a family are evaluated
from nested prefixes of the same random bank, preserving the locked
common-random-number design.

## Immutable dependencies

The package records and verifies:

- generalized theory tag;
- generalized design tag;
- generalized implementation tag;
- exact implementation commit;
- class registry hash;
- design configuration hash;
- implementation lock manifest hash;
- job registry;
- seed namespace inventory;
- output path;
- atomic-write and resume contract.

## Current boundary

The package does not execute the scientific validation. Execution remains
blocked until the scientific runner engine and final run command receive a
separate lock.
