import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
        allow_skipping_nodes=False)

data = {
    "x": {"a": 0, "b": 0},
    "y": {"a": 1, "b": 1},
}

bo = bonesis.BoNesis(pkn, data)

x = ~bo.obs("x")
y = ~bo.obs("y")

x >= y

x["c"] = y["c"]

for bn, cfgs in bo.boolean_networks(limit=3, extra="configurations"):
    print("-"*30)
    print(bn, cfgs)
print("-"*30)
