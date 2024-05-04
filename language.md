# Declarative language

## Summary

In the scope of a `BoNesis(dom, data)`{l=python} object, the following methods are
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

`O = obs({a: 1, b: 1, ...})`{l=python}

</td><td>

Observation from partial mapping of components to `0`{l=python} or `1`{l=python} (`dict`-like object)

</td></tr><tr><td>

`O = obs("name")`{l=python}

</td><td>

Named observation defined in the `data`{l=py} dictionnary

</td></tr>

<tr><th colspan="2">

Properties

</th>
</tr><td colspan="2">

*Attractors*

</td></tr>
<tr><td>

`fixed(C)`{l=python}

</td><td>

Configuration `C`{l=python} is a fixed point

</td></tr><tr><td>

`fixed(O)`{l=python}

</td><td>

There exists a trap space where observation `O`{l=python} is fixed

</td></tr><tr><td>

`in_attractor(C)`{l=python}

</td><td>

Configuration `C`{l=python} belongs to an attractor

</table>


## Objects

### Observations

## Properties

## Contexts

