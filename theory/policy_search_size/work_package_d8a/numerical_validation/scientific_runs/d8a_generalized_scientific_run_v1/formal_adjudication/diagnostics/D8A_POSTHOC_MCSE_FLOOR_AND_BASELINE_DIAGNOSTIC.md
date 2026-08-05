# D8-A Post-hoc MCSE-floor and Baseline Diagnostic

- Diagnostic ID: `TESS_D8A_POSTHOC_MCSE_FLOOR_AND_BASELINE_DIAGNOSTIC_V2`
- Formal status retained: **PASS**
- Prospective criteria changed: no
- Scientific simulation rerun: no

## MCSE-floor diagnostics

### reference_B500

- records: 17
- adjusted-zero fraction: 1
- raw normalized median / p90 / max: 0.0048534 / 0.0183308 / 0.0430574
- |raw residual| / MCSE median / p90 / max: 0.628251 / 2.84815 / 4.05921

### reference_B10000

- records: 17
- adjusted-zero fraction: 1
- raw normalized median / p90 / max: 0.0354857 / 0.0958359 / 0.112979
- |raw residual| / MCSE median / p90 / max: 0.92133 / 1.77053 / 2.48403

### combined_policy

- records: 17
- adjusted-zero fraction: 1
- raw normalized median / p90 / max: 0.0494954 / 0.147439 / 0.225355
- |raw residual| / MCSE median / p90 / max: 0.768496 / 1.54093 / 2.0807

### combined_tess_alpha_0.01

- records: 17
- adjusted-zero fraction: 1
- raw normalized median / p90 / max: 0.52876 / 1.46115 / 4.9071
- |raw residual| / MCSE median / p90 / max: 0.739142 / 1.5437 / 2.15354

### combined_tess_alpha_0.05

- records: 17
- adjusted-zero fraction: 1
- raw normalized median / p90 / max: 0.407284 / 0.889135 / 2.81378
- |raw residual| / MCSE median / p90 / max: 0.739142 / 1.5437 / 2.15354

## Baseline interpretations at B=10,000

- generalized better than no correction: 15/17
- generalized better than gradient-only: 14/17
- generalized better than smooth-only: 9/17
- gradient-only better than no correction: 16/17
- smooth-only better than no correction: 15/17

## Interpretation

A zero adjusted residual means that the raw approximation residual is contained within the prospectively locked simultaneous Monte Carlo uncertainty allowance. It does not mean that the raw residual itself is zero.
