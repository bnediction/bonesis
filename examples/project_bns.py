
import bonesis

dom = bonesis.InfluenceGraph.complete("abc", loops=False)
bo = bonesis.BoNesis(dom)

projections = bo.projected_boolean_networks()
with projections.view({"a","b"}) as view:
    for bn in view:
        print(bn)
    print(view.count())
with projections.view({"c"}) as view:
    for bn in view:
        print(bn)
    print(view.count())

functions = bo.local_functions()
for node in ["a","b"]:
    with functions.view(node) as view:
        for f in view:
            print(f)
        print(view.count())

print(functions.as_dict())
print(functions.as_dict("count"))

dom = bonesis.InfluenceGraph.complete("ab", loops=False,
        allow_skipping_nodes=True)
bo = bonesis.BoNesis(dom)
funcs = bo.local_functions(skip_empty=True, solutions="subset-minimal")
with funcs.view("a") as view:
    print(list(map(str,view)))
    print(view.count())
