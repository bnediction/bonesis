
__version__ = "0.0a0"

class BoNesis(object):
    def __init__(self, domain):
        self.domain = domain


"""
cfg1 ~ obs1
cfg2 ~ obs2
cfg3 ~ obs3

reach(cfg1, cfg2)
nonreach(cfg1, cfg3)
in_attractor(cfg2)
in_attractor(cfg3)
nonreach(cfg2, cfg3)


cfg1 -> only_attractors(obs2)



>>> import bonesis
>>> bo = bonesis.BoNesis(bn)
>>> cfg1 = bo.configuration(obs1)
>>> cfg2 = bo.configuration(obs2)
>>> cfg3 = bo.configuration(obs3)
>>> bo.nonreach(cfg1, cfg2)
>>> bo.fixpoint(cfg2)
>>> bo.reach(cfg1, cfg3)
>>> bo.in_attractor(cfg3)

>>> bo.reach_only_attractors(cfg1, obs2)

>>> bo.is_satisfiable()
True

"""
