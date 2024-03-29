import abc
from abc import ABC

from PySide6.QtCore import QRect

from foundry.game.gfx.objects.object_like import ObjectLike


# TODO sort out x_position and y_position
class MapObject(ObjectLike, ABC):
    def __init__(self):
        super(MapObject, self).__init__()

        self.name = type(self).__name__

    @property
    def x_position(self):
        return self.get_position()[0]

    @x_position.setter
    def x_position(self, value):
        self.set_position(value, self.y_position)

    @property
    def y_position(self):
        return self.get_position()[1]

    @y_position.setter
    def y_position(self, value):
        self.set_position(self.x_position, value)

    @abc.abstractmethod
    def set_position(self, x, y):
        pass

    @abc.abstractmethod
    def get_position(self):
        pass

    @property
    def rect(self):
        return QRect(self.x_position, self.y_position, 1, 1)

    def move_by(self, dx, dy):
        self.set_position(self.x_position + dx, self.y_position + dy)

    def point_in(self, x, y):
        return x, y == self.get_position()

    def __repr__(self):
        return f"MapObject #{self.type:#x}: '{self.name}' at {self.x_position}, {self.y_position}"
