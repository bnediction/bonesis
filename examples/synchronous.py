import bonesis

dom = bonesis.BooleanNetwork({"a": "b", "b": "a"})
bo = bonesis.BoNesis(dom)
x = bo.cfg()
y = bo.f(x)
y != x
bo.f(y) == x

with bo.mutant({"a": 1}):
    bo.f(x)["a"] != x["a"]

for h in x.assignments():
    print(h)

print(bo.aspmodel)
