# D8-A Scientific Summary Contract Audit

**Audit status:** SOURCE_FOUND_REVIEW_REQUIRED
**Scaled-MCSE definition status:** FORMULA_OR_IMPLEMENTATION_FOUND
**Scientific simulation run:** no

## Locked Monte Carlo schedule

- primary minimum: 2000
- primary maximum: 20000
- diagnostic minimum: 1000
- diagnostic maximum: 5000
- shared batch size: 250
- primary scaled-MCSE target: 0.03

## Adjudication

An exact formula or executable implementation was found.
The cited source locations must be reviewed before the summary engine is locked.

## Files searched

- text files scanned: 200
- total contextual hits: 62

## Highest-priority source hits

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/check_d8a_stopping_and_tess_adjudication.py` line 50

```text
46:
47:         initial = rule.decide(
48:             role,
49:             0,
50:             precision_pass=True,
51:         )
52:         if initial.stop:
53:             failures.append(
54:                 f"{role}: stopped before minimum"
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/check_d8a_stopping_and_tess_adjudication.py` line 60

```text
56:
57:         precision = rule.decide(
58:             role,
59:             schedule.initial_replicates,
60:             precision_pass=True,
61:         )
62:         if (
63:             not precision.stop
64:             or precision.reason
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/check_d8a_stopping_and_tess_adjudication.py` line 74

```text
70:
71:         maximum = rule.decide(
72:             role,
73:             schedule.maximum_replicates,
74:             precision_pass=False,
75:         )
76:         if (
77:             not maximum.stop
78:             or maximum.reason
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/d8a_runner_stopping.py` line 127

```text
123:         return self.schedule_for(
124:             class_role
125:         ).decide(
126:             completed_replicates,
127:             precision_pass=precision_pass,
128:         )
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 46

```text
42:         rule = make_rule()
43:         decision = rule.decide(
44:             "primary",
45:             0,
46:             precision_pass=True,
47:         )
48:         self.assertFalse(decision.stop)
49:
50:     def test_diagnostic_initial_stage_continues(
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 57

```text
53:         rule = make_rule()
54:         decision = rule.decide(
55:             "diagnostic",
56:             0,
57:             precision_pass=True,
58:         )
59:         self.assertFalse(decision.stop)
60:
61:     def test_primary_precision_pass_stops(
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 61

```text
57:             precision_pass=True,
58:         )
59:         self.assertFalse(decision.stop)
60:
61:     def test_primary_precision_pass_stops(
62:         self,
63:     ) -> None:
64:         rule = make_rule()
65:         decision = rule.decide(
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 68

```text
64:         rule = make_rule()
65:         decision = rule.decide(
66:             "primary",
67:             rule.primary.initial_replicates,
68:             precision_pass=True,
69:         )
70:         self.assertTrue(decision.stop)
71:         self.assertEqual(
72:             decision.reason,
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 83

```text
79:         rule = make_rule()
80:         decision = rule.decide(
81:             "diagnostic",
82:             rule.diagnostic.maximum_replicates,
83:             precision_pass=False,
84:         )
85:         self.assertTrue(decision.stop)
86:         self.assertEqual(
87:             decision.reason,
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 97

```text
93:         schedule = rule.primary
94:         decision = rule.decide(
95:             "primary",
96:             schedule.maximum_replicates - 1,
97:             precision_pass=False,
98:         )
99:         self.assertEqual(
100:             decision.next_batch_size,
101:             1,
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 110

```text
106:         with self.assertRaises(ValueError):
107:             rule.decide(
108:                 "unknown",
109:                 0,
110:                 precision_pass=False,
111:             )
112:
113:
114: if __name__ == "__main__":
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/tests/test_d8a_numerical_design.py` line 114

```text
110:         )
111:
112:     def test_stopping_is_precision_only(self) -> None:
113:         mc = CONFIG["monte_carlo"]
114:         self.assertTrue(mc["precision_stopping_only"])
115:         self.assertFalse(mc["effect_dependent_stopping"])
116:
117:     def test_no_post_hoc_cell_dropping(self) -> None:
118:         self.assertTrue(
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 96

```text
92:     "precision_limited_fraction_maximum": 0.1,
93:     "precision_stopping_only": true,
94:     "primary_maximum_replicates": 20000,
95:     "primary_minimum_replicates": 2000,
96:     "primary_scaled_mcse_target": 0.03,
97:     "raw_bank_storage": false,
98:     "reference_evaluation_streams_independent": true,
99:     "streaming_required": true
100:   },
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_DESIGN.json` line 66

```text
62:     "precision_limited_fraction_maximum": 0.1,
63:     "precision_stopping_only": true,
64:     "primary_maximum_replicates": 20000,
65:     "primary_minimum_replicates": 2000,
66:     "primary_scaled_mcse_target": 0.03,
67:     "raw_bank_storage": false,
68:     "reference_evaluation_streams_independent": true,
69:     "streaming_required": true
70:   },
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_run_prelock_v1/D8A_SCIENTIFIC_RUN_CONFIG.json` line 68

```text
64:     "precision_limited_fraction_maximum": 0.1,
65:     "precision_stopping_only": true,
66:     "primary_maximum_replicates": 20000,
67:     "primary_minimum_replicates": 2000,
68:     "primary_scaled_mcse_target": 0.03,
69:     "raw_bank_storage": false,
70:     "reference_evaluation_streams_independent": true,
71:     "streaming_required": true
72:   },
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/D8A_LOCKED_MONTE_CARLO_CONTRACT.json` line 28

```text
24:     "precision_limited_fraction_maximum": 0.1,
25:     "precision_stopping_only": true,
26:     "primary_maximum_replicates": 20000,
27:     "primary_minimum_replicates": 2000,
28:     "primary_scaled_mcse_target": 0.03,
29:     "raw_bank_storage": false,
30:     "reference_evaluation_streams_independent": true,
31:     "streaming_required": true
32:   },
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/D8A_PRECISION_ONLY_STOPPING_POLICY.md` line 22

```text
18: 2. at or beyond that minimum, stop only when the external locked precision
19:    assessment passes;
20: 3. otherwise continue by the shared locked batch size;
21: 4. stop at that role's maximum replicate count;
22: 5. distinguish `precision_target_met` from
23:    `maximum_replicates_reached`.
24:
25: The runner engine does not reinterpret the locked precision targets.
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/D8A_PRECISION_ONLY_STOPPING_POLICY.md` line 25

```text
21: 4. stop at that role's maximum replicate count;
22: 5. distinguish `precision_target_met` from
23:    `maximum_replicates_reached`.
24:
25: The runner engine does not reinterpret the locked precision targets.
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/check_d8a_stopping_and_tess_adjudication.py` line 65

```text
61:         )
62:         if (
63:             not precision.stop
64:             or precision.reason
65:             != "precision_target_met"
66:         ):
67:             failures.append(
68:                 f"{role}: precision stop incorrect"
69:             )
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/d8a_runner_stopping.py` line 62

```text
58:             and precision_pass
59:         ):
60:             return StoppingDecision(
61:                 stop=True,
62:                 reason="precision_target_met",
63:                 next_batch_size=0,
64:             )
65:
66:         remaining = (
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/d8a_runner_stopping.py` line 88

```text
84:                 self.batch_size,
85:                 remaining,
86:             )
87:             reason = (
88:                 "precision_target_not_met"
89:             )
90:
91:         return StoppingDecision(
92:             stop=False,
```

### `theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_runner_engine_v1/tests/test_stopping_rule.py` line 73

```text
69:         )
70:         self.assertTrue(decision.stop)
71:         self.assertEqual(
72:             decision.reason,
73:             "precision_target_met",
74:         )
75:
76:     def test_diagnostic_maximum_stops(
77:         self,
```
