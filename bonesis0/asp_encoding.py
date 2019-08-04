
import clingo as asp

from scipy.special import binom

def string_of_facts(facts):
    if not facts:
        return ""
    return "{}.".format(".\n".join(map(str,facts)))

def print_facts(facts):
    if facts:
        print(string_of_facts(facts))

def nb_clauses(d):
    return int(binom(d, d//2))

def pkn_to_facts(pkn, maxclause=None):
    facts = []
    facts.append(asp.Function("nbnode", [asp.Number(len(pkn.nodes()))]))
    for n in pkn.nodes():
        facts.append(asp.Function("node", [asp.String(n)]))
    for (orig, dest, data) in pkn.edges(data=True):
        if data["sign"] == "ukn":
            f = "{{in({},{},(-1;1))}} 1".format(
                    asp.String(orig), asp.String(dest))
            facts.append(f)
        else:
            s = asp.Number(int(data["sign"]))
            facts.append(asp.Function("in",
                [asp.String(orig), asp.String(dest), s]))
    def bounded_nb_clauses(d):
        nbc = nb_clauses(d)
        if maxclause:
            nbc = min(maxclause, nbc)
        return nbc
    for n, i in pkn.in_degree(pkn.nodes()):
        facts.append(asp.Function("maxC", [asp.String(n),
            asp.Number(bounded_nb_clauses(i))]))
    return facts

