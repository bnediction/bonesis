import unittest

class TestOverlayedDict(unittest.TestCase):
    def test(self):
        from bonesis.utils import OverlayedDict
        d = {"a": 1, "b": 2}
        od = OverlayedDict(d)
        self.assertEqual(set(od.keys()), {"a", "b"})
        self.assertEqual(set(od.items()), {("a", 1), ("b", 2)})
        self.assertEqual(od.get("a"), 1)
        self.assertEqual(od["a"], 1)
        od["a"] = 3
        self.assertEqual(set(od.keys()), {"a", "b"})
        self.assertEqual(set(od.items()), {("a", 3), ("b", 2)})
        self.assertEqual(od.get("a"), 3)
        self.assertEqual(od["a"], 3)
        self.assertEqual(d, {"a": 1, "b": 2})
