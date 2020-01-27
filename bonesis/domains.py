
import os

from boolean import boolean
import clingo
from colomoto import minibn

def s2v(s):
    return 1 if s > 0 else -1

class _BonesisDomain(object):
    pass

class BooleanNetwork(_BonesisDomain, minibn.BooleanNetwork):
    def __init__(self, bn):
        if isinstance(bn, str):
            if "\n" in bn or not os.path.exists(bn):
                bn = minibn.BooleanNetwork(bn)
            else:
                bn = minibn.BooleanNetwork.load(bn)
        elif isinstance(bn, dict):
            bn = minibn.BooleanNetwork(bn)
        assert isinstance(bn, minibn.BooleanNetwork)
        super().__init__()
        self.ba = bn.ba
        for n, f in bn.items():
            self[n] = self.ba.dnf(f).simplify()

    def asp_rules(self):
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
        for n, f in self.items():
            facts.append(clingo.Function("node", [n]))
            for cid, c in enumerate(clauses_of_dnf(f)):
                if isinstance(c, bool):
                    facts.append(clingo.Function("constant", [n, s2v(c)]))
                else:
                    for m, v in literals_of_clause(c):
                        facts.append(clingo.Function("clause", [n, cid,m, v]))
        return facts

class InfluenceGraph(_BonesisDomain):
    def __init__(self, ig):
        self.ig = ig

