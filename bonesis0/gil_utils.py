
from queue import Queue
from threading import Thread

class BGIteratorOnDemand:
    """
    Creates a thread at each iteration
    """
    def __init__(self, it, ctl):
        self.it = it
        self.ctl = ctl
        self.q = Queue(1)

    def __next__(self):
        def proxy():
            try:
                elt = next(self.it)
                self.q.put(elt)
            except StopIteration:
                self.q.put(None)
        t = Thread(target=proxy, daemon=True)
        t.start()
        try:
            elt = self.q.get()
        except KeyboardInterrupt:
            self.ctl.interrupt()
            elt = None
        if elt is None:
            raise StopIteration
        t.join()
        return elt


class BGIteratorPersistent(object):
    def __init__(self, it, ctl):
        self.it = it
        self.ctl = ctl
        self.q = Queue(1)
        self.w = Queue(1)
        def proxy():
            while self.w.get():
                try:
                    elt = next(self.it)
                    self.q.put(elt)
                except StopIteration:
                    self.q.put(None)
                    return
        self.t = Thread(target=proxy, daemon=True)
        self.t.start()

    def __next__(self):
        self.w.put(1)
        try:
            elt = self.q.get()
        except KeyboardInterrupt:
            self.ctl.interrupt()
            elt = None
        if elt is None:
            raise StopIteration
        return elt

    def quit(self):
        self.w.put(None)
