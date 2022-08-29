
import copy

from colomoto import minibn
import networkx as nx

from .asp_encoding import ASPModel_DNF
from .debug import *
from .domains import *
from .language import ManagedIface
from .manager import BonesisManager
from .snippets import *
from .utils import OverlayedDict
from .views import *

__language_api__ = ["obs", "cfg"]

settings = {
    "parallel": 1,
    "clingo_options": (),
    "solutions": "all",
    "quiet": False,
}

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

        self.settings = OverlayedDict(settings)
        self.aspmodel = ASPModel_DNF(self.domain, self.data, self.manager)

        self.iface = ManagedIface(self.manager)
        self.iface.install(self)

    def fork(self):
        fo = self.__class__(self.domain, self.data)
        fo.manager.reset_from(self.manager)
        return fo

    def debug(self, asp_output="/tmp/debug.asp"):
        with open(asp_output, "w") as fp:
            self.aspmodel.make()
            fp.write(str(self.aspmodel))

    def set_constant(self, cst, value):
        self.aspmodel.constants[cst] = value

    def install_language(self, scope):
        self.iface.install(scope)
    def uninstall_language(self, scope):
        self.iface.uninstall(scope)

    def has_optimizations(self):
        return bool(self.manager.optimizations)

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
            return self.load_code(fp.read(), defs=defs, dest_scope=None)

    def solver(self, *args, **kwargs):
        self.aspmodel.make()
        if "settings" not in kwargs:
            kwargs["settings"] = self.settings
        return self.aspmodel.solver(*args, **kwargs)

    def is_satisfiable(self):
        control = self.solver(1)
        return control.solve().satisfiable

    def boolean_networks(self, *args, **kwargs):
        return BooleanNetworksView(self, *args, **kwargs)
    def diverse_boolean_networks(self, *args, **kwargs):
        return DiverseBooleanNetworksView(self, *args, **kwargs)

    def projected_boolean_networks(self, **kwargs):
        return ProjectedBooleanNetworksViews(self, **kwargs)
    def local_functions(self, **kwargs):
        return LocalFunctionsViews(self, **kwargs)

    def influence_graphs(self, **kwargs):
        return InfluenceGraphView(self, **kwargs)

    def assignments(self, solutions="subset-minimal", **kwargs):
        return AllSomeView(self, solutions=solutions, **kwargs)
