
import clingo as asp

from scipy.special import binom

from functools import reduce


def py_of_symbol(symb):
    if symb.type is asp.SymbolType.String:
        return symb.string
    if symb.type is asp.SymbolType.Number:
        return symb.number
    if symb.type is asp.SymbolType.Function:
        return tuple(map(py_of_symbol, symb.arguments))
    raise ValueError

def string_of_facts(facts):
    if not facts:
        return ""
    return "{}.\n".format(".\n".join(map(str,facts)))

def print_facts(facts):
    if facts:
        print(string_of_facts(facts))

def nb_clauses(d):
    return int(binom(d, d//2))

def pkn_to_facts(pkn, maxclause=None, allow_skipping_nodes=False):
    facts = []
    if not allow_skipping_nodes:
        facts.append(asp.Function("nbnode", [asp.Number(len(pkn.nodes()))]))
        for n in pkn.nodes():
            facts.append(asp.Function("node", (n,)))
    else:
        facts.append("nbnode(NB) :- NB = #count{N: node(N)}")
        for n in pkn.nodes():
            facts.append("{{{}}}".format(asp.Function("node", (n,))))
    for (orig, dest, data) in pkn.edges(data=True):
        if data["sign"] in ["ukn","?","0",0]:
            args = asp.Tuple((orig, dest)).arguments
            f = "in({},{},(-1;1))".format(*args)
            facts.append(f)
        else:
            ds = data["sign"]
            if ds in ["-","+"]:
                ds += "1"
            s = int(ds)
            facts.append(asp.Function("in", (orig, dest, s)))
    def bounded_nb_clauses(d):
        nbc = nb_clauses(d)
        if maxclause:
            nbc = min(maxclause, nbc)
        return nbc
    for n, i in pkn.in_degree(pkn.nodes()):
        facts.append(asp.Function("maxC", (n, bounded_nb_clauses(i))))
    return facts

def obs_to_facts(pstate, obsid):
    return [asp.Function("obs", [obsid, n, 2*v-1]) for (n,v) in pstate.items()]

def dnfs_of_facts(fs):
    bn = {}
    for d in fs:
        if d.name == "clause":
            (i,cid,lit,sign) = list(map(py_of_symbol, d.arguments))
            if i not in bn:
                bn[i] = []
            if cid > len(bn[i]):
                bn[i] += [set() for j in range(cid-len(bn[i]))]
            bn[i][cid-1].add((sign,lit))
        elif d.name == "constant" and len(d.arguments) == 2:
            (i,v) = list(map(py_of_symbol, d.arguments))
            bn[i] = v == 1
    return bn

from colomoto.minibn import BooleanNetwork
def minibn_of_facts(fs):
    dnfs = dnfs_of_facts(fs)
    bn = BooleanNetwork()
    def make_lit(l):
        s,v=l
        v = bn.v(v)
        if s < 0:
            v = ~v
        return v
    def make_clause(ls):
        ls = list(map(make_lit, ls))
        if len(ls) == 1:
            return ls[0]
        return bn.ba.AND(*ls)
    def make_dnf(cs):
        if isinstance(cs, bool):
            return cs
        cs = filter(len, cs)
        cs = list(map(make_clause, cs))
        if len(cs) == 1:
            return cs[0]
        return bn.ba.OR(*cs)
    for (node, cs) in sorted(dnfs.items()):
        bn[node] = make_dnf(cs)
    return bn

def configurations_of_facts(fs):
    cfgs = {}
    for a in fs:
        if a.name != "cfg":
            continue
        cid, n, v = a.arguments
        n = n.string
        v = v.number
        cid = py_of_symbol(cid)
        if cid not in cfgs:
            cfgs[cid] = {}
        cfgs[cid][n] = max(v, 0)
    return cfgs

