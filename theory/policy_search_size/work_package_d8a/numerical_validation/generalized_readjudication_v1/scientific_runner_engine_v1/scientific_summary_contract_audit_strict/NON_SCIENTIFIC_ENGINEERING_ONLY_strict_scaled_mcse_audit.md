# D8-A Strict Scaled-MCSE Definition Audit

**Strict status:** TARGET_ONLY_FORMULA_NOT_FOUND
**Exact formula candidates:** 0
**Target-only occurrences:** 4
**Scientific simulation run:** no

## Adjudication

The numerical scaled-MCSE target is present, but no strong definition of the scaling denominator or formula was found in committed D8-A sources.

The runner engine must remain unlocked. The formula may not be invented after scientific output is inspected.

## Refs audited

- `HEAD`
- `d8a-numerical-design-lock-v1`
- `d8a-generalized-design-lock-v1`
- `d8a-generalized-implementation-lock-v1`
- `d8a-scientific-run-package-prelock-v1`
- `d8a-coincidence-gap-audit-v1`
- `d8a-generalized-theory-repair-v1`
- `d8a-theory-complete-v1`
- `d8a-theory-prelock-v1`

## Strong formula candidates

_None found._

## Target-only occurrences

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 92

```text
87:     "diagnostic_minimum_replicates": 1000,
88:     "effect_dependent_stopping": false,
89:     "generator": "numpy.random.PCG64DXSM",
90:     "master_seed": 20260804,
91:     "nested_common_random_numbers_across_sizes": true,
92:     "precision_limited_fraction_maximum": 0.1,
93:     "precision_stopping_only": true,
94:     "primary_maximum_replicates": 20000,
95:     "primary_minimum_replicates": 2000,
96:     "primary_scaled_mcse_target": 0.03,
97:     "raw_bank_storage": false,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 96

```text
91:     "nested_common_random_numbers_across_sizes": true,
92:     "precision_limited_fraction_maximum": 0.1,
93:     "precision_stopping_only": true,
94:     "primary_maximum_replicates": 20000,
95:     "primary_minimum_replicates": 2000,
96:     "primary_scaled_mcse_target": 0.03,
97:     "raw_bank_storage": false,
98:     "reference_evaluation_streams_independent": true,
99:     "streaming_required": true
100:   },
101:   "oracle_contract": {
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_DESIGN.json` line 62

```text
57:     "diagnostic_minimum_replicates": 1000,
58:     "effect_dependent_stopping": false,
59:     "generator": "numpy.random.PCG64DXSM",
60:     "master_seed": 20260804,
61:     "nested_common_random_numbers_across_sizes": true,
62:     "precision_limited_fraction_maximum": 0.1,
63:     "precision_stopping_only": true,
64:     "primary_maximum_replicates": 20000,
65:     "primary_minimum_replicates": 2000,
66:     "primary_scaled_mcse_target": 0.03,
67:     "raw_bank_storage": false,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_DESIGN.json` line 66

```text
61:     "nested_common_random_numbers_across_sizes": true,
62:     "precision_limited_fraction_maximum": 0.1,
63:     "precision_stopping_only": true,
64:     "primary_maximum_replicates": 20000,
65:     "primary_minimum_replicates": 2000,
66:     "primary_scaled_mcse_target": 0.03,
67:     "raw_bank_storage": false,
68:     "reference_evaluation_streams_independent": true,
69:     "streaming_required": true
70:   },
71:   "ordinary_hessian_coefficient_allowed": false,
```


## Broad-audit false-positive guard

- generic `precision_pass` plumbing excluded: 2
- current uncommitted runner engine excluded: True
- target constants treated as formulas: no
