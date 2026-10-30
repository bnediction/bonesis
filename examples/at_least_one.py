import bonesis

dom = bonesis.BooleanNetwork({"a": "b", "b": "a"})
bo = bonesis.BoNesis(dom)
x = bo.cfg()
y = bo.fixed(bo.cfg())
z = bo.fixed(bo.cfg())
y != z

with bo.at_least_one():
    x == z
    x == y

bo.aspmodel.make()
print(bo.aspmodel)

for h in x.assignments():
    print(h)
