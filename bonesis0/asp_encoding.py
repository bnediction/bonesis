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

import os

import clingo as asp
clingo_Tuple = asp.Tuple_ if hasattr(asp, "Tuple_") else asp.Tuple

from scipy.special import binom

from functools import reduce

from mpbn import MPBooleanNetwork

def py_of_symbol(symb):
    if symb.type is asp.SymbolType.String:
        return symb.string
    if symb.type is asp.SymbolType.Number:
        return symb.number
    if symb.type is asp.SymbolType.Function:
        return tuple(map(py_of_symbol, symb.arguments))
    raise ValueError

def symbol_of_py(obj):
    if isinstance(obj, str):
        return asp.String(obj)
    elif isinstance(obj, int):
        return asp.Number(obj)
    elif isinstance(obj, tuple):
        return clingo_Tuple([symbol_of_py(o) for o in obj])
    return obj

def symbols(*objs):
    return [symbol_of_py(obj) for obj in objs]

def portfolio_path(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
            f"{name}.cfg")

def parse_nb_threads(opt):
    if opt is None:
        return 0
    if isinstance(opt, str):
        opt = int(opt.split(",")[0])
    return opt

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
        facts.append(asp.Function("nbnode", symbols(len(pkn.nodes()))))
        for n in pkn.nodes():
            facts.append(asp.Function("node", symbols(n)))
    else:
        facts.append("nbnode(NB) :- NB = #count{N: node(N)}")
        for n in pkn.nodes():
            facts.append("{{{}}}".format(asp.Function("node", symbols(n))))
    for (orig, dest, data) in pkn.edges(data=True):
        if data["sign"] in ["ukn","?","0",0]:
            args = symbols(orig, dest)
            f = "in({},{},(-1;1))".format(*args)
            facts.append(f)
        else:
            ds = data["sign"]
            if ds in ["-","+"]:
                ds += "1"
            s = int(ds)
            facts.append(asp.Function("in", symbols(orig, dest, s)))
    def bounded_nb_clauses(d):
        nbc = nb_clauses(d)
        if maxclause:
            nbc = min(maxclause, nbc)
        return nbc
    for n, i in pkn.in_degree(pkn.nodes()):
        facts.append(asp.Function("maxC", symbols(n, bounded_nb_clauses(i))))
    facts += pkn.rules
    return facts

def obs_to_facts(pstate, obsid):
    return [asp.Function("obs", [obsid, n, 2*v-1]) for (n,v) in pstate.items()]

def dnfs_of_facts(fs, ns=""):
    bn = {}
    clause_func = f"{ns}clause"
    constant_func = f"{ns}constant"
    for d in fs:
        if d.name == clause_func:
            (i,cid,lit,sign) = list(map(py_of_symbol, d.arguments))
            if i not in bn:
                bn[i] = []
            if cid > len(bn[i]):
                bn[i] += [set() for j in range(cid-len(bn[i]))]
            bn[i][cid-1].add((sign,lit))
        elif d.name == constant_func and len(d.arguments) == 2:
            (i,v) = list(map(py_of_symbol, d.arguments))
            bn[i] = v == 1
    return bn

def minibn_of_facts(fs, ns=""):
    dnfs = dnfs_of_facts(fs, ns=ns)
    bn = MPBooleanNetwork()
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

def configurations_of_facts(fs, pred="cfg", keys="auto"):
    cfgs = {}
    auto_keys = keys == "auto"
    select = [] if auto_keys else (None if keys == "all" else keys)
    for a in fs:
        if a.name != pred:
            continue
        arity = len(a.arguments)
        if arity == 1 and auto_keys:
            select.append(py_of_symbol(a.arguments[0]))
            continue
        if arity != 3:
            continue
        cid, n, v = a.arguments
        n = n.string
        v = v.number
        cid = py_of_symbol(cid)
        if cid not in cfgs:
            cfgs[cid] = {}
        cfgs[cid][n] = max(v, 0)
    if select is not None:
        return {k: cfgs[k] for k in select}
    return cfgs
