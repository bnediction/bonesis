import bonesis

dom = bonesis.BooleanNetwork({
    "a": "c",
    "b": "a",
    "c": "b"})
data = {
    "111": {a: 1 for a in dom.keys()}
}

bo = bonesis.BoNesis(dom, data)
with bo.mutant(bo.Some("Ensure111", max_size=2)) as m:
    m.all_fixpoints(bo.obs("111"))

view = bo.assignments()
print(view.standalone())
for res in view:
    print(res)

for res in bo.assignments(solutions="all"):
    print(res)
