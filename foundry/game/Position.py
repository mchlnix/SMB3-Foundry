from typing import Union, overload
from dataclasses import dataclass
from PySide2.QtCore import QPoint


@dataclass
class Position:
    _x: float = 0
    _y: float = 0

    @property
    def x(self) -> int:
        return int(self._x)

    @x.setter
    def x(self, pos: Union[int, float]) -> None:
        self._x = pos

    @property
    def y(self) -> int:
        return int(self._y)

    @y.setter
    def y(self, pos: Union[int, float]) -> None:
        self._y = pos

    @overload
    def x_with_offset(self, offset: float) -> float:
        """"""

    @overload
    def x_with_offset(self, offset: int) -> int:
        """"""

    def x_with_offset(self, offset: Union[int, float]) -> Union[float, int]:
        """Provides an offset to the x position"""
        return self.x + offset

    @overload
    def y_with_offset(self, offset: float) -> float:
        """"""

    @overload
    def y_with_offset(self, offset: int) -> int:
        """"""

    def y_with_offset(self, offset: Union[int, float]) -> Union[float, int]:
        """Provides an offset to the y position"""
        return self.y + offset

    def invert(self) -> "Position":
        """
        Invert the y and x positions
        :return: The inverted position
        :rtype: Position
        """
        return Position(self._y, self._x)

    def to_qt(self) -> QPoint:
        """Returns the qpoint version of position"""
        return QPoint(int(self.x), int(self.y))

    def to_index(self, mod: int, width: bool = True) -> int:
        """
        Converts position to an index for a matrix
        :param int mod: Determines how big the width or height is
        :param bool width: Determines if the width or height is the low or high value
        :return: An index for a matrix
        :rtype: int
        """
        hi, lo = self.x if not width else self.y, self.x if width else self.y
        return hi * mod + lo

    @classmethod
    def from_pos(cls, pos: "Position") -> "Position":
        """
        Makes a position from a position
        :param Position pos: The position to be copied
        :return: The copied position
        :rtype: Position
        """
        return Position(pos._x, pos._y)

    @classmethod
    def from_qt(cls, qpoint: QPoint) -> "Position":
        """Transfer qpoint to a position"""
        x, y = qpoint.toTuple()
        return cls(x, y)

    @classmethod
    def scale_from(cls, pos: "Position", scale_factor: Union[int, float]) -> "Position":
        """Scales both x and y by a scale factor and creates a new object"""
        return cls(pos._x * scale_factor, pos._y * scale_factor)

    def __add__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Adds both x and y together"""
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x + other, self.y + other)
        else:
            return NotImplemented

    def __radd__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Adds both x and y together"""
        return self.__add__(other)

    def __sub__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Subtract both x and y together"""
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x - other, self.y - other)
        else:
            return NotImplemented

    def __rsub__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Subtract both x and y together"""
        if isinstance(other, Position):
            return Position(other.x - self.x, other.y - self.y)
        elif isinstance(other, (int, float)):
            return Position(other - self.x, other - self.y)

    def __mul__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Multiply both x and y together"""
        if isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x * other, self.y * other)
        else:
            return NotImplemented

    def __rmul__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Multiply both x and y together"""
        return self.__mul__(other)

    def __truediv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x / other, self.y / other)
        else:
            return NotImplemented

    def __rtruediv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(other.x / self.x, other.y / self.y)
        elif isinstance(other, (int, float)):
            return Position(other / self.x, other / self.y)
        else:
            return NotImplemented

    def __floordiv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(self.x // other.x, self.y // other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x // other, self.y // other)
        else:
            return NotImplemented

    def __rfloordiv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Divide both x and y together"""
        if isinstance(other, Position):
            return Position(other.x // self.x, other.y // self.y)
        elif isinstance(other, (int, float)):
            return Position(other // self.x, other // self.y)
        else:
            return NotImplemented

    def __mod__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Mod both x and y together"""
        if isinstance(other, Position):
            return Position(self.x % other.x, self.y % other.y)
        elif isinstance(other, (int, float)):
            return Position(self.x % other, self.y % other)
        else:
            return NotImplemented

    def __rmod__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Mod both x and y together"""
        if isinstance(other, Position):
            return Position(other.x % self.x, other.y % self.y)
        elif isinstance(other, (int, float)):
            return Position(other % self.x, other % self.y)
        else:
            return NotImplemented

    def __iadd__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity add"""
        if isinstance(other, Position):
            self.x += other.x
            self.y += other.y
        elif isinstance(other, (int, float)):
            self.x += other
            self.y += other
        else:
            return NotImplemented
        return self

    def __isub__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity subtract"""
        if isinstance(other, Position):
            self.x -= other.x
            self.y -= other.y
        elif isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
        else:
            return NotImplemented
        return self

    def __imul__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity multiply"""
        if isinstance(other, Position):
            self.x *= other.x
            self.y *= other.y
        elif isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
        else:
            return NotImplemented
        return self

    def __itruediv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity division"""
        if isinstance(other, Position):
            self.x /= other.x
            self.y /= other.y
        elif isinstance(other, (int, float)):
            self.x /= other
            self.y /= other
        else:
            return NotImplemented
        return self

    def __ifloordiv__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity divide"""
        if isinstance(other, Position):
            self.x //= other.x
            self.y //= other.y
        elif isinstance(other, (int, float)):
            self.x //= other
            self.y //= other
        else:
            return NotImplemented
        return self

    def __imod__(self, other: Union["Position", int, float]) -> Union["Position"]:
        """Implicity mod"""
        if isinstance(other, Position):
            self.x %= other.x
            self.y %= other.y
        elif isinstance(other, (int, float)):
            self.x %= other
            self.y %= other
        else:
            return NotImplemented
        return self


class LevelPosition(Position):
    SCREEN_WIDTH = 0x10

    @property
    def rel_x(self) -> int:
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
    def from_pos(cls, pos: Position) -> "LevelPosition":
        return cls(pos.x, pos.y)
