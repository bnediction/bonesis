# Declarative language for dynamical properties

## Summary

In the scope of a `BoNesis(dom, data)`{l=python} object, the following methods are
defined.

``````{list-table}
:header-rows: 1
:widths: 15 40

* - Objects
  -

* - *Observations*
  - Mapping a subset of components to a Boolean value
* - `O = obs({a: 1, b: 0, ...})`{l=python}
  - Observation from partial mapping of components to `0`{l=python} or `1`{l=python} (`dict`-like object)
* - `O = obs("name")`{l=python}
  - Named observation defined in the `data`{l=py} dictionnary

* - **Properties**
  -

* - *Attractors*
  - (recall that MP attractors are minimal trap spaces of the BN)
* - `fixed(C)`{l=python}
  - Configuration `C`{l=python} is a fixed point
* - `fixed(O)`{l=python}
  - There exists a trap space where observation `O`{l=python} is fixed
* - `in_attractor(C)`{l=python}
  - Configuration `C`{l=python} belongs to an attractor

``````


## Objects

### Observations

## Properties

## Contexts

