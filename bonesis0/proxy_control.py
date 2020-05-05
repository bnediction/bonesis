
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



