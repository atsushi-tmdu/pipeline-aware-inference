# D7 Empirical Trigger-Separation Audit

This is a read-only audit of frozen or historically available raw
candidate-score banks. It is not a new scientific simulation.

## Bank identity

### high_dependency_linear_20

- mapping status: `historical_surrogate_20_candidate`
- expected SHA-256: `88ec92a072e08861e8fe2b5072f66e6312b2a57bb4a133c3d134128264be2ccb`
- selected SHA-256: `ddf6d4fc37d1388b24fd35e4c785ef1e4851f6695cc756726245695f2efda35b`
- selected path: `/Users/sendaatsushi/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/public_release/frozen_raw_sanitized/high_dependency_linear_20/pipeline_phase3_quick_20260724_133334/null_reference_model_metrics.csv`

### mixed_realistic_20

- mapping status: `historical_surrogate_20_candidate`
- expected SHA-256: `d0989d69a16cc12e7317224dd517f28ea4e82c12c98d41e90cc8b29cdde8410b`
- selected SHA-256: `ba195e6d2c30d46b7ea1e0796a15dae5a789f5cc31edff2c2e471ad8b4a768fc`
- selected path: `/Users/sendaatsushi/Documents/pipeline-aware/pipeline-aware-inference/results_phase3c/public_release/frozen_raw_sanitized/mixed_realistic_20/pipeline_phase3_quick_20260724_141555/null_reference_model_metrics.csv`

### support2_real_structure_20

- mapping status: `historical_surrogate_incomplete_library`
- expected SHA-256: `abfa1c5b9ac19e9fd9b0ea05e575d64914caafbf8eed5df2db69fc76b86f323a`
- selected SHA-256: `15dc54a5554430c4cc7bdc37e6c416431ff52200efcfeb261ff35bc75d75ca62`
- selected path: `/Users/sendaatsushi/Documents/pipeline-aware/results_support2_phase4c_full/support2_phase4c_full_20260720_080619/null_reference_model_metrics.csv`

- audit error: `RuntimeError: candidate manifest has no rows for library support2_real_structure_20`

## Trigger audit

### high_dependency_linear_20

- base winner ties: 12 (0.001200)
- trigger threshold: 0.511855555556
- trigger tie mass: 0.000100
- trigger tie probability: 0
- strict / expected activation rate: 0.500000 / 0.500000
- stored threshold match: False
- stored tie-probability match: False

### mixed_realistic_20

- base winner ties: 4 (0.000400)
- trigger threshold: 0.528344444444
- trigger tie mass: 0.000100
- trigger tie probability: 0
- strict / expected activation rate: 0.500000 / 0.500000
- stored threshold match: False
- stored tie-probability match: False

## Separation summary

- high_dependency_linear_20, alpha=0.2: min |q-c|=0.0134833333333, closest=logreg_l1_c01, exact coincidences=0, within-one-spacing=0
- high_dependency_linear_20, alpha=0.1: min |q-c|=0.0262555555556, closest=logreg_l1_c01, exact coincidences=0, within-one-spacing=0
- high_dependency_linear_20, alpha=0.05: min |q-c|=0.0373444444444, closest=logreg_l1_c01, exact coincidences=0, within-one-spacing=0
- high_dependency_linear_20, alpha=0.025: min |q-c|=0.0475888888889, closest=logreg_l1_c01, exact coincidences=0, within-one-spacing=0
- high_dependency_linear_20, alpha=0.01: min |q-c|=0.0573444444444, closest=logreg_l1_c01, exact coincidences=0, within-one-spacing=0
- high_dependency_linear_20, alpha=0.005: min |q-c|=0.0635111111111, closest=linear_svm_c1, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.2: min |q-c|=0.00217777777778, closest=gaussian_nb, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.1: min |q-c|=0.00045, closest=decision_tree, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.05: min |q-c|=0.00913333333333, closest=decision_tree, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.025: min |q-c|=0.0168833333333, closest=decision_tree, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.01: min |q-c|=0.0258833333333, closest=decision_tree, exact coincidences=0, within-one-spacing=0
- mixed_realistic_20, alpha=0.005: min |q-c|=0.0332888888889, closest=decision_tree, exact coincidences=0, within-one-spacing=0

## Adjudication

- exact manifest matches: []
- historical surrogates: ['high_dependency_linear_20', 'mixed_realistic_20', 'support2_real_structure_20']
- missing libraries: []
- exact q_j=c coincidences: 0
- candidate/trigger pairs within one local score spacing: 0
- formal empirical bridge complete: False

Only exact manifest-hash matches can support a formal bridge to the current frozen empirical policy. Historical surrogate banks are descriptive diagnostics and must be labeled as such.
