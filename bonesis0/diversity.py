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

import random
import time
from threading import Thread
from queue import Queue

import clingo

from .asp_encoding import minibn_of_facts
from .clingo_solving import setup_clingo_solve_handler
from .gil_utils import setup_gil_iterator


class diversity_driver:
    preds = {("clause", 4), ("constant", 1)}

    def match_pred(self, a):
        return (a.name, len(a.arguments)) in self.preds

    def initialize(self, control):
        self.control = control
        self.control.add(
            "diversity",
            [],
            """
            #heuristic clause(N,C,L,S) : avoidclause(N,C,L,S). [10,false]
            #heuristic constant(N) : avoidconstant(N). [2,false]
            #heuristic clause(N,C,L,S). [1,false] %subset
            #external avoidclause(N,C,L,S) : clause(N,C,L,S).
            #external avoidconstant(N) : constant(N).""",
        )
        self.control.ground([("diversity", [])])
        self.control.configuration.solver[0].heuristic = "Domain"
        self.control.configuration.solve.models = "1"
        self.avoided = []

    def avoid(self, clues):
        for a in clues:
            self.control.assign_external(a, True)
        self.avoided.extend(clues)


class diversity_driver_fraction(diversity_driver):
    def __init__(self, pc_drive=100, pc_forget=100):
        super().__init__()
        self.pc_drive = pc_drive
        self.pc_forget = pc_forget

    def on_solution(self, atoms):
        self.atoms = [a for a in atoms if self.match_pred(a)]

    def push(self):
        self.forget()
        if self.pc_drive == 100:
            drive = self.atoms
        else:
            drive = random.sample(self.atoms, (len(self.atoms) * self.pc_drive) // 100)
        clues = [clingo.Function("avoid{}".format(a.name), a.arguments) for a in drive]
        self.avoid(clues)

    def forget(self):
        if self.pc_forget == 100:
            for a in self.avoided:
                self.control.assign_external(a, False)
            self.avoided.clear()
            return
        random.shuffle(self.avoided)
        nb = (len(self.avoided) * self.pc_forget) // 100
        for a in self.avoided[:nb]:
            self.control.assign_external(a, False)
        self.avoided = self.avoided[nb:]


def on_model_make_minibn(model):
    return minibn_of_facts(model.symbols(True))


class solve_diverse:
    def __init__(
        self,
        control,
        driver,
        skip_supersets=False,
        limit=0,
        on_model=on_model_make_minibn,
        settings={},
        progress=None,
    ):
        self.control = control
        self.skip_supersets = skip_supersets
        self.driver = driver
        self.driver.initialize(self.control)
        self.limit = limit
        self.on_model = on_model
        self.settings = settings
        self.progress = progress
        self.__counter = 0

    def inject_solution(self, atoms):
        self.driver.on_solution(atoms)
        self.prepare_next(atoms)
        self.__counter += 1

    def count(self):
        return self.__counter

    def prepare_next(self, atoms):
        self.driver.push()
        preds = {
            ("clause", 4): "in(A2,A0,A3), maxC(A0,C), A1=1..C",
            ("constant", 2): "node(A0), A1=(-1;1)",
        }

        def match_preds(a):
            return (a.name, len(a.arguments)) in preds

        exclude_cst = list(map(str, filter(match_preds, atoms)))
        if not self.skip_supersets:
            for n, ca in preds:
                nbatoms = len(
                    [a for a in atoms if a.name == n and len(a.arguments) == ca]
                )
                f = preds[(n, ca)]
                exclude_cst.append(
                    "{0} {{ {1}({2}) : {3} }} {0}".format(
                        nbatoms, n, ",".join(["A%d" % i for i in range(ca)]), f
                    )
                )
        self.control.add("skip", [], ":- {}.".format(",".join(exclude_cst)))
        self.control.ground([("skip", [])])

    def __iter__(self):
        self.start_time = time.time()
        self.first_time = None
        if self.progress:
            self.progressbar = self.progress(
                desc=self.progress_desc(), total=None, bar_format="{desc}"
            )
        return self

    def __next__(self):
        if self.limit and self.__counter >= self.limit:
            self.close_progress()
            raise StopIteration

        sh = setup_clingo_solve_handler(self.settings, self.control)
        with sh:
            it = setup_gil_iterator(self.settings, iter(sh), sh, self.control)
            model = next(it, None)
            if model is None:
                self.close_progress()
                raise StopIteration
            atoms = model.symbols(atoms=True)
            ret = self.on_model(model)

        self.__counter += 1
        now = time.time()
        if self.first_time is None:
            self.first_time = now
        self.update_progress()
        self.driver.on_solution(atoms)
        self.prepare_next(atoms)
        return ret

    def progress_desc(self):
        total = f"/{self.limit}" if self.limit else ""
        if self.__counter == 0:
            return f"Found 0{total} solutions"
        elapsed = time.time() - self.start_time
        first = self.first_time - self.start_time
        noun = "solution" if self.__counter == 1 else "solutions"
        desc = (
            f"Found {self.__counter}{total} {noun} in {elapsed:.1f}s "
            f"(first in {first:.1f}s"
        )
        if self.__counter > 1:
            rate = (elapsed - first) / (self.__counter - 1)
            desc += f"; rate {rate:.1f}s"
        return f"{desc})"

    def update_progress(self):
        desc = self.progress_desc()
        if self.progress:
            self.progressbar.set_description_str(desc, refresh=False)
            self.progressbar.update()
            self.progressbar.refresh()
        else:
            print(f"\r{desc}", end="", flush=True)

    def close_progress(self):
        if self.progress:
            self.progressbar.close()
        elif self.__counter:
            print()
