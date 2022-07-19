import abc
from typing import Tuple

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter

from foundry.game import EXPANDS_NOT


class ObjectLike(abc.ABC):
    _obj_index: int
    domain: int
    name: str

    x_position: int
    y_position: int

    # TODO too ambiguous to be part of an API?
    type: int
    selected: bool

    rect: QRect

    is_4byte: bool

    def __init__(self):
        self.selected = False

    @property
    def obj_index(self):
        return self._obj_index

    @obj_index.setter
    def obj_index(self, value):
        self._obj_index = value

    @abc.abstractmethod
    def render(self):
        pass

    @abc.abstractmethod
    def draw(self, painter: QPainter, block_length, transparent):
        pass

    @abc.abstractmethod
    def get_status_info(self):
        pass

    @abc.abstractmethod
    def set_position(self, x, y):
        pass

    def move_by(self, dx, dy):
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    @abc.abstractmethod
    def get_position(self) -> Tuple[int, int]:
        pass

    @abc.abstractmethod
    def resize_by(self, dx, dy):
        pass

    @abc.abstractmethod
    def point_in(self, x, y):
        pass

    def get_rect(self, block_length=1) -> QRect:
        if block_length != 1:
            x, y = self.rect.topLeft().toTuple()
            w, h = self.rect.size().toTuple()

            x *= block_length
            w *= block_length
            y *= block_length
            h *= block_length

            return QRect(x, y, w, h)
        else:
            return self.rect

    @abc.abstractmethod
    def change_type(self, new_type):
        pass

    @abc.abstractmethod
    def __contains__(self, point):
        pass

    @abc.abstractmethod
    def to_bytes(self):
        pass

    def expands(self):
        return EXPANDS_NOT

    def primary_expansion(self):
        return EXPANDS_NOT
