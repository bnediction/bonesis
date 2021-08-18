
import itertools

def matching_configurations(obs):
    bo = obs.mgr.bo
    nodes = list(bo.domain)
    mutations = set(obs.mgr.mutations if hasattr(obs.mgr, "mutations") else [])
    known = mutations.union(bo.data[obs.name])
    missing = [n for n in nodes if n not in known]
    for assigns in itertools.product((0,1), repeat=len(missing)):
        cfg = +obs
        for (n, b) in zip(missing, assigns):
            cfg[n] = b
        yield cfg

def bn_nocyclic_attractors(bn):
    return not bn.has_cyclic_attractor()
