
import random

import clingo

from .utils import aspf
from .asp_encoding import minibn_of_facts

class diversity_driver:
    preds = {("clause", 4), ("constant", 1)}
    def match_pred(self, a):
        return (a.name, len(a.arguments)) in self.preds
    def initialize(self, control):
        self.control = control
        self.control.load(aspf("diversity.asp"))
        self.control.ground([("diversity",[])])
        self.control.configuration.solver[0].heuristic = "Domain"
        self.control.configuration.solve.models = "1"
        self.avoided = []
    def avoid(self, clues):
        for a in clues:
            self.control.assign_external(a, True)
        self.avoided.extend(clues)

class diversity_driver_opposite(diversity_driver):
    def on_model(self, model):
        self.atoms = [a for a in model.symbols(atoms=True) \
                if self.match_pred(a)]
    def push(self):
        self.forget()
        clues = [clingo.Function("avoid{}".format(a.name), a.arguments) for a in self.atoms]
        self.avoid(clues)
    def forget(self):
        for a in self.avoided:
            self.control.assign_external(a, False)
        self.avoided.clear()

class diversity_driver_fraction(diversity_driver_opposite):
    def __init__(self, pc=50):
        super().__init__()
        self.pc = pc
    def push(self):
        self.forget()
        drive = random.sample(self.atoms, (len(self.atoms)*self.pc)//100)
        clues = [clingo.Function("avoid{}".format(a.name), a.arguments) for a in drive]
        self.avoid(clues)
    def forget(self):
        random.shuffle(self.avoided)
        nb = (len(self.avoided)*(100-self.pc))//100
        for a in self.avoided[:nb]:
            self.control.assign_external(a, False)
        self.avoided = self.avoided[nb:]


class solve_diverse:
    def __init__(self, control, driver, skip_supersets=False, limit=0):
        self.control = control
        self.skip_supersets = skip_supersets
        self.driver = driver
        self.driver.initialize(self.control)
        self.limit = limit

    def __iter__(self):
        self.__counter = 0
        return self

    def __next__(self):
        if self.limit and self.__counter == self.limit:
            raise StopIteration

        found = False
        with self.control.solve(yield_=True) as solutions:
            for model in solutions:
                found = True
                self.__counter += 1
                atoms = model.symbols(atoms=True)
                bn = minibn_of_facts(model.symbols(True))
                self.driver.on_model(model)
                break
        if not found:
            raise StopIteration

        self.driver.push()

        preds = {
            ("clause", 4): "in(A2,A0,A3), maxC(A0,C), A1=1..C",
            ("constant", 2): "node(A0), A1=(-1;1)"
        }
        def match_preds(a):
            return (a.name, len(a.arguments)) in preds
        exclude_cst = list(map(str, filter(match_preds, atoms)))
        if not self.skip_supersets:
            for (n, ca) in preds:
                nbatoms = len([a for a in atoms if a.name == n and len(a.arguments) == ca])
                f = preds[(n,ca)]
                exclude_cst.append("{0} {{ {1}({2}) : {3} }} {0}".format(nbatoms, n,
                    ",".join(["A%d"%i for i in range(ca)]), f))
        self.control.add("skip", [], ":- {}.".format(",".join(exclude_cst)))
        self.control.ground([("skip", [])])

        return bn

