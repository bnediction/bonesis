# Declarative language for dynamical properties

## Summary

In the scope of a `BoNesis(dom, data)`{l=python} object, the following methods are defined.

### Objects

#### <span class="obs">Observation</span>:
maps a subset of components to a Boolean value

<table class="language">
  <tr>
    <td><code><span class="obs">O</span> = obs({<span class="bokey">a</span>:0, <span class="bokey">b</span>:1,..})</code></td>
    <td>Observation from partial mapping of components to <code>0</code> or <code>1</code> (<code>dict</code>-like object)</td>
  </tr>
  <tr>
    <td><code><span class="obs">O</span> = obs("name")</code></td>
    <td><code>data</code> dictionary</td>
  </tr>
</table>


#### <span class="cfg">Configuration</span>:
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
  <tr>
    <td><code><span class="some">S</span> = Some(max_size=k)</code></td>
    <td>Represents a mutation of at most <code>k</code> components.<br/>
      Use <code><span class="some">S</span>.assignments()</code> to get satisfying valuations.</td>
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
