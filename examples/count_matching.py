import bonesis

dom1 = bonesis.InfluenceGraph.complete("abc", 1)

bo = bonesis.BoNesis(dom1)
bns = bo.boolean_networks()

def count_matching(m):
    print(m, len([bn for bn in bns if m(bn)]))

def match1(bn):
    A = list(bn.attractors())
    return A == [{"a": 0, "b": 0, "c": 0}]

count_matching(match1)
