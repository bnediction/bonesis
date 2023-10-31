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

import clingo
import os
import re
import tempfile

import boolean
import networkx as nx

from bonesis0.asp_encoding import *
from bonesis0.proxy_control import ProxyControl
from .domains import BooleanNetwork, BooleanNetworksEnsemble, InfluenceGraph

from .language import *
from .debug import dbg, debug_enabled

def s2v(s):
    return 1 if s > 0 else -1

clingo_encode = symbol_of_py

RE_ASP_FUNC = re.compile(r"(\w+)\(")
def apply_ns(rules, ns):
    def apply_ns_rule(r):
        return RE_ASP_FUNC.sub(f"{ns}\\1(", r)
    return list(map(apply_ns_rule, rules))


def unique_usage(method):
    name = method.__name__
    def wrapper(self, *args, **kwargs):
        key = (name, args, tuple(kwargs.items()))
        if key in self._silenced:
            return self._silenced[key]
        ret = method(self, *args, **kwargs)
        self._silenced[key] = ret
        return ret
    return wrapper

class ASPModel_DNF(object):
    default_constants = {
        "bounded_nonreach": 0,
    }
    def __init__(self, domain, data, manager, **constants):
        self.domain = domain
        self.data = data
        self.manager = manager
        self.constants = self.__class__.default_constants.copy()
        self.constants.update(constants)
        self.ba = boolean.BooleanAlgebra()
        self._silenced = {}
        self.__fresh_id = -1

    def solver(self, *args, ground=True, settings={}, **kwargs):
        arguments = []
        if not debug_enabled():
            arguments += ["-W", "no-atom-undefined"]
        arguments.extend(settings.get("clingo_options", ()))
        parallel = settings.get("parallel")
        if parallel:
            parallel = int(parallel)
            if parallel > 64:
                print("Warning: settings 'parallel' must be <= 64, Using 64.")
                parallel = 64
            arguments += ["-t", parallel]
        arguments.extend(args)
        arguments += [f"-c {const}={repr(value)}" for (const, value) \
                        in self.constants.items()]
        arguments = list(map(str,arguments))
        dbg(f"ProxyControl({arguments}, {kwargs})")
        control = ProxyControl(arguments, **kwargs)
        fd, progfile = tempfile.mkstemp(".lp", prefix="bonesis", text=True)
        try:
            with os.fdopen(fd, "w") as fp:
                fp.write(str(self))
            control.load(progfile)
        finally:
            os.unlink(progfile)
        if ground:
            control.ground([("base",())])
        return control

    def reset(self):
        self._silenced.clear()
        self.prefix = ""
        self.programs = {
            ("base", ()): "",
        }

    def make(self):
        self.reset()
        self.push(self.encode_domain(self.domain))
        self.push(self.encode_data(self.data))
        self.push(self.encode_properties(self.manager.properties))
        self.push(self.encode_optimizations(self.manager.optimizations))

    def __str__(self):
        s = self.prefix
        for (name, params), prog  in self.programs.items():
            fparams = f"({','.join(params)})" if params else ""
            s += f"#program {name}{fparams}.\n"
            s += prog
        return s

    def push(self, facts, progname="base", params=()):
        self.programs[(progname, params)] += string_of_facts(facts)

    def push_file(self, filename):
        with open(filename) as fp:
            self.prefix += fp.read()

    def fresh_atom(self, qualifier=""):
        self.__fresh_id += 1
        return clingo.Function(f"__bo{qualifier}{self.__fresh_id}")

    def encode_domain(self, domain):
        if hasattr(domain, "bonesis_encoder"):
            return getattr(domain, "bonesis_encoder")(self)
        if isinstance(domain, BooleanNetworksEnsemble):
            return self.encode_domain_BooleanNetworksEnsemble(domain)
        if isinstance(domain, BooleanNetwork):
            return self.encode_domain_BooleanNetwork(domain)
        if isinstance(domain, InfluenceGraph):
            return self.encode_domain_InfluenceGraph(domain)
        raise TypeError(f"I don't know what to do with {type(domain)}")

    def encode_domain_BooleanNetworksEnsemble(self, bns):
        preds = set()
        facts = []
        for i, bn in enumerate(bns):
            bn_asp = self.encode_domain_BooleanNetwork(bn)
            facts.extend([f"bn_ensemble({i},{f})" for f in bn_asp])
            preds.update([(f.name, len(f.arguments)) for f in bn_asp])
        facts.append(f"1{{which_bn(0..{len(bns)-1})}}1")
        for pname, arity in preds:
            args = [f"A{i}" for i in range(arity)]
            p = f"{pname}({','.join(args)})"
            facts.append(f"{p} :- which_bn(BN), bn_ensemble(BN,{p})")
        return facts

    def encode_domain_BooleanNetwork(self, bn):
        self.ba = bn.ba
        return [bn.asp_of_bn(encoding="dnf-bdd") + "\n" +
                str(asp.Function("nbnode", symbols(len(bn))))]

    def encode_domain_InfluenceGraph(self, pkn):
        self.load_template_domain()
        if pkn.canonic:
            self.load_template_canonic()
        facts = pkn_to_facts(pkn, pkn.maxclause, pkn.allow_skipping_nodes)
        if pkn.exact == "unsigned":
            self.load_template_edge()
            facts.append(":- in(L,N,_), not edge(L,N,_)")
        elif pkn.exact:
            self.load_template_edge()
            facts.append(":- in(L,N,S), not edge(L,N,S)")
        return facts

    def encode_obs_data(self, name, data):
        return [clingo.Function("obs", symbols(name, i, s2v(b)))
                for (i, b) in data.items() if b in (0,1,True,False)]

    def encode_data(self, data):
        facts = []
        for k, obs in data.items():
            facts.extend(self.encode_obs_data(k, obs))
        return facts

    @unique_usage
    def load_template_domain(self, ns="", allow_externals=False):
        rules = [
            "{clause(N,1..C,L,S): in(L,N,S), maxC(N,C), node(N)}" \
                if allow_externals else
                "{clause(N,1..C,L,S): in(L,N,S), maxC(N,C), node(N), node(L)}",
            ":- clause(N,_,L,S), clause(N,_,L,-S)",
            "1 { constant(N,(-1;1)) } 1 :- node(N), not clause(N,_,_,_)",
            "constant(N) :- constant(N,_)",
        ]
        if ns:
            rules = apply_ns(rules, ns)
        self.push(rules)

    @unique_usage
    def load_template_canonic(self, ns=""):
        rules = [
            "size(N,C,X) :- X = #count {L,S: clause(N,C,L,S)}; clause(N,C,_,_); maxC(N,_)",
            ":- clause(N,C,_,_); not clause(N,C-1,_,_); C > 1; maxC(N,_)",
            ":- size(N,C1,X1); size(N,C2,X2); X1 < X2; C1 > C2; maxC(N,_)",
            ":- size(N,C1,X); size(N,C2,X); C1 > C2; mindiff(N,C1,C2,L1) ; mindiff(N,C2,C1,L2) ; L1 < L2; maxC(N,_)",
            "clausediff(N,C1,C2,L) :- clause(N,C1,L,_);not clause(N,C2,L,_);clause(N,C2,_,_), C1 != C2; maxC(N,_)",
            "mindiff(N,C1,C2,L) :- clausediff(N,C1,C2,L); L <= L' : clausediff(N,C1,C2,L'), clause(N,C1,L',_), C1!=C2; maxC(N,_)",
            ":- size(N,C1,X1); size(N,C2,X2); C1 != C2; X1 <= X2; clause(N,C2,L,S) : clause(N,C1,L,S); maxC(N,_)",
        ]
        if ns:
            rules = apply_ns(rules, ns)
        self.push(rules)

    @unique_usage
    def load_template_edge(self, ns=""):
        rules = [
            "edge(L,N,S) :- clause(N,_,L,S)"
        ]
        if ns:
            rules = apply_ns(rules, ns)
        self.push(rules)

    @unique_usage
    def load_template_eval(self):
        rules = [
            "eval(X,N,C,-1) :- clause(N,C,L,-V), mcfg(X,L,V), not clamped(X,N,_)",
            "eval(X,N,C,1) :- mcfg(X,L,V): clause(N,C,L,V); clause(N,C,_,_), mcfg(X,_,_), not clamped(X,N,_)",
            "eval(X,N,1) :- eval(X,N,C,1), clause(N,C,_,_)",
            "eval(X,N,-1) :- eval(X,N,C,-1): clause(N,C,_,_); clause(N,_,_,_), mcfg(X,_,_)",
            "eval(X,N,V) :- clamped(X,N,V)",
            "eval(X,N,V) :- constant(N,V), mcfg(X,_,_), not clamped(X,N,_)",

            "eval(X,N,V) :- evalbdd(X,N,V), node(N), not clamped(X,N,_)",
            "evalbdd(X,V,V) :- mcfg(X,_,_), V=(-1;1)",
            "evalbdd(X,B,V) :- bdd(B,N,_,HI), mcfg(X,N,1), evalbdd(X,HI,V)",
            "evalbdd(X,B,V) :- bdd(B,N,LO,_), mcfg(X,N,-1), evalbdd(X,LO,V)",
            "evalbdd(X,B,V) :- mcfg(X,_,_), bdd(B,V)",

            "mcfg(X,N,V) :- ext(X,N,V)",
        ]
        self.push(rules)

    @unique_usage
    def load_template_cfg(self):
        rules = [
            "1 {cfg(X,N,(-1;1))} 1 :- cfg(X), node(N)",
        ]
        self.push(rules)

    @unique_usage
    def load_template_bind_cfg(self):
        rules = [
            "cfg(X,N,V) :- bind_cfg(X,O), obs(O,N,V), node(N)"
        ]
        self.push(rules)

    @unique_usage
    def load_template_bind_cfg_mutant(self):
        rules = [
            "cfg(X,N,V) :- bind_cfg(X,O,mutant(M)), obs(O,N,V), node(N), not mutant(M,N,_)",
            "cfg(X,N,V) :- bind_cfg(X,O,mutant(M)), obs(O,_,_), node(N), mutant(M,N,V), not weak_mutant(M,N,V)",
            # TODO: next rule should account for non-weak mutant on same node
            "cfg(X,N,V) :- bind_cfg(X,O,mutant(M)), obs(O,N,V), node(N), mutant(M,N,W), weak_mutant(M,N,W)"
        ]
        self.push(rules)

    def encode_bind_cfg(self, cfg, obs, mutant=None):
        args = (cfg, obs)
        if mutant is not None:
            self.load_template_bind_cfg_mutant()
            args = args + (clingo.Function("mutant", symbols(mutant)),)
        else:
            self.load_template_bind_cfg()
        return [clingo.Function("bind_cfg", symbols(*args))]

    @unique_usage
    def load_template_strong_constant(self):
        rules = [
            "weak_constant(N) :- cfg(X), node(N), constant(N,V), cfg(X,N,-V)",
            "strong_constant(N) :- node(N), constant(N), not weak_constant(N)",
        ]
        self.push(rules)

    @unique_usage
    def load_template_hypercube(self):
        rules = [
            "1 { hypercube(H,N,(-1;1;2)) } 1 :- hypercube(H), node(N)"
        ]
        self.push(rules)

    @unique_usage
    def load_template_bind_hypercube(self):
        rules = [
            "hypercube(H,N,V) :- bind_hypercube(H,O), obs(O,N,V), node(N)"
        ]
        self.push(rules)

    @unique_usage
    def saturating_configuration(self, fixed=None, free=None):
        cfgid = self.fresh_atom("cfg")
        free = f", {free}" if free else ""
        rules = [
            f"cfg({cfgid},N,-1); cfg({cfgid},N,1) :- node(N){free}",
            f"cfg({cfgid},N,-V) :- cfg({cfgid},N,V), saturate({cfgid}){free}",
            f"saturate({cfgid}) :- valid({cfgid},Z): expect_valid({cfgid},Z)",
            f":- not saturate({cfgid})",
        ]
        if fixed:
            rules.append(f"cfg({cfgid},N,V) :- node(N), {fixed}")
        self.push(rules)
        return cfgid

    def make_saturation_condition(self, satid):
        condid = self.fresh_atom("cond")
        condition = clingo.Function("valid", (satid, condid))
        self.push([clingo.Function("expect_valid", (satid, condid))])
        return condition

    def encode_argument(self, arg):
        if isinstance(arg, ConfigurationVar):
            return arg.name
        return arg

    def encode_properties(self, properties):
        facts = []
        for (name, args, kwargs) in properties:
            encoder = f"encode_{name}"
            if hasattr(self, encoder):
                facts.extend(getattr(self, encoder)(*args, **kwargs))
            else:
                if kwargs:
                    raise NotImplementedError(f"encode {name} with {kwargs}")
                tpl = f"load_template_{name}"
                if hasattr(self, tpl):
                    getattr(self, tpl)()
                args = tuple(map(self.encode_argument, args))
                facts.append(clingo.Function(name, symbols(*args)))
        return facts

    def encode_some(self, some):
        if some.dtype is None:
            raise TypeError(f"{some} has no type!")
        encoder = getattr(self, f"encode_some_{some.dtype.lower()}")
        return encoder(some.name, some.opts)

    def encode_some_different(self, s1, s2):
        for some in (s1, s2):
            if s1.dtype is None:
                raise TypeError(f"{some} has no type!")
        encoder = getattr(self, f"encode_some_{s1.dtype.lower()}_different")
        return encoder(s1, s2)

    def encode_some_freeze(self, name, opts):
        opts = SomeFreeze.default_opts | opts
        min_size = opts["min_size"]
        max_size = opts["max_size"]
        #TODO: user-specified domain
        exclude = opts["exclude"] or ()
        name = clingo_encode(name)
        rules = [
            f"{min_size}"
                f" {{ some_freeze({name},N,(1;-1)) : node(N) }}"
                f" {max_size}",
        ]
        for ex in exclude:
            assert isinstance(ex, str), "invalid exclude specification"
            ex = clingo_encode(ex)
            rules.append(f":- some_freeze({name},{ex},_)")
        if max_size > 1:
            rules += [
                f":- some_freeze({name},N,V), some_freeze({name},N,-V)"
            ]
        return rules

    def encode_some_freeze_different(self, s1, s2):
        n1 = clingo_encode(s1.name)
        n2 = clingo_encode(s2.name)
        ns = "some_freeze"
        return [
            f"{ns}_diff({n1},{n2}) :- {ns}({n1},N,V), {ns}({n2},N,-V)",
            f"{ns}_diff({n1},{n2}) :- {ns}({n1},N,_), not {ns}({n2},N,_)",
            f"{ns}_diff({n1},{n2}) :- not {ns}({n1},N,_), {ns}({n2},N,_)",
            f":- not {ns}_diff({n1},{n2})"
        ]

    def encode_mutant(self, name, mutations, pred="mutant"):
        if isinstance(mutations, Some):
            # copy 'Some' mutation
            name = clingo_encode(name)
            some = clingo_encode(mutations.name)
            return [f"{pred}({name},N,V) :- some_freeze({some},N,V)"]
        return [clingo.Function(pred, symbols(name, node, s2v(b)))
            for node, b in mutations.items()]

    def encode_weak_mutant(self, name, mutations):
        return self.encode_mutant(name, mutations, pred="weak_mutant")

    def apply_mutant_to_mcfg(self, mutant, mcfg):
        if mutant is None:
            return []
        return [f"clamped({mcfg},N,V) :- mutant({mutant},N,V)"]

    def encode_fixpoint(self, cfg, mutant=None):
        self.load_template_eval()
        myfp = self.fresh_atom("fp")
        cfgid = clingo_encode(cfg.name)
        rules = [
            # trigger eval
            f"mcfg({myfp},N,V) :- cfg({cfgid},N,V)",
            # check fixed point constraint
            f":- cfg({cfgid},N,V), eval({myfp},N,-V)"
        ] + self.apply_mutant_to_mcfg(mutant, myfp)
        return rules

    def encode_trapspace(self, cfg, mutant=None):
        self.load_template_eval()
        myts = self.fresh_atom("ts")
        cfgid = clingo_encode(cfg.name)
        rules = [
            # minimal trap space containing cfg
            f"mcfg({myts},N,V) :- cfg({cfgid},N,V)",
            f"mcfg({myts},N,V) :- eval({myts},N,V)",
            # trap space constraint
            f":- obs({clingo_encode(cfg.obs.name)},N,V), mcfg({myts},N,-V)",
        ] + self.apply_mutant_to_mcfg(mutant, myts)
        return rules

    def encode_hypercube(self, h):
        self.load_template_hypercube()
        H = clingo_encode(h.name)
        rules = [f"hypercube({H})" ]
        if h.min_dimension >= 1:
            rules.append(f":- #count {{ N: hypercube({H},N,2) }}"
                                        f"{h.min_dimension-1}")
        if h.max_dimension:
            rules.append(f":- {max_dimension+1} #count {{ N: hypercube({H},N,2) }}")
        return rules

    def encode_in_attractor(self, cfg, mutant=None):
        self.load_template_eval()

        X = clingo_encode(cfg.name)
        Z = self.fresh_atom("ts")

        Y = self.saturating_configuration(
                free=f"mcfg({Z},N,1),mcfg({Z},N,-1)",
                fixed=f"mcfg({Z},N,V),not mcfg({Z},N,-V)")
        T = self.fresh_atom("ts")
        condition = self.make_saturation_condition(Y)
        rules = [
            # minimal trap space containing X
            f"mcfg({Z},N,V) :- cfg({X},N,V)",
            f"mcfg({Z},N,V) :- eval({Z},N,V)",
            # minimal trap space containing Y
            f"mcfg({T},N,V) :- cfg({Y},N,V)",
            f"mcfg({T},N,V) :- eval({T},N,V)",
            # Z is a subset of T
            f"{condition} :- mcfg({T},N,V): mcfg({Z},N,V), node(N)",
        ] + self.apply_mutant_to_mcfg(mutant, Z)\
          + self.apply_mutant_to_mcfg(mutant, T)
        return rules

    def encode_attractor(self, h, mutant=None):
        self.load_template_eval()
        H = clingo_encode(h.name)
        Z = self.fresh_atom("ts")
        Y = self.saturating_configuration(
                free=f"hypercube({H},N,2)",
                fixed=f"hypercube({H},N,V), V!=2")
        T = self.fresh_atom("ts")
        condition = self.make_saturation_condition(Y)
        rules = [
            f"attractor({H})",

            # ensure H is closed
            f"mcfg({Z},N,V) :- hypercube({H},N,V), V != 2",
            f"mcfg({Z},N,1) :- hypercube({H},N,2)",
            f"mcfg({Z},N,-1) :- hypercube({H},N,2)",
            f":- eval({Z},N,V), not mcfg({Z},N,V)",

            # minimal trap space containing Y
            f"mcfg({T},N,V) :- cfg({Y},N,V)",
            f"mcfg({T},N,V) :- eval({T},N,V)",

            # Z is a subset of T
            f"{condition} :- mcfg({T},N,V): mcfg({Z},N,V),node(N)",
        ] + self.apply_mutant_to_mcfg(mutant, Z)\
          + self.apply_mutant_to_mcfg(mutant, T)
        return rules

    def encode_reach(self, cfg1, cfg2, mutant=None,
                     monotone=False,
                     max_changes=None):
        self.load_template_eval()
        Z = self.fresh_atom("reach")
        X = clingo_encode(cfg1.name)
        Y = clingo_encode(cfg2.name)
        rules = [
            # init mcfg
            f"mcfg({Z},N,V) :- cfg({X},N,V)",
            # extensions
            f"ext({Z},N,V) :- eval({Z},N,V), cfg({Y},N,V)",
            # constraints
            f":- cfg({Y},N,V), not mcfg({Z},N,V)",
            f":- cfg({Y},N,V), ext({Z},N,-V), not ext({Z},N,V)",
        ] + self.apply_mutant_to_mcfg(mutant, Z)
        if not monotone:
            rules += [
            f"{{ext({Z},N,V)}} :- eval({Z},N,V), cfg({Y},N,-V)"
            ]
        if isinstance(max_changes, int) and max_changes > 0:
            rules += [
                f":- {max_changes+1} #count {{ N: ext({Z},N,V),cfg({X},N,-V) }}"
            ]
        return rules

    def encode_nonreach(self, cfg1, cfg2, mutant=None, bounded="auto"):
        self.load_template_eval()
        Z = self.fresh_atom("nonreach")
        X = clingo_encode(cfg1.name)
        Y = clingo_encode(cfg2.name)
        rules = [
            f"mcfg(({Z},1..K),N,V) :- reach_steps({Z},K), cfg({X},N,V)",
            f"ext(({Z},I),N,V) :- eval(({Z},I),N,V), not locked(({Z},I),N)",
            f"reach_bad({Z},I,N) :- cfg({X},N,V), cfg({Y},N,V), ext(({Z},I),N,-V), not ext(({Z},I),N,V)",
            f"locked(({Z},I+1..K),N) :- reach_bad({Z},I,N), reach_steps({Z},K), I < K",
            f"nr_ok({Z}) :- reach_steps({Z},K), cfg({Y},N,V), not mcfg(({Z},K),N,V)",
            f":- not nr_ok({Z})",
        ]
        if bounded == "auto":
            rules += [
                f"reach_steps({Z},K) :- nbnode(K), bounded_nonreach <= 0",
                f"reach_steps({Z},bounded_nonreach) :- bounded_nonreach > 0",
            ]
        else:
            rules += [f"reach_steps({Z},{bounded})"]
        if mutant is not None:
            rules += [f"clamped(({Z},1..K),N,V) :- mutant({mutant},N,V), reach_steps({Z},K)"]
        return rules

    def encode_final_nonreach(self, cfg1, cfg2, mutant=None):
        return self.encode_nonreach(cfg1, cfg2, mutant=mutant, bounded=1)

    def encode_all_fixpoints(self, arg, mutant=None,
            _condition=None):
        self.load_template_eval()
        satcfg = self.saturating_configuration()
        mycfg = self.fresh_atom("cfg")
        condition = _condition or self.make_saturation_condition(satcfg)

        def make_cond(target):
            if isinstance(target, ObservationVar):
                from_pred = "obs"
            elif isinstance(target, ConfigurationVar):
                from_pred = "cfg"
            return f"{condition} :- cfg({satcfg},N,V): {from_pred}({clingo_encode(target.name)},N,V), node(N)"

        rules = [
            # trigger eval
            f"mcfg({mycfg},N,V) :- cfg({satcfg},N,V)",
            # not a fixed a point
            f"{condition} :- cfg({satcfg},N,V), eval({mycfg},N,-V)",
        ] + [
            make_cond(target) for target in arg
        ] + self.apply_mutant_to_mcfg(mutant, mycfg)
        return rules

    def encode_all_attractors_overlap(self, arg, mutant=None,
            _condition=None):
        self.load_template_eval()
        satcfg = self.saturating_configuration()
        mycfg = self.fresh_atom("cfg")
        condition = _condition or self.make_saturation_condition(satcfg)

        def make_cond(target):
            if isinstance(target, ObservationVar):
                from_pred = "obs"
            elif isinstance(target, ConfigurationVar):
                from_pred = "cfg"
            return f"{condition} :- mcfg({mycfg},N,V): {from_pred}({clingo_encode(target.name)},N,V), node(N)"

        rules = [
            # minimal trap space containing cfg
            f"mcfg({mycfg},N,V) :- cfg({satcfg},N,V)",
            f"mcfg({mycfg},N,V) :- eval({mycfg},N,V)",
        ] + [
            # contain at least one given observation
            make_cond(target) for target in arg
        ] + self.apply_mutant_to_mcfg(mutant, mycfg)
        return rules

    def encode_allreach(self, options, left, right, mutant=None):
        if isinstance(left, ConfigurationVar):
            left = (left,)

        self.load_template_eval()
        satcfg = self.saturating_configuration()
        condition = self.make_saturation_condition(satcfg)

        args = [right]
        kwargs = {"mutant": mutant,
            "_condition": condition}
        if "attractors_overlap" in options:
            rules = self.encode_all_attractors_overlap(*args, **kwargs)
        elif "fixpoints" in options:
            rules = self.encode_all_fixpoints(*args, **kwargs)
        else:
            raise TypeError(f"invalid options {options}")

        # satcfg is not reachable from one of the initial configurations (left)
        for cfg in left:
            cfgid = clingo_encode(cfg.name)
            mcfg0 = self.fresh_atom("cfg")
            rules += [
                # minimal trap space containing cfg
                f"mcfg({mcfg0},N,V) :- cfg({cfgid},N,V)",
                f"mcfg({mcfg0},N,V) :- eval({mcfg0},N,V)",
                # satcfg is not in it
                f"{condition} :- cfg({satcfg},N,V), not mcfg({mcfg0},N,V)",
            ]
            rules += self.apply_mutant_to_mcfg(mutant, mcfg0)
        return rules

    def encode_cfg_assign(self, cfg, node, b, mutant=None):
        return [clingo.Function("cfg", symbols(cfg.name, node, s2v(b)))]

    def encode_constant(self, node, b, mutant=None):
        return [clingo.Function("constant", symbols(node, s2v(b)))]

    def encode_cfg_node_eq(self, cfg1, cfg2, node, mutant=None):
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        n = clingo_encode(node)
        return [
            f":- node({n}), cfg({c1},{n},V), cfg({c2},{n},-V)"
        ]

    def encode_cfg_node_ne(self, cfg1, cfg2, node, mutant=None):
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        n = clingo_encode(node)
        return [
            f":- node({n}), cfg({c1},{n},V), cfg({c2},{n},V)"
        ]

    def encode_different(self, cfg1, right, mutant=None):
        if isinstance(right, ConfigurationVar):
            pred = "cfg"
        elif isinstance(right, ObservationVar):
            pred = "obs"
        else:
            raise NotImplementedError
        right_name = f"{pred}{right.name}"
        diff = clingo.Function("diff", symbols(cfg1.name, right_name))
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(right.name)
        return [
            f"{diff} :- node(N), cfg({c1},N,V), {pred}({c2},N,-V)",
            f":- not {diff}"
        ]

    def encode_custom(self, code):
        return [code.strip().rstrip(".")]

    def encode_opt_nodes(self, opt, priority):
        return [f"#{opt} {{ 1@{priority},N: node(N) }}"]
    def encode_opt_constants(self, priority):
        return [f"#{opt} {{ 1@{priority},N: constant(N) }}"]
    def encode_opt_strong_constants(self, opt, priority):
        self.load_template_strong_constant()
        return [f"#{opt} {{ 1@{priority},N: strong_constant(N) }}"]

    def encode_optimizations(self, optimizations):
        rules = []
        for i, (opt, obj) in enumerate(reversed(optimizations)):
            encoder = f"encode_opt_{obj}"
            rules += getattr(self, encoder)(opt, (i+1)*10)
        return rules

    show = {
        "boolean_network":
            ["clause/4", "constant/2"],
        "configuration":
            ["cfg/3"],
        "node":
            ["node/1"],
        "constant":
            ["constant/1"],
        "strong_constant":
            ["strong_constant/1"],
        "some":
            ["some_freeze/3"]
    }

    @staticmethod
    def minibn_of_json_facts(str_facts):
        fs = map(clingo.parse_term, str_facts)
        return minibn_of_facts(fs)

    @staticmethod
    def influence_graph_from_model(atoms):
        nodes = (py_of_symbol(a.arguments[0]) for a in atoms\
                    if a.name == "node")
        def make_edge(e):
            a, b, s = e
            return (a, b, {"sign": s, "label": "+" if s > 0 else "-"})
        edges = (make_edge(py_of_symbol(a)) for a in atoms\
                    if a.name == "edge")
        g = nx.DiGraph()
        g.add_nodes_from(nodes)
        g.add_edges_from(edges)
        return g
