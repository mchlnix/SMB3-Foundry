from functools import partial
from typing import Callable, Iterable

hex_int = partial(int, base=16)


def lrange(a1: int, a2: int | None = None, a3: int | None = None, /):
    if a2 is None:
        return list(range(a1))

    if a3 is None:
        return list(range(a1, a2))

    return list(range(a1, a2, a3))


def apply(func: Callable, iterable: Iterable, *iterables: Iterable):
    return list(map(func, iterable, *iterables))


def clamp(minimum, value, maximum):
    return max(minimum, min(value, maximum))
