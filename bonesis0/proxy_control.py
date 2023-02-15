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

import clingo

class ProxyControl(object):
    def __init__(self, arguments=[], **kwargs):
        self.cmdline_arguments = arguments
        self.input = ""
        self.control = clingo.Control(arguments, **kwargs)
        self.__simple = True

    ###

    @property
    def is_standalone_equivalent(self):
        return self.__simple

    def standalone(self, clingo_prog="clingo", custom_arguments=[],
                        output_filename=None):
        content = "#!/usr/bin/env bash\n%s %s \"${@}\" - <<EOF\n%s\nEOF\n" % (clingo_prog, \
            " ".join(self.cmdline_arguments+custom_arguments), self.input)
        if not output_filename:
            return content
        else:
            with open(output_filename, "w") as fp:
                fp.write(content)

    def export_rules(self, output_filename):
        with open(output_filename, "w") as fp:
            fp.write(self.input)

    ###

    def add(self, name, params, program):
        is_custom = name != "base" or params != []
        if is_custom:
            self.input += "#program {}({}).\n".format(name, ",".join(params))
        self.input += "{}\n".format(program)
        if is_custom:
            self.input += "#program base.\n"
        return self.control.add(name, params, program)

    def load(self, path):
        with open(path) as fp:
            self.input += fp.read()
        return self.control.load(path)

    def ground(self, *args):
        return self.control.ground(*args)

    def interrupt(self):
        return self.control.interrupt()

    def solve(self, *args, **kwargs):
        return self.control.solve(*args, **kwargs)

    def assign_external(self, *args):
        self.__simple = False
        return self.control.assign_external(*args)

    def register_observer(self, *args):
        self.__simple = False
        return self.control.register_observer(*args)

    def register_propagator(self, *args):
        self.__simple = False
        return self.control.register_propagator(*args)

    def release_external(self, *args):
        self.__simple = False
        return self.control.release_external(*args)



