
import bonesis
from bonesis.language import *

data = {
    1: {"a": 0},
    "D0": {"b": 0},
}

dom = bonesis.InfluenceGraph([
    ("a", "b", {"sign": "-"}),
    ("b", "a", {"sign": "-"}),
    ("a", "c", {"sign": "-"}),
    ("b", "c", {"sign": "+"}),
])

bo = bonesis.BoNesis(dom, data)

obs1 = bo.obs(1)
print(obs1)

cfg1 = ~bo.obs(1)
assert cfg1.name == 1
cfg2 = ~bo.obs(1)
assert cfg2.name == 1
cfg3 = +bo.obs(1)
assert cfg3.name != 1
cfg3 != cfg2

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

# equivalent calls
cfg0 >= cfg2
bo.reach(cfg0, cfg2)
cfg0 >= bo.obs(1) # creates an anonymous configuration linked to obs(1)
~bo.obs("D0") >= bo.obs(1) # same

fixed(cfg2)
cfg0 >= fixed(cfg2)
in_attractor(cfg2)

e = fixed(bo.obs(1))
cfg0 >= e

cfg2 // cfg0

bo.aspmodel.make()
print()
print(bo.aspmodel.constants)
print(bo.aspmodel)

print(bo.is_satisfiable())

