import unittest

import bonesis


class TestConfiguration(unittest.TestCase):
    def test_node_equal1(self):
        pkn = bonesis.InfluenceGraph.complete(
            "abc", sign=1, loops=False, allow_skipping_nodes=False
        )
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

    def test_node_diff1(self):
        pkn = bonesis.InfluenceGraph.complete(
            "abc", sign=1, loops=False, allow_skipping_nodes=False
        )
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

    def test_node_comp(self):
        pkn = bonesis.InfluenceGraph.complete(
            "ab", sign=1, loops=False, allow_skipping_nodes=False
        )
        data = {
            "x": {"a": 0},
            "y": {"a": 1},
        }
        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x["b"] = 1
        y["b"] < x["b"]

        vals = list(y.assignments())
        self.assertEqual(len(vals), 1)
        self.assertEqual(vals[0]["b"], 0)

        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x["b"] = 1
        y["b"] <= x["b"]

        vals = list(y.assignments())
        self.assertEqual(len(vals), 2)

        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        x["b"] = 1
        y["b"] > x["b"]

        vals = list(y.assignments())
        self.assertEqual(len(vals), 0)

        bo = bonesis.BoNesis(pkn, data)
        x = ~bo.obs("x")
        y = ~bo.obs("y")
        y["b"] > 0

        vals = list(y.assignments())
        self.assertEqual(len(vals), 1)
        self.assertEqual(vals[0]["b"], 1)
