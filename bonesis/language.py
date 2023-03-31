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

__language_api__ = {}

def language_api(cls):
    __language_api__[cls.__name__] = cls
    return cls

class ManagedIface(object):
    def __init__(self, manager, parent=None):
        self.manager = manager
        self.stack_manager = [] if parent is None else parent.stack_manager
        self.stack_manager.append(manager)
        self.recovery = {}
        def managed(cls):
            class Managed(cls):
                iface = self
                @property
                def mgr(_):
                    return self.stack_manager[-1]
            Managed.__name__ = cls.__name__
            return Managed
        for name, cls in __language_api__.items():
            setattr(self, name, managed(cls))

    def pop_manager(self):
        self.stack_manager.pop()

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

@language_api
class Some(object):
    def __init__(self, name=None, **opts):
        self.name = name
        self.opts = opts
        self.dtype = self.__class__.__name__[4:] or None
        self.publish()
    def publish(self):
        self.mgr.register_some(self)
    def _decl_dtype(self, dtype):
        if self.dtype is None:
            self.dtype = dtype
        else:
            assert self.dtype == dtype, "Some used with incompatible types"
    def __str__(self):
        return f"Some{self.dtype}(\"{self.name}\")"
    def copy(self):
        return self

    def __ne__(left, right):
        if not isinstance(right, Some):
            raise TypeError()
        left.mgr.register_predicate("some_different", left, right)

    def assignments(self, solutions="subset-minimal", **kwargs):
        from .views import SomeView
        return SomeView(self, self.mgr.bo, solutions=solutions, **kwargs)
    def complementary_assignments(self, solutions="subset-minimal", **kwargs):
        if self.dtype == "Freeze":
            from .views import SomeFreezeComplementaryView
            return SomeFreezeComplementaryView(self, self.mgr.bo,
                    solutions=solutions, **kwargs)
        raise TypeError()

@language_api
class SomeFreeze(Some):
    default_opts = {
        "min_size": 0,
        "max_size": 1,
        "exclude": (),
    }

class BoContext(object):
    def __enter__(self):
        mgr = self._make_context()
        return ManagedIface(mgr, self.iface)
    def __exit__(self, *args):
        self.iface.pop_manager()

@language_api
class mutant(BoContext):
    def __init__(self, mutations):
        if isinstance(mutations, Some):
            mutations._decl_dtype("Freeze")
        else:
            for node in mutations:
                self.mgr.assert_node_exists(node)
        self.mutations = mutations
    def _make_context(self):
        return self.mgr.mutant_context(self.mutations)

@language_api
class action(mutant):
    def _make_context(self):
        return self.mgr.mutant_context(self.mutations, weak=True)

@language_api
class scope_reachability(BoContext):
    def __init__(self, **options):
        """
        monotone:
          - if True, component having same value in origin and target
            configurations cannot oscillate
        max_changes:
          - if int, limit the dimension of the hypercube used from computing the
            reachability property
        """
        self.__options = options
    def _make_context(self):
        return self.mgr.scope_reachability_context(self.__options)

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

@declare_operator("__rshift__") # >>
def allreach_operator(left, right):
    return left.iface.allreach(left, right)

@declare_operator("__truediv__") # /
def nonreach_operator(left, right):
    return left.iface.nonreach(left, right)

@declare_operator("__floordiv__") # //
def final_nonreach_operator(left, right):
    return left.iface.final_nonreach(left, right)

@declare_operator("__ne__") # !=
def different_operator(left, right):
    return left.iface.different(left, right)


class BonesisTerm(object):
    def __init__(self):
        assert hasattr(self, "mgr"), \
                "do not instantiate non-managed class!"
    def _set_iface(self, iface):
        self.iface = iface
        self.mgr = self.iface.manager

    def __ge__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '>=' operator")
    def __rshift__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '>>' operator")
    def __truediv__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '/' operator")
    def __floordiv__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '//' operator")
    def __ne__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '!=' operator")
    def __eq__(a, b):
        raise TypeError(f"'{a.__class__.__name__}' objects do not support '==' operator")

class BonesisVar(BonesisTerm):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.publish()
    def publish(self):
        pass
    def __hash__(self):
        return hash((self.__class__.__name__,self.name))

@allreach_operator
class ObservationVar(BonesisVar):
    def __init__(self, arg):
        if isinstance(arg, dict):
            name = None
            self.data = arg.copy()
        else:
            name = arg
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

class HypercubeVar(BonesisVar):
    def __init__(self, obs=None,
                     min_dimension=0,
                     max_dimension=None,
                     dimension=None):
        if dimension is not None:
            min_dimension = max_dimension = dimension
        self.min_dimension = min_dimension
        self.max_dimension = max_dimension
        if isinstance(obs, dict):
            obs = self.iface.obs(obs)
        self.obs = obs
        super().__init__(None)
    def publish(self):
        self.mgr.register_hypercube(self)
    def __str__(self):
        return f"Hypercube({id(self)})"
    def assignments(self, **kwargs):
        from .views import HypercubeView
        return HypercubeView(self, self.mgr.bo, **kwargs)
__language_api__["hypercube"] = HypercubeVar

@different_operator
@reach_operator
@allreach_operator
@nonreach_operator
@final_nonreach_operator
class ConfigurationVar(BonesisVar):
    def __init__(self, name=None, obs=None):
        self.obs = obs
        super().__init__(name)
    def publish(self):
        self.mgr.register_configuration(self)
    def __str__(self):
        return f"Configuration({repr(self.name or id(self))})"
    def __getitem__(self, node):
        return ConfigurationVarState(self, node)
    def __setitem__(self, node, right):
        self.mgr.assert_node_exists(node)
        if isinstance(right, bool):
            right = int(right)
        if isinstance(right, int):
            if not right in [0,1]:
                raise TypeError("cannot assign integers other than 0/1")
            self.mgr.register_predicate("cfg_assign", self, node, right)
        elif isinstance(right, ConfigurationVarState):
            self.mgr.register_predicate("cfg_node_eq", self, right.parent, node)
        else:
            raise TypeError(f"Invalid type for assignment {type(right)}")
    def assignments(self, **kwargs):
        from .views import ConfigurationView
        return ConfigurationView(self, self.mgr.bo, **kwargs)
__language_api__["cfg"] = ConfigurationVar

class ConfigurationVarState(object):
    def __init__(self, parent, node):
        self.parent = parent
        self.node = node
    def __eq__(self, b):
        self.parent[self.node] = b
    def __ne__(self, right):
        if not isinstance(right, ConfigurationVarState):
            raise TypeError(f"Invalid type for equality {type(right)}")
        self.parent.mgr.register_predicate("cfg_node_ne",
                self.parent,
                right.parent,
                self.node)


@language_api
class BonesisPredicate(BonesisTerm):
    def __init__(self, *args):
        self.args = args
        if not hasattr(self, "predicate_name"):
            self.predicate_name = self.__class__.__name__
        def auto_iface(obj):
            if isinstance(obj, BonesisTerm):
                if not hasattr(self, "iface"):
                    self._set_iface(obj.iface)
            elif isinstance(obj, (list, set, tuple)):
                [auto_iface(e) for e in obj]
        for obj in self.args:
            auto_iface(obj)
        assert hasattr(self, "mgr"), "Could not find manager"
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
@different_operator
class fixed(BonesisPredicate):
    def __init__(self, arg):
        if isinstance(arg, ConfigurationVar):
            self.predicate_name = "fixpoint"
        elif isinstance(arg, ObservationVar):
            self.predicate_name = "trapspace"
            arg = +arg
        elif isinstance(arg, HypercubeVar):
            self.predicate_name = "attractor"
        else:
            self.type_error()
        super().__init__(arg)

@language_api
@different_operator
class in_attractor(BonesisPredicate):
    def __init__(self, arg):
        if not isinstance(arg, ConfigurationVar):
            self.type_error()
        super().__init__(arg)

@language_api
class all_fixpoints(BonesisPredicate):
    _unit_types = (ObservationVar,ConfigurationVar)
    def __init__(self, arg):
        if isinstance(arg, (set, list, tuple)):
            for e in arg:
                if not isinstance(e, self._unit_types):
                    self.type_error()
        elif isinstance(arg, self._unit_types):
            arg = (arg,)
        else:
            self.type_error()
        super().__init__(arg)


@language_api
class all_attractors_overlap(all_fixpoints):
    pass


class _ConfigurableBinaryPredicate(BonesisPredicate):
    def __init__(self, left, right, options=None):
        left = self.left_arg(left)
        self.options = self.default_options if options is None else options
        self.closed = False
        if isinstance(right, str):
            self.options = (right,)
        elif isinstance(right, tuple) and set({type(t) for t in right}) == {str}:
            self.options = right
        else:
            self.closed = True
            right = self.right_arg(right)
        for opt in self.options:
            if opt not in self.supported_options:
                raise TypeError(f"unsupported option '{opt}'")
        super().__init__(left, right)

    def publish(self):
        if not self.closed:
            return
        self.mgr.register_predicate(self.predicate_name, self.options, *self.args)

    def __xor__(self, right):
        return self.__class__(self.left(), right, options=self.options)


@language_api
class allreach(_ConfigurableBinaryPredicate):
    _right_types = (ObservationVar,ConfigurationVar)
    supported_options = {"fixpoints", "attractors_overlap"}
    default_options = ("attractors_overlap",)
    """
    left: cfg, reach(), obs
    right: obs, set([obs])
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
        if isinstance(arg, celf._right_types):
            return {arg}
        elif isinstance(arg, set):
            for elt in arg:
                if not isinstance(elt, celf._right_types):
                    celf.type_error()
            return arg
        celf.type_error()


@reach_operator
@allreach_operator
@nonreach_operator
@final_nonreach_operator
@language_api
class reach(BonesisPredicate):
    """
    left: cfg, reach()
    right: cfg, obs, reach(), fixed(), in_attractor()
    """
    def __init__(self, left, right):
        left = self.left_arg(left)
        right = self.right_arg(right)
        super().__init__(left, right)
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
        if isinstance(arg, (fixed, in_attractor, reach)):
            return celf.right_arg(arg.left())
        celf.type_error()


@language_api
class nonreach(reach):
    def __init__(self, left, right):
        if isinstance(right, fixed):
            self.predicate_name = "final_nonreach"
        super().__init__(left, right)
    @classmethod
    def right_arg(celf, arg):
        if isinstance(arg, ObservationVar):
            celf.type_error() # universal constraint
        return super().right_arg(arg)

@language_api
class final_nonreach(nonreach):
    def __init__(self, left, right):
        if not isinstance(right, (fixed, in_attractor)):
            self.type_error()
        super().__init__(left, right)

@language_api
class different(BonesisPredicate):
    """
    left: cfg, fixed(), in_attractor()
    right: cfg, fixed(), in_attractor(), obs
    """
    def __init__(self, left, right):
        if isinstance(left, fixed):
            if left.predicate_name != "fixpoint":
                self.type_error()
            left = left.left()
        elif isinstance(left, in_attractor):
            left = left.left()
        if isinstance(right, fixed):
            if right.predicate_name != "fixpoint":
                self.type_error()
            right = right.right()
        elif isinstance(right, in_attractor):
            right = right.right()
        if not isinstance(left, ConfigurationVar) or \
                not isinstance(right, (ConfigurationVar,ObservationVar)):
            self.type_error()
        super().__init__(left, right)

@language_api
class custom(BonesisPredicate):
    def __init__(self, arg):
        if not isinstance(arg, str):
            self.type_error()
        super().__init__(arg)


class BonesisOptimization(object):
    def __init__(self):
        super().__init__()
        self.publish()
    def publish(self):
        name = self.__class__.__name__
        idx = name.index("_")
        opt = name[:idx]
        name = name[idx+1:]
        self.mgr.append_optimization(opt, name)

@language_api
class maximize_nodes(BonesisOptimization):
    pass
@language_api
class maximize_constants(BonesisOptimization):
    pass
@language_api
class maximize_strong_constants(BonesisOptimization):
    pass
