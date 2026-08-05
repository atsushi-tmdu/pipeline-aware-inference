# D8-A Analytic Boundary Oracle

The finite-difference smooth-stratum oracle was not lockable because
second-differencing reproducible Gaussian-CDF values caused cancellation at
small steps.

The replacement oracle differentiates every polyhedral Gaussian CDF term
analytically with respect to its moving bounds. First derivatives are marginal
boundary densities times conditional CDFs. Mixed second derivatives are joint
boundary densities times the remaining conditional CDF. Pure second
derivatives also differentiate the conditional mean shift.

The bound derivatives are mapped to the four-dimensional threshold vector by
exact linear Jacobians and assembled with the ordinary product rule. The two
positive-part-square coincidence corrections remain separate and unchanged.
