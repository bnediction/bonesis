from tqdm import tqdm
import bonesis

dom1 = bonesis.InfluenceGraph.complete("abc", 1)

bo = bonesis.BoNesis(dom1)
bns = bo.boolean_networks()

def count_matching(m):
    print(m, len([bn for bn in tqdm(bns) if m(bn)]))

def all_fixpoints_0(bn):
    A = list(bn.attractors())
    return A == [{"a": 0, "b": 0, "c": 0}]
#count_matching(all_fixpoints_0)

def fixpoints_0(bn):
    A = list(bn.attractors())
    return {"a": 0, "b": 0, "c": 0} in A
count_matching(fixpoints_0)
