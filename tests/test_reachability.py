import unittest

import bonesis

class NonReachTest(unittest.TestCase):
    def setUp(self):
        self.bn1 = bonesis.BooleanNetwork({"a": "b", "b": "c", "c": 1})
        self.bn2 = bonesis.BooleanNetwork({"a": "b", "b": "c", "c": "c"})
        self.bn3 = bonesis.BooleanNetwork({"a": "b", "b": "c", "c": "!c"})
        self.data = {}
        for a in [0,1]:
            for b in [0,1]:
                for c in [0,1]:
                    self.data[f"{a}{b}{c}"] = {"a": a, "b": b, "c": c}

    def test_irreflexive(self):
        bo = bonesis.BoNesis(self.bn1, self.data)
        bo.set_constant("bounded_nonreach", 0)
        +bo.obs("000") / +bo.obs("000")
        self.assertFalse(bo.is_satisfiable())

    def test_positive(self):
        for x, y in [
                ("001", "000"),
                ("000", "010"),
                ("000", "110"),
                ("000", "100")]:
            bo = bonesis.BoNesis(self.bn1, self.data)
            bo.set_constant("bounded_nonreach", 0)
            +bo.obs(x) / +bo.obs(y)
            self.assertTrue(bo.is_satisfiable(), f"nonreach({x},{y})")

    def test_negative(self):
        for x, y in [
                ("000", "111"),
                ("010", "110"),
                ("010", "100")]:
            bo = bonesis.BoNesis(self.bn1, self.data)
            bo.set_constant("bounded_nonreach", 0)
            +bo.obs(x) / +bo.obs(y)
            self.assertFalse(bo.is_satisfiable(), f"nonreach({x},{y})")

    def test_bounded(self):
        for x, y, b, t in [
                ("001", "000", 1, self.assertTrue),
                ("000", "010", 2, self.assertTrue),
                ("000", "100", 1, self.assertFalse),
                ("000", "100", 2, self.assertTrue),
                ]:
            bo = bonesis.BoNesis(self.bn1, self.data)
            bo.set_constant("bounded_nonreach", b)
            +bo.obs(x) / +bo.obs(y)
            t(bo.is_satisfiable(), f"nonreach({x},{y},{b})")

    def test_final(self):
        for bn, x, y, t in [
                ("bn1", "000", "111", self.assertFalse),
                ("bn2", "001", "111", self.assertFalse),
                ("bn2", "110", "000", self.assertFalse),
                ("bn2", "001", "000", self.assertTrue),
                ("bn2", "110", "111", self.assertTrue),
                ]:
            bo = bonesis.BoNesis(getattr(self, bn), self.data)
            +bo.obs(x) // bo.fixed(~bo.obs(y))
            t(bo.is_satisfiable(), f"final_nonreach({x},{y}) [{bn}]")

    def test_scope(self):
        bn = self.bn3
        x = bn.zero()
        for scope, target, t in [
                ({}, {"a": 1, "c": 0}, self.assertTrue),
                ({"monotone": True}, {"a": 1, "c": 0}, self.assertFalse),
                ({"monotone": True}, {"a": 1}, self.assertTrue),
                ({"max_changes": 1}, {"a": 1}, self.assertFalse),
                ({"max_changes": 2}, {"a": 1}, self.assertFalse),
                ({"max_changes": 2}, {"b": 1}, self.assertTrue),
                ({"max_changes": 3}, {"a": 1}, self.assertTrue),
                ]:
            bo = bonesis.BoNesis(bn)
            with bo.scope_reachability(**scope):
                ~bo.obs(x) >= ~bo.obs(target)
                t(bo.is_satisfiable(),
                    f"scope_reachability({scope}) >= {target}")
