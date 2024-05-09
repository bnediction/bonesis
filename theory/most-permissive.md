# Most Permissive update mode

## Introduction

Given a BN $f$ and a configuration $x$, the *update mode* specifies how to compute the next configuration. There is a vast zoo of update modes {cite}`PS22`, but traditionally, two modes are usually considered in biological modeling: the *synchronous* (or parallel) deterministic mode, where the next configuration is given by its application to $f$ ($x$ is succeeded by $f(x)$), and the *fully asynchronous* (often denoted only asynchronous) where the next configuration results from the application of only one local function, chosen non-deterministically.

However, (a)synchronous update modes do not lead to a complete qualitative abstraction of quantitative systems and preclude the prediction of trajectories that are actually feasible when considering time scales or concentration scales. The *Most Permissive* (MP) {cite}`MPBNs` is a recently-introduced update mode which brings the formal guarantee to capture any trajectory that is feasible by any quantitative system compatible with the Boolean network.
The main idea behind the MP update mode is to systematically consider a potential delay when a component changes state, and consider any additional transitions that could occur if the changing component is in an intermediate state. It can be modeled as additional *dynamic* states "increase" ($\nearrow$) and "decrease" ($\searrow$): when a component can be activated, it will first go through the "increase" state where it can be interpreted as either 0 or 1 by the other components, until eventually reaching the Boolean 1 state; and symmetrically for deactivation.

## Definition

### Preliminaries: Subcubes and trap spaces

A **subcube** specifies for each dimension of the BN if it is either fixed to a Boolean value, or free: it can be characterized by a vector $h\in \{0,1,*\}^n$. Its *vertices* are denoted by $c(h) = \{ x\in \mathbb B^n\mid h_i\neq *\implies x_i=h_i\}$. For instance, $h=0**$ is a subcube of dimension 3, with $c(h) = \{000, 001, 010, 011\}$.

A subcube $h$ is a **trap space** whenever for each of its vertices $x\in c(h)$, $f(x)$ is also one of its vertices ($h$ is closed by $f$). In particular, the (sub)cube $\mathbf *_n$ is always a trap space.

A subcube $h$ is *smaller* than a subcube $h'$, denoted by $h \preceq h'$ whenever $c(h)\subseteq c(h')$. Equivalently, this means that each non-free component of $h'$ is fixed to the same value in $h$: $h \preceq h' \iff \forall i\in \{1,\ldots,n\}, h'_i\neq *\implies h_i=h'_i$.

### Most permissive dynamics

Given a set of components $K\subseteq \{1,\cdots,n\}$, a subcube $h$ is **$K$-closed** by $f$ whenever,
for each component $i\in K$ that is fixed in $h$, $f_i$ applied to any vertices of $h$
results in $h_i$. In other words, for all configurations in the $K$-closed subcube $h$,
the next states of the components $i \in K$ are in $h$:
$\forall x\in c(h),\, \forall i\in K,\, h_i\neq *\Rightarrow f_i(x)=h_i$.

We denote by $T_K(x)$ the *smallest* subcube of dimension $n$ that contains $x$ and that is $K$-closed by $f$.

```{admonition} Definition of Most permissive (MP) update mode
Given a BN $f$ of dimension $n$ and two distinct configurations $x$, $y$,
there is an MP transition from $x$ to $y$ whenever there exists a subset of
components $K\subseteq \{1,\cdots,n\}$ such that:
- $y$ is a vertex of the subcube $T_K(x)$, and
- for each each component $i\in K$, there exists a vertex $z$ of $T_K(x)$ such that $f_i(z)=y_i$.
```

## Elementary dynamical properties and their complexity

```{note}
Unless mentioned, proofs of following statements can be found in {cite}`MPBNs`.
```


### MP attractors are minimal trap spaces

The attractors of MP dynamics are the *minimal trap spaces* of the Boolean function $f$, i.e., the trap spaces which do not include strictly smaller trap spaces.
Thus, we denote MP attractors by subcubes, i.e., an MP attractor $A$ is a vector in $\{0,1,*\}^n$.
Therefore, a component with a $*$ value in an MP attractor $A$ indicates that the component that can always oscillate between 0 and 1 in the (cyclic) attractor.

The computational complexity of decision problems related to minimal trap spaces has been extensively addressed in {cite}`TrapSpaceComplexity` with different representations of Boolean networks.
For the case of local functions represented with propositional logic, as we consider here, deciding whether a subcube is a trap space is coNP-complete problem, whereas deciding whether it is a *minimal* trap space is a coNP<sup>coNP</sup>-complete problem, i.e., equivalent to the decision of satisfiability of $\forall\exists$ expressions.
In the case of *locally-monotone* BNs, deciding whether a subcube is a trap space is in PTIME, whereas deciding whether it is a minimal trap spaces is a coNP-complete problem, i.e., equivalent to the decision of satisfiability of $\forall$-expressions.


### MP reachability of attractors

Given a configuration $x$ and an MP attractor $A\in \{0,1,*\}^n$, there is an MP trajectory from $x$ to any configuration $y\in A$ if and only if $A$ is smaller than the smallest trap space *containing* $x$. We write $\operatorname{reach}(x,y)$ the existence of such a trajectory.

Let us denote by $\operatorname{TS}(x) \in \{0,1,*\}^n$ the smallest trap space containing $x$. The computation of $h=\operatorname{TS}(x)$ can be performed  from $x$ by iteratively freeing the components necessarily to fulfill the closeness property. Here is a sketch of algorithm, where `SAT(h, f[i] = -x[i])` is true if and only if there exists a configuration $y\in c(h)$ such that $f_i(y)=\neg x_i$:

```
Algorithm TS(x: configuration)
Returns subcube h
--
h := x
repeat
   changed := false
   for i in 1..n:
      if h[i] != * and SAT(h, f[i] = -x[i]):
          h[i] := *
          changed := true
while changed
```

In the worst case, this algorithm makes a quadratic number of calls to the `SAT` problem.
Therefore, the decision of MP reachability of attractors is in PTIME<sup>NP</sup> in general[^2], and PTIME in the locally-monotone case.

Note that the general MP reachability property is not addressed here, but its overall complexity is identical. With (a)synchronous update modes, it is a PSPACE-complete problem.

[^2]: this problem is actually in NP when allowing a number of variables quadratic with $n$

### Belonging to an MP attractor

In the following, we will consider the problem of deciding whether a given configuration $x$ belongs to an MP attractor of $f$. We write $\operatorname{IN-ATTRACTOR}(x)$ such a property. This can be verified in two steps: (1) compute the smallest trap spaces containing $x$, noted $\operatorname{TS}(x)$, and (2) verify whether $\operatorname{TS}(x)$ is a minimal trap space. This later property is true if and only if for any vertex $y$ of $\operatorname{TS}(x)$, the minimal trap space containing $y$ is equal to $\operatorname{TS}(x)$:

$$
\operatorname{IN-ATTRACTOR}(x) \equiv \forall y \in c(\operatorname{TS}(x)), \operatorname{TS}(y) = \operatorname{TS}(x) \enspace.
$$

Finally, given a set of perturbations $P$, we write $\operatorname{TS}_P(x)$ for the small trap space of perturbed BN $(f/P)$ containing $x$, and $\operatorname{IN-ATTRACTOR}_P(x)$ the property of $x$ belonging to an attractor of the perturbed BN $(f/P)$.


## Bibliography

```{bibliography}
:filter: docname in docnames
```
