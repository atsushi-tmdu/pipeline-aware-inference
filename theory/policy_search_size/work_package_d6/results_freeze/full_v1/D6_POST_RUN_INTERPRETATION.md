# D6 Post-Run Interpretation

## Formal outcome

**Locked scientific adjudication: FAIL.**

The outcome must remain FAIL because the prespecified decision rule required
every scientific check to pass and `delta_s_bias_per_cell` failed.

All fatal implementation checks passed. Every other scientific check passed,
including:

- rejection-contrast bias;
- rejection- and TESS-scale variance ratios;
- influence-normal coverage;
- complete-replication bootstrap standard deviations and coverage;
- the fixed-finite-\(K\) plus-one bridge.

## Single failing cell

- DGP: `gain_coupled_k20`
- alpha: `0.01`
- reference bank: `3000`
- evaluation bank: `5000`
- standardized TESS bias: `0.200781947`
- locked upper limit: `0.200000000`
- numerical excess: `0.000781947`
- excess divided by Monte Carlo SE of standardized bias: `0.035`

Only one of 24 main-regime cells exceeded the per-cell TESS-bias limit.

## Exact bias decomposition

The observed TESS bias was `0.0480373889`.

- finite-sample centering component:
  `0.0471247887`
  (98.10%);
- net Jensen-curvature component:
  `0.0009126001`
  (1.90%);
- decomposition error:
  `2.665e-15`.

Thus, the near-miss is driven almost entirely by finite-reference/evaluation
centering of the two policy probabilities in the deep tail. The nonlinear
TESS transform is a small amplifier rather than the primary source.

## Scientific interpretation

The D6 results provide strong qualified support for the fixed-finite-candidate
unique-winner theory. The locked PASS/FAIL label is not changed after observing
the results.

The result should be reported as:

> All fatal implementation, variance, coverage, bootstrap, and finite-bank
> bridge criteria passed. One of 24 main-regime cells marginally exceeded the
> prespecified standardized TESS-bias threshold at alpha 0.01, while the
> corresponding rejection-probability contrast remained within criterion.

No scientific simulation was rerun and no success criterion was modified.
