import bonesis

dom = bonesis.BooleanNetwork({
    "a": "c",
    "b": "a",
    "c": "b"})

M = {a:1 for a in dom}

bo = bonesis.BoNesis(dom)
with bo.mutant(bo.Some("Ensure111", max_size=2)) as m:
    m.all_fixpoints(bo.obs(M))

view = bo.assignments()
print(view.standalone())
for res in view:
    print(res)

for res in bo.assignments(solutions="all"):
    print(res)

bo = bonesis.BoNesis(dom)
control = bo.Some()
with bo.mutant(control) as m:
    m.all_fixpoints(bo.obs(M))

for res in control.assignments():
    print(res)
