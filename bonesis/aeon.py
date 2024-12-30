# Copyright or © or Copr. Loïc Paulevé (2023)
#
# loic.pauleve@cnrs.fr
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#

import itertools
import re

import boolean
import clingo

from colomoto.minibn import struct_of_dnf, NOT

import mpbn
import bonesis
from bonesis.domains import BonesisDomain
from bonesis0.asp_encoding import nb_clauses, symbols, minibn_of_facts
from bonesis.asp_encoding import s2v

RE_PARAMETER = re.compile(r'(\w+)\(([^\)]*)\)')

class AEONFunction(object):
    def __init__(self, func, struct):
        self.func = func
        self.struct = struct
    def __str__(self):
        return str(self.func)
    def __repr__(self):
        return str(self.func)

class AEONPartialFunction(object):
    def __init__(self, func, struct, params):
        self.func = func
        self.struct = struct
        self.params = params
    def __str__(self):
        return f"{self.func} [{self.params}]"
    def __repr__(self):
        return f"AEONPartialFunction({self.func},{self.params})"


def asp_of_AEONReg(dom, boenc, n, acting_n=None, regs=None, ns=""):
    regs = dom.am.predecessors(n) if regs is None else regs
    regs = [ dom.am.get_variable_name(x) for x in regs ]
    acting_n = n if acting_n is None else acting_n
    d = len(regs)
    boenc.load_template_domain(ns=ns, allow_externals=ns)
    if dom.canonic:
        boenc.load_template_canonic(ns=ns)
    rules = []
    nbc = dom.get_maxclause(d)
    rules.append(clingo.Function(f"{ns}maxC", symbols(n, nbc)))
    for m in regs:
        reg = dom.am.find_regulation(m, acting_n)
        args = symbols(m, n)
        monotonicity = reg.get("sign")
        if monotonicity in [True, "positive", "+"]:
            sign = 1
        elif monotonicity in [False, "negative", "-"]:
            sign = -1
        else:
            sign = "(-1;1)"
        rules.append("{}in({},{},{})".format(ns, *args, sign))
        if reg.get("essential"):
            boenc.load_template_edge(ns=ns)
            rules.append(":- not {}edge({},{},_)".format(ns, *args))
    return rules

def asp_of_AEONFunction(dom, n, func):
    rules = []
    if isinstance(func.struct, bool):
        rules.append(clingo.Function("constant", symbols(n, s2v(func.struct))))
        return rules
    for cid, c in enumerate(func.struct):
        if isinstance(c, bool):
            rules.append(clingo.Function("constant", symbols(n, s2v(c))))
        else:
            for m, s in c:
                rules.append(clingo.Function("clause", symbols(n, cid+1, m, s2v(s))))
    return rules

def asp_of_AEONParameters(dom, boenc):
    ns = "p_"
    rules = []
    for param_name, param_args in dom.params.items():        
        rules.append(clingo.Function(f"{ns}node", symbols(param_name)))
        n = next(iter(dom.param_nodes[param_name]))
        rules += asp_of_AEONReg(dom, boenc, n=param_name, acting_n=n, regs=param_args, ns=ns)
    return rules

def asp_of_AEONPartialFunction(dom, n, func):
    rules = []
    for cid, c in enumerate(func.struct):
        cid = cid + 1
        ps = tuple(set([v for (v,_) in c if v in func.params]))
        if not ps:
            for m, s in c:
                rules.append(clingo.Function("clause", symbols(n, cid, m, s2v(s))))
        else:
            for m, s in c:
                if m in func.params:
                    if s < 0:
                        raise NotImplementedError("negation of parameters is not supported yet")
                    continue
                rules.append(clingo.Function(f"pre_clause", symbols(n, cid, m, s2v(s))))

            ps = symbols(*ps)
            cases = [[(f"p_clause({p},C{i},M{i},S{i})", i),
                        (f"p_constant({p}, 1),C{i}=c", -1)] for i, p in enumerate(ps)]
            gid = ",".join([f"C{i}" for i in range(len(ps))])
            n, cid = symbols(n, cid)
            for glue in itertools.product(*cases):
                glue = dict(glue)
                contents = set(glue.values()) - {-1}
                glue = "; ".join(glue)
                for i in contents:
                    rules.append(f"clause({n},({cid},{gid}),M{i},S{i}) :- node({n}); {glue}")
            rules.append(f"clause({n},({cid},{gid}),M,S) :- pre_clause({n},{cid},M,S), clause({n},({cid},{gid}),_,_)")
            all_constants = "; ".join([c[1][0] for c in cases])
            rules.append(f"clause({n},({cid},{gid}),M,S) :- pre_clause({n},{cid},M,S), {all_constants}")
    return rules

def asp_of_AEONDomain(dom, boenc):
    rules = []
    rules.append(clingo.Function("nbnode", symbols(len(dom))))
    rules.extend(asp_of_AEONParameters(dom, boenc))
    for name, func in dom.items():
        rules.append(clingo.Function("node", symbols(name)))
        if func is None:
            rules.extend(asp_of_AEONReg(dom, boenc, name))
        elif isinstance(func, AEONFunction):
            rules.extend(asp_of_AEONFunction(dom, name, func))
        elif isinstance(func, AEONPartialFunction):
            rules.extend(asp_of_AEONPartialFunction(dom, name, func))
        else:
            raise TypeError()
    return rules

class AEONDomain(BonesisDomain, dict):
    bonesis_encoder = asp_of_AEONDomain
    def __init__(self, aeon_model, maxclause=None, canonic=True):
        super().__init__()
        self.am = aeon_model
        self.ba = boolean.BooleanAlgebra(NOT_class=NOT)
        self.maxclause = maxclause
        self.canonic = canonic # canonicty is ensured only for parameters and free functions
        self.params = {}
        self.param_nodes = {}
        self._f = bonesis.BooleanNetwork({})

        # Call `setitem` on each function to compute the necessary internal representations.
        for name in self.am.variable_names():
            func = self.am.get_update_function(name)
            self[name] = func

    def get_maxclause(self, d):
        if d == 0:
            return 0
        nbc = nb_clauses(d)
        if self.maxclause:
            nbc = min(self.maxclause, nbc)
        return nbc

    def __setitem__(self, node, func):
            # Let AEON parse the function expression to check that it's valid. 
            self.am.set_update_function(node, func)            
            func = self.am.get_update_function(node)

            if func is None:
                return super().__setitem__(node, func)
            
            # Remove unsupported logical operators.
            func = func.to_and_or_normal_form()

            # Transform the function into the format understood by bonesis. At the same time,
            # ensure that only variables are used as function arguments.
            def convert_to_ba(ba, bn, update):
                if update.is_const():
                    if update.as_const():
                        return ba.TRUE
                    else:
                        return ba.FALSE
                elif update.is_var():
                    return ba.Symbol(bn.get_variable_name(update.as_var()))
                elif update.is_not():
                    inner = convert_to_ba(ba, bn, update.as_not())
                    return ba.NOT(inner)
                elif update.is_and():
                    a, b = update.as_and()
                    a = convert_to_ba(ba, bn, a)
                    b = convert_to_ba(ba, bn, b)
                    return ba.AND(a, b)
                elif update.is_or():
                    a, b = update.as_and()
                    a = convert_to_ba(ba, bn, a)
                    b = convert_to_ba(ba, bn, b)
                    return ba.OR(a, b)
                elif update.is_param():
                    p_id, args = update.as_param()
                    p_name = self.am.get_explicit_parameter_name(p_id)
                    complex_args = [ arg for arg in args if not arg.is_var() ]                    
                    if len(complex_args):
                        # "Complex arguments", i.e. non-trivial expressions as function arguments, are not supported.
                        raise NotImplementedError(f"Function {p_name} uses unsupported complex arguments ({complex_args}).")
                    arg_names = [ bn.get_variable_name(arg.as_var()) for arg in args ]                    
                    if p_name not in self.params:
                        self.params[p_name] = arg_names
                    elif self.params[p_name] != arg_names:
                        # Using the same parameter multiple times with different arguments is also not supported.
                        # In theory, there is also a corner case when the parameter is used multiple times with the same
                        # arguments but different regulation monotonicity, which also does not work, but that hopefully 
                        # isn't something that people would normally try to do...
                        raise NotImplementedError(f"Function {p_name} is used multiple times with different arguments.")
                    return ba.Symbol(p_name)
                else:
                    # If everything is ok, we should never get here.
                    raise RuntimeError(f"Unexpected function expression {update}.")

            # Names of parameters used in the update function together with their arity.
            used_parameters = { }
            for p_id in func.support_parameters():
                p_name = self.am.get_explicit_parameter_name(p_id)
                p_arity = self.am.get_explicit_parameter_arity(p_id)
                used_parameters[p_name] = p_arity

            f = convert_to_ba(self.ba, self.am, func)
            self._f[node] = f
            f = self._f[node]
            s = struct_of_dnf(self.ba, f, list, sort=True)
            if len(used_parameters) > 0:
                func = AEONPartialFunction(f, s, used_parameters)
                # Update a map which assigns each parameter the set of network
                # variables that actually use said parameter.
                for name in used_parameters:
                    if name in self.param_nodes:
                        self.param_nodes[name].add(node)
                    else:
                        self.param_nodes[name] = {node}
            else:
                func = AEONFunction(f, s)

            return super().__setitem__(node, func)

    @classmethod
    def from_aeon_file(celf, filename, **opts):
        import biodivine_aeon
        with open(filename) as fp:
            data = fp.read()
        am = biodivine_aeon.BooleanNetwork.from_aeon(data)
        return celf(am, **opts)


class AEONParametersView(bonesis.BonesisView):
    project = True
    show_templates = ["boolean_network"]
    ns = "p_"
    def configure_show(self):
        for tpl in self.show_templates:
            for x in self.aspmodel.show[tpl]:
                self.control.add("base", [], f"#show {self.ns}{x}.")
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        return minibn_of_facts(atoms, ns=self.ns)

__all__ = ["AEONDomain", "AEONParametersView"]

if __name__ == "__main__":
    import sys
    dom = AEONDomain.from_aeon_file(sys.argv[1])
    bo = bonesis.BoNesis(dom)
    bo.aspmodel.make()
    print(str(bo.aspmodel))
