import bonesis

f = bonesis.BooleanNetwork({
    "a": "c & (!a | !b)",
    "b": "c & a",
    "c": "a|b|c",
    })

bo = bonesis.BoNesis(f)
x = bo.cfg()
~bo.obs({"a": 1, "b": 0, "c": 0}) >= bo.in_attractor(x) != bo.obs({"a": 1, "b": 1})

for v in x.assignments():
    print(v)
for v in x.assignments(scope=["a","b"]):
    print(v)
