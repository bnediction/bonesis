# Copyright or © or Copr. Loïc Paulevé (2023)
#
# loic.pauleve@cnrs.fr
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
#

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

