# D8-A Theory-Complete Checkpoint

**Theory status:** complete under stated assumptions
**Scientific numerical design locked:** no
**Scientific simulation run:** no

## Main completed results

### Joint empirical-quantile theorem

The complete-vector threshold estimator satisfies the declared
\(B^{-1}\) mean expansion, first-order covariance expansion, and
fixed-dimensional higher-moment bound under the stated local-density,
tail-moment, and quantile assumptions.

### Regular policy-map smoothness

Under fixed finite pools, continuous unique winners, strict
candidate-trigger separation, and explicit coordinate trace regularity,
the regular policy contrast is twice continuously differentiable.

### Second-order policy bias

\[
E(\widehat\Delta_\pi)-\Delta_\pi
=
\frac{C_{\Delta,B}}{B}
-
\frac{\Delta_\pi}{n}
-
\frac{C_{\Delta,B}}{Bn}
+
o(B^{-1}+n^{-1}).
\]

### TESS second-order bias

\[
E(\widehat\Delta_S)-\Delta_S
=
\frac{C_{S,R,B}}{B}
+
\frac{C_{S,E}}{n}
+
o(B^{-1}+n^{-1}).
\]

## Assumption boundary

The completed theory remains restricted to fixed finite continuous
candidate pools, almost-surely unique winners, strict threshold separation,
independent reference and evaluation banks, local quantile regularity, finite
higher moments, and explicit coordinate trace regularity.

It does not cover plus-one rates, discrete winner ties, exact threshold
coincidence, failed fits, or growing candidate dimension.

## Lineage

The earlier checkpoint `d8a-theory-prelock-v1` remains the immutable record of
the prelock scaffold. Its verifier is expected to fail in the developed
working tree because files have legitimately advanced beyond that checkpoint;
the tagged commit remains independently reproducible.

No D8-A scientific numerical design has been locked and no D8-A scientific
simulation has been run.
