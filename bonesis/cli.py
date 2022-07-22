from argparse import ArgumentParser
from itertools import islice
import json
import sys

import bonesis

def json_to_bn(args):
    str_facts = json.load(sys.stdin)
    bn = bonesis.ASPModel_DNF.minibn_of_json_facts(str_facts)
    sys.stdout.write(bn.source())

def main_utils():
    ap = ArgumentParser()
    sap = ap.add_subparsers(help="commands")
    p = sap.add_parser("json-to-bn",
            help="Convert json facts (stdin) to BooleanNet (stdout)")
    p.set_defaults(func=json_to_bn)

    args = ap.parse_args()
    if not hasattr(args, "func"):
        return ap.print_help()
    return args.func(args)

def main_attractors():
    ap = ArgumentParser()
    ap.add_argument("bnet_file",
            help="file specifying the Boolean network in bnet format")
    ap.add_argument("--fixpoints-only", action="store_true",
            help="Enumerate only fixed points")
    args = ap.parse_args()
    dom = bonesis.BooleanNetwork(args.bnet_file)
    bo = bonesis.BoNesis(dom)
    x = bo.cfg() if args.fixpoints_only else bo.hypercube()
    bo.fixed(x)

    publish = print

    for sol in x.assignments():
        publish(sol)



def main_reprogramming():
    ap = ArgumentParser()
    ap.add_argument("bnet_file",
            help="file specifying the Boolean network in bnet format")
    ap.add_argument("marker",
            help="Marker specification (partial configuration) - JSON format")
    ap.add_argument("max_size", type=int,
            help="Maximum number of perturbation")
    ap.add_argument("--reachable-from",
            help="Initial configuration for source-marker reprogramming - JSON format")
    ap.add_argument("--fixpoints", action="store_true",
            help="Reprogram fixed points only")
    ap.add_argument("--allow-no-fixpoint", action="store_true",
            help="When reprogramming fixed points, allow having no fixed points")
    ap.add_argument("--exclude",
            help="Perturbation blacklist - JSON format")
    ap.add_argument("--limit", type=int,
            help="Maximum number of solutions")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--parallel", "-t", default=1, help="Parallel solving")
    args = ap.parse_args()

    bonesis.settings["quiet"] = not args.verbose
    bonesis.settings["parallel"] = args.parallel

    f = bonesis.BooleanNetwork(args.bnet_file)
    M = json.loads(args.marker)
    k = args.max_size
    meth_prefix = ""
    meth_suffix = ""
    meth_args = (f, M, k)
    meth_kwargs = {}
    if args.exclude:
        meth_kwargs["exclude"] = json.loads(args.exclude)
    if args.reachable_from:
        z = json.loads(args.reachable_from)
        meth_prefix = "source_"
        meth_args = (f, z, M, k)
    if args.fixpoints:
        meth_suffix = "_fixpoints"
        meth_kwargs["at_least_one"] = not args.allow_no_fixpoint

    from bonesis import reprogramming
    meth = f"{meth_prefix}marker_reprogramming{meth_suffix}"
    meth = getattr(reprogramming, meth)
    it = meth(*meth_args, **meth_kwargs)

    has_one = False
    if args.limit:
        it = islice(it, args.limit)
    for sol in it:
        has_one = True
        print(sol)
    if not has_one:
        print("No solution", file=sys.stderr)
