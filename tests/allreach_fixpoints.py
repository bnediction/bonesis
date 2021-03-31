import bonesis
import mpbn
import pandas as pd

from bonesis.language import *

pkn = bonesis.InfluenceGraph.complete("abc", 1)
data = {
    "x": {"a": 0, "b": 0, "c": 1},
    "y": {"a": 1, "b": 1},
}
bo = bonesis.BoNesis(pkn, data)

+bo.obs("x") >> "fixpoints" ^ {bo.obs("y")}

bns = bo.boolean_networks(limit=10)
print(bns.standalone())
for bn in bns:
    print("-"*20)
    print(bn)
    ait = bn.attractors(reachable_from=data["x"])
    cols = list(sorted(data["y"].keys()))
    a = pd.DataFrame(ait)[cols].sort_values(by=cols).drop_duplicates()
    print(a)

