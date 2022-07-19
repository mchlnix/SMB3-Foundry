import abc
from typing import Tuple

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter


class ObjectLike(abc.ABC):
    name: str

    # TODO too ambiguous to be part of an API?
    type: int
    selected: bool

    rect: QRect

    x_position: int
    y_position: int

    def __init__(self):
        self.selected = False

    @abc.abstractmethod
    def draw(self, painter: QPainter, block_length, transparent):
        pass

    def set_position(self, x, y):
        self.x_position = x
        self.y_position = y

    def move_by(self, dx, dy):
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    def get_position(self) -> Tuple[int, int]:
        return self.x_position, self.y_position

    def point_in(self, x, y):
        return self.rect.contains(x, y)

    def get_rect(self, block_length=1) -> QRect:
        x, y = self.rect.topLeft().toTuple()
        w, h = self.rect.size().toTuple()

        x *= block_length
        w *= block_length
        y *= block_length
        h *= block_length

        return QRect(x, y, w, h)

    @abc.abstractmethod
    def change_type(self, new_type):
        pass
