class Cohesive39:
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

def route_39(event):
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

def dispatch_39(event):
    if isinstance(event, int):
        return "int"
    if isinstance(event, str):
        return "str"
    if isinstance(event, bytes):
        return "bytes"
    return "other"

from typing import Protocol


class Five39(Protocol):
    def a(self): ...
    def b(self): ...
    def c(self): ...
    def d(self): ...
    def e(self): ...

from typing import Protocol


class Narrow39(Protocol):
    def read(self): ...
    def write(self, x): ...
    def close(self): ...
