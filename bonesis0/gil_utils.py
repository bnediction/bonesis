from queue import Queue
from threading import Thread
import signal

def setup_gil_iterator(settings, it, sh, ctl):
    g = settings.get("clingo_gil_workaround")
    soft = settings["soft_interrupt"]
    if g == 1:
        it = BGIteratorPersistent(it, sh, ctl, soft_interrupt=soft)
    elif g == 2:
        it = BGIteratorOnDemand(it, sh, ctl, soft_interrupt=soft)
    return it

class BGIteratorOnDemand:
    """
    Creates a thread at each iteration
    """
    def __init__(self, it, sh, ctl, soft_interrupt=False):
        self.it = it
        self.ctl = ctl
        self.sh = sh
        self.q = Queue(1)
        self.soft_interrupt = soft_interrupt

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
            if not self.soft_interrupt:
                raise
        if elt is None:
            raise StopIteration
        t.join()
        return elt


class BGIteratorPersistent(object):
    def __init__(self, it, sh, ctl, soft_interrupt=False):
        self.it = it
        self.sh = sh
        self.ctl = ctl
        self.q = Queue(1)
        self.w = Queue(1)
        self.soft_interrupt = soft_interrupt
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
            if not self.soft_interrupt:
                raise
        if isinstance(elt, Exception):
            raise elt
        if elt is None:
            raise StopIteration
        return elt

    def quit(self):
        self.w.put(None)
