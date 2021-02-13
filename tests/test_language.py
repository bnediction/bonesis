
import unittest

import bonesis
import bonesis.language as bol

class LanguageTest(unittest.TestCase):
    def setUp(self):
        self.dom = bonesis.InfluenceGraph.complete("abc", 0)
        self.data = {
            "x": {"a": 0},
            "y": {"b": 0},
            "z": {"a": 1, "b": 1, "c": 1}}
    def _fresh_bo(self):
        return bonesis.BoNesis(self.dom, self.data)

    def test_different(self):
        bo = self._fresh_bo()
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        self.assertIsInstance(x != y, bol.different)
        fp_x = bo.fixed(x)
        fp_y = bo.fixed(y)
        self.assertIsInstance(fp_x != fp_y, bol.different)
        self.assertIsInstance(x != fp_y, bol.different)
        self.assertIsInstance(fp_x != y, bol.different)
        tp_z = bo.fixed(bo.obs("z"))
        with self.assertRaises(TypeError):
            tp_z != x
        with self.assertRaises(TypeError):
            bo.obs("x") != y

    def test_cfg_node_eq(self):
        bo = self._fresh_bo()
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x["c"] = y["c"]
        self.assertIsNone(x["c"] == y["c"])

    def test_cfg_node_ne(self):
        bo = self._fresh_bo()
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        self.assertIsNone(x["c"] != y["c"])
