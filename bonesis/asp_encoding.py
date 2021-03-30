
import clingo
import os
import tempfile

import boolean

from bonesis0.asp_encoding import *
from bonesis0.utils import aspf
from bonesis0.proxy_control import ProxyControl
from .domains import BooleanNetwork, InfluenceGraph

from .language import *
from .debug import dbg

def s2v(s):
    return 1 if s > 0 else -1

def clingo_encode(val):
    return clingo.Function("", (val,)).arguments[0]

def unique_usage(method):
    name = method.__name__
    def wrapper(self, *args, **kwargs):
        key = name
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
        arguments.extend(settings.get("clingo_options", ()))
        if settings.get("parallel"):
            arguments += ["-t", settings["parallel"]]
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
        if isinstance(domain, BooleanNetwork):
            return self.encode_domain_BooleanNetwork(domain)
        elif isinstance(domain, InfluenceGraph):
            return self.encode_domain_InfluenceGraph(domain)
        raise TypeError(f"I don't know what to do with {type(domain)}")

    def encode_BooleanFunction(self, n, f, ensure_dnf=True):
        def clauses_of_dnf(f):
            if f == self.ba.FALSE:
                return [False]
            if f == self.ba.TRUE:
                return [True]
            if isinstance(f, boolean.OR):
                return f.args
            else:
                return [f]
        def literals_of_clause(c):
            def make_literal(l):
                if isinstance(l, boolean.NOT):
                    return (l.args[0].obj, -1)
                else:
                    return (l.obj, 1)
            lits = c.args if isinstance(c, boolean.AND) else [c]
            return map(make_literal, lits)
        facts = []
        if ensure_dnf:
            f = self.ba.dnf(f).simplify()
        for cid, c in enumerate(clauses_of_dnf(f)):
            if isinstance(c, bool):
                facts.append(clingo.Function("constant", [n, s2v(c)]))
            else:
                for m, v in literals_of_clause(c):
                    facts.append(clingo.Function("clause", [n, cid+1, m, v]))
        return facts

    def encode_domain_BooleanNetwork(self, bn):
        self.ba = bn.ba
        facts = []
        facts.append(asp.Function("nbnode", [asp.Number(len(bn))]))
        for n, f in bn.items():
            facts.append(clingo.Function("node", [n]))
            facts += self.encode_BooleanFunction(n, f, ensure_dnf=False)
        return facts

    def encode_domain_InfluenceGraph(self, pkn):
        self.push_file(aspf("bn-domain.asp"))
        if pkn.canonic:
            self.push_file(aspf("canonical-bn.asp"))
        facts = pkn_to_facts(pkn, pkn.maxclause, pkn.allow_skipping_nodes)
        if pkn.exact:
            self.load_template_edge()
            facts.append(":- in(L,N,S), not edge(L,N,S)")
        return facts

    def encode_data(self, data):
        facts = []
        for k, obs in data.items():
            for (n, b) in obs.items():
                if b not in [0,1]:
                    continue
                facts.append(clingo.Function("obs", [k, n, s2v(b)]))
        return facts

    @unique_usage
    def load_template_edge(self):
        rules = [
            "edge(L,N,S) :- clause(N,_,L,S)"
        ]
        self.push(rules)

    @unique_usage
    def load_template_eval(self):
        self.push_file(aspf("eval.asp"))

    @unique_usage
    def load_template_reach(self):
        self.load_template_eval()
        self.push_file(aspf("reach.asp"))

    @unique_usage
    def load_template_nonreach(self):
        self.load_template_eval()
        self.push_file(aspf("nonreach.asp"))

    @unique_usage
    def load_template_final_nonreach(self):
        self.load_template_nonreach()
        rules = [
            "nonreach(X,Y,1) :- final_nonreach(X,Y)",
        ]
        self.push(rules)

    @unique_usage
    def load_template_fixpoint(self):
        self.load_template_eval()
        self.push_file(aspf("fixpoint.asp"))

    @unique_usage
    def load_template_trapspace(self):
        self.load_template_eval()
        self.push_file(aspf("trapspace.asp"))

    @unique_usage
    def load_template_cfg(self):
        rules = [
            "1 {cfg(X,N,(-1;1))} 1 :- cfg(X), node(N)",
            "cfg(X,N,V) :- cfg(X), node(N), clamped(X,N,V)",
            "clamped(do_not_use,do_not_use,do_not_use)",
        ]
        self.push(rules)

    @unique_usage
    def load_template_bind_cfg(self):
        rules = [
            "cfg(X,N,V) :- bind_cfg(X,O), obs(O,N,V), node(N), not clamped(X,N,_)"
        ]
        self.push(rules)


    @unique_usage
    def load_template_strong_constant(self):
        rules = [
            "weak_constant(N) :- cfg(X), node(N), constant(N,V), cfg(X,N,-V)",
            "strong_constant(N) :- node(N), constant(N), not weak_constant(N)",
        ]
        self.push(rules)

    @unique_usage
    def saturating_configuration(self):
        cfgid = self.fresh_atom("cfg")
        rules = [
            f"cfg({cfgid},N,-1); cfg({cfgid},N,1) :- node(N)",
            f"cfg({cfgid},N,-V) :- cfg({cfgid},N,V), saturate({cfgid})",
            f"saturate({cfgid}) :- valid({cfgid},Z): expect_valid({cfgid},Z)",
            f":- not saturate({cfgid})",
        ]
        self.push(rules)
        return cfgid

    def make_saturation_condition(self, satid):
        condid = self.fresh_atom("cond")
        condition = clingo.Function("valid", (satid, condid))
        self.push([clingo.Function("expect_valid", (satid, condid))])
        return condition

    @unique_usage
    def load_template_all_attractors(self):
        self.load_template_eval()
        self.push_file(aspf("QBF-attractor.asp"))

    @unique_usage
    def load_template_allreach_fixpoints(self):
        self.load_template_eval()
        self.push_file(aspf("QBF-reachable-fixpoint.asp"))

    @unique_usage
    def load_template_allreach_attractors(self):
        self.load_template_eval()
        self.push_file(aspf("QBF-reachable-attractor.asp"))

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
                facts.append(clingo.Function(name, args))
        return facts

    def encode_fixpoint(self, cfg):
        self.load_template_fixpoint()
        return [clingo.Function("is_fp", (cfg.name,))]

    def encode_trapspace(self, cfg):
        self.load_template_trapspace()
        return [clingo.Function("is_tp", (cfg.name,n)) \
                    for n in self.data[cfg.obs.name]]

    def encode_all_fixpoints(self, arg, mutant=None):
        self.load_template_eval()
        satcfg = self.saturating_configuration()
        mycfg = self.fresh_atom("cfg")
        condition = self.make_saturation_condition(satcfg)
        rules = [
            # trigger eval
            f"mcfg({mycfg},N,V) :- cfg({satcfg},N,V)",
            # not a fixed a point
            f"{condition} :- cfg({satcfg},N,V), eval({mycfg},N,-V)",
        ] + [
            # match one given observation
            f"{condition} :- cfg({satcfg},N,V): obs({clingo_encode(obs.name)},N,V)"
                for obs in arg]
        if mutant is not None:
            rules.append(f"clamped({mycfg},N,V) :- mutant({mutant},N,V)")
        return rules

    def encode_mutant(self, name, mutations):
        mutant = clingo_encode(name)
        return [clingo.Function("mutant", (mutant, node, s2v(b)))
            for node, b in mutations.items()]

    def encode_all_attractors(self, arg):
        self.load_template_all_attractors()
        return [clingo.Function("is_global_at", ((clingo.Function("obs"), obs.name),))
                for obs in arg]

    def encode_allreach(self, options, left, right):
        if "attractors_contain" in options:
            self.load_template_allreach_attractors()
            pred = "is_global_at"
        elif "fixpoints" in options:
            self.load_template_allreach_fixpoints()
            pred = "is_global_fp"
        else:
            raise TypeError(f"invalid options {options}")
        if isinstance(left, ConfigurationVar):
            left = {left}
        return [clingo.Function(pred, ((clingo.Function("obs"), obs.name), cfg.name))
                    for obs in right for cfg in left]

    def encode_cfg_assign(self, cfg, node, b):
        return [clingo.Function("cfg", (cfg.name, node, s2v(b)))]

    def encode_clamped(self, cfg, node, b):
        return [clingo.Function("clamped", (cfg.name, node, s2v(b)))]

    def encode_constant(self, node, b):
        return [clingo.Function("constant", (node, s2v(b)))]

    def encode_cfg_node_eq(self, cfg1, cfg2, node):
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        n = clingo_encode(node)
        return [
            f":- node({n}), cfg({c1},{n},V), cfg({c2},{n},-V)"
        ]

    def encode_cfg_node_ne(self, cfg1, cfg2, node):
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        n = clingo_encode(node)
        return [
            f":- node({n}), cfg({c1},{n},V), cfg({c2},{n},V)"
        ]

    def encode_different(self, cfg1, cfg2):
        diff = clingo.Function("diff", (cfg1.name, cfg2.name))
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        return [
            f"{diff} :- node(N), cfg({c1},N,V), cfg({c2},N,-V)",
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
    }
