import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", 0, loops=False, exact="unsigned")
bo = bonesis.BoNesis(pkn, {"h": {"b": 0, "c": 1}})
bo.trapspace(bo.obs("h"))

for x in bo.boolean_networks(limit=2):
    print(x)

bn = bonesis.BooleanNetwork({
    "a": "0",
    "b": "a",
    "c": "!b",
    "d": "d",
    "e": "0"})
bo = bonesis.BoNesis(bn, {"h": {"b": 0, "c": 1, "d": 1, "e": 0}})
bo.trapspace(bo.obs("h"))
print(bo.is_satisfiable())

