
import clingo
import os
import tempfile

from bonesis0.asp_encoding import *
from bonesis0.utils import aspf
from bonesis0.proxy_control import ProxyControl
from .domains import BooleanNetwork, InfluenceGraph

from .language import ConfigurationVar
from .debug import dbg

def s2v(s):
    return 1 if s > 0 else -1

def clingo_encode(val):
    return clingo.Function("", (val,)).arguments[0]

def unique_usage(method):
    name = method.__name__
    def wrapper(self, *args, **kwargs):
        if name in self._silenced:
            return
        self._silenced.add(name)
        return method(self, *args, **kwargs)
    return wrapper

class ASPModel_DNF(object):
    default_constants = {
        "bounded_nonreach": 3,
    }
    def __init__(self, domain, data, properties, **constants):
        self.domain = domain
        self.data = data
        self.properties = properties
        self.constants = self.__class__.default_constants.copy()
        self.constants.update(constants)
        self._silenced = set()

    def solver(self, *args, ground=True, settings={}, **kwargs):
        arguments = []
        arguments.extend(settings.get("clingo_options", ()))
        if "parallel" in settings:
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
        self.push(self.encode_properties(self.properties))

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

    def encode_domain(self, domain):
        if isinstance(domain, BooleanNetwork):
            return self.encode_domain_BooleanNetwork(domain)
        elif isinstance(domain, InfluenceGraph):
            return self.encode_domain_InfluenceGraph(domain)
        raise TypeError(f"I don't know what to do with {type(domain)}")

    def encode_domain_BooleanNetwork(self, bn):
        def clauses_of_dnf(f):
            if f == bn.ba.FALSE:
                return [False]
            if f == bn.ba.TRUE:
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
        for n, f in bn.items():
            facts.append(clingo.Function("node", [n]))
            for cid, c in enumerate(clauses_of_dnf(f)):
                if isinstance(c, bool):
                    facts.append(clingo.Function("constant", [n, s2v(c)]))
                else:
                    for m, v in literals_of_clause(c):
                        facts.append(clingo.Function("clause", [n, cid,m, v]))
        return facts

    def encode_domain_InfluenceGraph(self, pkn):
        self.push_file(aspf("bn-domain.asp"))
        if pkn.canonic:
            self.push_file(aspf("canonical-bn.asp"))
        facts = pkn_to_facts(pkn, pkn.maxclause, pkn.allow_skipping_nodes)
        if pkn.exact:
            self.load_template_edge()
            facts.append(":- X = #count { L,N,S: edge(L,N,S)}, \
                            Y = #count { L,N,S: in(L,N,S)}, X != Y")
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
    def load_template_fixpoint(self):
        self.load_template_eval()
        self.push_file(aspf("fixpoint.asp"))

    @unique_usage
    def load_template_trapspace(self):
        self.load_template_eval()
        self.push_file(aspf("trapspace.asp"))

    @unique_usage
    def load_template_attractor(self):
        self.load_template_eval()
        self.push_file(aspf("attractor.asp"))

    @unique_usage
    def load_template_cfg(self):
        rules = [
            "1 {cfg(X,N,(-1;1))} 1 :- cfg(X), node(N)"
        ]
        self.push(rules)

    @unique_usage
    def load_template_bind_cfg(self):
        rules = [
            "cfg(X,N,V) :- bind_cfg(X,O), obs(O,N,V), node(N)"
        ]
        self.push(rules)

    def encode_argument(self, arg):
        if isinstance(arg, ConfigurationVar):
            return arg.name
        return arg

    def encode_properties(self, manager):
        facts = []
        for (name, args) in manager.properties:
            encoder = f"encode_{name}"
            if hasattr(self, encoder):
                facts.extend(getattr(self, encoder)(*args))
            else:
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

    def encode_constant(self, node, b):
        return [clingo.Function("constant", (node, s2v(b)))]

    def encode_in_attractor(self, cfg):
        self.load_template_attractor()
        return [clingo.Function("is_at", (cfg.name,))]

    def encode_different(self, cfg1, cfg2):
        diff = clingo.Function("diff", (cfg1.name, cfg2.name))
        c1 = clingo_encode(cfg1.name)
        c2 = clingo_encode(cfg2.name)
        return [
            f"{diff} :- node(N), cfg({c1},N,V), cfg({c2},N,-V)",
            f":- not {diff}"
        ]

    show = {
        "boolean_network":
            ["clause/4", "constant/2"],
        "configuration":
            ["cfg/3"],
        "node":
            ["node/1"],
        "constant":
            ["constant/1"],
    }
