import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", 0, loops=False, exact="unsigned")
bo = bonesis.BoNesis(pkn, {"h": {"b": 0, "c": 1}})
bo.trapspace(bo.obs("h"))

for x in bo.boolean_networks(limit=2):
    print(x)

