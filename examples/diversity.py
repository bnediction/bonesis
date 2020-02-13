
import pandas as pd

import bonesis
bonesis.enable_debug()

N = 20

bonesis.settings["parallel"] = 1

dom = bonesis.InfluenceGraph.complete("abc", 1)

bo = bonesis.BoNesis(dom)

print(pd.DataFrame(list(bo.boolean_networks(limit=N))))
print(pd.DataFrame(list(bo.diverse_boolean_networks(limit=N))))
