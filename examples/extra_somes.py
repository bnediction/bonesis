import bonesis

dom = bonesis.InfluenceGraph.complete(["a","b","c"])
data = {
    "never_b": {"b": 0},
}

bo = bonesis.BoNesis(dom, data)
bad_control = bo.Some(min_size=1)
with bo.mutant(bad_control) as m:
    m.fixed(bo.obs("never_b"))
s2 = bo.Some(min_size=1, name="s2")
with bo.mutant(s2) as m:
    m.fixed(bo.obs("never_b"))

for bn, cfgs, somes in bo.boolean_networks(extra=("configurations", "somes"), limit=3):
    print(bn, cfgs, somes)
