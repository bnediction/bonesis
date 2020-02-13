
from threading import Timer

from .debug import dbg
from .utils import OverlayedDict
from bonesis0.asp_encoding import minibn_of_facts

class BonesisView(object):
    def __init__(self, bo):
        self.bo = bo
        self.aspmodel = bo.aspmodel
        self.limit = 0
        self.settings = OverlayedDict(bo.settings)

    def configure(self, **opts):
        args = [self.limit]
        if self.project:
            args.append("--project")
        self.control = self.bo.solver(*args, settings=self.settings, **opts)
        self.interrupted = False
        self.configure_show()

    def configure_show(self):
        for tpl in self.show_templates:
            for x in self.aspmodel.show[tpl]:
                self.control.add("base", [], f"#show {x}.")
        self.control.ground([("base",[])])

    def interrupt(self):
        dbg(f"{self} interrupted")
        self.interrupted = True
        self.control.interrupt()

    def __iter__(self):
        self.configure()
        self._iterator = self.control.solve(yield_=True)
        return self

    def __next__(self):
        t = Timer(self.settings["timeout"], self.interrupt) \
                if "timeout" in self.settings else None
        try:
            self.cur_model = next(self._iterator)
        finally:
            t.cancel() if t is not None else None
        return self.format_model(self.cur_model)

    def count(self):
        c = 0
        self.configure()
        for _ in self.control.solve(yield_=True):
            c += 1
        return c

    def standalone(self, *args, **kwargs):
        self.configure(ground=False)
        return self.control.standalone(*args, **kwargs)

class BooleanNetworksView(BonesisView):
    project = True
    show_templates = ["boolean_network"]
    def format_model(self, model):
        atoms = model.symbols(shown=True)
        return minibn_of_facts(atoms)
