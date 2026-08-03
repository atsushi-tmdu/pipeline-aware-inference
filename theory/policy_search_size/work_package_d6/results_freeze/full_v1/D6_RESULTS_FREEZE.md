# D6 Full Scientific Validation Results Freeze

**Formal status:** FAIL
**Substantive interpretation:** strong qualified support with one borderline
deep-tail TESS-centering failure.

## Source identity

- branch: `tess-top-tier-theory`
- lock tag: `tess-theory-work-package-d6-v1-lock-20260803`
- source commit: `d26f92f33bcd29e97d7d7a4993bf5bafb2fb76df`
- lock tag commit: `d26f92f33bcd29e97d7d7a4993bf5bafb2fb76df`
- full-grid replication rows: `72000`
- bootstrap outer rows: `6000`
- elapsed seconds: `2042.590`

## Preserved result

All fatal implementation checks passed. The only failed scientific check was
`delta_s_bias_per_cell`.

The freeze contains compact scientific summaries, the locked adjudication,
the full-run log, source-output hashes, and the exact post-run TESS-bias
decomposition. Large replication-level and bootstrap-level raw outputs remain
in the ignored `outputs/full_v1` directory and are represented by the frozen
source hash manifest.

No criteria were changed and the scientific run was not repeated.
