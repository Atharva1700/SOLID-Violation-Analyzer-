class Cohesive1:
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

def route_1(event):
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

class Logged1:
    def __init__(self):
        self._db = []
        self._template = "<p>{}</p>"
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

from typing import Protocol


class Five1(Protocol):
    def a(self): ...
    def b(self): ...
    def c(self): ...
    def d(self): ...
    def e(self): ...

from typing import Protocol


class Narrow1(Protocol):
    def read(self): ...
    def write(self, x): ...
    def close(self): ...
