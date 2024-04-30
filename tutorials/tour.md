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

# Feature tour of BoNesis

A quick tutorial demonstrating the main features of BoNesis for the synthesis of Most Permissive Boolean Networks from network architecture and dynamical constraints.

```{code-cell}
---
tags: [remove-output]
---
import bonesis
import pandas as pd
from colomoto_jupyter import tabulate
```

The synthesis uses two inputs:
1. the domain of BNs, which can be a single BN, or specified by an influence graph
2. a table (dictionnary) specifying the (partial) observations of the systems

## Synthesis from influence graph and dynamical constraints

### Influence graph

Let us define an influence graph from a list of pairwise interactions, with a sign.

```{code-cell}
influences = [
("Pax6","Pax6",dict(sign=1)),
("Pax6","Hes5",dict(sign=1)),
("Pax6","Mash1",dict(sign=1)),
("Hes5","Mash1",dict(sign=-1)),
("Hes5","Scl",dict(sign=1)),
("Hes5","Olig2",dict(sign=1)),
("Hes5","Stat3",dict(sign=1)),
("Mash1","Hes5",dict(sign=-1)),
("Mash1","Zic1",dict(sign=1)),
("Mash1","Brn2",dict(sign=1)),
("Zic1","Tuj1",dict(sign=1)),
("Brn2","Tuj1",dict(sign=1)),
("Scl","Olig2",dict(sign=-1)),
("Scl","Stat3",dict(sign=1)),
("Olig2","Scl",dict(sign=-1)),
("Olig2","Myt1L",dict(sign=1)),
("Olig2","Sox8",dict(sign=1)),
("Olig2","Brn2",dict(sign=-1)),
("Stat3","Aldh1L1",dict(sign=1)),
("Myt1L","Tuj1",dict(sign=1)),
]
```

```{code-cell}
---
tags: [remove-stdout]
---
dom1 = bonesis.InfluenceGraph(influences)
dom1
```

Here, `dom1` delimits any BN that uses *at most* the listed influences, with the right sign. Thus, some solutions may use only a subset of this influence graph.

If you want to enforce BNs using *all* the given influences, use the option `exact=True`:

```{code-cell}
dom2 = bonesis.InfluenceGraph(influences, exact=True)
```

For influence graphs with large in-degrees, it is necessary to specify a bound on the number of clauses in the disjunction normal form (DNF) of the BNs with the `maxclause` argument. See `help(bonesis.InfluenceGraph)` for other options.

+++

### Observations

They are specified by a Python dictionnary associating observation names to observed states of a subset of nodes:

```{code-cell}
data = {
    "zero": {n: 0 for n in dom1}, # all nodes are 0
    "init": {n: 1 if n == "Pax6" else 0 for n in dom1}, # all nodes are 0 but Pax6
    "tM": {"Pax6": 1, "Tuj1": 0, "Scl": 0, "Aldh1L1": 0, "Olig2": 0, "Sox8": 0},
    "fT": {"Pax6": 1, "Tuj1": 1, "Brn2": 1, "Zic1": 1, "Aldh1L1": 0, "Sox8": 0},
    "tO": {"Pax6": 1, "Tuj1": 0 ,"Scl": 0, "Aldh1L1": 0, "Olig2": 1, "Sox8": 0},    
    "fMS": {"Pax6": 1, "Tuj1": 0, "Zic1": 0, "Brn2": 0, "Aldh1L1": 0, "Sox8": 1},
    "tS": {"Pax6": 1, "Tuj1": 0, "Scl": 1, "Aldh1L1": 0, "Olig2": 0, "Sox8": 0},
    "fA": {"Pax6": 1, "Tuj1": 0, "Zic1": 0, "Brn2": 0, "Aldh1L1": 1, "Sox8": 0},
}
pd.DataFrame.from_dict(data, orient="index").fillna('')
```

## Dynamical properties

```{code-cell}
bo = bonesis.BoNesis(dom1, data)
```

The `data` dictionnary specifies *observations* that can be used to constraint *configurations* (or states) of the network.

There are two shortcuts for binding a configuration to an observation:
`~bo.obs("A")` is a unique pre-defined configuration bound to the observation `"A"`;
`+bo.obs("A")` returns a *new* configuration bound to `"A"`. Thus in the following code:
```python
cfg1 = ~bo.obs("A")
cfg2 = ~bo.obs("A")
cfg3 = +bo.obs("A")
cfg4 = +bo.obs("A")
```
`cfg1` and `cfg2` refers to the *same* configuration; whereas `cfg3` and `cfg4` *may* be different.

### Attractor constraints

We detail two kind of attractor constraints: fixed points and trap spaces. Both are specified with the `fixed` predicate, which, depending on the argument will enforce the existence of one of the two kinds of attractor.

#### Fixed points

When giving a configuration as argument, `fixed` ensures that the configuration is a fixed point:

```{code-cell}
bo.fixed(~bo.obs("fA"))
bo.fixed(~bo.obs("fMS"));
```

#### Trap spaces

A trap space specification is given by an observation, which enforces that all the nodes in the given observations can never change of value (thus any reachable attractor have these nodes fixed):

```{code-cell}
---
editable: true
slideshow:
  slide_type: ''
---
fT_tp = bo.fixed(bo.obs("fT"))
```

### Reachability constraints

Reachability relates to the presence or absence of trajectory between two configurations.

#### Existence of trajectory

They can be specified using the `reach` function, or equivalently the `>=` operator between two configurations. The right-hand side can also be a `fixed` constraint.

```{code-cell}
~bo.obs("init") >= ~bo.obs("tM") >= fT_tp
~bo.obs("init") >= ~bo.obs("tO") >= ~bo.obs("fMS")
~bo.obs("init") >= ~bo.obs("tS") >= ~bo.obs("fA");
```

#### Absence of trajectory

They can be specified using the `nonreach` function, or equivalently the `/` operator between two configurations. The right-hand side can also be a `fixed` constraint.

```{code-cell}
~bo.obs("zero") / fT_tp
~bo.obs("zero") / ~bo.obs("fMS")
~bo.obs("zero") / ~bo.obs("fA");
```

### Enumeration of compatible BNs

Enumerations of solutions are done through iterators. The basic one being the `boolean_networks` which returns `mpbn.MPBooleanNetwork` objects.

```{code-cell}
---
editable: true
slideshow:
  slide_type: ''
---
for bn in bo.boolean_networks(limit=2): # limit is optional
    print(bn)
```

Display as a table:

```{code-cell}
---
tags: [remove-stdout]
---
solutions = list(bo.boolean_networks())
pd.DataFrame(solutions)
```

```{code-cell}
len(solutions)
```

Resulting objects are `MPBooleanNetwork` from the [`mpbn`](https://mpbn.readthedocs.io/) Python library. One can then compute reachability and attractor properties directly:

```{code-cell}
pd.DataFrame(solutions[0].attractors())
```

```{code-cell}
pd.DataFrame(solutions[0].attractors(reachable_from=data["init"]))
```

### Universal constraints

We can also enforce universal constraints on fixed points and reachable fixed points.

#### Universal fixed points

The following constraint ensures that any fixed point has to match with at least one of the observation given in argument.

```{code-cell}
bo.all_fixpoints({bo.obs(obs) for obs in ["fA", "fMS", "fT", "zero"]});
```

#### Universal reachable fixed points

The following constraint ensures that any fixed point *reachable* from the configuration on left-hand side has to match with at least one of the given observation.

```{code-cell}
~bo.obs("init") >> "fixpoints" ^ {bo.obs(obs) for obs in ["fA", "fMS", "fT"]};
```

```{code-cell}
---
tags: [remove-stdout]
---
bo.boolean_networks().count()
```

## Project solutions per nodes

To better understand the composition of the different solutions, one can project the solutions on each node: given a node A, it enumerates all the Boolean functions for A that are used in at least one full solution.

The projected solutions can be accessed from the following object:

```{code-cell}
---
tags: [remove-stdout]
---
projs = bo.local_functions()
```

The `projs` object as `as_dict` method which offers a diret access to all the projected solutions. By default, it will enumerate the Boolean functions for each node. The method "count" instead returns the number of solutions per node. There is also a `keys` parameter to specify a subset of nodes for the computation.

```{code-cell}
counts = projs.as_dict(method="count")
counts
```

Note that the projected solutions gives an over-approximation of the full set of solutions: the full set of solutions is, in general, a strict subset of the cartesian product:

```{code-cell}
from functools import reduce
reduce(int.__mul__, counts.values())
```

Access to the solutions of a specific node can be done as follows, where `view` is an object similar to the one returned by `bo.boolean_network()` (iterator over solutions).

```{code-cell}
with projs.view("Tuj1") as view:
    functions = [f for f in view]
[str(f) for f in functions]
```

Finally, `projs` has a `as_dataframe` method for pretty display of the projected solutions using *pandas*.

```{code-cell}
projs.as_dataframe()
```

## Exportation

A self-contained bash-script for customizing the ASP code and performing the enumeration off-line can be exported as follows.

```{code-cell}
view = bo.boolean_networks()
```

```{code-cell}
view.standalone(output_filename="tutorial.asp")
```
