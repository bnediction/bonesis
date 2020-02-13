
from threading import Timer

from .debug import dbg
from .utils import OverlayedDict
from bonesis0.asp_encoding import minibn_of_facts
from bonesis0 import diversity

class BonesisView(object):
    def __init__(self, bo, limit=0):
        self.bo = bo
        self.aspmodel = bo.aspmodel
        self.limit = limit
        self.settings = OverlayedDict(bo.settings)

    def configure(self, **opts):
        args = [self.limit]
        if self.project:
            args.append("--project")
        self.control = self.bo.solver(*args, settings=self.settings, **opts)
        self.interrupted = False
        self.configure_show()
        self.control.ground([("base",[])])

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

class DiverseBooleanNetworksView(BooleanNetworksView):
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
                limit=self.limit, on_model=super().format_model,
                skip_supersets=self.skip_supersets)

    def format_model(self, model):
        return model

    def __iter__(self):
        self.configure()
        self._iterator = iter(self.diverse)
        return self
