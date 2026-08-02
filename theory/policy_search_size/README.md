# Policy-Level Search Size Theory Reproduction

This directory contains repository-ready numerical verification for Work Packages A and B.

## What is reproduced

### Work Package A
- sharp same-rate two-candidate rejection envelopes;
- Monte Carlo verification of the exact formulas;
- fixed expected-candidate-budget divergence construction;
- the corresponding figure and machine-readable tables.

### Work Package B
- threshold-coherent policy ordering;
- exact single-crossing and arbitrary finite-crossing constructions;
- Monte Carlo verification of the single-crossing construction;
- the corresponding figures and machine-readable tables.

The numerical calculations are checks of exact constructions. They are not substitutes for the mathematical proofs in the theory memos.

## Requirements

Python 3.10 or later with:

```bash
python3 -m pip install numpy pandas matplotlib
```

## Run everything

From the repository root:

```bash
bash theory/policy_search_size/run_all.sh
```

The scripts write only inside:

- `work_package_a/results/`
- `work_package_b/results/`

Each work package records:
- a validation summary;
- Python and package versions;
- deterministic seeds;
- generated CSV and figure files.

The top-level runner then creates:

```text
REPRODUCTION_MANIFEST_SHA256.json
```

containing SHA-256 hashes for the source and generated files.

## Pass criteria

- Work Package A: maximum Monte Carlo absolute rejection-probability error <= 0.0025.
- Work Package B: maximum Monte Carlo absolute rejection-probability error <= 0.0020.
- Exact crossing and ordering assertions must pass.
- Any failed assertion terminates the runner with a nonzero exit status.

## Git policy

Run the scripts locally before committing. Track the source memos, verification scripts, validation summaries, environment files, CSV results, figures, and final SHA-256 manifest. Keep the empirical `ess-study` manuscript frozen separately.
