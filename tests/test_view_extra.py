import unittest

import bonesis
import mpbn

class testExtraView(unittest.TestCase):
    def setUp(self):
        pkn = bonesis.InfluenceGraph.complete("abc", sign=1, loops=False,
                allow_skipping_nodes=False)
        data = {
            "x": {"a": 0, "b": 0},
            "y": {"a": 1, "b": 1},
        }
        bo = bonesis.BoNesis(pkn, data)
        ~bo.obs("x") >= ~bo.obs("y")
        self.bo1 = bo

    def test_no_extra(self):
        c = 2
        for bn in self.bo1.boolean_networks(limit=c):
            self.assertIsInstance(bn, mpbn.MPBooleanNetwork)
            c -= 1
        self.assertEqual(c, 0)

    def test_extra_configurations(self):
        for view in [self.bo1.boolean_networks,
                        self.bo1.diverse_boolean_networks]:
            c = 2
            for bn, cfg in view(limit=c, extra="configurations"):
                self.assertIsInstance(bn, mpbn.MPBooleanNetwork)
                self.assertIsInstance(cfg, dict)
                self.assertEqual(set(cfg.keys()), {"x","y"})
                c -= 1
            self.assertEqual(c, 0)
