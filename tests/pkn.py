import bonesis

pkn = bonesis.InfluenceGraph.complete(3, 1, loops=False, exact=True)

bo = bonesis.BoNesis(pkn)

bns = bo.boolean_networks()
print(bns.standalone())
print(bns.count())

