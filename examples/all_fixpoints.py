import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", -1, loops=False)
data = {
    "fp0": {"a": 0, "b": 0, "c": 0},
    "110": {"a": 1, "b": 1, "c": 0},
}
bo = bonesis.BoNesis(pkn, data)
bo.fixed(bo.obs("fp0"))
bo.all_fixpoints(bo.obs("fp0"))

bns = bo.boolean_networks(limit=10)
print(bns.standalone())
for bn in bns:
    print("-"*20)
    print(bn)
    print(list(bn.attractors()))

with bo.mutant({"a": 1, "b": 1}) as m1:
#    m1.fixed(m1.obs("110"))
    m1.all_fixpoints(m1.obs("110"))
print(bns.standalone())
for bn in bns:
    print("-"*20)
    print(bn)
