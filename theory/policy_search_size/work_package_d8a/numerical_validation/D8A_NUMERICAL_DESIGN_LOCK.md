# D8-A Numerical Design Lock

**Lock status:** prepared
**Scientific numerical design locked:** yes
**Scientific simulation run:** no

## Locked scope

The design contains 75 admissible policy cells:

- 34 primary cells;
- 41 diagnostic cells.

It uses three dependence structures, three common monotone score
transformations, three candidate probabilities, and three trigger
probabilities, subject to the prespecified latent-separation rule.

## Locked experiments

- reference-only;
- evaluation-only;
- combined reference/evaluation.

## Locked principles

- exact empirical-quantile convention;
- independent reference and evaluation streams;
- common random numbers nested across sample sizes;
- precision-only Monte Carlo stopping;
- no post-hoc cell deletion;
- separate fatal implementation checks and finite-sample usefulness checks.

No D8-A scientific simulation has been run.
