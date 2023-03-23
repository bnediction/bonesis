# Copyright or © or Copr. Loïc Paulevé (2023)
#
# loic.pauleve@cnrs.fr
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#

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
        self.push_term("hypercube", h)
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

    def scope_reachability_context(self, *a, **k):
        return _ReachabilityScopeManager(self, *a, **k)


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

class _ReachabilityScopeManager(BonesisManager):
    def __init__(self, parent, options):
        for prop in ["bo", "properties",
                "observations", "anon_observations",
                "configurations", "some"]:
            setattr(self, prop, getattr(parent, prop))
        self.__options = options
    def register_predicate(self, name, *args, **kwargs):
        if name in ["bind_cfg",
                    "different",
                    "fixpoint"] or name.startswith("cfg_"):
            return super().register_predicate(name, *args, **kwargs)
        if name not in ["reach"]:
            raise TypeError(f"Unsupported predicate {name} in scoped reachability")
        super().register_predicate(name, *args, **self.__options, **kwargs)
