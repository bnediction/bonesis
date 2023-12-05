# Copyright or © or Copr. Loïc Paulevé (2023)
#
# loic.pauleve@cnrs.fr
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#


from colomoto import minibn

import networkx as nx
from functools import reduce

import bonesis

def prune_domain_for_marker(f, M):
    def get_doi(g):
        return reduce(set.union, (nx.ancestors(g, m) for m in M), set(M))
    if isinstance(f, minibn.BooleanNetwork):
        keep = get_doi(f.influence_graph())
        return f.__class__({i: f[i] for i in keep})
    else:
        return f.subgraph(get_doi(f))

def marker_reprogramming_fixpoints(f, M, k, at_least_one=True, **some_opts):
    bo = bonesis.BoNesis(f)
    control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(control):
        if at_least_one:
            bo.fixed(~bo.obs(M))
        bo.all_fixpoints(bo.obs(M))
    return control.assignments()

def source_marker_reprogramming_fixpoints(f, z, M, k, at_least_one=True,
        **some_opts):
    bo = bonesis.BoNesis(f)
    control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(control):
        if at_least_one:
            ~bo.obs(z) >= bo.fixed(~bo.obs(M))
        ~bo.obs(z) >> "fixpoints" ^ {bo.obs(M)}
    return control.assignments()

def trapspace_reprogramming(f, M, k, algorithm="cegar", **some_opts):
    """
    Marker/Trapspace reprogramming of BN domain `f`.

    Returns mutations which ensure that all the minimal trap spaces match with
    the given marker `M`.
    """
    f = prune_domain_for_marker(f, M)
    if algorithm == "cegar":
        meth = _trapspace_reprogramming_cegar
    else:
        meth = _trapspace_reprogramming_complementary
    return meth(f, M, k, **some_opts)

marker_reprogramming = trapspace_reprogramming


def _trapspace_reprogramming_complementary(f, M, k, **some_opts):
    bo = bonesis.BoNesis(f)
    bad_control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(bad_control):
        x = bo.cfg()
        bo.in_attractor(x) != bo.obs(M)
    return bad_control.complementary_assignments()

def source_marker_reprogramming(f, z, M, k, **some_opts):
    f = prune_domain_for_marker(f, M)
    bo = bonesis.BoNesis(f)
    bad_control = bo.Some(max_size=k, **some_opts)
    with bo.mutant(bad_control):
        x = bo.cfg()
        ~bo.obs(z) >= bo.in_attractor(x) != bo.obs(M)
    return bad_control.complementary_assignments()


###
### CEGAR-based implementations
###

from bonesis.views import SomeView

def _trapspace_reprogramming_cegar(dom, M, k, **some_opts):
    data = {"M": M}

    bo = bonesis.BoNesis(dom, data)
    P = bo.Some(max_size=k, **some_opts)
    with bo.mutant(P):
        # there exists at least one minimal trap spaces matching M
        bo.fixed(bo.obs("M"))

    class BoCegar(SomeView):
        single_shot = False
        project = False
        ice = 0
        def __iter__(self):
            self.configure()
            return self

        def __next__(self):
            while True:
                with self.control.solve(yield_=True) as candidates:
                    found_P = False
                    for candidate in candidates:
                        found_P = True
                        P = self.parse_model(candidate)

                        ## check candidate
                        boc = bonesis.BoNesis(dom, data)
                        with boc.mutant(P):
                            x = boc.cfg()
                            boc.in_attractor(x)
                            x != boc.obs("M")
                        view = x.assignments(limit=1)
                        view.configure()
                        if (ce := next(iter(view.control.solve(yield_=True)), None)) is not None:
                            self.ice += 1
                            x = [a for a in ce.symbols(shown=True)
                                    if a.name == "cfg" and a.arguments[0].string == "__cfg0"]
                        else:
                            p = candidate.symbols(shown=True)
                        break

                    if not found_P:
                        raise StopIteration

                if ce is None:
                    inject = f":- {','.join(map(str, p))}."
                    self.control.add("skip", [], inject)
                    self.control.ground([("skip", [])])
                    return P
                ns = f"_ce{self.ice}_"
                cets = f"{ns}ts"
                fixts = f"{ns}fix"
                inject = [f"mcfg({cets},{a.arguments[1]},{a.arguments[2]})." for a in x]
                inject += [
                        # compute trap space of counter example
                        f"mcfg({cets},N,V) :- {ns}eval({cets},N,V).",
                        f"clamped({cets},N,V) :- mutant(_,N,V).",
                        # choose sub-space in it
                        f"1 {{mcfg({fixts},N,V):mcfg({cets},N,V)}} :- mcfg({cets},N,_).",
                        # saturate it
                        f"mcfg({fixts},N,V) :- {ns}eval({fixts},N,V).",
                        f"clamped({fixts},N,V) :- clamped({cets},N,V).",

                        f"{ns}eval(X,N,C,-1) :- clause(N,C,L,-V), mcfg(X,L,V), not clamped(X,N,_).",
                        f"{ns}eval(X,N,C,1) :- mcfg(X,L,V): clause(N,C,L,V); clause(N,C,_,_), mcfg(X,_,_), not clamped(X,N,_).",
                        f"{ns}eval(X,N,1) :- {ns}eval(X,N,C,1), clause(N,C,_,_).",
                        f"{ns}eval(X,N,-1) :- {ns}eval(X,N,C,-1): clause(N,C,_,_); clause(N,_,_,_), mcfg(X,_,_).",
                        f"{ns}eval(X,N,V) :- clamped(X,N,V).",
                        f"{ns}eval(X,N,V) :- constant(N,V), mcfg(X,_,_), not clamped(X,N,_).",

                        f"{ns}eval(X,N,V) :- {ns}evalbdd(X,N,V), node(N), not clamped(X,N,_).",
                        f"{ns}evalbdd(X,V,V) :- mcfg(X,_,_), V=(-1;1).",
                        f"{ns}evalbdd(X,B,V) :- bdd(B,N,_,HI), mcfg(X,N,1), {ns}evalbdd(X,HI,V).",
                        f"{ns}evalbdd(X,B,V) :- bdd(B,N,LO,_), mcfg(X,N,-1), {ns}evalbdd(X,LO,V).",
                        f"{ns}evalbdd(X,B,V) :- mcfg(X,_,_), bdd(B,V).",
                    ]
                # TS(y) must match with M
                inject.append(f":- obs(\"M\",N,V), mcfg({fixts},N,-V).")
                inject = "\n".join(inject)
                self.control.add(f"cegar{ns}", [], inject)
                self.control.ground([(f"cegar{ns}", [])])

    return BoCegar(P, bo, solutions="subset-minimal")
