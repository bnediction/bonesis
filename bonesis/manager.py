
import clingo

class BonesisManager(object):
    def __init__(self, bo):
        self.bo = bo
        self.register = []
        self.observations = set()
        self.configurations = set()

    def push(self, rule):
        print(f"{self.__class__.__name__}.push({rule})")
        self.register.append(rule)

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
                i = 1
                cfg.name = (cfg.obs.name, i)
                while cfg.name in self.configurations:
                    i += 1
                    cfg.name = (cfg.obs.name, i)
            else:
                cfg.name = f"__cfg{len(self.configurations)}"
        if cfg.name not in self.configurations:
            self.configurations.add(cfg.name)
            self.push_term("cfg", cfg.name)

    def bind_configuration(self, cfg, obs):
        self.push_term("bind_cfg", cfg.name, obs.name)


