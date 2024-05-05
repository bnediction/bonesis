# Boolean networks

## Basic definition

A Boolean network (BN) of dimension $n$ is specified by a function $f: \mathbb B^n\to\mathbb B^n$ where $\mathbb B = \{0,1\}$ is the Boolean domain. For $i\in \{1,\cdots,n\}$, $f_i:\mathbb B^n\to\mathbb B$ is referred to as the *local function* of the *component* $i$.

The Boolean vectors $x\in\mathbb B^n$ are called *configurations*, where for any $i\in\{1,\cdots,n\}$, $x_i$ denotes the *state* of component $i$ in the configuration $x$.

## Vocabulary

Vocabulary of objects related to BNs varies within scientific communities. 
In the scope of this documentation, we use use the following terms:

- **Components**, also known as *nodes* (of the network), or *variables*.
- **Configuration**,  also known as *state*, or *point*.
    Associates to each component of the network a Boolean state.
    It can be represented by a binary vector $\mathbf x$ of dimension $n$. Then
    $\mathbf x_i$ refers to the state of the component $i$.
- **Influence graph**, also known as interaction graph. See below.

## Influence graph

The *influence graph* of a BN $f$ is a signed directed graph $(\{1,\cdots,n\}, E_+,E_-)$ between its components. It captures the dependencies of local functions.
Intuitively, a component $i$ influence on a component $j$ if there exists a
configuration in which the sole modification of the state of $i$ changes the the
result of the local function $f_j$.
Formally,
- $i \xrightarrow+ j$ (i.e., $(i,j)\in E_+$) if and only if there exists a configuration $x$ such that $f_i(x_1,\cdots,x_{i-1},0,x_{i+1},\cdots,x_n) < f_i(x_1,\cdots,x_{i-1},1,x_{i+1},\cdots,x_n)$.
- $i \xrightarrow- j$ (i.e., $(i,j)\in E_-$) if and only if there exists a configuration $x$ such that $f_i(x_1,\cdots,x_{i-1},0,x_{i+1},\cdots,x_n) > f_i(x_1,\cdots,x_{i-1},1,x_{i+1},\cdots,x_n)$.

## Locally-monotone Boolean networks

A BN $f$ is *locally monotone* whenever every of its local functions are *unate*: for each $i\in\{1,\cdots,n\}$, there exists an ordering of components $\preceq^i\in \{\leq, \geq\}^n$ such that $\forall x,y\in \mathbb B^n$, $(x_1\preceq^i_1 y_1 \wedge \cdots \land x_n\preceq^i_n y_n) \implies f_i(x) \leq f_i(y)$. Intuitively, a BN is locally monotone whenever each of its local function can be expressed in propositional logic such that each variable appears either never or always with the same sign. For instance $f_1(x) = x_1\vee (\neg x_3 \wedge x_2)$ is unate, whereas $f_1(x) = x_2 \oplus x_3 = (x_2\wedge\neg x_3)\vee (\neg x_2\wedge x_3)$ is not unate.

*Example.* The BN $f$ of dimension $3$ with $f_1(x)=\neg x_2$, $f_2(x)=\neg x_1$, and $f_3(x) = \neg x_1\wedge x_2$ is locally monotone; and an instance of application is $f(000)=110$.

Equivalently, a BN $f$ is unate if and only if its influence graph $G(f)$ is has
no double-signed edges, i.e., there is no pair of components $(i,j)$ such that
$i\xrightarrow+j$ and $i\xrightarrow-j$.

Locally monotone BNs should not be confused with *monotone* BNs where a component appears in *all* local functions with the same sign. Monotone BNs are a particular case of locally-monotone BNs.

## Mutations

Mutations reflect knock-outs and constitutive activation of genes, possibly combined.
Mathematically, a mutation can be specified by a map associating a set of components to a Boolean value, for instance, $M = \{ 2 \mapsto 0, 4 \mapsto 1\}$. Given a mutation $M$, the *mutated BN* $f/M$ is given by, for each component $i\in \{1,\cdots,n\}$:

$$
(f/M)_i(x) = \begin{cases}
b & \text{ if }i \mapsto b \in M\\
f_i(x) & \text{otherwise.}
\end{cases}
$$
