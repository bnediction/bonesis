import datetime

import bonesis

dom = bonesis.InfluenceGraph.complete("abcd", sign=1, canonic=True, exact=True,
                                      maxclause=32)
bo = bonesis.BoNesis(dom)

bo.fixed(~bo.obs({"a":1}))
for bn in bo.diverse_boolean_networks(limit=3):
    print(datetime.datetime.now(), "solution")

bo.all_fixpoints(bo.obs({"a":1}))

print(datetime.datetime.now(), "solving")
sols = []
for bn in bo.diverse_boolean_networks(limit=3, timeout=5, fail_if_timeout=False):
    print(datetime.datetime.now(), "solution")
    sols.append(bn)
print(len(sols))

sols = []
try:
    print(datetime.datetime.now(), "solving")
    for bn in bo.diverse_boolean_networks(limit=3, timeout=5):
        print(datetime.datetime.now(), "solution")
        sols.append(bn)
except TimeoutError:
    print("GOT TIMEOUT")
print(len(sols))

print(datetime.datetime.now(), "solving")
for bn in bo.diverse_boolean_networks(limit=3, timeout=5):
    print(datetime.datetime.now(), "solution")
    sols.append(bn)
