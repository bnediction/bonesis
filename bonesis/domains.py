
import os

from boolean import boolean
from colomoto import minibn
import networkx as nx

class BonesisDomain(object):
    pass

class BooleanNetwork(BonesisDomain, minibn.BooleanNetwork):
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

class InfluenceGraph(BonesisDomain, nx.MultiDiGraph):
    def __init__(self, graph,
            maxclause=None,
            allow_skipping_nodes=False,
            canonic=True):
        nx.MultiDiGraph.__init__(self, graph)
        # TODO: ensures graph is well-formed
        self.maxclause = maxclause
        self.allow_skipping_nodes = allow_skipping_nodes
        self.canonic = canonic

    @classmethod
    def complete(celf, n, sign=0, loops=True, **kwargs):
        g = nx.complete_graph(n, nx.DiGraph)
        for e in g.edges(data=True):
            e[2]["sign"] = sign
        if loops:
            for i in g:
                g.add_edge(i, i, sign=sign)
        return celf(g, **kwargs)

    @classmethod
    def all_on_one(celf, n, sign=1, **kwargs):
        g = nx.DiGraph()
        for i in range(n):
            g.add_edge(i, 0, sign=sign)
        return celf(g, **kwargs)
