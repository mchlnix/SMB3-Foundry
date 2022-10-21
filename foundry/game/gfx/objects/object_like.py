import abc

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter


class ObjectLike(abc.ABC):
    # TODO too ambiguous to be part of an API?
    # This whole thing with everything needing to be a property to be type consistent kinda blows...
    selected: bool

    rect: QRect

    def __init__(self):
        self.selected = False
        self._name = ""
        self._type = 0

        self._x_position = 0
        self._y_position = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def x_position(self):
        return self._x_position

    @x_position.setter
    def x_position(self, value):
        self._x_position = value

    @property
    def y_position(self):
        return self._y_position

    @y_position.setter
    def y_position(self, value):
        self._y_position = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @abc.abstractmethod
    def draw(self, painter: QPainter, block_length, transparent):
        pass

    def copy(self):
        pass

    def set_position(self, x, y):
        self.x_position = x
        self.y_position = y

    def move_by(self, dx, dy):
        x, y = self.get_position()
        new_x = x + dx
        new_y = y + dy

        self.set_position(new_x, new_y)

    def get_position(self) -> tuple[int, int]:
        return self.x_position, self.y_position

    def point_in(self, x, y):
        return self.rect.contains(x, y)

    def get_rect(self, block_length=1) -> QRect:
        x = self.rect.topLeft().x()
        y = self.rect.topLeft().y()

        w = self.rect.size().width()
        h = self.rect.size().height()

        x *= block_length
        w *= block_length
        y *= block_length
        h *= block_length

        return QRect(x, y, w, h)

    @abc.abstractmethod
    def change_type(self, new_type):
        pass
