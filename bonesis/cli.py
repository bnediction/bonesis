from argparse import ArgumentParser, RawDescriptionHelpFormatter
from itertools import islice
import json
import sys
import textwrap

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

def _load_domain(args):
    ext = args.input.lower().split(".")[-1]
    if ext == "bnet":
        dom = bonesis.BooleanNetwork(args.input)
    elif ext == "aeon":
        from bonesis.aeon import AEONDomain
        dom = AEONDomain.from_aeon_file(args.input, canonic=False)
    elif ext == "sif":
        dom = bonesis.InfluenceGraph.from_sif(args.input, canonic=False,
                unsource=False, exact=True)
    else:
        raise ValueError("Unknon file type for input")
    return dom

def _setup_argument_domain(ap):
    ap.add_argument("input",
            help="file specifying the domain of Boolean networks (supported: .bnet, .sif, .aeon)")

def main_attractors():
    ap = ArgumentParser(description=textwrap.dedent("""\
    This program lists the attractors (possibly restricted to fixed points) of
    the given Boolean network or domain of Boolean networks.

    The command line currently supports two types of inputs:

    - a single Boolean network, given in BoolNet format (.bnet extension).
      In that case, we recommend using mpbn <https://github.com/pauleve/mpbn> instead.

    - a domain of Boolean networks specifed with an AEON file (.aeon extension)
      In that case, the union of the attractors of all the Boolean networks in
      that domain is returned.
    """),
        formatter_class=RawDescriptionHelpFormatter
    )
    _setup_argument_domain(ap)
    ap.add_argument("--fixpoints-only", action="store_true",
            help="Enumerate only fixed points")
    ap.add_argument("--limit", type=int,
            help="Maximum number of solutions")
    args = ap.parse_args()

    bonesis.settings["quiet"] = True

    dom = _load_domain(args)

    bo = bonesis.BoNesis(dom)
    x = bo.cfg() if args.fixpoints_only else bo.hypercube()
    bo.fixed(x)

    it = x.assignments()
    if args.limit:
        it = islice(it, args.limit)

    publish = print
    for sol in it:
        publish(sol)



def main_reprogramming():
    ap = ArgumentParser()
    _setup_argument_domain(ap)
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

    dom = _load_domain(args)

    M = json.loads(args.marker)
    k = args.max_size
    meth_prefix = ""
    meth_suffix = ""
    meth_args = (dom, M, k)
    meth_kwargs = {}
    if args.exclude:
        meth_kwargs["exclude"] = json.loads(args.exclude)
    if args.reachable_from:
        z = json.loads(args.reachable_from)
        meth_prefix = "source_"
        meth_args = (dom, z, M, k)
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
