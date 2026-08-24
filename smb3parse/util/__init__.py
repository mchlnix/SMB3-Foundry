from typing import Callable, Iterable

# I haven't figured out how to do type stubs for nested rust modules
from rsmb3parse import util  # type: ignore

from .rom import INESHeader, Rom

clamp = util.clamp
hex_int = util.hex_int

Point = util.Point
Rect = util.Rect


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
