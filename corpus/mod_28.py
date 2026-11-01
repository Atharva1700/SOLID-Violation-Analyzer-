class Cohesive28:
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

def route_28(event):
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

class Mixed28:
    def __init__(self):
        self._db = []
        self._template = "<p>{}</p>"

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

from typing import Protocol


class Five28(Protocol):
    def a(self): ...
    def b(self): ...
    def c(self): ...
    def d(self): ...
    def e(self): ...

from typing import Protocol


class Narrow28(Protocol):
    def read(self): ...
    def write(self, x): ...
    def close(self): ...
