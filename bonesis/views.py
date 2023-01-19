
import itertools
import multiprocessing
import os
from threading import Timer, Lock
import time

import clingo

import networkx as nx
import pandas as pd

from .debug import dbg
from .language import SomeFreeze
from .snippets import bn_nocyclic_attractors
from .utils import OverlayedDict, frozendict
from bonesis0.asp_encoding import (minibn_of_facts,
        configurations_of_facts,
        parse_nb_threads,
        portfolio_path,
        py_of_symbol, symbol_of_py)
from bonesis0 import diversity


class BonesisView(object):
    single_shot = True
    def __init__(self, bo, limit=0, mode="auto", extra=None, **settings):
        self.bo = bo
        self.aspmodel = bo.aspmodel
        self.limit = limit
        if mode == "auto":
            mode = "optN" if self.bo.has_optimizations() else "solve"
        self.mode = mode
        self.settings = OverlayedDict(bo.settings)
        for k,v in settings.items():
            self.settings[k] = v
        self.filters = []

        def parse_extra(extra):
            if isinstance(extra, str):
                if extra == "configurations":
                    return configurations_of_facts
                elif extra == "boolean-network":
                    return minibn_of_facts
                raise ValueError(f"Unknown extra '{extra}'")
            return extra
        if isinstance(extra, (tuple, list)):
            extra = tuple(map(parse_extra, extra))
        elif extra is not None:
            extra = (parse_extra(extra),)
        self.extra_model = extra

    def add_filter(self, func):
        self.filters.append(func)

    def configure(self, ground=True, **opts):
        args = [0]
        if self.single_shot and hasattr(clingo, "version") and clingo.version() >= (5,5,0):
            args.append("--single-shot")
        if self.project:
            args.append("--project")
        if self.mode == "optN":
            args += ["--opt-mode=optN", "--opt-strategy=usc"]

        settings = OverlayedDict(self.settings)
        if self.settings["solutions"] == "subset-minimal":
            if parse_nb_threads(settings.get("parallel")) > 1:
                args += ["--configuration", portfolio_path('subset_portfolio')]
            args += ["--heuristic", "Domain",
                    "--enum-mode", "domRec", "--dom-mod", "5,16"]

        if not self.settings["quiet"] and ground:
            print("Grounding...", end="", flush=True)
            start = time.process_time()
        self.control = self.bo.solver(*args, settings=settings,
                ground=False, **opts)
        self.interrupted = False
        self.configure_show()
        if ground:
            self.control.ground([("base",())])
        if ground and not self.settings["quiet"]:
            end = time.process_time()
            print(f"done in {end-start:.1f}s")

    def configure_show(self):
        for tpl in self.show_templates:
            for x in self.aspmodel.show[tpl]:
                self.control.add("base", [], f"#show {x}.")

    def interrupt(self):
        dbg(f"{self} interrupted")
        self.interrupted = True
        self.control.interrupt()

    def __iter__(self):
        self.configure()
        self._iterator = iter(self.control.solve(yield_=True))
        self._counter = 0
        return self

    def __next__(self):
        if self.limit and self._counter >= self.limit:
            raise StopIteration

        t = Timer(self.settings["timeout"], self.interrupt) \
                if "timeout" in self.settings else None
        t.start() if t is not None else None
        try:
            self.cur_model = next(self._iterator)
            if self.mode == "opt":
                try:
                    while True:
                        self.cur_model = next(self._iterator)
                except StopIteration:
                    pass
            elif self.mode == "optN":
                while not self.cur_model.optimality_proven:
                    self.cur_model = next(self._iterator)
        finally:
            t.cancel() if t is not None else None

        pmodel = self.parse_model(self.cur_model)
        for func in self.filters:
            if not func(pmodel):
                print(f"Skipping solution not verifying {func.__name__}")
                return next(self)
        self._counter += 1
        return pmodel

    def parse_model(self, m):
        model = self.format_model(m)
        if self.extra_model:
            atoms = m.symbols(atoms=True)
            extra = tuple((extra(atoms) for extra in self.extra_model))
            model = (model,) + extra
        return model

    def count(self):
        k = self.parse_model
        if not self.filters:
            self.parse_model = lambda x: 1
        c = len(list(self))
        self.parse_model = k
        return c

    def standalone(self, *args, **kwargs):
        self.configure(ground=False)
        return self.control.standalone(*args, **kwargs)


class NodesView(BonesisView):
    project = True
    show_templates = ["node"]
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        return {py_of_symbol(a.arguments[0]) for a in atoms\
                    if a.name == "node"}

class NonConstantNodesView(BonesisView):
    project = True
    constants = "constant"
    show_templates = ["node", "strong_constant"]
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        nodes = {py_of_symbol(a.arguments[0]) for a in atoms\
                    if a.name == "node"}
        constants = {py_of_symbol(a.arguments[0]) for a in atoms\
                    if a.name == self.constants}
        return nodes.difference(constants)

class NonStrongConstantNodesView(NonConstantNodesView):
    constants = "strong_constant"
    show_templates = ["node", "strong_constant"]


class InfluenceGraphView(BonesisView):
    project = True
    def configure_show(self):
        self.control.add("base", [], \
            "#show."\
            "#show node/1."\
            "#show edge(A,B,S): clause(B,_,A,S).")

    def format_model(self, model):
        atoms = model.symbols(shown=True)
        return self.aspmodel.influence_graph_from_model(atoms)


class BooleanNetworksView(BonesisView):
    project = True
    show_templates = ["boolean_network"]
    def __init__(self, *args, no_cyclic_attractors=False, **kwargs):
        super().__init__(*args, **kwargs)
        if no_cyclic_attractors:
            self.add_filter(bn_nocyclic_attractors)
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        return minibn_of_facts(atoms)


class ProjectedBooleanNetworksContext(object):
    def __init__(self, parent_view, nodes):
        self.parent = parent_view
        self.nodes = nodes
        self.externals = [clingo.Function("myshow", [clingo.String(n)])\
                for n in self.nodes]

    def __enter__(self):
        self.parent.acquire()
        for e in self.externals:
            self.parent.control.assign_external(e, True)
        return self.parent

    def __exit__(self, *args):
        for e in self.externals:
            self.parent.control.assign_external(e, False)
        self.parent.release()


class ProjectedBooleanNetworksViews(BooleanNetworksView):
    single_shot = False
    def __init__(self, *args, skip_empty=False, ground=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_empty = skip_empty
        super().configure(ground=ground)
        self.lock = Lock()

    def acquire(self):
        return self.lock.acquire(False)
    def release(self):
        return self.lock.release()

    def configure(self, **kwargs):
        return

    def configure_show(self):
        self.control.add("base", [], \
            "#external myshow(N): node(N)."\
            "#show."\
            "#show clause(A,B,C,D): myshow(A), clause(A,B,C,D)."\
            "#show constant(A,B): constant(A,B), myshow(A).")
        if self.skip_empty:
            self.control.add("base", [], "node(N) :- myshow(N).")

    def view(self, nodes):
        for n in nodes:
            if n not in self.bo.domain:
                raise ValueError(f"Undefined node '{n}'")
        return ProjectedBooleanNetworksContext(self, nodes)


class LocalFunctionsViews(ProjectedBooleanNetworksViews):
    def view(self, node):
        return super().view((node,))

    def format_model(self, model):
        bn = super().format_model(model)
        if not bn:
            return None
        return bn.popitem()[1]

    do = {
        "list": list,
        "count": lambda v: v.count(),
    }
    def as_dict(self, method="list", keys=None):
        if method not in self.do:
            raise ValueError("unknown method")
        func = self.do[method]
        d = {}
        nodes = self.bo.domain if keys is None else keys
        for n in nodes:
            with self.view(n) as fs:
                d[n] = func(fs)
        return d

    def as_dataframe(self, *args, **kwargs):
        d = self.as_dict(*args, **kwargs)
        return pd.DataFrame.from_dict(d, orient="index").fillna("").T


class DiverseBooleanNetworksView(BooleanNetworksView):
    single_shot = False
    project = False
    def __init__(self, bo, driver="fraction",
            driver_kwargs=dict(pc_drive=50, pc_forget=50),
            skip_supersets=False,
            **kwargs):
        super().__init__(bo, **kwargs)
        self.driver_cls = driver if type(driver) is not str else \
                            getattr(diversity, f"diversity_driver_{driver}")
        self.driver_kwargs = driver_kwargs
        self.skip_supersets = skip_supersets

    def configure(self, **opts):
        super().configure(**opts)
        self.driver = self.driver_cls(**self.driver_kwargs)
        self.diverse = diversity.solve_diverse(self.control.control, self.driver,
                limit=self.limit, on_model=super().parse_model,
                skip_supersets=self.skip_supersets)

    def parse_model(self, model):
        return model

    def __iter__(self):
        self.configure()
        self._iterator = iter(self.diverse)
        self._counter = 0
        return self

class ConfigurationView(BonesisView):
    project = True
    def __init__(self, cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cfg = cfg
    def configure_show(self):
        name = symbol_of_py(self.cfg.name)
        self.control.add("base", [],
            "#show."
            f"#show cfg(X,N,V) : cfg(X,N,V), X={name}.")
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        x = self.cfg.name
        return configurations_of_facts(atoms, keys=[x])[x]

class HypercubeView(BonesisView):
    project = True
    def __init__(self, h, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.h = h
    def configure_show(self):
        name = symbol_of_py(self.h.name)
        self.control.add("base", [],
            "#show."
            f"#show hypercube(X,N,V) : hypercube(X,N,V), X={name}.")
    def format_model(self, model):
        pairs = []
        for a in model.symbols(shown=True):
            _, n, v = py_of_symbol(a)
            if v == 2:
                v = '*'
            elif v == -1:
                v = 0
            pairs.append((n,v))
        return dict(sorted(pairs))

class AllSomeView(BonesisView):
    project = True
    show_templates = ["some"]
    def format_model(self, model):
        def init_some(dtype):
            if dtype == "Freeze":
                return {}
            raise NotImplementedError
        somes = {name: init_some(some.dtype)
            for name, some in self.bo.manager.some.items()}

        for a in model.symbols(shown=True):
            if a.name == "some_freeze":
                name, n, v = py_of_symbol(a)
                somes[name][n] = max(v,0)
        return somes

class SomeView(AllSomeView):
    def __init__(self, some, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.some = some
    def configure_show(self):
        if self.some.dtype == "Freeze":
            name = symbol_of_py(self.some.name)
            self.control.add("base", [],
                    "#show."
                    f"#show some_freeze(M,N,V) : some_freeze(M,N,V), M={name}.")
        else:
            raise NotImplementedError
    def format_model(self, model):
        somes = super().format_model(model)
        return somes[self.some.name]

def SomeFreezeComplementaryView(some, *args, **kwargs):
        subset_min = kwargs["solutions"] == "subset-minimal"

        kwargs["solutions"] = "all"
        coview = SomeView(some, *args, **kwargs)
        opts = SomeFreeze.default_opts | some.opts

        nodes = list(some.mgr.bo.domain)
        if opts["exclude"]:
            nodes = filter(lambda n: n not in opts["exclude"], nodes)
        elements = [(n,0) for n in nodes] + [(n,1) for n in nodes]

        def freeze_add(fs, e):
            coe = (e[0], 1-e[1])
            if coe in fs:
                return fs
            return fs.union((e,))

        def enlarge_candidates(candidates, elements):
            return map(lambda y: freeze_add(*y),
                    itertools.product(candidates, elements))

        candidates = [frozendict({})]
        for _ in range(opts["min_size"]):
            candidates = enlarge_candidates(candidates, elements)

        min_size = opts["min_size"]
        max_size = opts["max_size"]
        good = set()
        for size in range(min_size, max_size+1):
            some.opts["min_size"] = size
            some.opts["max_size"] = size
            coassignments = set(map(frozendict, coview))

            bad = set()
            for candidate in candidates:
                if len(candidate) != size:
                    continue
                if candidate not in coassignments:
                    ignore = False
                    for g in good:
                        if g.issubset(candidate):
                            ignore = True
                            break
                    if not ignore:
                        yield dict(candidate)
                        if subset_min and size > 1:
                            good.add(candidate)
                else:
                    bad.add(candidate)
            if size == 0 and not bad:
                break
            if size != opts["max_size"]:
                if subset_min and size == 1:
                    elements = [next(iter(c)) for c in bad]
                    if not elements:
                        break
                candidates = enlarge_candidates(bad, elements)
        # restore
        opts["min_size"] = min_size
        opts["max_size"] = max_size
