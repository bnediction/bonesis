from queue import Queue
from threading import Thread

def setup_gil_iterator(settings, it, sh, ctl):
    g = settings.get("clingo_gil_workaround")
    if g == 1:
        it = BGIteratorPersistent(it, sh, ctl)
    elif g == 2:
        it = BGIteratorOnDemand(it, sh, ctl)
    return it

class BGIteratorOnDemand:
    """
    Creates a thread at each iteration
    """
    def __init__(self, it, sh, ctl):
        self.it = it
        self.ctl = ctl
        self.sh = sh
        self.q = Queue(1)

    def __next__(self):
        def proxy():
            elt = next(self.it, None)
            self.q.put(elt)
        t = Thread(target=proxy, daemon=True)
        t.start()
        try:
            elt = self.q.get()
        except KeyboardInterrupt:
            self.sh.cancel()
            self.ctl.interrupt()
            elt = None
        if elt is None:
            raise StopIteration
        t.join()
        return elt


class BGIteratorPersistent(object):
    def __init__(self, it, sh, ctl):
        self.it = it
        self.sh = sh
        self.ctl = ctl
        self.q = Queue(1)
        self.w = Queue(1)
        def proxy():
            while self.w.get():
                try:
                    elt = next(self.it, None)
                except Exception as e:
                    self.q.put(e)
                    break
                self.q.put(elt)
                if elt is None:
                    break
        self.t = Thread(target=proxy, daemon=True)
        self.t.start()

    def __next__(self):
        self.w.put(1)
        try:
            elt = self.q.get()
        except KeyboardInterrupt:
            self.sh.cancel()
            self.ctl.interrupt()
            elt = None
        if isinstance(elt, Exception):
            raise elt
        if elt is None:
            raise StopIteration
        return elt

    def quit(self):
        self.w.put(None)
