class Cohesive3:
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

def route_3(event):
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

from typing import Protocol


class Narrow3(Protocol):
    def read(self): ...
    def write(self, x): ...
    def close(self): ...
