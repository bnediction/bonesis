import bonesis

dom = bonesis.InfluenceGraph.complete("abc", sign=1, exact=True, loops=False)

dom2 = bonesis.BooleanNetwork({
    "a": "c",
    "b": "a",
    "c": "b"})

bo = bonesis.BoNesis(dom)

"""
x = bo.cfg()
bo.in_attractor(x)

for i, sol in enumerate(x.assignments()):
    print(i, sol)

"""
#h = bo.hypercube({"a": 1})
h = bo.hypercube()
bo.fixed(h)

bo.aspmodel.make()
print(str(bo.aspmodel))

assert bo.is_satisfiable()

for i, sol in enumerate(h.assignments()):
    print(i, sol)
