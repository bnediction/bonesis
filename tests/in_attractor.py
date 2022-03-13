import bonesis

f = bonesis.BooleanNetwork({
    "a": "c & (!a | !b)",
    "b": "c & a",
    "c": "a|b|c",
    })

bo = bonesis.BoNesis(f)
x = bo.cfg("x")
bo.in_attractor(x)

for v in x.assignments():
    print(v)
