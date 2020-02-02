
import bonesis

data = {
    1: {"a": 0},
    "D0": {"b": 0},
}
bo = bonesis.BoNesis(None, data)

obs1 = bo.obs(1)
print(obs1)

cfg1 = ~bo.obs(1)
assert cfg1.name == 1
cfg2 = ~bo.obs(1)
assert cfg2.name == 1
cfg3 = +bo.obs(1)
assert cfg3.name != 1

defs = bo.load_code("""
print(globals().keys())
print(locals().keys())
cfg0 = ~obs("D0")
""")
globals().update(defs)
print(defs["cfg0"])
print(f"cfg0={cfg0}")

defs = bo.load_code("""
cfg1 = cfg0
""", defs, dest_scope=globals())
print(defs.keys())
print(f"cfg1={cfg1}")

