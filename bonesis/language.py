
__language_api__ = {}

def language_api(cls):
    __language_api__[cls.__name__] = cls
    return cls

class ManagedIface(object):
    def __init__(self, manager):
        self.manager = manager
        self.recovery = {}
        def managed(cls):
            class Managed(cls):
                iface = self
                mgr = self.manager
            Managed.__name__ = cls.__name__
            return Managed
        for name, cls in __language_api__.items():
            setattr(self, name, managed(cls))

    def install(self, scope):
        sid = id(scope)
        is_dict = isinstance(scope, dict)
        rec = self.recovery[sid] = {}
        for k in __language_api__:
            hasv = (k in scope) if is_dict else hasattr(scope, k)
            if hasv:
                rec[k] = scope[k] if is_dict else getattr(scope, k)
            cls = getattr(self, k)
            setv = scope.__setitem__ if is_dict else scope.__setattr__
            setv(k, getattr(self, k))

    def uninstall(self, scope):
        sid = id(scope)
        is_dict = isinstance(scope, dict)
        rec = self.recovery[sid]
        for k in __language_api__:
            if k in rec:
                setv = scope.__setitem__ if is_dict else scope.__setattr__
                setv(k, rec[k])
            else:
                delv = scope.__delitem__ if is_dict else scope.__delattr__
                delv(k)
        del self.recovery[sid]


def declare_operator(operator):
    def decorator(func):
        def wrapper(K):
            setattr(K, operator, func)
            return K
        return wrapper
    return decorator

@declare_operator("__ge__") # >=
def reach_operator(left, right):
    return left.iface.reach(left, right)

@declare_operator("__floordiv__") # //
def nonreach_operator(left, right):
    return left.iface.nonreach(left, right)

@declare_operator("__ne__")
def different_operator(left, right):
    return left.iface.different(left, right)


class BonesisTerm(object):
    def __init__(self):
        assert hasattr(self, "mgr"), \
                "do not instantiate non-managed class!"
    def _set_iface(self, iface):
        self.iface = iface
        self.mgr = self.iface.manager

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
    def publish(self):
        self.mgr.register_observation(self)
    def __invert__(self):
        return self.iface.cfg(self.name, obs=self)
    def __pos__(self):
        return self.iface.cfg(None, obs=self)
    def __str__(self):
        return f"Observation({repr(self.name)})"
__language_api__["obs"] = ObservationVar

@different_operator
@reach_operator
@nonreach_operator
class ConfigurationVar(BonesisVar):
    def __init__(self, name=None, obs=None):
        self.obs = obs
        super().__init__(name)
    def publish(self):
        self.mgr.register_configuration(self)
    def __str__(self):
        return f"Configuration({repr(self.name or id(self))})"
__language_api__["cfg"] = ConfigurationVar

@language_api
class BonesisPredicate(BonesisTerm):
    def __init__(self, *args):
        self.args = args
        if not hasattr(self, "predicate_name"):
            self.predicate_name = self.__class__.__name__
        for obj in self.args:
            if isinstance(obj, BonesisTerm):
                if not hasattr(self, "iface"):
                    self._set_iface(obj.iface)
                else:
                    assert obj.iface is self.iface, "mixed managers"
        super().__init__()
        self.publish()
    @classmethod
    def type_error(celf):
        raise TypeError(f"Invalid arguments for {celf.__name__}")
    def publish(self):
        self.mgr.register_predicate(self.predicate_name, *self.args)
    def left(self):
        return self.args[0]
    def right(self):
        return self.args[-1]
    def __repr__(self):
        return f"{self.__class__.__name__}{tuple(map(repr,self.args))}"

@language_api
class constant(BonesisPredicate):
    def __init__(self, node, value):
        super().__init__(node, value)
        assert node in self.mgr.bo.domain

@language_api
class fixed(BonesisPredicate):
    def __init__(self, arg):
        if isinstance(arg, ConfigurationVar):
            self.predicate_name = "fixpoint"
        elif isinstance(arg, ObservationVar):
            self.predicate_name = "trapspace"
            arg = +arg
        else:
            self.type_error()
        super().__init__(arg)

@language_api
class in_attractor(BonesisPredicate):
    def __init__(self, arg):
        if not isinstance(arg, ConfigurationVar):
            self.type_error()
        super().__init__(arg)

@reach_operator
@nonreach_operator
@language_api
class reach(BonesisPredicate):
    """
    left: cfg, reach()
    right: cfg, obs, reach(), fixed()
    """

    @classmethod
    def left_arg(celf, arg):
        if isinstance(arg, ConfigurationVar):
            return arg
        if isinstance(arg, reach):
            return celf.left_arg(arg.right())
        celf.type_error()

    @classmethod
    def right_arg(celf, arg):
        if isinstance(arg, ConfigurationVar):
            return arg
        if isinstance(arg, ObservationVar):
            return celf.right_arg(+arg)
        if isinstance(arg, (fixed, reach)):
            return celf.right_arg(arg.left())
        celf.type_error()

    def __init__(self, left, right):
        left = self.left_arg(left)
        right = self.right_arg(right)
        super().__init__(left, right)

@language_api
class nonreach(reach):
    @classmethod
    def right_arg(celf, arg):
        if isinstance(arg, ObservationVar):
            celf.type_error() # universal constraint
        return super().right_arg(arg)

@language_api
class different(BonesisPredicate):
    def __init__(self, left, right):
        if not isinstance(left, ConfigurationVar) or \
                not isinstance(right, ConfigurationVar):
            self.type_error()
        super().__init__(left, right)
