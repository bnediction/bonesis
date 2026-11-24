# Declarative language for dynamical properties

## Summary


```{note}
This document summarizes (most of) constraints that can be specified with BoNesis.
Do not hesitate to open a discussion or an issue on our [GitHub project](https://github.com/bnediction/bonesis) to suggest new language features, or ask for help on how to express your desired properties.
```

In the scope of a `BoNesis(dom, data)` object, the following methods are defined.

### Objects

#### <span class="obs">Observation</span>

{code .obs}`TEST`

:::{table} <span class="obs">Observation</span>: maps a subset of components to a Boolean value
:class: language

|  |  |
| --- | --- |
| `O ` ` = obs({a:0, b:1, ...})` | Observation from partial mapping of components to `0` or `1` (`dict`-like object) |
| `O = obs("name")` | Observation from partial mapping given by `data["name"]` |

:::


#### <span class="cfg">Configuration</span>
maps each component to a Boolean value

<table class="language">
  <tr>
    <td><code><span class="cfg">C</span> = cfg()</code></td>
    <td>Allocates a fresh configuration</td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> = +<span class="obs">O</span></code></td>
    <td>Fresh configuration matching with the observation <code><span class="obs">O</span></code></td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> = ~<span class="obs">O</span></code></td>
    <td>Default configuration matching with the observation <code><span class="obs">O</span></code></td>
  </tr>
</table>

#### <span class="dyncfg">Dynamic configuration</span>

maps each component to either a Boolean value or a most permissive dynamic state (see [](theory/most-permissive.md)) . Currently, there is no way to enforce the type of dynamic state, nor to prevent a component to be assigned to a Boolean value.

Dynamic configurations are, by definition, *transient* configurations. They are
useful to account for intermediary states that cannot be modeled as Boolean
zRlue.

<table class="language">
  <tr>
    <td><code><span class="dyncfg">D</span> = dyncfg()</code></td>
    <td>Allocates a dynamical configurations</td>
  </tr>
  <tr>
    <td><code><span class="dyncfg">D</span> = dyncfg(<span class="obs">O</span>)</code></td>
    <td>Dynamical configuration matching with the observation <code><span class="obs">O</span></code></td>
  </tr>
</table>

Dynamic configurations can be used in place of (Boolean) configurations in all the constraints.
Note that whenever it is involved in a fixed point constraint (`fixed(D)`), all components will necessarily be assigned to a Boolean state.

#### <span class="some">Variable</span>

<table class="language">
  <tr>
    <td><code><span class="some">S</span> = Some(max_size=k, exclude=(), domain=())</code></td>
    <td>Represents a mutation of at most <code>k</code> (default: <code>1</code>) components.<br>
      Use <code><span class="some">S</span>.assignments()</code> to get satisfying valuations.<br>
      Options <code>exclude</code> and <code>domain</code> can be used to restrict the components to consider.
      </td>
  </tr>
</table>


### Properties

#### Constraints on configurations

<table class="language">
  <tr>
    <td><code><span class="cfg">C</span> != <span class="cfg">C'</span></code></td>
    <td>The configurations <code><span class="cfg">C</span></code> and <code><span class="cfg">C'</span></code> differ on at least one component</td>
  </tr>
  <tr>
    <td><nobr><code><span class="cfg">C</span>[<span class="bokey">a</span>] == <span class="cfg">C'</span>[<span class="bokey">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr><br/>
    <td rowspan="2">The state of the component <code><span class="bokey">a</span></code> in the configuration <code><span class="cfg">C</span></code> is equal (resp. different) to the state of the component <code><span class="bokey">b</span></code> in the configuration <code><span class="cfg">C'</span></code> (resp. 0 and 1)</td>
    </tr>
    <tr>
    <td>
        <nobr><code><span class="cfg">C</span>[<span class="bokey">a</span>] != <span class="cfg">C'</span>[<span class="bokey">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr></td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> != <span class="obs">O</span></code></td>
    <td>The configuration <code><span class="cfg">C</span></code> does not match with the observation <code><span class="obs">O</span></code></td>
  </tr>
</table>


#### Attractor properties

<table class="language">
  <tr>
    <td><code>fixed(<span class="cfg">C</span>)</code></td>
    <td>The configuration <code><span class="cfg">C</span></code> is a fixed point</td>
  </tr>
  <tr>
    <td><code>fixed(<span class="obs">O</span>)</code></td>
    <td>There exists a trap space where observation <code><span class="obs">O</span></code> is fixed</td>
  </tr>
  <tr>
    <td><code>in_attractor(<span class="cfg">C</span>)</code></td>
    <td>The configuration <code><span class="cfg">C</span></code> belongs to an attractor</td>
  </tr>
</table>


#### Reachability

<table class="language">
  <tr>
    <td><code><span class="cfg">C</span> >= <span class="cfg">C'</span></code> or <code>reach(<span class="cfg">C</span>,<span class="cfg">C'</span>)</code></td>
    <td>There exists an MP trajectory from the configuration <code><span class="cfg">C</span></code> to the configuration <code><span class="cfg">C'</span></code></td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> >= <span class="obs">O</span></code></td>
    <td>... to a configuration matching with the observation <code><span class="obs">O</span></code> (equiv to <code><span class="cfg">C</span> >= +<span class="obs">O</span></code>)</td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> >= fixed(<span class="obs">O</span>)</code></td>
    <td>... to a configuration in a trap space where the observation <code><span class="obs">O</span></code> is fixed</td>
  </tr>
  <tr>
    <td colspan="2" style="border: none; font-style: italic;">Note: can be composed, e.g., <code><span class="cfg">C1</span> >= <span class="cfg">C2</span> >= fixed(<span class="cfg">C3</span>)</code></td>
  </tr>
  <tr>
    <td><code><span class="cfg">C</span> / _</code> or <code>nonreach(<span class="cfg">C</span>, _)</code></td>
    <td style="padding: 0px 8px;">Absence of MP trajectory from the configuration <code><span class="cfg">C</span></code> to ... (same as reach)</td>
  </tr>
</table>


#### Universal properties

<table class="language">
  <tr>
    <td><code>all_fixpoints({<span class="obs">O</span>,<span class="obs">O'</span>,..})</code></td>
    <td>All the fixed points match with at least one given observation</td>
  </tr>
  <tr>
    <td>
    <code><span class="cfg">C</span> >> "fixpoints" ^ {<span class="obs">O</span>,<span class="obs">O'</span>,..}</code></td>
    <td>All the fixed points reachable from the configuration <code>C</code> ...</td>
  </tr>
</table>


### Contexts

<table class="language">
  <tr>
    <td>
      <nobr><code>with mutant({<span class="bokey">a</span>:0,..} <span style="color:gray">|</span> <span class="some">S</span>):</code></nobr><br>
      <code>&nbsp;&nbsp;&nbsp;&nbsp;...</code>
    </td>
    <td>The properties within the <code>with</code> block are subject to mutation specified by <code>{<span class="bokey">a</span>:0,..}</code> (resp. <code><span class="some">S</span></code>)</td>
  </tr>
</table>

### Optimizations

<table class="language">
<tr>
    <td><code>maximize_nodes()</code></td>
    <td>Maximize the number of nodes in the Boolean network (to be used in
    conjunction with option `allow_skipping_nodes=True` of `InfluenceGraph`)</td>
</tr>
<tr id="maximize-constants">
    <td><code>maximize_constants()</code></td>
    <td>Maximize the number of nodes having a constant Boolean function</td>
</tr>
<tr id="maximize-strong-constants">
    <td><code>maximize_strong_constants()</code></td>
    <td>Maximize the number of nodes having a constant Boolean function and being assigned to this constant in all defined configurations.</td>
</tr>
</table>
