# D8-A Second-Derivative Sufficient Conditions

## Proposed assumptions

### D8A-S1: finite pools

The base and expanded candidate pools are fixed and finite.

### D8A-S2: continuous unique winners

The complete score vector has a joint density and base/full winner ties have
probability zero.

### D8A-S3: strict threshold separation

\[
\min_{j\in\mathcal J_0}|q_j-c|>0.
\]

### D8A-S4: local density smoothness

The joint score density has two locally integrable derivatives in a
neighborhood of every candidate and trigger boundary relevant to the policy.

### D8A-S5: positive boundary densities

Candidate marginal densities and the base-maximum density are positive at
their population thresholds.

### D8A-S6: dominated boundary traces

The boundary densities, conditional winner probabilities, conditional jump
fields, and their first threshold derivatives admit locally integrable
dominating functions.

### D8A-S7: codimension-two regularity

Pairwise intersections of moving threshold faces and winner boundaries admit
finite iterated traces, and no positive-probability mass is concentrated on
those intersections.

## Proposed theorem target

Under D8A-S1--S7, the map

\[
\theta\mapsto\Delta_\pi(\theta)
\]

is twice continuously differentiable in a neighborhood of the population
threshold vector.

Its gradient is the D7 boundary-gradient vector, and its Hessian consists of
candidate-candidate, candidate-trigger, and trigger-trigger iterated boundary
terms.

## What is still missing

This memo states sufficient conditions and the proof architecture. It does
not yet supply a complete measure-theoretic boundary-differentiation proof.

A final theorem will require either:

- an explicit repeated Leibniz/coarea argument on every winner cell; or
- a general moving-boundary differentiation lemma whose assumptions are
  verified for the D7 policy regions.
