# Lemma D8-A.3a: Coordinate Moving-Face Differentiation

## Setup

Let \(W\subset\mathbb R^K\) be a fixed winner cell. For distinct coordinate
indices \(j_1,\ldots,j_m\), \(m\le2\), and signs
\(s_r\in\{-1,+1\}\), define

\[
P(t)
=
\int_W
\prod_{r=1}^m
I\{s_r(x_{j_r}-t_r)>0\}
f(x)\,dx.
\]

Here \(s_r=+1\) denotes an upper-tail face \(x_{j_r}>t_r\), and
\(s_r=-1\) denotes a lower-tail face \(x_{j_r}<t_r\).

## Trace-regularity assumption

For every winner cell and every collection of at most two threshold
coordinates:

1. the one-face trace integral is continuously differentiable in its face
   location;
2. the two-face trace integral is continuous in both locations;
3. all local trace integrals and their required first derivatives admit an
   integrable dominating envelope.

## Conclusion

Under these conditions, \(P\) is twice continuously differentiable.

For one moving face,

\[
\frac{\partial P}{\partial t_r}
=
-s_r
\int_{W\cap\{x_{j_r}=t_r\}}
\prod_{u\ne r}
I\{s_u(x_{j_u}-t_u)>0\}
f(x)\,d\mathcal H^{K-1}(x).
\]

For two distinct moving faces,

\[
\frac{\partial^2P}
{\partial t_r\partial t_u}
=
s_rs_u
\int_{
W\cap\{x_{j_r}=t_r\}
\cap\{x_{j_u}=t_u\}
}
f(x)\,d\mathcal H^{K-2}(x).
\]

Pure second derivatives are the derivatives of the corresponding one-face
trace integrals.

## Proof

Apply Fubini's theorem in the moving coordinate and the ordinary fundamental
theorem of calculus. The domination assumptions permit differentiation under
the remaining integral. Repeat for the second derivative. Continuity follows
from dominated convergence and continuity of the declared trace maps.

Because \(W\) is fixed, winner boundaries do not move with the threshold
vector.
