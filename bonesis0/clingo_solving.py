import clingo

def setup_clingo_solve_handler(settings, ctrl):
    if settings.get("timeout"):
        sh = BoSolveHandle(ctrl, timeout=settings.get("timeout"),
                    fail_if_timeout=settings.get("fail_if_timeout"))
    else:
        sh = ctrl.solve(yield_=True)
    return sh

class BoSolveHandle(object):
    def __init__(self, clingo_ctrl, timeout=0, fail_if_timeout=True):
        self.clingo_sh = clingo_ctrl.solve(async_=True, yield_=True)
        self.timeout = timeout
        self.fail_if_timeout = fail_if_timeout
        self.__exited = False

    def cancel(self):
        self.clingo_sh.cancel()

    def __iter__(self):
        with self.clingo_sh:
            while True:
                self.clingo_sh.resume()
                if self.timeout > 0:
                    ready = self.clingo_sh.wait(self.timeout)
                    if not ready: # time out
                        self.clingo_sh.cancel()
                        if self.fail_if_timeout:
                            raise TimeoutError
                        else:
                            break
                else:
                    ready = self.clingo_sh.wait()
                m = self.clingo_sh.model()
                if m is None:
                    break
                yield m
