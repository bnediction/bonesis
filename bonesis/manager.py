
import clingo

from .language import BonesisTerm

class BonesisManager(object):
    def __init__(self, bo):
        self.bo = bo
        self.properties = []
        self.observations = set()
        self.configurations = set()
        self.optimizations = []

    def assert_node_exists(self, node, assertion=KeyError):
        if not node in self.bo.domain:
            raise assertion(node)

    def push(self, rule):
        self.properties.append(rule)

    def push_term(self, name, *args, **kwargs):
        self.push((name, args, kwargs))

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
                self.register_predicate("bind_cfg", cfg.name, cfg.obs.name)

    def register_predicate(self, name, *args, **kwargs):
        for obj in args:
            if isinstance(obj, BonesisTerm):
                assert obj.mgr is self, "mixed managers"
        self.push_term(name, *args, **kwargs)

    def append_optimization(self, opt, name):
        self.optimizations.append((opt, name))

    def mutant_context(self, mutations):
        return _MutantManager(self, mutations)

class _MutantManager(BonesisManager):
    _mutant_id = 0
    def __init__(self, parent, mutations):
        self.bo = parent.bo
        self.properties = parent.properties
        self.observations = parent.observations
        self.configurations = parent.configurations
        self.parent = parent
        self.managed_configurations = set()
        self._mutations = mutations
        self.mutations = self.get_mutations()
        self.__class__._mutant_id += 1
        self.mutant_name = self.__class__._mutant_id
        self.push_term("mutant", self.mutant_name, self.mutations)

    def get_mutations(self):
        m = self._mutations.copy()
        if hasattr(self.parent, "mutations"):
            m.update(self.parent.mutations)
        return m

    def register_predicate(self, name, *args, **kwargs):
        super().register_predicate(name, *args, **kwargs,
                mutant=self.mutant_name)
