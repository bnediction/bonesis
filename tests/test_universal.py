import unittest

import bonesis

class TestUniversal(unittest.TestCase):
    def setUp(self):
        self.dom1 = bonesis.InfluenceGraph.complete("abc", 1)
        self.data1 = {
            "0": {"a": 0, "b": 0, "c": 0},
            "1": {"a": 1, "b": 1, "c": 1},
        }

    def test_allfixpoints(self):
        bo = bonesis.BoNesis(self.dom1, self.data1)
        bo.fixed(bo.obs("0"))
        bo.all_fixpoints({bo.obs("0")})
        self.assertEqual(bo.boolean_networks().count(), 355)
        bo.all_fixpoints({bo.obs("0"), bo.obs("1")})
        self.assertEqual(bo.boolean_networks().count(), 355)
        bo.all_fixpoints({bo.obs("1")})
        self.assertEqual(bo.boolean_networks().count(), 0)
