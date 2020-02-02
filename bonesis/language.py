
__language_api__ = {}

def language_api(cls):
    __language_api__[cls.__name__] = cls
    return cls

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
        return self.make_cfg(self.name, obs=self)
    def __pos__(self):
        return self.make_cfg(None, obs=self)
    def __str__(self):
        return f"Observation({repr(self.name)})"
__language_api__["obs"] = ObservationVar

@supports_reach
class ConfigurationVar(BonesisVar):
    def __init__(self, name=None, obs=None):
        self.obs = obs
        super().__init__(name)
    def publish(self):
        self.mgr.register_configuration(self)
        if self.obs is not None:
            self.mgr.bind_configuration(self, self.obs)
    def __str__(self):
        return f"Configuration({repr(self.name or id(self))})"
__language_api__["cfg"] = ConfigurationVar

class BonesisPredicate(BonesisTerm):
    def __init__(self, *args):
        self.args = args
        super().__init__()
    def publish(self):
        self.mgr.register_prediate(self.__class__.__name__, self.args)
    def right(self):
        r = self.args[-1]
        if isinstance(r, BonesisPredicate):
            r = r.right()
        return r
    def __repr__(self):
        return f"{self.__class__.__name__}{tuple(map(repr,self.args))}"

class UnaryPrediate(BonesisPrediacte):
    def __init__(self, a):
        super().__init__(a)

class BinaryPredicate(BonesisPredicate):
    def __init__(self, a, b):
        super().__init_(a, b)

@language_api
class fixpoint(UnaryPredicate):
    pass

@language_api
class stable(UnaryPredicate):
    pass

@supports_reach
@language_api
class reach(BonesisPredicate):
    pass

