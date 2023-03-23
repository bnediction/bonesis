import unittest

import bonesis

class TestFixed(unittest.TestCase):
    def setUp(self):
        self.dom1 = bonesis.InfluenceGraph.complete("abc", 1)
        self.data1 = {
            "000": {"a": 0, "b": 0, "c": 0},
            "111": {"a": 1, "b": 1, "c": 1},
        }
        self.dom2 = bonesis.InfluenceGraph.complete("abc", -1)

    def test_fixpoints(self):
        bo = bonesis.BoNesis(self.dom1, self.data1)
        bo.fixed(~bo.obs("000"))
        self.assertEqual(bo.boolean_networks().count(), 6859)

    def test_trapspace(self):
        bo = bonesis.BoNesis(self.dom1, self.data1)
        bo.fixed(bo.obs("000"))
        self.assertEqual(bo.boolean_networks().count(), 6859)

    def test_mintrap(self):
        bo = bonesis.BoNesis(self.dom1)
        h = bo.hypercube(min_dimension=1)
        bo.fixed(h)
        self.assertEqual(len(list(h.assignments(limit=1))), 0)

        bo = bonesis.BoNesis(self.dom2)
        h = bo.hypercube(min_dimension=2)
        bo.fixed(h)
        val = next(iter(h.assignments()))
        self.assertGreaterEqual(sum((1 for v in val.values() if v == '*')), 2)

        bo = bonesis.BoNesis(self.dom2)
        h = bo.hypercube(max_dimension=0)
        bo.fixed(h)
        val = next(iter(h.assignments()))
        self.assertEqual(sum((1 for v in val.values() if v == '*')), 0)
