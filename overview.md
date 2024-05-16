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
