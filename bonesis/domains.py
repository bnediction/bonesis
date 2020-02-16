
import os
import tempfile

from boolean import boolean
from colomoto import minibn
from colomoto_jupyter import import_colomoto_tool
import networkx as nx
import pandas as pd

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

sign_map = {
    "->": 1,
    "-|": -1,
    "+": 1,
    "-": -1,
    "+1": 1,
    "-1": -1,
    "ukn": 0,
    "?": 0,
    "unspecified": 0,
}
def sign_of_label(label):
    if label in sign_map:
        return sign_map[label]
    label = label.lower()
    if label.startswith("act"):
        return 1
    if label.startswith("inh"):
        return -1
    raise ValueError(label)

class InfluenceGraph(BonesisDomain, nx.MultiDiGraph):
    def __init__(self, graph,
            maxclause=None,
            allow_skipping_nodes=False,
            canonic=True,
            exact=False):
        nx.MultiDiGraph.__init__(self, graph)
        # TODO: ensures graph is well-formed
        self.maxclause = maxclause
        self.allow_skipping_nodes = allow_skipping_nodes
        self.canonic = canonic
        self.exact = exact

    def sources(self):
        return set([n for n,i in self.in_degree(self.nodes()) if i == 0])
    def unsource(self):
        self.add_edges_from([(n, n, {"sign": 1}) for n in self.sources()])

    @classmethod
    def from_sif(celf, filename, sep="\\s+", unsource=True, **kwargs):
        df = pd.read_csv(filename, header=None,
                names=("in", "sign", "out"), sep=sep)
        df["sign"] = df["sign"].map(sign_of_label)
        g = nx.from_pandas_edgelist(df, "in", "out", ["sign"], nx.MultiDiGraph())
        pkn = celf(g, **kwargs)
        if unsource:
            pkn.unsource()
        return pkn

    @classmethod
    def from_ginsim(celf, lrg, **kwargs):
        ginsim = import_colomoto_tool("ginsim")
        fd, filename = tempfile.mkstemp(".sif")
        os.close(fd)
        try:
            ginsim.service("reggraph").export(lrg, filename)
            pkn = celf.from_sif(filename, **kwargs)
        finally:
            os.unlink(filename)
        return pkn

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
