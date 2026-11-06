import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", 0)
bo = bonesis.BoNesis(pkn, {"h": {"b": 0, "c": 1}})
h = bo.cube(bo.obs("h"))
bo.fixed(h)

for f in bo.boolean_networks(limit=2):
    print("-"*10)
    print(f)
    for a in f.attractors():
        print("- ", a)
    print()

