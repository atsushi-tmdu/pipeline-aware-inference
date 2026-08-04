# D8-A Generalized Run Contract

## Scientific execution remains blocked

This design lock does not authorize a scientific run.

Execution requires a later implementation lock that verifies:

- generalized oracle coefficients;
- both active coincidence branches;
- exact transformation invariance;
- seed derivation and independent streams;
- streaming and atomic batch output;
- all acceptance calculations.

## Canonical simulation

Only the identity member of each of the 25 latent equivalence classes is
simulated.

The two nonidentity members are regenerated deterministically from the same
latent banks and used solely for invariance audits.

## Prohibited actions

- counting transformed members as independent evidence;
- deleting a transformed member that fails invariance;
- changing class roles after output inspection;
- replacing generalized coefficients by smooth-only coefficients;
- beginning the scientific run before implementation lock;
- using an engineering smoke test as scientific evidence.

## Engineering smoke test

A later implementation package may run at most two diagnostic equivalence
classes with at most 20 replicates each and must label all output
`NON_SCIENTIFIC_ENGINEERING_ONLY`.
