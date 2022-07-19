from abc import ABC

from PySide6.QtCore import QRect

from foundry.game.gfx.objects.object_like import ObjectLike
from smb3parse.data_points import Position


# TODO sort out x_position and y_position
class MapObject(ObjectLike, ABC):
    def __init__(self, pos: Position):
        super(MapObject, self).__init__()

        self.pos = pos

        self.rect = QRect(self.x_position, self.y_position, 1, 1)

        self.is_single_block = True

    @property
    def x_position(self):
        return self.pos.xy[0]

    @x_position.setter
    def x_position(self, value):
        self.pos = Position.from_xy(value, self.pos.y)

    @property
    def y_position(self):
        return self.pos.y

    @y_position.setter
    def y_position(self, value):
        self.pos.y = value

    def set_position(self, x, y):
        x = int(x)
        y = int(y)

        self.rect = QRect(x, y, 1, 1)

        self.x_position = x
        self.y_position = y

    def get_position(self):
        return self.pos.xy

    def render(self):
        pass

    def to_bytes(self):
        return self.type

    def move_by(self, dx, dy):
        self.set_position(self.x_position + dx, self.y_position + dy)

    def resize_to(self, x, y):
        return

    def resize_by(self, dx, dy):
        return

    def point_in(self, x, y):
        return self.rect.contains(x, y)

    def __contains__(self, point):
        pass

    def __repr__(self):
        return f"MapObject #{hex(self.type)}: '{self.name}' at {self.x_position}, {self.y_position}"
