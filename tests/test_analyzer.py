import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from solid_check.analyzer import analyse_source, cyclomatic, lcom1  # noqa: E402
import ast  # noqa: E402


def fn(src):
    return ast.parse(src).body[0]


def test_cyclomatic_counts_decision_points():
    f = fn("def f(x):\n    if x:\n        return 1\n    for i in x:\n        pass\n    return 0")
    assert cyclomatic(f) == 3  # 1 + if + for


def test_cyclomatic_counts_boolean_operators_and_comprehension_ifs():
    f = fn("def f(a, b):\n    return a and b or [i for i in a if i]")
    # 1 + (values-1 of 'and' = 1) + ('or' = 1) + comprehension if (1) + comprehension base (1)
    assert cyclomatic(f) == 5


def test_lcom_is_zero_for_fully_shared_state():
    cls = ast.parse("class A:\n def a(self): return self.x\n def b(self): self.x=1\n def c(self): return self.x").body[0]
    assert lcom1(cls.body) == 0


def test_lcom_detects_two_disjoint_clusters():
    src = ("class A:\n def a1(self): return self.p\n def a2(self): return self.p\n"
           " def b1(self): return self.q\n def b2(self): return self.q")
    cls = ast.parse(src).body[0]
    # pairs: (a1,a2) share, (b1,b2) share, 4 cross pairs share nothing -> 4 - 2 = 2
    assert lcom1(cls.body) == 2


def test_srp_flagged_for_two_disjoint_clusters_with_state():
    src = ("class A:\n def __init__(self):\n  self.p=1\n  self.q=2\n"
           " def a1(self): return self.p\n def a2(self): return self.p\n def a3(self): return self.p\n"
           " def b1(self): return self.q\n def b2(self): return self.q\n def b3(self): return self.q\n")
    classes, _ = analyse_source(src, "m")
    assert "SRP" in classes[0].flags


def test_stateless_protocol_is_not_srp_but_is_isp_when_wide():
    src = ("from typing import Protocol\nclass P(Protocol):\n" + "".join(f" def m{i}(self): ...\n" for i in range(6)))
    classes, _ = analyse_source(src, "m")
    assert classes[0].flags == ["ISP"]


def test_ocp_flag_needs_three_isinstance_calls():
    two = "def f(x):\n if isinstance(x,int): return 1\n if isinstance(x,str): return 2\n"
    three = two + " if isinstance(x,bytes): return 3\n"
    assert analyse_source(two, "m")[1][0].flags == []
    assert analyse_source(three, "m")[1][0].flags == ["OCP"]


def test_method_length_is_measured():
    classes, _ = analyse_source("class A:\n def f(self):\n  x=1\n  return x\n", "m")
    assert classes[0].max_method_len == 3
