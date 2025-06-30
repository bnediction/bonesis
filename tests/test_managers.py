
import unittest

import bonesis
import bonesis.language as bol

class ManagersTest(unittest.TestCase):
    def setUp(self):
        self.dom = bonesis.InfluenceGraph.complete("abc", 0)
        self.data = {
            "x": {"a": 0},
            "y": {"b": 0},
            "z": {"a": 1, "b": 1, "c": 1}}
    def _fresh_bo(self):
        return bonesis.BoNesis(self.dom, self.data)

    def test_override(self):
        bo = self._fresh_bo()
        with bo.scope_reachability(monotone=True):
            with bo.scope_reachability(monotone=False):
                ~bo.obs("x") >= ~bo.obs("y")

        for pname, args, kwargs in bo.manager.properties:
            match pname:
                case "reach":
                    self.assertEqual(kwargs, {"monotone": False})


    def test_mixed_cascade(self):
        mutant = {"c": 0}
        bo = self._fresh_bo()
        with bo.scope_reachability(monotone=True):
            with bo.mutant(mutant):
                ~bo.obs("x") >= ~bo.obs("y")

        for pname, args, kwargs in bo.manager.properties:
            match pname:
                case "mutant":
                    self.assertEqual(args, (1, mutant))
                    self.assertEqual(kwargs, {})
                case "reach":
                    self.assertEqual(kwargs, {"mutant": 1, "monotone": True})

