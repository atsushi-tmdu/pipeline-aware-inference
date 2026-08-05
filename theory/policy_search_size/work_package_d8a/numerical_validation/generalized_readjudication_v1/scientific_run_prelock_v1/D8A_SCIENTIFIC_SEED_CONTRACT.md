# D8-A Scientific Seed Inventory Contract

The locked master seed is inherited from `d8a_seed_contract.py`.

For each family job and stream, the seed namespace is

\[
\text{SHA256}(
\text{class-key}\,\|\,\text{family}\,\|\,\text{stream}
).
\]

The first four unsigned 32-bit words form the immutable spawn prefix.
The replicate index is appended as the final spawn-key component.

Reference and evaluation streams use distinct names and therefore distinct
spawn prefixes.

Nested sample-size points within a replicate use prefixes of one generated
bank and do not receive separate seeds.
