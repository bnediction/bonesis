
__version__ = "0.0a0"

from colomoto import minibn
import networkx as nx

from .asp_encoding import ASPModel_DNF
from .domains import *
from .language import ManagedIface
from .manager import BonesisManager
from .views import *

__language_api__ = ["obs", "cfg"]

class BoNesis(object):
    def __init__(self, domain, data=None):
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

        self.aspmodel = ASPModel_DNF(self.domain, self.data, self.manager)

        self.iface = ManagedIface(self.manager)
        self.iface.install(self)

    def set_constant(self, cst, value):
        self.aspmodel.constant[cst] = value

    def install_language(self, scope):
        self.iface.install(scope)
    def uninstall_language(self, scope):
        self.iface.uninstall(scope)

    def load_code(self, prog, defs=None, dest_scope=None):
        scope = {}
        self.install_language(scope)
        exec(prog, scope, defs)
        self.uninstall_language(scope)
        del scope["__builtins__"]
        ret = defs if defs else scope
        if dest_scope is not None:
            dest_scope.update(ret)
        return ret
    def load(self, script, defs=None, dest_scope=None):
        with open(script) as fp:
            return self._load_code(fp.read(), defs=defs, dest_scope=None)

    def solver(self, *args, **kwargs):
        self.aspmodel.make()
        return self.aspmodel.solver(*args, **kwargs)

    def is_satisfiable(self):
        control = self.solver(1)
        return control.solve().satisfiable

    def boolean_networks(self):
        return BooleanNetworksView(self.aspmodel)
