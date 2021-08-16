import unittest

import bonesis

class TestFilters(unittest.TestCase):
    def setUp(self):
        self.dom1 = bonesis.InfluenceGraph.complete("ab", 0)

    def test_nocyclic(self):
        bo = bonesis.BoNesis(self.dom1)
        view = bo.boolean_networks(no_cyclic_attractors=True)
        self.assertEqual(view.count(), 115) # over 196
        view = bo.boolean_networks(limit=10, no_cyclic_attractors=True)
        self.assertEqual(view.count(), 10)
