import unittest

import bonesis

class TestFixed(unittest.TestCase):
    def setUp(self):
        self.dom1 = bonesis.InfluenceGraph.complete("abc", 1)
        self.data1 = {
            "000": {"a": 0, "b": 0, "c": 0},
            "111": {"a": 1, "b": 1, "c": 1},
        }

    def test_fixpoints(self):
        bo = bonesis.BoNesis(self.dom1, self.data1)
        bo.fixed(~bo.obs("000"))
        self.assertEqual(bo.boolean_networks().count(), 6859)

    def test_trapspace(self):
        bo = bonesis.BoNesis(self.dom1, self.data1)
        bo.fixed(bo.obs("000"))
        self.assertEqual(bo.boolean_networks().count(), 6859)
