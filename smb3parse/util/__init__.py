from typing import Callable, Iterable

# I haven't figured out how to do type stubs for nested rust modules
from rsmb3parse.util import Point, Rect, clamp, hex_int

from .rom import INESHeader, Rom


def apply(func: Callable, iterable: Iterable, *iterables: Iterable):
    return list(map(func, iterable, *iterables))


__all__ = [
    "apply",
    "clamp",
    "hex_int",
    "Point",
    "Rect",
    "INESHeader",
    "Rom",
]
