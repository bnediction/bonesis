import unittest

import bonesis

class TestConfiguration(unittest.TestCase):
    def test_node_equal1(self):
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

    def test_node_diff1(self):
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
