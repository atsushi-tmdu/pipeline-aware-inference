# Work Package D0

This directory contains the draft protocol for two-bank inference for policy-level TESS.

## Status

`D0_PROTOCOL.md` is a draft and must be scientifically reviewed before it is tagged as locked. Do not begin result-dependent numerical redesign before the lock commit.

## Intended sequence

1. Review assumptions, estimands, theorem ladder, and stop rules.
2. Change `status` in `D0_CONFIG.json` from `draft_not_locked` to `locked`.
3. Commit the protocol separately.
4. Create annotated tag `tess-theory-work-package-d0-v1-lock-20260802`.
5. Begin D1 only after the tag exists.

## First proof target

D1: fixed local threshold, known activation trigger, reference-estimated candidate quantiles, independent evaluation bank, asymptotic linearity, and two-bank bootstrap validity.
