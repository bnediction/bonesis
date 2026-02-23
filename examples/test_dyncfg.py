
import bonesis
from bonesis.snippets import all_different

dom = bonesis.BooleanNetwork({
    "a": 1,
    "b": "a",
    "c": "!a&b"})
data = {
    "O1": {"a": 0, "b": 0, "c": 0},
    "O2": {        "b": 1, "c": 0},
    "O3": {"a": 1, "b": 1, "c": 1}
}

bo = bonesis.BoNesis(dom, data)
x1 = ~bo.obs("O1")
x2 = ~bo.obs("O2")
x3 = ~bo.obs("O3")
all_different({x1,x2,x3})
x1 >= x2 >= x3
print(bo.is_satisfiable())


bo = bonesis.BoNesis(dom, data)
x1 = ~bo.obs("O1")
x2 = bo.dyncfg("O2")
x3 = ~bo.obs("O3")
all_different({x1,x2,x3})
x1 >= x2 >= x3
print(bo.is_satisfiable())
