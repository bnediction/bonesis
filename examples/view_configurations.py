import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
        allow_skipping_nodes=False)

data = {
    "x": {"a": 0, "b": 0},
    "y": {"a": 1, "b": 1},
}

bo = bonesis.BoNesis(pkn, data)
~bo.obs("x") >= ~bo.obs("y")

for i, bn in enumerate(bo.boolean_networks(limit=3)):
    print(f"### {i}")
    print(bn)
print("-"*30)
for i, (bn, cfgs) in enumerate(bo.boolean_networks(limit=3,
        extra="configurations")):
    print(f"### {i}")
    print(bn, cfgs)
print("-"*30)
for i, (bn, cfgs) in enumerate(bo.diverse_boolean_networks(limit=3,
                        extra="configurations")):
    print(f"### {i}")
    print(bn, cfgs)

