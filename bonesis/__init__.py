
__version__ = "0.0a0"

from colomoto import minibn
import networkx as nx

from .asp_encoding import ASPModel_DNF
from .domains import *
from .language import ObservationVar, ConfigurationVar
from .manager import BonesisManager

__language_api__ = ["obs", "cfg"]

class BoNesis(object):
    def __init__(self, domain, data=None,
            **opts):
        if not isinstance(domain, BonesisDomain):
            if isinstance(domain, minibn.BooleanNetwork):
                domain = BooleanNetwork(domain)
            elif isinstance(domain, (nx.DiGraph, nx.MultiDiGraph)):
                domain = InfluenceGraph(domain)
            else:
                raise TypeError(f"Cannot handle domain with type '{type(domain)}'")
        self.domain = domain
        self.data = data or {}
        self.manager = BonesisManager(self)

        self.aspmodel = ASPModel_DNF(self.domain, self.data, self.manager,
                **opts)

        def managed(cls):
            class Managed(cls):
                mgr = self.manager
            return Managed
        self.cfg = managed(ConfigurationVar)
        self.obs = managed(ObservationVar)
        self.obs.make_cfg = self.cfg


    def install_language(self, scope):
        for k in __language_api__:
            scope[k] = getattr(self, k)
    def uninstall_language(self, scope):
        for k in __language_api__:
            del scope[k]

    def load_code(self, prog, defs=None, dest_scope=None):
        scope = {}
        self.install_language(scope)
        exec(prog, scope, defs)
        self.uninstall_language(scope)
        del scope["__builtins__"]
        print(f"/scope={scope.keys()}")
        if defs:
            print(f"/defs={defs.keys()}")
        ret = defs if defs else scope
        if dest_scope is not None:
            dest_scope.update(ret)
        return ret
    def load(self, script, defs=None, dest_scope=None):
        with open(script) as fp:
            return self._load_code(fp.read(), defs=defs)
