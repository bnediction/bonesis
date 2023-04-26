import bonesis

dom = bonesis.InfluenceGraph.complete("abc")

bo = bonesis.BoNesis(dom)
print(bo.reach.iface.stack_manager)

cfg0 = bo.cfg()
with bo.mutant({"a": 0}) as m:
    cfg0 >= m.cfg()
    with bo.action({"b": 1}) as n:
        cfg1 = n.cfg()
        cfg0 >= cfg1
    cfg0 >= m.cfg()
cfg0 >= m.cfg()

bo.aspmodel.make()
print(bo.aspmodel)

print(bo.is_satisfiable())
