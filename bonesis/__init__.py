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

import ast
import copy

import os

from colomoto import minibn
import networkx as nx

from .asp_encoding import ASPModel_DNF
from .debug import *
from .domains import *
from .language import ManagedIface
from .manager import BonesisManager
from .snippets import *
from .utils import OverlayedDict
from .views import *

__language_api__ = ["obs", "cfg"]

settings = {
    "parallel": 1,
    "clingo_options": (
        tuple(os.environ["CLINGO_OPTS"].split()) if "CLINGO_OPTS" in os.environ else ()
    ),
    "clingo_opt_strategy": "bb",
    "solutions": "all",
    "quiet": False,
    "timeout": 0,
    "soft_interrupt": False,  # if True, silently end solving
    "fail_if_timeout": True,  # if timeout raise TimeoutError
    "clingo_gil_workaround": 1,
    # 0/None: no GIL wrapper for clingo
    # 1: run clingo in a single background thread
    # 2: separate thread for each solution
}

_FORBIDDEN_LOAD_CODE_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.Delete,
    ast.Global,
    ast.Nonlocal,
    ast.Try,
    ast.Raise,
    ast.Assert,
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
    ast.NamedExpr,
)

_FORBIDDEN_LOAD_CODE_NAMES = {
    "__builtins__",
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "globals",
    "input",
    "locals",
    "open",
}


class UnsafeBonesisCodeError(ValueError):
    pass


class _LoadCodeValidator(ast.NodeVisitor):
    def generic_visit(self, node):
        if isinstance(node, _FORBIDDEN_LOAD_CODE_NODES):
            self._error(node, f"unsupported syntax '{node.__class__.__name__}'")
        super().generic_visit(node)

    def visit_Name(self, node):
        if node.id in _FORBIDDEN_LOAD_CODE_NAMES or node.id.startswith("__"):
            self._error(node, f"forbidden name '{node.id}'")

    def visit_Attribute(self, node):
        if node.attr.startswith("_"):
            self._error(node, f"forbidden attribute '{node.attr}'")
        self.visit(node.value)

    def visit_Call(self, node):
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            self._error(node, "unsupported call target")
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            self._validate_assignment_target(target)
        self.visit(node.value)

    def visit_AnnAssign(self, node):
        self._error(node, "annotated assignments are not supported")

    def visit_AugAssign(self, node):
        self._error(node, "augmented assignments are not supported")

    def _validate_assignment_target(self, target):
        if isinstance(target, ast.Name):
            if target.id in _FORBIDDEN_LOAD_CODE_NAMES or target.id.startswith("__"):
                self._error(target, f"forbidden assignment target '{target.id}'")
            return
        if isinstance(target, ast.Subscript):
            self.visit(target)
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._validate_assignment_target(elt)
            return
        self._error(target, "unsupported assignment target")

    def _error(self, node, message):
        line = getattr(node, "lineno", "?")
        raise UnsafeBonesisCodeError(f"unsafe BoNesis code at line {line}: {message}")


def _compile_load_code(prog, filename, safe):
    tree = ast.parse(prog, filename=filename, mode="exec")
    if safe:
        _LoadCodeValidator().visit(tree)
    return compile(tree, filename, "exec")


class BoNesis(object):
    def __init__(self, domain, data=None):
        if not isinstance(domain, BonesisDomain):
            if isinstance(domain, minibn.BooleanNetwork):
                domain = BooleanNetwork(domain)
            elif isinstance(domain, (nx.DiGraph, nx.MultiDiGraph)):
                domain = InfluenceGraph(domain)
            else:
                raise TypeError(f"Cannot handle domain with type '{type(domain)}'")
        self.domain = domain
        self.data = data or {}
        self.manager = BonesisManager(self)

        self.settings = OverlayedDict(settings)
        self.aspmodel = ASPModel_DNF(self.domain, self.data, self.manager)

        self.iface = ManagedIface(self.manager)
        self.iface.install(self)

    def fork(self):
        fo = self.__class__(self.domain, self.data)
        fo.manager.reset_from(self.manager)
        return fo

    def debug(self, asp_output="/tmp/debug.asp"):
        with open(asp_output, "w") as fp:
            self.aspmodel.make()
            fp.write(str(self.aspmodel))

    def set_constant(self, cst, value):
        self.aspmodel.constants[cst] = value

    def install_language(self, scope):
        self.iface.install(scope)

    def uninstall_language(self, scope):
        self.iface.uninstall(scope)

    def has_optimizations(self):
        return bool(self.manager.optimizations)

    def load_code(
        self, prog, defs=None, dest_scope=None, safe=False, filename="<bonesis>"
    ):
        """
        Load BoNesis DSL code into the current BoNesis object.

        The BoNesis language symbols are installed in the execution namespace,
        allowing code to use calls such as `obs(...)`, `cfg(...)`,
        `fixed(...)`, and `dyncfg(...)` without prefixing them with the BoNesis
        object.

        Parameters
        ----------
        prog: str
            BoNesis DSL code to execute.
        defs: dict, optional
            Local namespace used when executing `prog`. This can be used to pass
            predefined objects and to collect variables defined by the code.
        dest_scope: dict, optional
            Dictionary updated with the execution namespace returned by the
            loader.
        safe: bool (default: False)
            Whether to validate the code with the safe AST checker before
            execution and to disable Python builtins during execution.
        filename: str (default: "<bonesis>")
            Filename reported in syntax errors and validation errors.

        Returns
        -------
        dict
            Execution namespace containing variables defined by the loaded
            code.

        Raises
        ------
        UnsafeBonesisCodeError
            If `safe` is True and the code contains unsupported or unsafe
            Python syntax.
        SyntaxError
            If `prog` is not valid Python syntax.
        """

        scope = {}
        self.install_language(scope)
        if safe:
            scope["__builtins__"] = {}
        try:
            compiled = _compile_load_code(prog, filename, safe)
            exec(compiled, scope, defs)
        finally:
            self.uninstall_language(scope)
            scope.pop("__builtins__", None)
        ret = defs if defs else scope
        if dest_scope is not None:
            dest_scope.update(ret)
        return ret

    def load(self, script, defs=None, dest_scope=None, safe=False):
        """
        Load BoNesis DSL code from a file.

        Parameters
        ----------
        script: str or path-like
            File containing BoNesis DSL code.
        defs: dict, optional
            Local namespace used when executing the file content.
        dest_scope: dict, optional
            Dictionary updated with the execution namespace returned by the
            loader.
        safe: bool (default: False)
            Whether to validate the file content with the safe AST checker
            before execution and to disable Python builtins during execution.

        Returns
        -------
        dict
            Execution namespace containing variables defined by the loaded
            code.

        Raises
        ------
        UnsafeBonesisCodeError
            If `safe` is True and the file contains unsupported or unsafe
            Python syntax.
        SyntaxError
            If the file content is not valid Python syntax.
        """

        with open(script) as fp:
            return self.load_code(
                fp.read(),
                defs=defs,
                dest_scope=dest_scope,
                safe=safe,
                filename=str(script),
            )

    def solver(self, *args, **kwargs):
        self.aspmodel.make()
        if "settings" not in kwargs:
            kwargs["settings"] = self.settings
        return self.aspmodel.solver(*args, **kwargs)

    def is_satisfiable(self):
        control = self.solver(1)
        return control.solve().satisfiable

    def boolean_networks(self, *args, **kwargs):
        return BooleanNetworksView(self, *args, **kwargs)

    def diverse_boolean_networks(self, *args, **kwargs):
        return DiverseBooleanNetworksView(self, *args, **kwargs)

    def projected_boolean_networks(self, **kwargs):
        return ProjectedBooleanNetworksViews(self, **kwargs)

    def local_functions(self, **kwargs):
        return LocalFunctionsViews(self, **kwargs)

    def influence_graphs(self, **kwargs):
        return InfluenceGraphView(self, **kwargs)

    def assignments(self, solutions="subset-minimal", **kwargs):
        return AllSomeView(self, solutions=solutions, **kwargs)
