import bonesis

dom = bonesis.BooleanNetwork({
    "a": "a",
    "b": "a & c",
    "c": "!b"})
data = {
    "never_b": {"b": 0},
}

bo = bonesis.BoNesis(dom, data)
bad_control = bo.Some()
with bo.mutant(bad_control) as m:
    m.fixed(bo.obs("never_b"))

for res in bad_control.complementary_assignments():
    print(res)
