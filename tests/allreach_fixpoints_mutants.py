import bonesis
from mpbn import MPBooleanNetwork
import pandas as pd

from bonesis.language import *

pkn = bonesis.InfluenceGraph.complete("abc", 1)
data = {
    "x": {"a": 0, "b": 0},
    "y": {"a": 1, "b": 1},
}
bo = bonesis.BoNesis(pkn, data)

fixed(~bo.obs("x"))
all_fixpoints({bo.obs("x")})
with bo.mutant({"c":1}) as mc:
    y = mc.obs("y")
    for cfg in bonesis.matching_configurations(mc.obs("x")):
        cfg >= mc.fixed(+y)
        cfg >> "fixpoints" ^ {y}

def validate(bn):
    print("# all fixpoints")
    fps = [a for a in bn.attractors() if '*' not in a.values()]
    print(pd.DataFrame(fps))
    print("# reachable from x with mutation")
    bn["c"] = True
    orig = data["x"].copy()
    orig["c"] = 1
    fps = [a for a in bn.attractors(reachable_from=orig) if '*' not in a.values()]
    print(pd.DataFrame(fps))


bn = MPBooleanNetwork({
    "a": "b&c",
    "b": "c",
    "c": "0",
})
print(bn)
validate(bn)
print("="*40)

bns = bo.boolean_networks(limit=3)
bns.standalone(output_filename="/tmp/test.sh")
found = False
for bn in bns:
    found = True
    print("-"*20)
    print(bn)
    validate(bn)
print(found)

