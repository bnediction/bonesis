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


bo = bonesis.BoNesis(dom)
x = ~bo.obs({"a": 0, "b": 1})
y = ~bo.obs({"a": 1, "b": 0})
bo.f(x, iterate=3) << y

bo.aspmodel.make()
print(bo.aspmodel)

print(bo.is_satisfiable())
