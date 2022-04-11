
import copy

import clingo

from .language import BonesisTerm, Some

class BonesisManager(object):
    def __init__(self, bo):
        self.bo = bo
        self.properties = []
        self.observations = set()
        self.anon_observations = {}
        self.configurations = set()
        self.hypercubes = set()
        self.some = {}
        self.optimizations = []

    def reset_from(self, m2):
        for attr in ["properties",
                        "observations",
                        "anon_observations",
                        "configurations",
                        "hypercubes",
                        "some",
                        "optimizations"]:
            setattr(self, attr, copy.copy(getattr(m2, attr)))

    def assert_node_exists(self, node, assertion=KeyError):
        if not node in self.bo.domain:
            raise assertion(node)

    def push(self, rule):
        self.properties.append(rule)

    def push_term(self, name, *args, **kwargs):
        self.push((name, args, kwargs))

    def register_observation(self, obs):
        if obs.name is None and hasattr(obs, "data"):
            key = tuple(sorted(obs.data.items()))
            name = self.anon_observations.get(key, None)
            if name is None:
                name = f"_obs{len(self.anon_observations)}"
                self.anon_observations[key] = name
            obs.name = name
        elif not obs.name in self.bo.data:
            raise ValueError(f"No data registered at key {repr(obs.name)}")
        if obs.name not in self.observations:
            self.observations.add(obs.name)
            if hasattr(obs, "data"):
                self.push_term("obs_data", obs.name, obs.data)
            else:
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

    def register_hypercube(self, h):
        name = f"_h{len(self.hypercubes)}"
        h.name = name
        self.push_term("hypercube", name)
        if h.obs:
            self.register_predicate("bind_hypercube", name, h.obs.name)

    def register_predicate(self, name, *args, **kwargs):
        for obj in args:
            if isinstance(obj, BonesisTerm):
                assert obj.mgr is self, "mixed managers"
        self.push_term(name, *args, **kwargs)

    def register_some(self, some):
        if some.name is None:
            some.name = f"__some{len(self.some)}"
        assert some.name not in self.some, "Duplicate Some identifier"
        self.some[some.name] = some
        self.push_term("some", some)

    def append_optimization(self, opt, name):
        self.optimizations.append((opt, name))

    def mutant_context(self, *args, **kwargs):
        return _MutantManager(self, *args, **kwargs)

class _MutantManager(BonesisManager):
    _mutant_id = 0
    def __init__(self, parent, mutations, weak=False):
        for prop in ["bo", "properties",
                "observations", "anon_observations",
                "configurations", "some"]:
            setattr(self, prop, getattr(parent, prop))
        self.parent = parent
        self.managed_configurations = set()
        self._mutations = mutations
        self.mutations = self.get_mutations()
        self.__class__._mutant_id += 1
        self.mutant_name = self.__class__._mutant_id
        self.push_term("mutant", self.mutant_name, self.mutations)
        if weak:
            self.push_term("weak_mutant", self.mutant_name, self._mutations)

    def get_mutations(self):
        m = self._mutations.copy()
        if hasattr(self.parent, "mutations"):
            m.update(self.parent.mutations)
        return m

    def register_predicate(self, name, *args, **kwargs):
        super().register_predicate(name, *args, **kwargs,
                mutant=self.mutant_name)
