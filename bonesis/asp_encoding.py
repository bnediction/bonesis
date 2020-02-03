
import clingo
import os
import tempfile

from bonesis0.asp_encoding import *
from bonesis0.utils import aspf
from bonesis0.proxy_control import ProxyControl
from .domains import BooleanNetwork, InfluenceGraph

def s2v(s):
    return 1 if s > 0 else -1

def unique_usage(method):
    name = method.__name__
    def nothing(*args, **kwargs):
        pass
    def wrapper(self, *args, **kwargs):
        setattr(self, f"__save_{name}", method)
        setattr(self, name, nothing)
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

    def solver(self, *args, **kwargs):
        self.make()
        arguments = list(map(str,args)) + \
            [f"-c {const}={repr(value)}" for (const, value) in self.constants.items()]
        control = ProxyControl(arguments, **kwargs)
        fd, progfile = tempfile.mkstemp(".lp", prefix="bonesis", text=True)
        try:
            with os.fdopen(fd, "w") as fp:
                fp.write(str(self))
            control.load(progfile)
        finally:
            os.unlink(progfile)
        control.ground([("base",())])
        return control

    def make(self):
        self.prefix = ""
        self.programs = {
            ("base", ()): "",
        }
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

    def load_template(self, name):
        getattr(self, f"load_template_{name}")()

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
            self.push_file(asp("canonical-bn.asp"))
        return pkn_to_facts(pkn, pkn.maxclause, pkn.allow_skipping_nodes)

    def encode_data(self, data):
        facts = []
        for k, obs in data.items():
            for (n, b) in obs.items():
                if b not in [0,1]:
                    continue
                facts.append(clingo.Function("obs", [k, n, s2v(b)]))
        return facts

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

    def encode_properties(self, manager):
        facts = []
        for (name, args) in manager.properties:
            self.load_template(name)
            facts.append(clingo.Function(name, args))
        return facts
