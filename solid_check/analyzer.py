"""Static SOLID heuristics on Python source, using only the ast module.

Metrics per class and function:
  cyclomatic complexity (McCabe-style count of decision points), method length (lines),
  LCOM (LCOM1 over non-dunder methods: pairs sharing no self attribute minus pairs
  sharing one, floored at 0).

Flags (thresholds fixed before measuring, see THRESHOLDS):
  SRP  class with LCOM >= 3 and at least 4 non-dunder methods
  OCP  a function with at least 3 isinstance() calls (type dispatch to extend by editing)
  ISP  a Protocol or ABC class with at least 6 methods
Not detected: LSP and DIP (they need type information this analysis does not have).
"""
import ast
import time
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

THRESHOLDS = {"lcom": 3, "min_methods_for_lcom": 4, "isinstance_chain": 3, "protocol_methods": 6}


@dataclass
class ClassReport:
    module: str
    name: str
    methods: int
    lcom: int
    max_cc: int
    max_method_len: int
    flags: list = field(default_factory=list)


@dataclass
class FunctionReport:
    module: str
    name: str
    cc: int
    length: int
    isinstance_calls: int
    flags: list = field(default_factory=list)


def cyclomatic(node):
    cc = 1
    for n in ast.walk(node):
        if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler)):
            cc += 1
        elif isinstance(n, ast.BoolOp):
            cc += len(n.values) - 1
        elif isinstance(n, ast.comprehension):
            cc += len(n.ifs) + 1
    return cc


def length(node):
    return node.end_lineno - node.lineno + 1


def isinstance_calls(node):
    return sum(1 for n in ast.walk(node)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance")


def self_attrs(fn):
    return {n.attr for n in ast.walk(fn)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "self"}


def lcom1(methods):
    names = {m.name for m in methods}
    attrs = {m.name: self_attrs(m) - names for m in methods}
    p = q = 0
    for a, b in combinations(methods, 2):
        if attrs[a.name] & attrs[b.name]:
            q += 1
        else:
            p += 1
    return max(p - q, 0)


def base_names(cls):
    out = set()
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.add(b.id)
        elif isinstance(b, ast.Attribute):
            out.add(b.attr)
    return out


def analyse_source(source: str, module: str):
    tree = ast.parse(source, filename=module)
    classes, functions = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            public = [m for m in methods if not (m.name.startswith("__") and m.name.endswith("__"))]
            rep = ClassReport(
                module=module, name=node.name, methods=len(public),
                lcom=lcom1(public) if len(public) >= 2 else 0,
                max_cc=max((cyclomatic(m) for m in methods), default=0),
                max_method_len=max((length(m) for m in methods), default=0))
            is_interface = bool(base_names(node) & {"Protocol", "ABC"})
            has_state = any(self_attrs(m) for m in public)
            # LCOM only means something for classes with instance state; interfaces are stateless
            if (not is_interface and has_state
                    and rep.lcom >= THRESHOLDS["lcom"]
                    and rep.methods >= THRESHOLDS["min_methods_for_lcom"]):
                rep.flags.append("SRP")
            if is_interface and rep.methods >= THRESHOLDS["protocol_methods"]:
                rep.flags.append("ISP")
            classes.append(rep)
        elif isinstance(node, ast.FunctionDef):
            rep = FunctionReport(module, node.name, cyclomatic(node), length(node), isinstance_calls(node))
            if rep.isinstance_calls >= THRESHOLDS["isinstance_chain"]:
                rep.flags.append("OCP")
            functions.append(rep)
    return classes, functions


def analyse_tree(root: Path):
    """Analyse every .py file under root. Returns (class_reports, function_reports, seconds)."""
    t0 = time.perf_counter()
    classes, functions = [], []
    for p in sorted(Path(root).glob("*.py")):
        c, f = analyse_source(p.read_text(), p.stem)
        classes += c
        functions += f
    return classes, functions, time.perf_counter() - t0


def module_flags(classes, functions):
    """Set of flags per module, from class and function reports."""
    out = {}
    for r in classes + functions:
        if r.flags:
            out.setdefault(r.module, set()).update(r.flags)
    return out
