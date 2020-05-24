from dataclasses import dataclass
from PySide2.QtCore import QPoint


@dataclass
class Position:
    _x: float = 0
    _y: float = 0

    @property
    def x(self):
        return int(self._x)

    @x.setter
    def x(self, pos):
        self._x = pos

    @property
    def y(self):
        return int(self._y)

    @y.setter
    def y(self, pos):
        self._y = pos

    def x_with_offset(self, offset: float):
        """Provides an offset to the x position"""
        return self.x + offset

    def y_with_offset(self, offset: float):
        """Provides an offset to the y position"""
        return self.y + offset

    def to_qt(self) -> QPoint:
        """Returns the qpoint version of position"""
        return QPoint(int(self.x), int(self.y))

    def scale_to(self, scale_factor):
        """Scales both x and y by a scale factor"""
        self.x *= scale_factor
        self.y *= scale_factor

    @classmethod
    def from_qt(cls, qpoint: QPoint):
        """Transfer qpoint to a position"""
        return cls(*qpoint.toTuple())

    @classmethod
    def scale_from(cls, pos, scale_factor):
        """Scales both x and y by a scale factor and creates a new object"""
        return cls(pos.x * scale_factor, pos.y * scale_factor)

    def __add__(self, other):
        """Adds both x and y together"""
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        else:
            return Position(self.x + other, self.y + other)

    def __radd__(self, other):
        """Adds both x and y together"""
        return self.__add__(other)

    def __sub__(self, other):
        """Subtract both x and y together"""
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        else:
            return Position(self.x - other, self.y - other)

    def __rsub__(self, other):
        """Subtract both x and y together"""
        if isinstance(other, Position):
            return Position(other.x - self.x, other.y - self.y)
        else:
            return Position(other - self.x, other - self.y)

    def __mul__(self, other):
        """Multiply both x and y together"""
        if isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y)
        else:
            return Position(self.x * other, self.y * other)

    def __rmul__(self, other):
        """Multiply both x and y together"""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(self.x / other.x, self.y / other.y)
        else:
            return Position(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(other.x / self.x, other.y / self.y)
        else:
            return Position(other / self.x, other / self.y)

    


class LevelPosition(Position):
    SCREEN_WIDTH = 0x10

    @property
    def rel_x(self):
        """The x position in terms of the screen the position is in"""
        return self.x % self.SCREEN_WIDTH

    @property
    def rel_x_inverse(self) -> int:
        """The x position in terms of the screen from right to left"""
        return self.SCREEN_WIDTH - self.rel_x

    @property
    def screen_pos(self) -> int:
        """Provides a way to combine the x and y position, useful for recreating in-game logic"""
        return self.x + (self.y * self.SCREEN_WIDTH)

    @classmethod
    def from_pos(cls, pos: Position):
        return cls(pos.x, pos.y)
