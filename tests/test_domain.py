import unittest

import bonesis

class TestInfluenceGraph(unittest.TestCase):
    def test_complete(self):
        dom = bonesis.InfluenceGraph.complete(3, 1, loops=False, exact=True)
        bo = bonesis.BoNesis(dom)
        bns = bo.boolean_networks()
        self.assertEqual(bns.count(), 8)
