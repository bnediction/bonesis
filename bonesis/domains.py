
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
            canonic=False):
        nx.MultiDiGraph.__init__(self, graph)
        # TODO: ensures graph is well-formed
        self.maxclause = maxclause
        self.allow_skipping_nodes = allow_skipping_nodes
        self.canonic = canonic
