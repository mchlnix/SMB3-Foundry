"""
Describes all objects, that are part of a level, i. e. platforms, enemies, items, jumps, auto scroll objects etc.
"""
from abc import ABC
from typing import Optional

MIN_DOMAIN = 0
MAX_DOMAIN = 7
DOMAIN_COUNT = 8
MIN_Y_VALUE = 0
MAX_Y_VALUE = 27
MIN_ID_VALUE = 0
MAX_ID_VALUE = 0xFF
MIN_X_VALUE = 0
MAX_X_VALUE = 0xFF
MIN_ADDITIONAL_LENGTH = 0
MAX_ADDITIONAL_LENGTH = 0xFF

MAX_ENEMY_ITEM_ID = 0xEC


class InLevelObject(ABC):
    """
    Describes objects that are positioned at a specific place in a level and have some sort of representation, be it
    visible like platforms and enemies or invisible, like auto scroll items or jumps.
    """

    def __init__(self, data: bytearray):
        self._data: bytearray = data
        self._domain: int = 0
        self._id: int = 0
        self._x: int = 0
        self._y: int = 0
        self._length: Optional[int] = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def additional_length(self):
        return self._length

    @additional_length.setter
    def additional_length(self, value):
        self._length = value

    @property
    def has_additional_length(self):
        return self.additional_length is not None
