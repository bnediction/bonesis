class reach(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __ge__(self, right):
        print(f"reach({self},{right})")
        return reach(self, right)
    def __str__(self):
        return "{} -> {}".format(self.a, self.b)

class universal_reach(reach):
    def __str__(self):
        return "{} => {}".format(self.a, self.b)

class cfg(object):
    def __init__(self, i):
        self.i = i
    def __ge__(self, right):
        print(f"reach({self},{right})")
        return reach(self, right)
    def __rshift__(self, right):
        print(f"universal_reach({self},{right})")
        return universal_reach(self, right)
    def __str__(self):
        return f"cfg({self.i})"

cfg1 = cfg(1)
cfg2 = cfg(2)
cfg3 = cfg(3)

cfg(1) >= cfg(2) >= cfg(3) >= cfg(4)

cfg1 >> 3
cfg(1) >> 3
print(cfg1)

"""
data = {
    1: obs1...
    2: obs2..
}
bo = bonesis.BoNesis(bn, data)
bo.__enter__() # with bo:

cfg1 = ~obs(1)
cfg2 = ~obs(2)
cfg3 = ~obs(3)

cfg2[a] == cfg3[a]
cfg(2,a) == cfg(3,a)
cfg(2)[a] == cfg(3)[a]

cfg2 != cfg3

cfg1 >= cfg2    # there is a trajectory from cfg1 to cfg2
~obs1 >= obs2    # there is a trajectory from a configuration matching obs1

cfg1 // cfg3    # there is no trajectory from cfg1 to cfg3


fixed(cfg2)     # cfg2 is a fixed point
fixed(obs2)     # trap space on obs2
in_attractor(cfg2)
in_attractor(obs2)

# shortcuts
cfg1 >= fixed(obs2)
cfg1 >= fixed(cfg2)
cfg1 >= in_attractor(cfg2)


cfg1 >= fixed(obs5)
cfg1 >= cfg2 >= fixed(obs3); \
        cfg2 >= fixed(obs4); \
        cfg2 // fixed(obs5) # unversal constraint

cfg2 // fixed(cfg5) # existential constraint


cfg1 >> fixed(obs2) # all attractors reached from cfg1 have obs2 fixed
cfg1 >> in_attractor(obs2) # all attractors reached from cfg1 have a
                    #   configuration matching obs2
cfg1 // in_attractor(obs3)    # none attractor reached from cfg1 have a cfg matching obs3

cfg1 >= fixed(obs2)
cfg1 >> fixed(obs2)
cfg1 // {obs3}

with mutation(node1,UP):
    cfg1 = ~ obs(1)
    cfg1 // in_attractor(obs(2))

with mutation(v("N"),v("S")):
    # there exists a mutation s.t.
    cfg1 = ~ obs(1)
    cfg1 // in_attractor(obs(2))



bo.__exit__()

bo.is_satisfiable()

TODO: views

"""

