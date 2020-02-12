
import sys

__enabled = False

def enable_debug():
    global __enabled
    __enabled = True

def disable_debug():
    global __enabled
    __enabled = False

def debug_enabled():
    return __enabled

def dbg(msg):
    if debug_enabled():
        print(f"bonesis: {msg}", file=sys.stderr)

