# Inputs / outputs

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

- A singleton locally-monotone BN $\mathbb F=\{f\}$. In that case, *BoNesis* can be employed as a model checker to verify that $f$ has the specified dynamical properties. In this paper, this is the main setting we will consider, in order to predict perturbations to reprogram the attractors of $f$.
- An explicit ensemble of locally-monotone BNs $\mathbb F=\{ f^1,\cdots, f^m \}$.
- Any locally-monotone BN matching with a given *influence graph* $\mathcal G$: $\mathbb F = \{ f\mid G(f)\subseteq \mathcal G\}$. An influence graph is a signed digraph between components, i.e., of the form $(\{1,\cdots,n\},V)$ with $V\subseteq \{1,\cdots,n\}\times \{+1,-1\}\times \{1,\cdots n\}$. The influence graph of a BN $f$, denoted by $G(f)$ has an edge $i\xrightarrow{s} j$ if and only there exists a configuration $x\in\mathbb B^n$ such that $f_j(x_1, \ldots, x_{i-1}, 1, x_{i+1},\ldots, x_n) - f_j(x_1, \ldots, x_{i-1}, 0, x_{i+1},\ldots, x_n) = s$.
- Any locally-monotone BN matching with a partially-defined BN following the AEON framework <cite data-citep="Benes2021">(<a href="https://doi.org/10.1007/978-3-030-85633-5_14">Beneš et al., 2021</a>)</cite>.


