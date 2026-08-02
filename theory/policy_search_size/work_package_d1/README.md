# Work Package D1

D1 proves fixed-threshold two-bank inference for the regular known-trigger model specified in the locked D0 protocol.

## Files

- `D1_THEORY_MEMO.md`: assumptions, lemmas, theorems, proofs, and exact benchmark.
- `d1_core.py`: reusable estimator and exact independent-normal benchmark.
- `tests/test_d1_core.py`: deterministic unit checks.
- `D1_RUNTIME_PREFLIGHT.py`: runtime-only local preflight; not scientific evidence.
- `D1_CONFIG_DRAFT.json`: current status and items that remain unlocked.
- `references.bib`: theory references.

## Run the runtime-only preflight

From the repository root:

```bash
bash theory/policy_search_size/work_package_d1/run_preflight.sh
```

Optional overrides:

```bash
bash theory/policy_search_size/work_package_d1/run_preflight.sh \
  --B 1000 --n 1000 --outer 30 --bootstrap 100
```

The output is written to `preflight_output/`. It is labeled `NOT SCIENTIFIC EVIDENCE` and must be used only to choose feasible repetition counts before a separate D1 numerical protocol is locked.

## Git sequence

1. Place the D1 draft files on `tess-top-tier-theory` after the frozen D0 commit.
2. Run unit tests and the runtime-only preflight locally.
3. Review runtime only.
4. Create and lock a separate D1 numerical validation protocol.
5. Run and freeze scientific numerical validation after that lock.
