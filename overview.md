# Overview

BoNesis takes two inputs:
1. a *domain* of Boolean networks (BNs),
2. a set of Boolean *dynamical properties*,

and can then enumerate the BNs from the domain that verify the given properties.

The synthesis task is conducted from a `BoNesis` object, that can be instantiated
as follows:

```py
bo = bonesis.BoNesis(dom, data)
```

where `dom` is an object representing the {ref}`bn-domain`, and `data`
is a `dict`-like object defining *named observations*, that are (possibly
partial) mappings from network components to Boolean values.

Dynamical properties are then specified using a specific [declarative language](language.md), whose predicate are available as `BoNesis` methods.


## Input

(bn-domain)=
### Domain of Boolean networks

Single Boolean network
: From `.bnet` files (see example below), `colomoto.minibn.BooleanNetwork`, or [`mpbn.MPBooleanNetwork](https://mpbn.readthedocs.io/) objects.
    ```py
    dom = bonesis.BooleanNetwork("model.bnet")
    ```
    Useful for reprogramming prediction and model-checking.
    There are no restriction on the type of Boolean network (can be
    non-monotone).


Explicit ensemble of Boolean networks:
: Instantiated with `bonesis.BooleanNetworkEnsemble` with a list of
`bonesis.BooleanNetwork` or `mpbn.MPBooleanNetwork` objects.
    ```py
    dom = bonesis.BooleanNetworkEnsemble([bn1, bn2, bn3])
    ```
    Can also be constructed from a zipfile: in that case, all the files ending
    with `.bnet` will be loaded as compound `bonesis.BooleanNetwork` objects:
    ```py
    dom = bonesis.BooleanNetworkEnsemble.from_zip("models.zip")
    ```
    There are no restriction on the type of Boolean network (can be
    non-monotone).


Influence graph (GRN)
: Implicit domain of any *locally-monotone* Boolean network whose [influence graph](theory/boolean-networks.md#influence-graph) is a subgraph of the given (partially) signed directed graph. The influence graph is instantiated with a `bonesis.InfluenceGraph` class which inherits from [`networkx.MutiDiGraph`](https://networkx.org/documentation/stable/reference/classes/multidigraph.html). The sign of edges must be specified with a `"sign"` data attribute. If the sign is `"?"` (or `"ukn"`), then BoNesis will consider any possible sign.


    ```py
    edges = [("a", "b", {"sign": 1}),
             ("b", "a", {"sign": -1})]
    dom = bonesis.InfluenceGraph(edges)
    ```

    Positive sign can be indicated using values `1`, `"+"`, `"+1"` `"->"`;
    negative sign can be indicated using values `0`, `"-"`, `"-1"` `"-|"`;
    unknown sign can be indicated using values `"?"`, `"ukn"`, `"unspecified"`.

    *Options.*
    - `exact` (default `False`): When `False`, considers Boolean networks whose
      influence graph is a subgraph (not all regulations have to be used).
      When `True`, considers only Boolean networks having the exact same
      influence graph; this is always unsatisfiable in presence of unknown sign.
      When `"unsigned"`, it behaves like `True` except that unknown signs are
      ignored.
    - `allow_skipping_nodes` (default `False`). If `True`, allow to BoNesis to
      ignore nodes of the graph. No Boolean function will be synthesized for
      them. This is intended to be use in conjunction with maximization
      statements on the number of nodes.
    - `canonic` (default `True`): Ensures that an enumeration of *distinct*
      Boolean networks. This adds some complexity in the encoding. Setting to
      `False` can help to addresslarge instances when enumeration of Boolean
      functions is not needed.
    - `maxclause` (default `None`): Maximum number of clauses to consider for
      each Boolean function to synthesize in disjunctive normal form. When
      `None` the maximum bound is automatically computed for each node. As it is exponential
      with the number of regulators, it is recommended to set to an integer for
      large instances (e.g., `maxclause=32`).


    See [tour tutorial](tutorials/tour.md#influence-graph) for further examples.

    The influence graph domain can also be loaded from specific file formats:

    - from CSV files:
        ```py
        dom = bonesis.InfluenceGraph.from_csv("grn.csv")
        ```
        *Options.* By default, the field separator is comma (`sep=","`), source component is taken from first column (`column_source=0`),
        target component from second column (`column_target=1`) and sign value from
        second column (`column_sign=2`).
        Moreover, a self-positive regulation will be added to components without regulators (`unsource=True`). Other options are passed to `InfluenceGraph` constructor.

    - from SIF files:
        ```py
        dom = bonesis.InfluenceGraph.from_sif("grn.sif")
        ```
        *Options.* By default, a self-positive regulation will be added to components without regulators (`unsource=True`). Other options are passed to `InfluenceGraph` constructor.


    Specific influence graphs can be constructed as follows:

    - complete graph:
        ```py
        dom = bonesis.InfluenceGraph.complete(nodes)
        ```
        where `nodes` is the list of nodes of the complete graph (see [`networkx.complete_graph`](https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.complete_graph.html)).
        *Options.* By default, self-loops are added on each node (`loops=True`), and sign is unspecified (`sign=0`).
        Other options are passed to `InfluenceGraph` constructor.


    *Current limitation: [locally-monotone Boolean networks](theory/boolean-networks.md#locally-monotone-boolean-networks)*.




Partially-specified Boolean network (AEON)
: From `.aeon` files in [AEON Format](https://biodivine.fi.muni.cz/aeon/manual/v0.4.0/model_editor/import_export.html#aeon-format) or [`biodivine_aean.BooleanNetwork`](https://github.com/sybila/biodivine-aeon-py) object.
    ```py
    dom = bonesis.aeon.AEONDomain.from_file("partial-bn.aeon")
    ```

    In addition to enforcing completely or partially the Boolean functions of
    components, the AEON format enables a fine-grained specification of
    mandatory and optional influences, as well as having unknown signs.

    *Current limitation: functions specified in AEON can be non-monotone, but
    unspecified functions will be assumed to be monotone.*


### Named observations [optional]

In addition to the mandatory domain, the `BoNesis` constructor accepts a second optional
`dict`-like object associating names to *Boolean* observations over network components,
also represented with a `dict`-like object.
The name can then be used as argument to the [`obs`](language.md#obs-from-name)
object.

An observation can be partial (it does not have to assocate a Boolean value for
each component), and it can refer to components that are not referenced in the
domain (in that case, they will be ignored).

```py
data = {
   "init": {"a": 1, "b": 0, "c": 1},
   "phenotype1": {"b": 1}
}
bo = bonesis.BoNesis(dom, data)
~bo.obs("init") >= ~bo.obs("phenotype1")
```

### Dynamical properties

The properties that the Boolean network must satisfes are specified using
predicates that can be declared using the language and methods of the `BoNesis`
object. See [](language.md).

### Optimization statements

It is possible to restrict the solutions to optimal ones, according to an
ordered list of objectives.
See implemented [](language.md#optimizations).

```py
# build a domain while allowing to ignore any number of node
dom = bonesis.InfluenceGraph(..., allow_skipping_nodes=True)
bo = bonesis.BoNesis(dom, data)
...
# consider only solutions accounting for the maximum possible number of nodes
bo.maximize_nodes()
```


## Outputs

The inputs defined above delineate a set of constraints that must hold
alltogether.
Generally, the constraints involve *choices* (free variables), such as the
choice of Boolean functions in the defined *domain*, whenever it is not a single
Boolean network, and the choice of state of components in configurations
tied with partial observations.

BoNeis gives access to the solutions with *views*. A view specifies which
objects are to be enumarated from the solution space, and returns an iterator
other them.
Views support a number of options, including:
- `solutions` with value either `"all"`{l=py} (default), `"subset-minimal"`{l=py}, or `"subset-maximal"`{l=py}: enable to focus only on most sparse/dense solutions. Precise meaning depend on the object being enumerated.
- `limit` (default `0`{l=py}): maximum number of solutions to extract; `0`{l=py} means all.
- `progress`: a [`tqdm`](https://tqdm.github.io)-like object which will be
  notified after each iteration.
- [`extra`](#extra)

View classes are defined in the module
[`bonesis.views`](https://github.com/bnediction/bonesis/blob/main/bonesis/views.py). They take a BoNesis object as first argument.
For convenience, most usual views are provided as methods of the BoNesis object.

### Boolean networks

#### `boolean_networks()`: basic enumeration

The view `bo.boolean_networks()` returns an iterator over the Boolean networks
of the given domaine that verify the specified properties.
Boolean networks are returned as [`mpbn.MPBooleanNetwork`](https://mpbn.readthedocs.io) objects, which are `dict`-like objects associating nodes to a Boolean function in disjunctive normal form.

*Examples of usage*:
- tabular view of the results, using `pandas`:
    ```py
    view = bo.boolean_networks()
    import pandas as pd
    solutions = pd.DataFrame(view)
    ```
- export to individual model files:
    ```py
    for i, f in enumerate(bo.boolean_networks(limit=5)):
        f.save(f"solution{i}.bnet")
    ```

#### `diverse_boolean_networks()`: sampling with diversity

When facing numerous solutions, one often observe that the basic
enumeration of a limited number of Boolean networks results in very lookalike
networks.
One can circumvent this issue by employing the `bo.diverse_boolean_networks()`
view which, after each solution, will attempt to force the solver to browse
distant solutions.
Note that the enumeration speed can be largely reduced by this process.

#### Projections

To better understand the composition of the different solutions, one can project the solutions on each node: given a node A, it enumerates all the Boolean functions for A that are used in at least one full solution.

The projected solutions can be accessed from the following object:
```py
projs = bo.local_functions()
```

The `projs` object as `as_dict` method which offers direct access to all the projected solutions. By default, it will enumerate the Boolean functions for each node. The method "count" instead returns the number of solutions per node. There is also a `keys` parameter to specify a subset of nodes for the computation.

```py
counts = projs.as_dict(method="count")
counts
```

Note that the projected solutions gives an over-approximation of the full set of solutions: the full set of solutions is, in general, a strict subset of the cartesian product (see [Feature tour](tutorials/tour.md#projection) for a concrete example).

Access to the solutions of a specific node can be done as follows:
```py
with projs.view("Tuj1") as view:
    Tuj1_functions = [f for f in view]
```

Finally, `projs` has a `as_dataframe` method for pretty display of the projected solutions using `pandas`. The option `keys` enables to specify a subset of nodes to consider.

```py
table = projs.as_dataframe()
```

### Influence graphs

The view `bo.influence_graphs()` returns an iterator over the distinct influence
graphs of satisfying Boolean networks.
This is an efficient approach to capture the space of solutions whenever there
are too many possible Boolean network.

Influence graphs are returned as [`networkx.DiGraph`](https://networkx.org/documentation/stable/reference/classes/digraph.html) objects, with sign and label stored as `"sign"`{l=py} and `"label"`{l=py} attributes, respectively.

The option `solution="subset-minimal"`{l=py} will return all the influence graphs which are minimal by signed-edge inclusion. Thus, any satisfying Boolean network employs necessarily all the influences of at least one of the returned graphs.

### Nodes

`bonesis.NonConstantNodesView(bo)`
: View over the nodes that jointly received a non-constant Boolean function.
A typical usage is with option `solutions="subset-minimal"`{l=py} or with
[`bo.maximize_constants()`](language.md#maximize-constants).

`bonesis.NonStrongConstantNodesView(bo)`
: View over the nodes that jointly received a non-constant Boolean function or
differ of state in at least two configurations.
A typical usage is with option `solutions="subset-minimal"`{l=py}
or with [`bo.maximize_strong_constants()`{l=py}](language.md#maximize-strong-constants).

`bonesis.NodesView(bo)`
: Iterator over the sets of nodes involved in the solutions. Think of it as the
influence graph view, but with edges ignored. This is useful in conjunction with domains having option `allow_skipping_nodes=True`{l=py}.

### Assignments

BoNesis [](language.md) enables to define objects with only a partial
specification.
This is the case of *configurations* ([`cfg` objects](language.md#cfg)), which
can be either free or bound to a partial assignment of the state of components
(observations) and *variables* ([`Some` objects](language.md#some)).

Each of these object have an `assignment()` method, which is a view other their
satisfying complete value assignment.
In the case of `Some` object, the option `solution` defaults to
`"subset-minimal"`{l=py}.

This is mostly used with a single Boolean network as the domain. Otherwsie, keep
in my that an assignment is returned if there exists at least one Boolean
network of the domain with which it is a satisfying assignment.

*Examples*
- ```py
  x = bo.fixed(~bo.obs("final"))
  for val in x.assignments():
     ...
  ```
- ```py
  x = ~bo.obs("init")
  y = bo.fixed(~bo.obs("final"))
  bo.fixed(x)
  freeze = bo.Some(max_k=3)
  with bo.mutant(freeze):
    x >= y

  for val in freeze.assignment():
    ...
  ```

### The `extra` option

The views provide an efficient iteration over specified object types by the
means of projection techniques implemeted in the *clingo* solver, and
each iteration will return a distinct object.

The `extra` option of views enables to extract, for each solution, *a*
corresponding satisfying assignment of other objects of specified types.
The option supports values among `"configurations"`{l=py}, `"boolean-network"`{l=py}, `"somes"`{l=py}, or a tuple of them.

*Examples*
- Extract a possible complete assignment of configurations for each returned
  Boolean network:
  ```py
  # Get up to 5 distinct Boolean networks together with an instance of
  # satisfying assignment of configurations.
  for f, cfgs in f.boolean_networks(limit=5, extra="configurations"):
    ...
  ```

- Extract a Boolean network and configuration assignments alongside distinct
  influence graphs:
  ```py
  # Get all distinct subset-minimal influence graphs, and for each of them one
  # instance of Boolean networks and configuration assignements
  for ig, f, cfgs in f.influence_graphs(solutions="subset-minimal",
                            extra=("boolean-network", "configurations")):
    ...
  ```
