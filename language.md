# Declarative language

## Summary

In the scope of a `BoNesis(dom, data)` object, the following methods are
defined.

<table class="table">
<tr><th colspan="2">

Objects

</th>
</tr><td colspan="2">

*Observations*

</td>
</tr>
<tr><td>

`O = obs({a: 1, b: 1, ...})`

</td><td>

Observation from partial mapping of components to `0` or `1` (`dict`-like object)

</td></tr><tr><td>

`O = obs("name")`

</td><td>

Named observation defined in the `data` dictionnary

</td></tr>

<tr><th colspan="2">

Properties

</th>
</tr><td colspan="2">

*Attractors*

</td></tr>
<tr><td>

`fixed(C)`

</td><td>

Configuration `C` is a fixed point

</td></tr><tr><td>

`fixed(O)`

</td><td>

There exists a trap space where observation `O` is fixed

</td></tr><tr><td>

`in_attractor(C)`

</td><td>

Configuration `C` belongs to an attractor

</table>


## Objects

### Observations

## Properties

## Contexts

