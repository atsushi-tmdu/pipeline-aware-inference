# D8-A Generalized Numerical Design

This directory re-adjudicates the historical 75-row prospective design after
the candidate-threshold coincidence repair.

No scientific simulation is run here.

The 75 historical rows consist of 25 distinct latent scientific cells, each
represented under three common monotone score transformations. Because the
policy, empirical order statistics, winner identities, and rejection
decisions are exactly invariant under a common strictly increasing
transformation, the three transformed rows are not independent scientific
replicates.

The repaired design therefore uses:

- 25 scientific equivalence classes;
- 17 primary equivalence classes;
- 8 diagnostic equivalence classes;
- 50 deterministic reparameterization-audit rows.

Only the canonical identity member of each class is simulated. The
exponential and hyperbolic-sine members audit exact reparameterization
invariance.
