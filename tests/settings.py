from bonesis.utils import OverlayedDict
s1 = {"a": 1, "b": 2}
s2 = OverlayedDict(s1)
print(list(s2.keys()))
print(list(s2.items()))
print(s2.get("a"))
s2["a"] = 3
print(list(s2.keys()))
print(list(s2.items()))
print(s2.get("a"))
