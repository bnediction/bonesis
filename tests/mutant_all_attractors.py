import bonesis
import mpbn

pkn = bonesis.InfluenceGraph.complete("abc", -1, loops=False)
data = {
    "a0": {"a": 0, "b": 0},
    "a1": {"a": 1, "b": 1},
}
bo = bonesis.BoNesis(pkn, data)

bo.all_attractors({bo.obs(a) for a in data})

with bo.mutant({"c": 1}) as m:
    m.all_attractors(bo.obs("a0"))

bns = bo.boolean_networks(limit=10)
print(bns.standalone())
for bn in bns:
    print("-"*20)
    print(bn)
    print(list(mpbn.MPBooleanNetwork(bn).attractors()))
