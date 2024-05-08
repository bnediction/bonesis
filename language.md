# Declarative language for dynamical properties

## Summary

In the scope of a `BoNesis(dom, data)`{l=python} object, the following methods are defined.

### Objects

**<span style="color:magenta">Observation</span>**: maps a subset of components to a Boolean value.

<table>
  <tr>
    <td><code><span style="color:magenta">O</span> = obs({<span style="color:olive">a</span>:0, <span style="color:olive">b</span>:1,..})</code></td>
    <td>Observation from partial mapping of components to <code>0</code> or <code>1</code> (<code>dict</code>-like object)</td>
  </tr>
  <tr>
    <td><code><span style="color:magenta">O</span> = obs("name")</code></td>
    <td>Named observation defined in the <code>data</code>dictionary</td>
  </tr>
</table>

**<span style="color:blue">Configuration</span>**: maps each component to a Boolean value.

<table>
  <tr>
    <td><code><span style="color:blue">C</span> = cfg()</code></td>
    <td>Allocates a fresh configuration</td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> = +<span style="color:magenta">O</span></code></td>
    <td>Fresh configuration matching with the observation <code><span style="color:magenta">O</span></code></td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> = ~<span style="color:magenta">O</span></code></td>
    <td>Default configuration matching with the observation <code><span style="color:magenta">O</span></code></td>
  </tr>
  <tr>
    <td><code><span style="color:green">S</span> = Some(max_size=k)</code></td>
    <td>Represents a mutation of at most <code>k</code> components.<br/>
      Use <code><span style="color:green">S</span>.assignments()</code> to get satisfying valuations.</td>
  </tr>
</table>

### Properties

**Constraints on configurations**

<table>
  <tr>
    <td><code><span style="color:blue">C</span> != <span style="color:blue">C'</span></code></td>
    <td>The configurations <code><span style="color:blue">C</span></code> and <code><span style="color:blue">C'</span></code> differ on at least one component</td>
  </tr>
  <tr>
    <td><nobr><code><span style="color:blue">C</span>[<span style="color:olive">a</span>] == <span style="color:blue">C'</span>[<span style="color:olive">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr><br/>
        <nobr><code><span style="color:blue">C</span>[<span style="color:olive">a</span>] != <span style="color:blue">C'</span>[<span style="color:olive">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr></td>
    <td>The state of the component <code><span style="color:olive">a</span></code> in the configuration <code><span style="color:blue">C</span></code> is equal (resp. different) to the state of the component <code><span style="color:olive">b</span></code> in the configuration <code><span style="color:blue">C'</span></code> (resp. 0 and 1)</td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> != <span style="color:magenta">O</span></code></td>
    <td>The configuration <code><span style="color:blue">C</span></code> does not match with the observation <code><span style="color:magenta">O</span></code></td>
  </tr>
</table>

**Attractor properties**

<table>
  <tr>
    <td><code>fixed(<span style="color:blue">C</span>)</code></td>
    <td>The configuration <code><span style="color:blue">C</span></code> is a fixed point</td>
  </tr>
  <tr>
    <td><code>fixed(<span style="color:magenta">O</span>)</code></td>
    <td>There exists a trap space where observation <code><span style="color:magenta">O</span></code> is fixed</td>
  </tr>
  <tr>
    <td><code>in_attractor(<span style="color:blue">C</span>)</code></td>
    <td>The configuration <code><span style="color:blue">C</span></code> belongs to an attractor</td>
  </tr>
</table>

**Reachability**

<table>
  <tr>
    <td><code><span style="color:blue">C</span> >= <span style="color:blue">C'</span></code> or <code>reach(<span style="color:blue">C</span>,<span style="color:blue">C'</span>)</code></td>
    <td>There exists an MP trajectory from the configuration <code><span style="color:blue">C</span></code> to the configuration <code><span style="color:blue">C'</span></code></td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> >= <span style="color:magenta">O</span></code></td>
    <td>... to a configuration matching with the observation <code><span style="color:magenta">O</span></code> (equiv to <code><span style="color:blue">C</span> >= +<span style="color:magenta">O</span></code>)</td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> >= fixed(<span style="color:magenta">O</span>)</code></td>
    <td>... to a configuration in a trap space where the observation <code><span style="color:magenta">O</span></code> is fixed</td>
  </tr>
  <tr>
    <td colspan="2">Note: can be composed, e.g., <code><span style="color:blue">C1</span> >= <span style="color:blue">C2</span> >= fixed(<span style="color:blue">C3</span>)</code></td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> / _</code> or <code>nonreach(<span style="color:blue">C</span>, _)</code></td>
    <td>Absence of MP trajectory from the configuration <code><span style="color:blue">C</span></code> to ... (same as reach)</td>
  </tr>
</table>

**Universal properties**

<table>
  <tr>
    <td><code>all_fixpoints({<span style="color:magenta">O</span>,<span style="color:magenta">O'</span>,..})</code></td>
    <td>All the fixed points match with at least one given observation</td>
  </tr>
  <tr>
    <td><code><span style="color:blue">C</span> >> "fixpoints" ^ {<span style="color:magenta">O</span>,<span style="color:magenta">O'</span>,..}</code></td>
    <td>All the fixed points reachable from the configuration <code>C</code> ...</td>
  </tr>
</table>

### Contexts

<table>
  <tr>
    <td>
      <nobr><code>with mutant({<span style="color:olive">a</span>:0,..} <span style="color:gray">|</span> <span style="color:green">S</span>):</code></nobr><br>
      <code>&nbsp;&nbsp;&nbsp;&nbsp;...</code>
    </td>
    <td>The properties within the <code>with</code> block are subject to mutation specified by <code>{<span style="color:olive">a</span>:0,..}</code> (resp. <code><span style="color:green">S</span></code>)</td>
  </tr>
</table>
