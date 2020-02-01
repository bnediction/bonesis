
__version__ = "0.0a0"

from .manager import BonesisManager
from .language import ObservationVar, ConfigurationVar

__language_api__ = ["obs", "cfg"]

class BoNesis(object):
    def __init__(self, domain, data=None):
        self.domain = domain
        self.data = data or {}
        self.manager = BonesisManager(self)

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
