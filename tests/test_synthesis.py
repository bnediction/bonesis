import unittest

import bonesis

def bodebug(bo):
    with open("/tmp/debug.asp", "w") as fp:
        bo.aspmodel.make()
        fp.write(str(bo.aspmodel))


class configurationTest(unittest.TestCase):
    def test_equal1(self):
        pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
                allow_skipping_nodes=False)
        data = {
            "x": {"a": 0},
            "y": {"a": 1},
        }
        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x >= y
        x["c"] = y["c"]

        for _, cfgs in bo.boolean_networks(limit=15, extra="configurations"):
            self.assertEqual(cfgs["x"]["c"], cfgs["y"]["c"])

    def test_equal1(self):
        pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
                allow_skipping_nodes=False)
        data = {
            "x": {"a": 0},
            "y": {"a": 1},
        }
        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x >= y
        x["c"] != y["c"]

        for _, cfgs in bo.boolean_networks(limit=15, extra="configurations"):
            self.assertNotEqual(cfgs["x"]["c"], cfgs["y"]["c"])


class nonreachTest(unittest.TestCase):
    def setUp(self):
        self.bn1 = bonesis.BooleanNetwork({"a": "b", "b": "c", "c": 1})
        self.bn2 = bonesis.BooleanNetwork({"a": "b", "b": "c", "c": "c"})
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
