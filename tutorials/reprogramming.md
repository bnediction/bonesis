---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Marker and source-marker reprogramming

The *reprogramming* of Boolean networks refers to the identification of modifications of the Boolean functions which ensure certain dynamical properties.
In the literature, these modifications typically fix the Boolean functions of a few components to a constant values, mimicking *mutations*, and the dynamical properties typically refers to properties over the attractors of the dynamical model.

In general, *BoNesis* enables identifying mutations which enforce any dynamical properties that can be expressed in the declarative language. The general structure would be as follows:

```{code-block} python
:lineno-start: 1

bo = BoNesis(...)
M = bo.Some(max_size=k)
with bo.mutant(M):
    ... dynamical properties...

solutions = M.assignments()
```

There, the `Some` is a variable representing a mutation of up to `k` nodes to a constant value.
The block with the `with` statement declares then that, under the application of the mutation, the described properties must hold.
Finally, the `assignments()` method returns an iterator over all the mutant that fulfill the properties.

*BoNesis* provides specific implementations for the so-called marker (or phenotype) reprogramming, which enforce a desired property over the (reachable) attractors. Recall that BoNesis operators on the Most Permissive update mode, for which attractors correspond to the minimal trap spaces of the Boolean network.
The desired target attractors are specified by a set of markers, associating a subset of nodes of the network to fixed values (e.g., $A=1,C=0$). After reprogramming, all the configurations in all (reachable) attractors must be compatible with these markers. Importantly, the target attractors are not necessarily attractors of the original (wild-type) BN: the reprogramming can destroy and create new attractors. In particular, if there is no attractor in the original model matching with the marker, the reprogramming will identify perturbations that will create such an attractor and ensure its reachability.

This tutorial demonstrates the usage of pre-defined marker and source-marker reprogramming functions available in the `bonesis.reprogramming` module. Details on the underlying methodology are provided in {cite}`MarkerReprogramming` and {cite}`CEGAR-MTS`.

Alternatively, the computation of reprogramming perturbations from single Boolean networks can be performed using the command line program `bonesis-reprogramming`.

```{code-cell} ipython3
:tags: [remove-output]

import bonesis
from bonesis.reprogramming import *

from colomoto_jupyter import tabulate # for display
import pandas as pd # for display
import mpbn # for analyzing individual Boolean networks with MP update mode
from colomoto.minibn import BooleanNetwork
```

*BoNesis* provides implementations for the following BN reprogramming problems:

* P1: **Marker reprogramming of fixed points** (function `marker_reprogramming_fixpoints`): after reprogramming, all the fixed points of the BN match with the given markers; optionally, we can also ensure that at least one fixed point exists.
* P2: **Source-marker reprogramming of fixed points** (function `source_marker_reprogramming_fixpoints`): after reprogramming, all the fixed points that are *reachable from the given initial configuration* match with the given markers.
* P3: **Marker reprogramming of attractors** (function `marker_reprogramming` aka `trapspace_reprogramming`): after reprogramming, all the configurations of all the MP attractors (the minimal trap spaces) of the BN match with the given markers.
* P4: **Source-marker reprogramming of attractors** (function `source_marker_reprogramming`): after reprogramming, all the configurations of all the attractors that are *reachable from the given initial configuration* match with the given markers.

## Marker-reprogramming of fixed points (P1)

We identify the perturbations $P$ of at most $k$ components so that all the fixed points of $f/P$ match with the given marker $M$.  With the *BoNesis* Python interface, this reprogramming property is implemented by `marker_reprogramming_fixpoints(f,M,k)` function, where `f` is a BN, `M` the marker (specified as Python dictionary associating a subset of components to a Boolean value), and `k` the maximum number of components that can be perturbed (at most $n$).

```{code-cell} ipython3
f = BooleanNetwork({
    "A": "B",
    "B": "!A",
    "C": "!A & B"
})
f
```

This example BN has two components in negative feedback: they will oscillate forever. The state of the third component `C` is then determined by the state of the oscillating components. The following command returns its influence graph:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
f.influence_graph()
```

With the (fully) asynchronous update mode, the system has a single attractor, consisting of all the configurations of the network.

```{code-cell} ipython3
---
tags: [remove-stdout]
---
f.dynamics("asynchronous")
```

Recall that the fixed points are identical in asynchronous and MP. We use [`mpbn`](https://github.com/bnediction/mpbn) to analyze the dynamical properties with the MP update mode:

```{code-cell} ipython3
mf = mpbn.MPBooleanNetwork(f)
list(mf.fixedpoints())
```

```{code-cell} ipython3
list(mf.attractors())
```

Indeed, the network has no fixed points, and its attractor is the full hypercube of dimension 3.

Using the `marker_reprogramming_fixpoints` snippet defined above, we identify all perturbations of at most 2 components which ensure that (1) all the fixed points have `C` active, and (2) at least one fixed point exists:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming_fixpoints(f, {"C": 1}, 2))
```

Indeed, fixing `A` to 0 breaks the negative feedback, and make `B` converge to 1. There, `C` converges to state 1.
Then, remark that fixing `C` to 1 is not enough to fulfill the property, as `A` and `B` still oscillate. Thus, one of these 2 must be fixed as well, to any value. The solution `{'A': 0, 'C': 1}` is not returned as `{'A': 0}` is sufficient to acquire the desired dynamical property.

By default, the `marker_reprogramming_fixpoints` function ensures that the perturbed BN possesses at least one fixed point. When relaxing this constraint, we obtain that the empty perturbation is the (unique) minimal solution, as `f` has no fixed point:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming_fixpoints(f, {"C": 1}, 2, ensure_exists=False))
```

## Source-marker reprogramming of fixed points (P2)

Given an initial configuration $z$, we identify the perturbations $P$ of at most $k$ components so that all the fixed points of $f/P$ that are reachable from $z$ in $f/P$ match with the given marker $M$.
With the *BoNesis* Python interface, this reprogramming property is implemented by `source_marker_reprogramming_fixpoints(f,z,M,k)` function, where `f` is a BN, `z` the initial configuration (Python dictionary), `M` the marker, and `k` the maximum number of components that can be perturbed (at most $n$).

Let us consider the following toy BN with two positive feedback cycles:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
f = BooleanNetwork({
    "A": "B",
    "B": "A",
    "C": "!D & (A|B)",
    "D": "!C"
})
f.influence_graph()
```

This BN has 3 fixed points, 2 of which are reachable from the configuration where `A` and `B` are active, and `C` and `D` inactive:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
z = {"A": 1, "B": 1, "C": 0, "D": 0}
f.dynamics("asynchronous", init=z)
```

```{code-cell} ipython3
list(mpbn.MPBooleanNetwork(f).fixedpoints())
```

```{code-cell} ipython3
list(mpbn.MPBooleanNetwork(f).fixedpoints(reachable_from=z))
```

Let us compare the results of the global marker-reprogramming of fixed points (P1) with the source-marker reprogramming of fixed points (P2), the objective being to have fixed points having `C` active.
In the first case, putting aside the perturbation of `C`, this necessitates to act on either `A` or `B` to prevent the existence of the fixed points where `A`, `B` and `C` are inactive:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming_fixpoints(f, {"C": 1}, 2))
```

Considering only the fixed points reachable from the configuration `z`, there is no need to act on `A` or `B`:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(source_marker_reprogramming_fixpoints(f, z, {"C": 1}, 2))
```

## Marker reprogramming of attractors (P3)

We identify the perturbations $P$ of at most $k$ components so that the configurations of the all the attractors of $f/P$ match with the given marker $M$ (i.e., in each attractor, the specified markers cannot oscillate).
With the *BoNesis* Python interface, this reprogramming property is implemented by `marker_reprogramming(f,M,k)` as follows, where `f` is a BN, `M` the marker, and `k` the maximum number of components that can be perturbed (at most $n$).

The `marker_reprogramming` function gives access to two implementations with the `algorithm` option: `"cegar"` (default) using counter-example guided resolution {cite}`CEGAR-MTS`, and `"complementary"` which might be faster on small instances and with low $k$.

Let us consider the following BN:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
f = mpbn.MPBooleanNetwork({
    "A": "!B",
    "B": "!A",
    "C": "A & !B & !D",
    "D": "C | E",
    "E": "!C & !E",
})
f.influence_graph()
```

Essentially, `A` and `B` always stabilize to opposite states. Whenever `A` is active (and `B` inactive) then `C` will oscillate, otherwise it stabilizes to 0. In each case `D` and `E` oscillate.
This lead to the following MP attractors:

```{code-cell} ipython3
tabulate(list(f.attractors()))
```

Let us say that our objective is to reprogram the BN such that all the attractors of the component `C` fixed to 1.
The reprogramming of fixed points (P1) gives the following solutions:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming_fixpoints(f, {"C": 1}, 3))
```

Putting aside the trivial solution of perturbing `C`, let us analyze the BN perturbed with the `D` forced to 0:

```{code-cell} ipython3
pf = f.copy()
pf["D"] = 0
tabulate(pf.attractors())
```

The (only) fixed point of the network indeed has `C` active. However, it possesses another (cyclic) attractor, where `C` is inactive.
This example points out that focusing on fixed point reprogramming may lead to predicting perturbations which are not sufficient to ensure that all the attractors show the desired marker.

The complete attractor reprogramming returns that the perturbation of `D` must be coupled with a perturbation of `A` or `B`, in this case to destroy the cyclic attractor.

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming(f, {"C": 1}, 3))
```

## Source-marker reprogramming of attractors (P4)

Given an initial configuration $z$, we identify the perturbations $P$ of at most $k$ components so that the configurations of the all the attractors of $f/P$ that are reachable from $z$  match with the given marker $M$ (i.e., in each reachable attractor, the specified markers cannot oscillate).
Thus, P4 is the same problem as P3, except that we focus only on attractors reachable from $z$, therefore potentially requiring fewer perturbations.
With the *BoNesis* Python interface, this reprogramming property is implemented by `source_marker_reprogramming(f,z,M,k)` function, where `f` is a BN, `z` the initial configuration, `M` the marker, and `k` the maximum number of components that can be perturbed (at most $n$).

Let us consider again the BN `f` analyzed in the previous section. By focusing only on attractors reachable from the configuration where `A` is fixed to 1 and other nodes to 0, the reprogramming required to make all attractors have `C` fixed to 1 consists only of fixing `D` to 0. Note that in the specific example, the reprogramming of reachable fixed point would give an equivalent result.

```{code-cell} ipython3
---
tags: [remove-stdout]
---
z = f.zero()
z["A"] = 1
list(source_marker_reprogramming(f, z, {"C": 1}, 3))
```

## Reprogramming of ensembles of Boolean networks

Instead of a Boolean network, the first argument `f` of the reprogramming function can be any domain of Boolean networks, representing either implicitly or explicitly an ensemble of Boolean networks.
In such a case, a mutation is returned if it is a reprogramming solution for at least *one* Boolean network of the ensemble.

For example, let us define an influence graph to delimit the domain of admissible Boolean networks:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
dom = bonesis.InfluenceGraph([
    ("C", "B", {"sign": 1}),
    ("A", "C", {"sign": 1}),
    ("B", "C", {"sign": -1}),
    ("C", "D", {"sign": 1}),
], exact=True, canonic=False) # we disable canonic encoding
dom
```

This domain encloses all the BNs having exactly (`exact=True`) the specified influence graph, 4 distinct BNs in this case:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
dom.canonic = True # we set canonic encoding for enumerating BNs
F = list(bonesis.BoNesis(dom).boolean_networks())
dom.canonic = False
pd.DataFrame(F)
```

Let us explore the attractors of each individual BNs:

```{code-cell} ipython3
for i, f in enumerate(F):
    print(f"Attractors of BN {i}:", list(f.attractors()))
```

In this example, we focus on reprogramming the attractors so that the component `D` is fixed to 1.

On the one hand, when reprogramming fixed points only, because one BN already verifies this property, the empty perturbation is a solution:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming_fixpoints(dom, {"D": 1}, 2))
```

On the other hand, the reprogramming of attractors returns solutions that work on every BN:

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(marker_reprogramming(dom, {"D": 1}, 2, algorithm="complementary"))
```

Indeed, fixed `C` to 1, ensures  in each case that `D` is fixed to 1.

The computation of universal solutions for the reprogramming of fixed points can be tackled by following a similar encoding than the reprogramming of attractors, i.e., by identifying perturbations which do not fulfill the property for at least one BN in the domain (the complement results in perturbations working for all the BNs):

```{code-cell} ipython3
def universal_marker_reprogramming_fixpoints(f: BooleanNetwork,
                                             M: dict[str,bool],
                                             k: int):
    bo = bonesis.BoNesis(f)
    coP = bo.Some(max_size=k)
    with bo.mutant(coP):
        x = bo.cfg()
        bo.fixed(x) # x is a fixed point
        x != bo.obs(M) # x does not match with M
    return coP.complementary_assignments()
```

```{code-cell} ipython3
---
tags: [remove-stdout]
---
list(universal_marker_reprogramming_fixpoints(dom, {"D": 1}, 2))
```

## Bibliography

```{bibliography}
:filter: docname in docnames
```
