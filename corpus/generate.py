"""Generate 40 synthetic modules with planted SOLID violations and confounders.

Labels record which principles were planted (ground truth). The analyzer never reads them.
Seeded: python corpus/generate.py
"""
import json
import random
from pathlib import Path

SEED = 20261031
N = 40
HERE = Path(__file__).resolve().parent

SRP_CLASS = '''class {name}:
    def __init__(self):
        self._db = []
        self._template = "<p>{{}}</p>"

    def load_a(self):
        self._db.append(1)
        return len(self._db)

    def load_b(self):
        return self._db[:]

    def load_c(self):
        self._db.clear()

    def render_a(self):
        return self._template.format("a")

    def render_b(self):
        return self._template.upper()

    def render_c(self):
        return self._template * 2
'''

COHESIVE_CLASS = '''class {name}:
    def __init__(self):
        self._items = []

    def add(self, x):
        self._items.append(x)

    def remove(self, x):
        self._items.remove(x)

    def size(self):
        return len(self._items)

    def first(self):
        return self._items[0] if self._items else None

    def clear(self):
        self._items.clear()

    def items(self):
        return list(self._items)
'''

OCP_FUNC = '''def {name}(event):
    if isinstance(event, int):
        return "int"
    if isinstance(event, str):
        return "str"
    if isinstance(event, bytes):
        return "bytes"
    return "other"
'''

BRANCHY_CLEAN_FUNC = '''def {name}(event):
    # many decisions, but no type dispatch: complex, not an OCP violation
    if event is None:
        return 0
    if event > 10 and event < 100:
        return 1
    if event % 2 == 0 or event % 3 == 0:
        return 2
    for i in range(3):
        if i == event:
            return 3
    return 4
'''

ISP_PROTOCOL = '''from typing import Protocol


class {name}(Protocol):
    def a(self): ...
    def b(self): ...
    def c(self): ...
    def d(self): ...
    def e(self): ...
    def f(self): ...
    def g(self): ...
'''

SMALL_PROTOCOL = '''from typing import Protocol


class {name}(Protocol):
    def read(self): ...
    def write(self, x): ...
    def close(self): ...
'''


SRP_SHARED_LOG = '''class {name}:
    def __init__(self):
        self._db = []
        self._template = "<p>{{}}</p>"
        self._log = []

    def load_a(self):
        self._db.append(1)
        self._log.append("a")

    def load_b(self):
        self._log.append("b")
        return self._db[:]

    def load_c(self):
        self._db.clear()
        self._log.append("c")

    def render_a(self):
        self._log.append("ra")
        return self._template.format("a")

    def render_b(self):
        self._log.append("rb")
        return self._template.upper()

    def render_c(self):
        self._log.append("rc")
        return self._template * 2
'''

BRIDGE_CLASS = '''class {name}:
    def __init__(self):
        self._a = []
        self._b = []

    def a1(self):
        self._a.append(1)

    def a2(self):
        return len(self._a)

    def a3(self):
        self._a.clear()

    def b1(self):
        self._b.append(1)

    def b2(self):
        return len(self._b)

    def b3(self):
        self._b.clear()

    def both(self):
        return len(self._a) + len(self._b)
'''

OCP_TWO = '''def {name}(event):
    if isinstance(event, int):
        return "int"
    if isinstance(event, str):
        return "str"
    return "other"
'''

ISP_FIVE = '''from typing import Protocol


class {name}(Protocol):
    def a(self): ...
    def b(self): ...
    def c(self): ...
    def d(self): ...
    def e(self): ...
'''


def build(seed=SEED):
    """Each module: a cohesive class and a clean function (confounders), plus optional
    planted violations, plus optional hard confounders. Labels list only planted violations."""
    rng = random.Random(seed)
    labels = {}
    for i in range(N):
        mod = f"mod_{i:02d}"
        parts, planted = [], set()
        parts.append(COHESIVE_CLASS.format(name=f"Cohesive{i}"))
        parts.append(BRANCHY_CLEAN_FUNC.format(name=f"route_{i}"))
        # planted violations, about half the modules
        if rng.random() < 0.5:
            k = rng.choice(["SRP", "SRP_LOG", "OCP", "ISP"])
            if k == "SRP":
                parts.append(SRP_CLASS.format(name=f"Mixed{i}")); planted.add("SRP")
            elif k == "SRP_LOG":  # real SRP violation, but the shared logger hides it from LCOM
                parts.append(SRP_SHARED_LOG.format(name=f"Logged{i}")); planted.add("SRP")
            elif k == "OCP":
                parts.append(OCP_FUNC.format(name=f"dispatch_{i}")); planted.add("OCP")
            else:
                parts.append(ISP_PROTOCOL.format(name=f"Wide{i}")); planted.add("ISP")
        # hard confounders, never planted
        h = rng.random()
        if h < 0.25:
            parts.append(BRIDGE_CLASS.format(name=f"Bridged{i}"))
        elif h < 0.5:
            parts.append(ISP_FIVE.format(name=f"Five{i}"))
        elif h < 0.75:
            parts.append(OCP_TWO.format(name=f"two_{i}"))
        parts.append(SMALL_PROTOCOL.format(name=f"Narrow{i}"))
        (HERE / f"{mod}.py").write_text("\n".join(parts))
        labels[mod] = sorted(planted)
    (HERE / "labels.json").write_text(json.dumps(labels, indent=2))
    return labels


if __name__ == "__main__":
    labels = build()
    print(sum(1 for v in labels.values() if v), "of", N, "modules have planted violations")
