
import clingo

from .language import BonesisTerm

class BonesisManager(object):
    def __init__(self, bo):
        self.bo = bo
        self.properties = []
        self.observations = set()
        self.configurations = set()

    def assert_node_exists(self, node, assertion=KeyError):
        if not node in self.bo.domain:
            raise assertion(node)

    def push(self, rule):
        self.properties.append(rule)

    def push_term(self, name, *args):
        self.push((name, args))

    def register_observation(self, obs):
        if not obs.name in self.bo.data:
            raise ValueError(f"No data registered at key {repr(obs.name)}")
        if obs.name not in self.observations:
            self.observations.add(obs.name)
            self.push_term("obs", obs.name)

    def register_configuration(self, cfg):
        if cfg.name is None:
            if cfg.obs:
                i = 0
                cfg.name = (cfg.obs.name, i)
                while cfg.name in self.configurations:
                    i += 1
                    cfg.name = (cfg.obs.name, i)
            else:
                cfg.name = f"__cfg{len(self.configurations)}"
        if cfg.name not in self.configurations:
            self.configurations.add(cfg.name)
            self.push_term("cfg", cfg.name)
            if cfg.obs:
                self.push_term("bind_cfg", cfg.name, cfg.obs.name)

    def register_predicate(self, name, *args):
        for obj in args:
            if isinstance(obj, BonesisTerm):
                assert obj.mgr is self, "mixed managers"
        self.push_term(name, *args)

    def mutant_context(self, mutations):
        return _MutantManager(self, mutations)

class _MutantManager(BonesisManager):
    def __init__(self, parent, mutations):
        self.bo = parent.bo
        self.properties = parent.properties
        self.observations = parent.observations
        self.configurations = parent.configurations
        self.parent = parent
        self._mutations = mutations
        self.managed_configurations = set()

    @property
    def mutations(self):
        m = self._mutations.copy()
        if hasattr(self.parent, "mutations"):
            m.update(self.parent.mutations)
        return m

    def register_configuration(self, cfg):
        super().register_configuration(cfg)
        if cfg.name not in self.managed_configurations:
            for n, v in self._mutations.items():
                self.push_term("clamped", cfg, n, v)
