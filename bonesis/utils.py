
from itertools import chain

def frozendict(d):
    return frozenset(d.items())

class OverlayedDict(dict):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.overlayed = set()
    def __getitem__(self, key):
        if key in self.overlayed:
            return super().__getitem__(key)
        return self.parent[key]
    def get(self, key, default=None):
        if key not in self.overlayed:
            return self.parent.get(key, default)
        return self[key]
    def __setitem__(self, k, v):
        self.overlayed.add(k)
        super().__setitem__(k, v)
    def __contains__(self, k):
        return super().__contains__(k) or k in self.parent
    def keys(self):
        return chain(super().keys(),
                [k for k in self.parent.keys() if k not in self.overlayed])
    def items(self):
        return chain(super().items(),
                [(k,v) for (k,v) in self.parent.items() if k not in self.overlayed])
    def values(self):
        return chain(super().values(),
                [v for (k,v) in self.parent.items() if k not in self.overlayed])

