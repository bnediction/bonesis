
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

