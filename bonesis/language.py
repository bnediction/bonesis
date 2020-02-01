
def operator_type_error(name, *args):
    raise TypeError(f"Invalid types for {name} operator {tuple(map(type,args))}")

def reach_operator(left, right):
    # TODO: support reach as left and right
    if not isinstance(left, ConfigurationVar) \
            or not isinstance(right, (ConfigurationVar, ObservationVar)):
        operator_type_error("reach", left, right)
    return reach(left, right)

def supports_operator(operator, func):
    def wrapper(K):
        setattr(K, operator, func)
        return K
    return wrapper
supports_reach = supports_operator("__ge__", reach_operator)


class BonesisTerm(object):
    pass

class BonesisVar(BonesisTerm):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.publish()
    def publish(self):
        pass

class ObservationVar(BonesisVar):
    def __init__(self, name):
        super().__init__(name)
    def __invert__(self):
        return self.make_cfg(self)
    def __str__(self):
        return f"Observation({repr(self.name)})"

@supports_reach
class ConfigurationVar(BonesisVar):
    def __init__(self, name=None):
        self.obs = None
        if isinstance(name, ObservationVar):
            self.obs = name
            name = None
        super().__init__(name)
    def publish(self):
        self.mgr.register_configuration(self)
        if self.obs is not None:
            self.mgr.bind_configuration(self, self.obs)
    def __str__(self):
        return f"Configuration({repr(self.name or id(self))})"

class BonesisPredicate(BonesisTerm):
    pass

class BinaryPredicate(BonesisPredicate):
    def __init__(self, l, r):
        self.left = l
        self.right = r
        super().__init__()
    def __repr__(self):
        return f"{self.__class__.__name__}({self.left},{self.right})"

@supports_reach
class reach(BinaryPredicate):
    pass


