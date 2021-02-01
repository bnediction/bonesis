
import bonesis

pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False, allow_skipping_nodes=True)

data = {
    "x": {"a": 0, "b": 0},
    "y": {"a": 1, "b": 1},
}

bo = bonesis.BoNesis(pkn, data)

~bo.obs("x") >= ~bo.obs("y")

bo.maximize_nodes()

view = bonesis.NodesView(bo)
print(view.standalone())
print(view.count())
for nodes in view:
    print(nodes)

bo.maximize_strong_constants()

print("-"*10)
view = bonesis.NonStrongConstantNodesView(bo)

print(view.standalone())
for nodes in view:
    print(nodes)


