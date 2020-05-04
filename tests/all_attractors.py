import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", -1, loops=False)
data = {
    "fp0": {"a": 0, "b": 0, "c": 0},
}
bo = bonesis.BoNesis(pkn, data)
bo.all_attractors(bo.obs("fp0"))

bns = bo.boolean_networks(limit=10)
print(bns.standalone())
for bn in bns:
    print("-"*20)
    print(bn)
    print(list(bn.attractors()))
