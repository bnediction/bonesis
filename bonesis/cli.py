from argparse import ArgumentParser
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
