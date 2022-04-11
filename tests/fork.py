import bonesis

dom = bonesis.InfluenceGraph.complete("abc")
data = {"A": {"a": 1}}

bo1 = bonesis.BoNesis(dom, data)
print(id(bo1))

bo2 = bo1.fork()
print(id(bo2))
print(id(bo2.manager.bo))
