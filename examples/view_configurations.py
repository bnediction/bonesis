import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
        allow_skipping_nodes=False)

data = {
    "x": {"a": 0, "b": 0},
    "y": {"a": 1, "b": 1},
}

bo = bonesis.BoNesis(pkn, data)
~bo.obs("x") >= ~bo.obs("y")

for bn, cfgs in bo.boolean_networks(limit=3, extra="configurations"):
    print("-"*30)
    print(bn, cfgs)
print("-"*30)
