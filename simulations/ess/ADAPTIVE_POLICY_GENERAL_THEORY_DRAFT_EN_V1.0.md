# General decomposition of adaptive search-policy multiplicity

Let \(R_0(\alpha)\) and \(R_1(\alpha)\) denote the rejection indicators under
the base and full searches, respectively, and let \(A\) indicate whether the
additional search is activated. The adaptive policy satisfies the exact
identity

\[
R_A(\alpha)
=
R_0(\alpha)
+
A\{R_1(\alpha)-R_0(\alpha)\}.
\]

Define the incremental rejection effect

\[
D_\alpha=R_1(\alpha)-R_0(\alpha)\in\{-1,0,1\}.
\]

Then

\[
\pi_A(\alpha)
=
\pi_0(\alpha)+E(A D_\alpha).
\]

For a random expansion indicator \(C\), independent of the search state and
satisfying \(E(C)=r\),

\[
\pi_{\mathrm{random}}(\alpha)
=
\pi_0(\alpha)+rE(D_\alpha).
\]

Hence, for any data-dependent activation policy with \(E(A)=r\),

\[
\boxed{
\pi_A(\alpha)-\pi_{\mathrm{random}}(\alpha)
=
\operatorname{Cov}(A,D_\alpha)
}
\]

and the same sign determines the TESS contrast because TESS is monotone in
the global-null rejection probability at fixed \(\alpha\).

This identity explains why the ordering derived in the independent-p-value
toy model need not persist in an ML pipeline. In the toy model, promising
activation is negatively associated with incremental rejection opportunity.
In the Phase 3C model libraries, promising base-stage performance can identify
replications in which additional model families are also unusually likely to
produce an extreme selected performance, yielding a positive covariance and
the reversed ordering.
