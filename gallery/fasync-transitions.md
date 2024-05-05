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

## Declare asynchronous transitions

By default, reachability properties (e.g., `x >= y`) are computed with regards to the
[](../theory/most-permissive).
However, this can be restricted with the `scope_reachability` context.


```{code-cell} ipython3
:tags: [remove-cell]
import bonesis
dom = bonesis.InfluenceGraph.complete("ABC", sign=1, exact=True)
bo = bonesis.BoNesis(dom)
```

In the context of `scope_reachabbility(max_change=1)`{l=py}, trajectories are computed by changing at most 1 component. This boils down to consider only one transition with the (fully) asynchronous mode:

```{code-cell} ipython3
with bo.scope_reachability(max_changes=1):
    x = ~bo.obs({"A":1,"B":0,"C":0})
    y = ~bo.obs({"A":1,"B":1,"C":0})
    x >= y  # realized by one fully-asynchronous transition
```

```{code-cell} ipython3
:tags: [remove-cell]
list(bo.boolean_networks(limit=1))[0]
```
