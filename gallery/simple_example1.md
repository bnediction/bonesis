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

## Toy example on reachability, fixed point, and mutant

This is a simple example of BoNesis usage for Boolean network synthesis from
properties combining reachability, fixed points, and mutants.

```{code-cell} ipython3
:tags: [remove-output]
import bonesis
```

We take as domain any possible Boolean network between 3 variables,
and define 2 observations: one (complete) for the initial configuration,
and one (incomplete) for the final one:

```{code-cell} ipython3
# use complete graph as domain
dom = bonesis.InfluenceGraph.complete(["A","B","C"])
# named observations
data = {
    "init": {"A": 0, "B": 0, "C": 0},
    "marker": {"A": 1, "C": 0}
}
```

We declare that, in the wild-type, there is a configuration matching with the
final observation (`"marker"`) which is a fixed point reachable from the
initial configuration.
Moreover, in the mutant where `C` is KO, the final configuration is no longer
reachable.

```{code-cell} ipython3
bo = bonesis.BoNesis(dom, data)
x = ~bo.obs("init")
y = ~bo.obs("marker")
x >= bo.fixed(y)  # y is a fixed point and can be reached from x
with bo.mutant({"C": 0}):
    x / y
```

Existence of a solution can be verified as follows.

```{code-cell} ipython3
bo.is_satisfiable()
```

Then, we enumerate 3 solutions, and display the first one.
Solution objects are `mpbn.MPBooleanNetwork` objects
(https://mpbn.readthedocs.io).

```{code-cell} ipython3
:tags: [remove-stdout]
solutions = list(bo.boolean_networks(limit=3))
solutions[0] # show one solution
```

Computation of (most permissive) attractors can then be performed using `mpbn`
as follows.

```{code-cell} ipython3
# list attractors
import pandas as pd
pd.DataFrame(solutions[0].attractors())
```

The Boolean network can be exported to the standard BoolNet textual format, which is
supported by many tools for analyzing Boolean networks.

```{code-cell} ipython3
solutions[0].save("solution.bnet")
```
