# D8-A Historical Precision-Scaling Reconstruction Audit

**Status:** PARTIAL_SCALING_EVIDENCE_FOUND
**Scientific simulation run:** no

## Family-level finding

- `reference_only`: 11 formula-level candidate(s) found
- `evaluation_only`: no formula-level candidate found
- `combined`: 26 formula-level candidate(s) found

## Adjudication

Some family scaling evidence was found, but the full precision contract is not recoverable from committed sources.
The runner engine must remain unlocked.

## Python formula candidates

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/check_d8a_final_theory.py` line 38

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
policy_bias = final_policy_bias_approximation(
        population_delta=0.03,
        reference_bias_coefficient=coefficient,
        reference_size=3000,
        evaluation_size=5000,
        retain_interaction=True,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/check_d8a_final_theory.py` line 38

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
final_policy_bias_approximation(
        population_delta=0.03,
        reference_bias_coefficient=coefficient,
        reference_size=3000,
        evaluation_size=5000,
        retain_interaction=True,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 46

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
def combined_bias_approximation(
    delta: float,
    reference_coefficient: float,
    B: int,
    n: int,
    retain_interaction: bool = True,
) -> float:
    if B < 1 or n < 1:
        raise ValueError("sample sizes must be positive")
    value = reference_coefficient / B - delta / n
    if retain_interaction:
        value -= reference_coefficient / (B * n)
    return float(value)
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 55

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
value = reference_coefficient / B - delta / n
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 57

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
value -= reference_coefficient / (B * n)
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 67

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
return exact_conditional_expectation(
        delta + reference_coefficient / B,
        n,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 67

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
exact_conditional_expectation(
        delta + reference_coefficient / B,
        n,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1229

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
def final_policy_bias_approximation(
    population_delta: float,
    reference_bias_coefficient: float,
    reference_size: int,
    evaluation_size: int,
    *,
    retain_interaction: bool = True,
) -> float:
    return combined_bias_approximation(
        population_delta,
        reference_bias_coefficient,
        reference_size,
        evaluation_size,
        retain_interaction=retain_interaction,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1401

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
def tess_second_order_bias_approximation(
    reference_coefficient: float,
    evaluation_coefficient: float,
    reference_size: int,
    evaluation_size: int,
) -> float:
    if reference_size < 1 or evaluation_size < 1:
        raise ValueError(
            "sample sizes must be positive"
        )
    return float(
        reference_coefficient / reference_size
        + evaluation_coefficient / evaluation_size
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1411

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
return float(
        reference_coefficient / reference_size
        + evaluation_coefficient / evaluation_size
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1411

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
float(
        reference_coefficient / reference_size
        + evaluation_coefficient / evaluation_size
    )
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 28

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def second_order_reference_coefficient(
    gradient: FloatArray,
    threshold_bias: FloatArray,
    hessian: FloatArray,
    threshold_covariance: FloatArray,
) -> float:
    g = np.asarray(gradient, dtype=float)
    b = np.asarray(threshold_bias, dtype=float)
    h = np.asarray(hessian, dtype=float)
    s = np.asarray(threshold_covariance, dtype=float)
    d = g.size
    if b.shape != (d,) or h.shape != (d, d) or s.shape != (d, d):
        raise ValueError("shape mismatch")
    if not np.allclose(h, h.T) or not np.allclose(s, s.T):
        raise ValueError("hessian and covariance must be symmetric")
    return float(g @ b + 0.5 * np.trace(h @ s))
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 126

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def uniform_order_statistic_bias(
    reference_size: int,
    probability: float,
) -> float:
    k = quantile_order_index(reference_size, probability)
    return float(k / (reference_size + 1) - probability)
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 134

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def scalar_quantile_bias_coefficient(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    if density_at_quantile <= 0.0:
        raise ValueError("density_at_quantile must be positive")
    lattice = quantile_lattice_offset(
        reference_size,
        probability,
    )
    return float(
        lattice / density_at_quantile
        - probability
        * (1.0 - probability)
        * density_derivative_at_quantile
        / (2.0 * density_at_quantile**3)
    )
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 646

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def scalar_quantile_mean_bias_leading_term(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    coefficient = scalar_quantile_bias_coefficient(
        reference_size,
        probability,
        density_at_quantile,
        density_derivative_at_quantile,
    )
    return float(coefficient / reference_size)
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 658

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
return float(coefficient / reference_size)
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 658

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
float(coefficient / reference_size)
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 681

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def scalar_quantile_taylor_bias_from_exact_beta_moments(
    reference_size: int,
    probability: float,
    density_at_quantile: float,
    density_derivative_at_quantile: float,
) -> float:
    order_index = quantile_order_index(
        reference_size,
        probability,
    )
    mean_shift = (
        beta_order_statistic_mean(
            reference_size,
            order_index,
        )
        - probability
    )
    second_moment = (
        beta_order_statistic_second_central_about_probability(
            reference_size,
            probability,
        )
    )
    return float(
        inverse_cdf_first_derivative(
            density_at_quantile
        )
        * mean_shift
        + 0.5
        * inverse_cdf_second_derivative(
            density_at_quantile,
            density_derivative_at_quantile,
        )
        * second_moment
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1237

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
return combined_bias_approximation(
        population_delta,
        reference_bias_coefficient,
        reference_size,
        evaluation_size,
        retain_interaction=retain_interaction,
    )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1237

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
combined_bias_approximation(
        population_delta,
        reference_bias_coefficient,
        reference_size,
        evaluation_size,
        retain_interaction=retain_interaction,
    )
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 1337

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def tess_reference_bias_coefficient(
    alpha: float,
    adaptive_probability: float,
    comparator_probability: float,
    adaptive_reference_mean_bias: float,
    comparator_reference_mean_bias: float,
    adaptive_reference_variance: float,
    comparator_reference_variance: float,
) -> float:
    return float(
        tess_first_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_reference_mean_bias
        + 0.5
        * tess_second_derivative(
            adaptive_probability,
            alpha,
        )
        * adaptive_reference_variance
        - tess_first_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_reference_mean_bias
        - 0.5
        * tess_second_derivative(
            comparator_probability,
            alpha,
        )
        * comparator_reference_variance
    )
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 31

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def test_reference_coefficient(self) -> None:
        g = np.array([2.0, -1.0])
        b = np.array([0.3, 0.2])
        h = np.array([[1.0, 0.5], [0.5, 2.0]])
        s = np.array([[4.0, 1.0], [1.0, 3.0]])
        expected = float(g @ b + 0.5 * np.trace(h @ s))
        self.assertAlmostEqual(
            second_order_reference_coefficient(g, b, h, s),
            expected,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 47

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
def test_combined_bias_matches_exact_truncated_mean(self) -> None:
        delta, coefficient, B, n = 0.08, -0.6, 1000, 500
        exact_bias = (
            exact_mean_from_truncated_reference_expansion(
                delta, coefficient, B, n
            )
            - delta
        )
        self.assertAlmostEqual(
            combined_bias_approximation(delta, coefficient, B, n, True),
            exact_bias,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 48

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
delta, coefficient, B, n = 0.08, -0.6, 1000, 500
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 49

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
exact_bias = (
            exact_mean_from_truncated_reference_expansion(
                delta, coefficient, B, n
            )
            - delta
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 50

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
exact_mean_from_truncated_reference_expansion(
                delta, coefficient, B, n
            )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 55

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
self.assertAlmostEqual(
            combined_bias_approximation(delta, coefficient, B, n, True),
            exact_bias,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_core.py` line 56

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
combined_bias_approximation(delta, coefficient, B, n, True)
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 41

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
def test_final_policy_bias_retains_interaction(self) -> None:
        delta = 0.03
        coefficient = -0.7
        B, n = 3000, 5000
        observed = final_policy_bias_approximation(
            delta,
            coefficient,
            B,
            n,
            retain_interaction=True,
        )
        expected = (
            coefficient / B
            - delta / n
            - coefficient / (B * n)
        )
        self.assertAlmostEqual(observed, expected)
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 52

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
expected = (
            coefficient / B
            - delta / n
            - coefficient / (B * n)
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 140

Strength: 4 (bias/residual token, reference/B token, evaluation/n token, scaling operator)

```python
def test_tess_total_bias_is_sum_of_rates(self) -> None:
        observed = tess_second_order_bias_approximation(
            reference_coefficient=-0.6,
            evaluation_coefficient=0.2,
            reference_size=3000,
            evaluation_size=5000,
        )
        self.assertAlmostEqual(
            observed,
            -0.6 / 3000 + 0.2 / 5000,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 45

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
observed = final_policy_bias_approximation(
            delta,
            coefficient,
            B,
            n,
            retain_interaction=True,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 45

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
final_policy_bias_approximation(
            delta,
            coefficient,
            B,
            n,
            retain_interaction=True,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 141

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
observed = tess_second_order_bias_approximation(
            reference_coefficient=-0.6,
            evaluation_coefficient=0.2,
            reference_size=3000,
            evaluation_size=5000,
        )
```

### `combined` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_final_theory.py` line 141

Strength: 3 (bias/residual token, reference/B token, evaluation/n token)

```python
tess_second_order_bias_approximation(
            reference_coefficient=-0.6,
            evaluation_coefficient=0.2,
            reference_size=3000,
            evaluation_size=5000,
        )
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_quantile_expansion.py` line 38

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def test_uniform_exact_bias_identity(self) -> None:
        B = 1000
        p = 0.99
        exact = uniform_order_statistic_bias(B, p)
        lattice = quantile_lattice_offset(B, p)
        self.assertAlmostEqual((B + 1) * exact, lattice, places=12)
```

### `reference_only` — `HEAD:theory/policy_search_size/work_package_d8a/tests/test_d8a_scalar_quantile_lemma.py` line 47

Strength: 3 (bias/residual token, reference/B token, scaling operator)

```python
def test_uniform_exact_bias(self) -> None:
        B, p = 1000, 0.99
        exact = uniform_order_statistic_bias(B, p)
        lattice = quantile_lattice_offset(B, p)
        self.assertAlmostEqual(
            exact,
            lattice / (B + 1),
            places=15,
        )
```


## Textual scaling contexts

### `HEAD:theory/policy_search_size/work_package_d8a/D8A_CONFIG_DRAFT.json` line 8

```text
3:     "candidate": "partial_qj Delta=f_j(q_j) beta_j",
4:     "status": "established under stated boundary-differentiation conditions",
5:     "trigger": "partial_c Delta=f_T(c) beta_c"
6:   },
7:   "deterministic_second_order_stochastic_remainder_assumed": false,
8:   "exact_identity": "E_E(delta_hat|theta_hat)=(1-1/n)Delta(theta_hat)",
9:   "final_policy_bias_theorem": {
10:     "formula": "E(delta_hat)-delta=C_delta,B/B-delta/n-C_delta,B/(Bn)+o(B^-1+n^-1)",
11:     "status": "proved"
12:   },
13:   "gaussian_hessian_preflight": "PASS",
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_coincidence_repair.py` line 65

```text
60:     print(
61:         "Positive-part-square coefficient: "
62:         f"{gaussian_cell_branch_kink_coefficient(threshold):.12f}"
63:     )
64:     print(
65:         "Directional expansion normalized error: "
66:         f"{abs(exact-approx)/local_step**2:.3e}"
67:     )
68:     print(
69:         "Ordinary C2 theorem at candidate coincidence: NO"
70:     )
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_generalized_policy_theorem.py` line 22

```text
17:     components = gaussian_toy_policy_local_components(
18:         threshold,
19:         trigger,
20:     )
21:
22:     maximum_normalized_error = 0.0
23:     for direction in (
24:         np.array([1.1, -0.7, 0.3]),
25:         np.array([-0.8, 1.2, -0.2]),
26:         np.array([0.6, 0.6, 0.1]),
27:     ):
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_generalized_policy_theorem.py` line 41

```text
36:             trigger,
37:             step * direction[0],
38:             step * direction[1],
39:             step * direction[2],
40:         )
41:         maximum_normalized_error = max(
42:             maximum_normalized_error,
43:             abs(exact - approx) / step**2,
44:         )
45:
46:     covariance = np.array(
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_generalized_policy_theorem.py` line 42

```text
37:             step * direction[0],
38:             step * direction[1],
39:             step * direction[2],
40:         )
41:         maximum_normalized_error = max(
42:             maximum_normalized_error,
43:             abs(exact - approx) / step**2,
44:         )
45:
46:     covariance = np.array(
47:         [
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_generalized_policy_theorem.py` line 67

```text
62:     print("=" * 80)
63:     print("D8-A generalized policy theorem preflight")
64:     print("=" * 80)
65:     print("Status: PASS")
66:     print(
67:         "Maximum directional normalized error: "
68:         f"{maximum_normalized_error:.3e}"
69:     )
70:     print(
71:         "Synthetic generalized expectation coefficient: "
72:         f"{coefficient:.10f}"
```

### `HEAD:theory/policy_search_size/work_package_d8a/coincidence_repair/check_d8a_generalized_policy_theorem.py` line 68

```text
63:     print("D8-A generalized policy theorem preflight")
64:     print("=" * 80)
65:     print("Status: PASS")
66:     print(
67:         "Maximum directional normalized error: "
68:         f"{maximum_normalized_error:.3e}"
69:     )
70:     print(
71:         "Synthetic generalized expectation coefficient: "
72:         f"{coefficient:.10f}"
73:     )
```

### `HEAD:theory/policy_search_size/work_package_d8a/d8a_core.py` line 57

```text
52: ) -> float:
53:     if B < 1 or n < 1:
54:         raise ValueError("sample sizes must be positive")
55:     value = reference_coefficient / B - delta / n
56:     if retain_interaction:
57:         value -= reference_coefficient / (B * n)
58:     return float(value)
59:
60:
61: def exact_mean_from_truncated_reference_expansion(
62:     delta: float,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_ACCEPTANCE_CRITERIA.md` line 36

```text
31: =
32: \frac{
33: \left[
34: |B\{\widehat{\operatorname{Bias}}_R-C_B/B\}|
35: -
36: z_\star B\,\operatorname{MCSE}
37: \right]_+
38: }{
39: 1+|C_B|
40: }.
41: \]
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_ACCEPTANCE_CRITERIA.md` line 52

```text
47:
48: The median must improve by at least 40% from \(B=500\) to \(B=10{,}000\).
49:
50: ## Combined policy approximation
51:
52: The MCSE-adjusted absolute residual is divided by
53:
54: \[
55: (B^{-1}+n^{-1})
56: (1+|C_{\Delta,B}|+|\Delta_\pi|).
57: \]
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_ACCEPTANCE_CRITERIA.md` line 87

```text
82: baseline.
83:
84: ## Precision limitation
85:
86: No more than 10% of primary cells may reach the maximum replicate count
87: without meeting the locked MCSE target.
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 6

```text
1: {
2:   "acceptance": {
3:     "combined_policy_approximation": {
4:       "largest_pair_median_maximum": 0.15,
5:       "largest_pair_p90_maximum": 0.4,
6:       "metric": "MCSE-adjusted absolute residual divided by (1/B+1/n)*(1+|C_Delta,B|+|Delta_pi|)"
7:     },
8:     "exact_evaluation_identity": {
9:       "familywise_alpha": 0.01,
10:       "method": "Bonferroni simultaneous Monte Carlo z check",
11:       "required": true
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 22

```text
17:       "all correlation matrices positive definite",
18:       "all cells satisfy latent separation >=0.10",
19:       "Hessian symmetry error <=1e-8",
20:       "independent Hessian methods relative discrepancy <=1e-5",
21:       "reference and evaluation streams independent",
22:       "quantile convention exactly k_B=ceil(B*p)"
23:     ],
24:     "interpretation": "Failure of an asymptotic usefulness threshold is not automatically a contradiction of the theorem; fatal exact identity or implementation failures are adjudicated separately.",
25:     "reference_approximation": {
26:       "largest_B_median_maximum": 0.15,
27:       "largest_B_p90_maximum": 0.4,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 29

```text
24:     "interpretation": "Failure of an asymptotic usefulness threshold is not automatically a contradiction of the theorem; fatal exact identity or implementation failures are adjudicated separately.",
25:     "reference_approximation": {
26:       "largest_B_median_maximum": 0.15,
27:       "largest_B_p90_maximum": 0.4,
28:       "median_improvement_from_B500_to_B10000_minimum": 0.4,
29:       "metric": "MCSE-adjusted |B*(bias-C_B/B)|/(1+|C_B|)"
30:     },
31:     "second_order_improvement": {
32:       "comparison": "absolute bias residual versus first-order-only baseline",
33:       "minimum_fraction_improved_primary_cells": 0.75
34:     },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 38

```text
33:       "minimum_fraction_improved_primary_cells": 0.75
34:     },
35:     "tess_approximation": {
36:       "largest_pair_median_maximum": 0.25,
37:       "largest_pair_p90_maximum": 0.6,
38:       "metric": "MCSE-adjusted absolute residual divided by (1/B+1/n)*(1+|C_S,R,B|+|C_S,E|)"
39:     }
40:   },
41:   "cell_registry": {
42:     "diagnostic_cells": 41,
43:     "latent_separation_minimum": 0.1,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 52

```text
47:     "total_cells": 75
48:   },
49:   "experiments": {
50:     "combined": {
51:       "input_randomness": "independent reference and evaluation banks",
52:       "policy_prediction": "C_Delta,B/B-Delta_pi/n-C_Delta,B/(B*n)",
53:       "tess_prediction": "C_S,R,B/B+C_S,E/n"
54:     },
55:     "evaluation_only": {
56:       "input_randomness": "evaluation bank at population thresholds",
57:       "policy_mean_identity": "E(delta_hat)=(1-1/n)*Delta_pi",
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 57

```text
52:       "policy_prediction": "C_Delta,B/B-Delta_pi/n-C_Delta,B/(B*n)",
53:       "tess_prediction": "C_S,R,B/B+C_S,E/n"
54:     },
55:     "evaluation_only": {
56:       "input_randomness": "evaluation bank at population thresholds",
57:       "policy_mean_identity": "E(delta_hat)=(1-1/n)*Delta_pi",
58:       "targets": [
59:         "policy covariance estimator",
60:         "adaptive rejection estimator",
61:         "comparator product estimator",
62:         "TESS contrast"
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_DESIGN.json` line 213

```text
208:     "comparator_estimator": "mean(R0)+mean(A)*mean(M)",
209:     "full_rejection": "R1=I(X[J1]>q[J1])",
210:     "full_winner": "argmax over candidate_pool_full",
211:     "incremental": "M=(1-R0)*R1",
212:     "policy_contrast": "Delta_pi=Cov(A,M)",
213:     "quantile_convention": "k_B=ceil(B*p)",
214:     "threshold_dimension": 4
215:   },
216:   "tess": {
217:     "alpha_values": [
218:       0.01,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/D8A_NUMERICAL_VALIDATION_PROTOCOL.md` line 112

```text
107: Population thresholds are fixed. This verifies the exact covariance identity
108:
109: \[
110: E(\widehat\Delta_\pi)
111: =
112: (1-1/n)\Delta_\pi
113: \]
114:
115: and the \(n^{-1}\) TESS expansion.
116:
117: ### Combined
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/check_d8a_numerical_design.py` line 67

```text
62:     print(f"Diagnostic cells: {diagnostic}")
63:     print(
64:         "Minimum latent separation: "
65:         f"{min(cell['latent_separation'] for cell in registry):.12f}"
66:     )
67:     print("Quantile convention locked: k_B=ceil(B*p)")
68:     print("Reference/evaluation streams independent: YES")
69:     print("Effect-dependent stopping allowed: NO")
70:     print("Post-hoc cell deletion allowed: NO")
71:     print("Scientific numerical design locked: YES")
72:     print("Scientific simulation run: NO")
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_ACCEPTANCE_CRITERIA.md` line 40

```text
35: Replace the historical ordinary-Hessian coefficient by
36: \(C_{\Delta,B}^{\mathrm{gen}}\).
37:
38: At \(B=10{,}000\), over the 17 primary equivalence classes:
39:
40: - median normalized residual at most \(0.15\);
41: - 90th percentile at most \(0.40\);
42: - median improvement from \(B=500\) to \(B=10{,}000\) at least 40%.
43:
44: ## Combined policy approximation
45:
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_ACCEPTANCE_CRITERIA.md` line 48

```text
43:
44: ## Combined policy approximation
45:
46: At \((B,n)=(10{,}000,10{,}000)\), over the 17 primary classes:
47:
48: - median normalized residual at most \(0.15\);
49: - 90th percentile at most \(0.40\).
50:
51: The approximation is
52:
53: \[
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_ACCEPTANCE_CRITERIA.md` line 67

```text
62:
63: Use \(C_{S,R,B}^{\mathrm{gen}}\) and the unchanged \(C_{S,E}\).
64:
65: At the largest pair:
66:
67: - median normalized residual at most \(0.25\);
68: - 90th percentile at most \(0.60\).
69:
70: ## Improvement reporting
71:
72: The generalized approximation is compared with:
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_ACCEPTANCE_CRITERIA.md` line 88

```text
83: be smaller than Monte Carlo resolution in some cells.
84:
85: ## Precision limitation
86:
87: No more than 10% of the 17 primary equivalence classes may reach the maximum
88: replicate count without meeting the locked MCSE target.
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_DESIGN.json` line 75

```text
70:   },
71:   "ordinary_hessian_coefficient_allowed": false,
72:   "parent_theory_tag": "d8a-generalized-theory-repair-v1",
73:   "primary_acceptance_denominator": 17,
74:   "primary_scientific_classes": 17,
75:   "quantile_convention": "k_B=ceil(B*p)",
76:   "reference_B": [
77:     250,
78:     500,
79:     1000,
80:     3000,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/D8A_GENERALIZED_ORACLE_CONTRACT.md` line 118

```text
113: ## Tolerances
114:
115: - deterministic probability absolute tolerance: \(10^{-10}\);
116: - coefficient relative tolerance: \(10^{-8}\);
117: - transformation-invariance absolute tolerance: \(10^{-10}\);
118: - directional expansion normalized-error target: \(10^{-4}\);
119: - contrast variance positivity floor: \(10^{-12}\).
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/D8A_IMPLEMENTATION_LOCK.md` line 43

```text
38:
39: ## Final engineering evidence
40:
41: - engineering unit tests: 55/55 PASS;
42: - scientific equivalence classes audited: 25/25;
43: - maximum analytic directional normalized error at radius 0.002:
44:   \(4.4624\times10^{-5}\);
45: - maximum full-oracle directional normalized error:
46:   \(2.2298\times10^{-5}\);
47: - maximum kink-identity error:
48:   \(2.2205\times10^{-16}\);
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/D8A_IMPLEMENTATION_LOCK.md` line 45

```text
40:
41: - engineering unit tests: 55/55 PASS;
42: - scientific equivalence classes audited: 25/25;
43: - maximum analytic directional normalized error at radius 0.002:
44:   \(4.4624\times10^{-5}\);
45: - maximum full-oracle directional normalized error:
46:   \(2.2298\times10^{-5}\);
47: - maximum kink-identity error:
48:   \(2.2205\times10^{-16}\);
49: - maximum derivative-step discrepancy: \(0\);
50: - maximum covariance negative part: \(0\);
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/analytic_radius_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_analytic_radius_diagnostic.csv` line 1

```text
1: label,class_id,class_role,dependence,candidate_probability,trigger_probability,target,direction_index,radius,exact,approximation,normalized_error
2: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,delta_pi,0,0.004,0.0017283559069805055,0.0017283565079135664,3.755831630674732e-05
3: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,delta_pi,0,0.002,0.0017084177197159156,0.0017084177938524335,1.853412947205521e-05
4: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,delta_pi,0,0.001,0.0016983694914443348,0.0016983695002425019,8.798167056012218e-06
5: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,delta_pi,0,0.0005,0.0016933256184257506,0.0016933256192926951,3.4677781479697245e-06
6: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,delta_pi,1,0.004,0.0016976362830769254,0.0016976356173362597,4.1608791607507245e-05
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/analytic_radius_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_analytic_radius_diagnostic_summary.json` line 6

```text
1: {
2:   "classes_audited": 25,
3:   "direction_count": 4,
4:   "implementation_lock_created": false,
5:   "label": "NON_SCIENTIFIC_ENGINEERING_ONLY",
6:   "maximum_normalized_error_by_radius": {
7:     "0.000500": 0.0007805988078146697,
8:     "0.001000": 0.0003919007618424786,
9:     "0.002000": 0.00019921482519169587,
10:     "0.004000": 0.00010876150327576717
11:   },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/full_oracle_audit/NON_SCIENTIFIC_ENGINEERING_ONLY_full_oracle_audit.csv` line 1

```text
1: label,class_id,class_role,dependence,candidate_probability,trigger_probability,minimum_covariance_eigenvalue,maximum_kink_identity_error,maximum_step_discrepancy,maximum_directional_normalized_error,transform_invariance_pass,all_values_finite,delta_generalized_coefficient,tess_reference_alpha_0.01,tess_evaluation_alpha_0.01,tess_reference_alpha_0.05,tess_evaluation_alpha_0.05
2: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-000,diagnostic,asymmetric,0.9,0.5,1.0199569433079685,8.326672684688674e-17,0.0,1.4824752536668484e-05,True,True,-0.13002903780359143,-16.86464725373041,0.2941932295372407,-3.3044352283202185,0.05764380701180194
3: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-001,diagnostic,asymmetric,0.9,0.7,0.7442572495805354,7.979727989493313e-17,0.0,1.2974621377281892e-05,True,True,-0.20575586990900852,-27.57448448138811,0.048283423151833205,-5.402905649444449,0.009460585923107612
4: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-002,diagnostic,asymmetric,0.95,0.5,1.1921369220544844,0.0,0.0,1.3362755346690847e-05,True,True,-0.0348377109336643,-2.945341706414765,0.16086593999019438,-0.577106105315365,0.031519845695134
5: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-003,diagnostic,asymmetric,0.95,0.7,1.1236728284656783,1.3877787807814457e-17,0.0,1.6018686377350377e-05,True,True,-0.09587241541429176,-10.439210184875698,0.08201564056441413,-2.045444139551277,0.016070029089660043
6: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-004,diagnostic,asymmetric,0.95,0.85,0.8752880244658244,7.45931094670027e-17,0.0,1.673715332994874e-05,True,True,-0.15844532150864973,-18.023101309549,-0.0005592788946042759,-3.531421084285304,-0.00010958431884078301
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/full_oracle_audit/NON_SCIENTIFIC_ENGINEERING_ONLY_full_oracle_audit_summary.json` line 8

```text
3:   "all_values_finite": true,
4:   "classes_audited": 25,
5:   "implementation_lock_created": false,
6:   "label": "NON_SCIENTIFIC_ENGINEERING_ONLY",
7:   "maximum_covariance_negative_part": 0.0,
8:   "maximum_directional_normalized_error": 2.2297858004449722e-05,
9:   "maximum_kink_identity_error": 2.220446049250313e-16,
10:   "maximum_step_discrepancy": 0.0,
11:   "results_file": "NON_SCIENTIFIC_ENGINEERING_ONLY_full_oracle_audit.csv",
12:   "scientific_execution_authorized": false,
13:   "scientific_simulation_run": false
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 18

```text
13:     "inferred_gradient_gap": 3.9049938276161687e-07,
14:     "rows": [
15:       {
16:         "approximation": 0.21979581890201308,
17:         "exact": 0.21979581457466052,
18:         "normalized_error": 6.761488374404379e-05,
19:         "radius": 0.008,
20:         "residual": -4.327352559618802e-09,
21:         "residual_over_signed_radius": -5.409190699523503e-07,
22:         "sign": 1
23:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 27

```text
22:         "sign": 1
23:       },
24:       {
25:         "approximation": 0.22039694847800773,
26:         "exact": 0.22039694677612742,
27:         "normalized_error": 0.00010636751895942709,
28:         "radius": 0.004,
29:         "residual": -1.7018803033508334e-09,
30:         "residual_over_signed_radius": -4.2547007583770835e-07,
31:         "sign": 1
32:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 36

```text
31:         "sign": 1
32:       },
33:       {
34:         "approximation": 0.22069823378648804,
35:         "exact": 0.22069823298962873,
36:         "normalized_error": 0.00019921482519169587,
37:         "radius": 0.002,
38:         "residual": -7.968593007667835e-10,
39:         "residual_over_signed_radius": -3.9842965038339173e-07,
40:         "sign": 1
41:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 45

```text
40:         "sign": 1
41:       },
42:       {
43:         "approximation": 0.22084905657084894,
44:         "exact": 0.22084905617894818,
45:         "normalized_error": 0.0003919007618424786,
46:         "radius": 0.001,
47:         "residual": -3.9190076184247857e-10,
48:         "residual_over_signed_radius": -3.9190076184247857e-07,
49:         "sign": 1
50:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 54

```text
49:         "sign": 1
50:       },
51:       {
52:         "approximation": 0.2209245129955596,
53:         "exact": 0.2209245128004099,
54:         "normalized_error": 0.0007805988078146697,
55:         "radius": 0.0005,
56:         "residual": -1.9514970195366743e-10,
57:         "residual_over_signed_radius": -3.9029940390733486e-07,
58:         "sign": 1
59:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 63

```text
58:         "sign": 1
59:       },
60:       {
61:         "approximation": 0.22221581281872357,
62:         "exact": 0.22221581253331937,
63:         "normalized_error": 4.459440629267508e-06,
64:         "radius": 0.008,
65:         "residual": -2.854042002731205e-10,
66:         "residual_over_signed_radius": 3.5675525034140065e-08,
67:         "sign": -1
68:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 72

```text
67:         "sign": -1
68:       },
69:       {
70:         "approximation": 0.221605958615112,
71:         "exact": 0.22160595860028903,
72:         "normalized_error": 9.264360112393177e-07,
73:         "radius": 0.004,
74:         "residual": -1.4822976179829084e-11,
75:         "residual_over_signed_radius": 3.705744044957271e-09,
76:         "sign": -1
77:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 81

```text
76:         "sign": -1
77:       },
78:       {
79:         "approximation": 0.22130249214972744,
80:         "exact": 0.22130249215531111,
81:         "normalized_error": 1.3959181033307289e-06,
82:         "radius": 0.002,
83:         "residual": 5.5836724133229154e-12,
84:         "residual_over_signed_radius": -2.7918362066614577e-09,
85:         "sign": -1
86:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 90

```text
85:         "sign": -1
86:       },
87:       {
88:         "approximation": 0.22115112407614046,
89:         "exact": 0.22115112408037083,
90:         "normalized_error": 4.230366057456081e-06,
91:         "radius": 0.001,
92:         "residual": 4.230366057456081e-12,
93:         "residual_over_signed_radius": -4.230366057456081e-09,
94:         "sign": -1
95:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 99

```text
94:         "sign": -1
95:       },
96:       {
97:         "approximation": 0.2210755313291233,
98:         "exact": 0.2210755313314068,
99:         "normalized_error": 9.134026868196088e-06,
100:         "radius": 0.0005,
101:         "residual": 2.283506717049022e-12,
102:         "residual_over_signed_radius": -4.567013434098044e-09,
103:         "sign": -1
104:       }
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 128

```text
123:     "inferred_gradient_gap": 4.087381168820958e-09,
124:     "rows": [
125:       {
126:         "approximation": 0.21979581946005627,
127:         "exact": 0.21979581822306132,
128:         "normalized_error": 1.9328046108046948e-05,
129:         "radius": 0.008,
130:         "residual": -1.2369949509150047e-09,
131:         "residual_over_signed_radius": -1.5462436886437558e-07,
132:         "sign": 1
133:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 137

```text
132:         "sign": 1
133:       },
134:       {
135:         "approximation": 0.22039694903605092,
136:         "exact": 0.2203969488796137,
137:         "normalized_error": 9.777326517856899e-06,
138:         "radius": 0.004,
139:         "residual": -1.5643722428571039e-10,
140:         "residual_over_signed_radius": -3.9109306071427596e-08,
141:         "sign": 1
142:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 146

```text
141:         "sign": 1
142:       },
143:       {
144:         "approximation": 0.22069823434453123,
145:         "exact": 0.22069823432044858,
146:         "normalized_error": 6.020663134709281e-06,
147:         "radius": 0.002,
148:         "residual": -2.4082652538837124e-11,
149:         "residual_over_signed_radius": -1.2041326269418562e-08,
150:         "sign": 1
151:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 155

```text
150:         "sign": 1
151:       },
152:       {
153:         "approximation": 0.22084905712889213,
154:         "exact": 0.22084905712339195,
155:         "normalized_error": 5.500183641871104e-06,
156:         "radius": 0.001,
157:         "residual": -5.500183641871104e-12,
158:         "residual_over_signed_radius": -5.500183641871104e-09,
159:         "sign": 1
160:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 164

```text
159:         "sign": 1
160:       },
161:       {
162:         "approximation": 0.2209245135536028,
163:         "exact": 0.2209245135516563,
164:         "normalized_error": 7.785994071696223e-06,
165:         "radius": 0.0005,
166:         "residual": -1.9464985179240557e-12,
167:         "residual_over_signed_radius": -3.892997035848111e-09,
168:         "sign": 1
169:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 173

```text
168:         "sign": 1
169:       },
170:       {
171:         "approximation": 0.22221581337676677,
172:         "exact": 0.22221581308086838,
173:         "normalized_error": 4.623412330068133e-06,
174:         "radius": 0.008,
175:         "residual": -2.958983891243605e-10,
176:         "residual_over_signed_radius": 3.698729864054506e-08,
177:         "sign": -1
178:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 182

```text
177:         "sign": -1
178:       },
179:       {
180:         "approximation": 0.2216059591731552,
181:         "exact": 0.2216059591530808,
182:         "normalized_error": 1.2546508970645576e-06,
183:         "radius": 0.004,
184:         "residual": -2.007441435303292e-11,
185:         "residual_over_signed_radius": 5.01860358825823e-09,
186:         "sign": -1
187:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 191

```text
186:         "sign": -1
187:       },
188:       {
189:         "approximation": 0.22130249270777064,
190:         "exact": 0.22130249271072763,
191:         "normalized_error": 7.392489398405644e-07,
192:         "radius": 0.002,
193:         "residual": 2.9569957593622576e-12,
194:         "residual_over_signed_radius": -1.4784978796811288e-09,
195:         "sign": -1
196:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 200

```text
195:         "sign": -1
196:       },
197:       {
198:         "approximation": 0.22115112463418365,
199:         "exact": 0.22115112463710043,
200:         "normalized_error": 2.9167779302952113e-06,
201:         "radius": 0.001,
202:         "residual": 2.9167779302952113e-12,
203:         "residual_over_signed_radius": -2.9167779302952113e-09,
204:         "sign": -1
205:       },
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/gradient_quadrature_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_gradient_quadrature_diagnostic_summary.json` line 209

```text
204:         "sign": -1
205:       },
206:       {
207:         "approximation": 0.2210755318871665,
208:         "exact": 0.22107553188879314,
209:         "normalized_error": 6.506573058118192e-06,
210:         "radius": 0.0005,
211:         "residual": 1.6266432645295481e-12,
212:         "residual_over_signed_radius": -3.2532865290590962e-09,
213:         "sign": -1
214:       }
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/oracle_tolerance_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_directional_radius_diagnostic.csv` line 1

```text
1: label,class_id,target,direction_index,radius,exact,approximation,normalized_error
2: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-017,delta_pi,0,0.002,-0.01331189439295305,-0.013311894294073158,2.4719973030357112e-05
3: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-017,delta_pi,0,0.001,-0.013305907729286914,-0.013305907643578776,8.570813850306003e-05
4: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-017,delta_pi,0,0.0005,-0.013302944049228743,-0.013302943994802361,0.0002177055272167827
5: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-017,delta_pi,0,0.00025,-0.01330146961995085,-0.01330146958953185,0.0004867040104272746
6: NON_SCIENTIFIC_ENGINEERING_ONLY,d8a-generalized-class-017,delta_pi,1,0.002,-0.013280964641899762,-0.013280964592401677,1.2374521112662462e-05
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/run_d8a_full_oracle_audit.py` line 356

```text
351:                     class_max_kink_identity
352:                 ),
353:                 "maximum_step_discrepancy": (
354:                     class_max_step
355:                 ),
356:                 "maximum_directional_normalized_error": (
357:                     class_max_directional
358:                 ),
359:                 "transform_invariance_pass": (
360:                     transform_audit["passed"]
361:                 ),
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/run_d8a_full_oracle_audit.py` line 409

```text
404:             maximum_kink_identity_error
405:         ),
406:         "maximum_step_discrepancy": (
407:             maximum_step_discrepancy
408:         ),
409:         "maximum_directional_normalized_error": (
410:             maximum_directional_error
411:         ),
412:         "implementation_lock_created": False,
413:         "scientific_execution_authorized": False,
414:         "results_file": csv_path.name,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/targeted_gradient_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_targeted_gradient_diagnostic.csv` line 1

```text
1: label,backend,qmc_points,radius,estimated_integration_error_sum,baseline,plus,minus,plus_normalized_residual,minus_normalized_residual,corrected_central_gradient,analytic_directional_gradient,directional_gradient_difference,observed_symmetric_quadratic,predicted_symmetric_quadratic,symmetric_quadratic_difference
2: NON_SCIENTIFIC_ENGINEERING_ONLY,fixed_genz,0,0.008,0.0,0.22099999944195703,0.21979581457466052,0.22221581253331937,6.761488417772465e-05,4.459440629267508e-06,-0.15100316710344455,-0.15100291448167136,-2.5262177319462786e-07,0.09084550051455254,0.09088153767673204,-3.6037162179508586e-05
3: NON_SCIENTIFIC_ENGINEERING_ONLY,fixed_genz,0,0.004,0.0,0.22099999944195703,0.22039694677612742,0.22160595860028903,0.00010636751895942709,9.264360112393177e-07,-0.15100312536383434,-0.15100291448167136,-2.108821629820401e-07,0.09082789069990438,0.09088153767673204,-5.364697682766484e-05
4: NON_SCIENTIFIC_ENGINEERING_ONLY,fixed_genz,0,0.002,0.0,0.22099999944195703,0.22069823298962873,0.22130249215531111,0.00019921482519169587,1.3959181033307289e-06,-0.15100311509241165,-0.15100291448167136,-2.0061074029742443e-07,0.09078262822037608,0.09088153767673204,-9.890945635596116e-05
5: NON_SCIENTIFIC_ENGINEERING_ONLY,fixed_genz,0,0.001,0.0,0.22099999944195703,0.22084905617894818,0.22115112408037083,0.0003919007618424786,4.230366057456081e-06,-0.15100311254723225,-0.15100291448167136,-1.98065560896854e-07,0.09068770245868052,0.09088153767673204,-0.0001938352180515246
6: NON_SCIENTIFIC_ENGINEERING_ONLY,scipy_qmvnt,20000,0.008,2.1902529535146548e-05,0.22100027403236416,0.21979602691994338,0.22221607999719412,0.0010401949510074893,0.0001158115092540768,-0.15100661201543739,-0.15100291448167136,-3.697533766028327e-06,0.09030353444660841,0.09088153767673204,-0.000578003230123636
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/targeted_gradient_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_targeted_gradient_diagnostic_summary.json` line 7

```text
2:   "adjudication": "ANALYTIC_GRADIENT_SUPPORTED",
3:   "backend_summaries": {
4:     "fixed_genz": {
5:       "maximum_absolute_gradient_difference": 2.5262177319462786e-07,
6:       "maximum_absolute_symmetric_quadratic_difference": 0.0001938352180515246,
7:       "maximum_plus_normalized_residual": 0.0003919007618424786,
8:       "rows_used": 4
9:     },
10:     "scipy_qmvnt": {
11:       "maximum_absolute_gradient_difference": 6.929095103247462e-08,
12:       "maximum_absolute_symmetric_quadratic_difference": 6.876364127259005e-05,
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/implementation_v1/targeted_gradient_diagnostic/NON_SCIENTIFIC_ENGINEERING_ONLY_targeted_gradient_diagnostic_summary.json` line 13

```text
8:       "rows_used": 4
9:     },
10:     "scipy_qmvnt": {
11:       "maximum_absolute_gradient_difference": 6.929095103247462e-08,
12:       "maximum_absolute_symmetric_quadratic_difference": 6.876364127259005e-05,
13:       "maximum_plus_normalized_residual": 0.0001380545955331769,
14:       "rows_used": 4
15:     }
16:   },
17:   "class_id": "d8a-generalized-class-016",
18:   "class_record": {
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/scientific_run_prelock_v1/D8A_SCIENTIFIC_RUN_CONFIG.json` line 68

```text
63:     "nested_common_random_numbers_across_sizes": true,
64:     "precision_limited_fraction_maximum": 0.1,
65:     "precision_stopping_only": true,
66:     "primary_maximum_replicates": 20000,
67:     "primary_minimum_replicates": 2000,
68:     "primary_scaled_mcse_target": 0.03,
69:     "raw_bank_storage": false,
70:     "reference_evaluation_streams_independent": true,
71:     "streaming_required": true
72:   },
73:   "output_root_relative_to_repo": "theory/policy_search_size/work_package_d8a/numerical_validation/scientific_runs/d8a_generalized_scientific_run_v1",
```

### `HEAD:theory/policy_search_size/work_package_d8a/numerical_validation/generalized_readjudication_v1/tests/test_d8a_generalized_design.py` line 143

```text
138:         )
139:
140:     def test_quantile_convention_is_unchanged(self) -> None:
141:         self.assertEqual(
142:             CONFIG["quantile_convention"],
143:             "k_B=ceil(B*p)",
144:         )
145:
146:     def test_sample_grids_are_preserved(self) -> None:
147:         self.assertEqual(
148:             CONFIG["reference_B"],
```


## Guardrails

- current uncommitted runner engine excluded: yes
- scientific-run output excluded: yes
- duplicated historical file contents de-duplicated: yes
- target constants alone treated as formulas: no
