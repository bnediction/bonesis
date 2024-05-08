# Declarative language for dynamical properties

## Summary

In the scope of a `BoNesis(dom, data)`{l=python} object, the following methods are defined.

### Objects

#### <span style="color:purple">Observation</span>:
maps a subset of components to a Boolean value

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:purple">O</span> = obs({<span style="color:olive">a</span>:0, <span style="color:olive">b</span>:1,..})</code></td>
    <td style="padding: 0px 8px;">Observation from partial mapping of components to <code>0</code> or <code>1</code> (<code>dict</code>-like object)</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:purple">O</span> = obs("name")</code></td>
    <td style="padding: 0px 8px;">Named observation defined in the <code>data</code> dictionary</td>
  </tr>
</table>


#### <span style="color:blue">Configuration</span>:
maps each component to a Boolean value

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> = cfg()</code></td>
    <td style="padding: 0px 8px;">Allocates a fresh configuration</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> = +<span style="color:purple">O</span></code></td>
    <td style="padding: 0px 8px;">Fresh configuration matching with the observation <code><span style="color:purple">O</span></code></td>
  </tr>
  <tr style="border-bottom: 1px solid black;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> = ~<span style="color:purple">O</span></code></td>
    <td style="padding: 0px 8px;">Default configuration matching with the observation <code><span style="color:purple">O</span></code></td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:green">S</span> = Some(max_size=k)</code></td>
    <td style="padding: 0px 8px;">Represents a mutation of at most <code>k</code> components.<br/>
      Use <code><span style="color:green">S</span>.assignments()</code> to get satisfying valuations.</td>
  </tr>
</table>


### Properties

#### Constraints on configurations

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> != <span style="color:blue">C'</span></code></td>
    <td style="padding: 0px 8px;">The configurations <code><span style="color:blue">C</span></code> and <code><span style="color:blue">C'</span></code> differ on at least one component</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><nobr><code><span style="color:blue">C</span>[<span style="color:olive">a</span>] == <span style="color:blue">C'</span>[<span style="color:olive">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr><br/>
        <nobr><code><span style="color:blue">C</span>[<span style="color:olive">a</span>] != <span style="color:blue">C'</span>[<span style="color:olive">b</span>] <span style="color:gray">|</span> 0 <span style="color:gray">|</span> 1</code></nobr></td>
    <td style="padding: 0px 8px;">The state of the component <code><span style="color:olive">a</span></code> in the configuration <code><span style="color:blue">C</span></code> is equal (resp. different) to the state of the component <code><span style="color:olive">b</span></code> in the configuration <code><span style="color:blue">C'</span></code> (resp. 0 and 1)</td>
  </tr>
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> != <span style="color:purple">O</span></code></td>
    <td style="padding: 0px 8px;">The configuration <code><span style="color:blue">C</span></code> does not match with the observation <code><span style="color:purple">O</span></code></td>
  </tr>
</table>


#### Attractor properties

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code>fixed(<span style="color:blue">C</span>)</code></td>
    <td style="padding: 0px 8px;">The configuration <code><span style="color:blue">C</span></code> is a fixed point</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code>fixed(<span style="color:purple">O</span>)</code></td>
    <td style="padding: 0px 8px;">There exists a trap space where observation <code><span style="color:purple">O</span></code> is fixed</td>
  </tr>
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code>in_attractor(<span style="color:blue">C</span>)</code></td>
    <td style="padding: 0px 8px;">The configuration <code><span style="color:blue">C</span></code> belongs to an attractor</td>
  </tr>
</table>


#### Reachability

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> >= <span style="color:blue">C'</span></code> or <code>reach(<span style="color:blue">C</span>,<span style="color:blue">C'</span>)</code></td>
    <td style="padding: 0px 8px;">There exists an MP trajectory from the configuration <code><span style="color:blue">C</span></code> to the configuration <code><span style="color:blue">C'</span></code></td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> >= <span style="color:purple">O</span></code></td>
    <td style="padding: 0px 8px;">... to a configuration matching with the observation <code><span style="color:purple">O</span></code> (equiv to <code><span style="color:blue">C</span> >= +<span style="color:purple">O</span></code>)</td>
  </tr>
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> >= fixed(<span style="color:purple">O</span>)</code></td>
    <td style="padding: 0px 8px;">... to a configuration in a trap space where the observation <code><span style="color:purple">O</span></code> is fixed</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td colspan="2" style="padding: 0px 8px; font-style: italic;">Note: can be composed, e.g., <code><span style="color:blue">C1</span> >= <span style="color:blue">C2</span> >= fixed(<span style="color:blue">C3</span>)</code></td>
  </tr>
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code><span style="color:blue">C</span> / _</code> or <code>nonreach(<span style="color:blue">C</span>, _)</code></td>
    <td style="padding: 0px 8px;">Absence of MP trajectory from the configuration <code><span style="color:blue">C</span></code> to ... (same as reach)</td>
  </tr>
</table>


#### Universal properties

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;"><code>all_fixpoints({<span style="color:purple">O</span>,<span style="color:purple">O'</span>,..})</code></td>
    <td style="padding: 0px 8px;">All the fixed points match with at least one given observation</td>
  </tr>
  <tr style="background-color: #EEEEEE;">
    <td style="padding: 0px 8px; border-right: 1px solid black;">
    <code><span style="color:blue">C</span> >> "fixpoints" ^ {<span style="color:purple">O</span>,<span style="color:purple">O'</span>,..}</code></td>
    <td style="padding: 0px 8px;">All the fixed points reachable from the configuration <code>C</code> ...</td>
  </tr>
</table>


### Contexts

<table style="margin-left: 0 !important; margin-right: auto !important;">
  <tr>
    <td style="padding: 0px 8px; border-right: 1px solid black;">
      <nobr><code>with mutant({<span style="color:olive">a</span>:0,..} <span style="color:gray">|</span> <span style="color:green">S</span>):</code></nobr><br>
      <code>&nbsp;&nbsp;&nbsp;&nbsp;...</code>
    </td>
    <td style="padding: 0px 8px;">The properties within the <code>with</code> block are subject to mutation specified by <code>{<span style="color:olive">a</span>:0,..}</code> (resp. <code><span style="color:green">S</span></code>)</td>
  </tr>
</table>
