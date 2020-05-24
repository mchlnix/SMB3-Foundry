from dataclasses import dataclass
from PySide2.QtCore import QSize


@dataclass
class Size:
    """Defines a 2d shape"""
    _width: float = 0
    _height: float = 0

    @property
    def width(self):
        return int(self._width)

    @width.setter
    def width(self, width):
        self._width = width

    @property
    def height(self):
        return int(self._height)

    @height.setter
    def height(self, height):
        self._height = height

    def to_qt(self) -> QSize:
        return QSize(self.width, self.height)

    def scale_to(self, scale_factor):
        """Scales width and height by a scale factor"""
        self.width *= scale_factor
        self.height *= scale_factor

    @classmethod
    def scale_from(cls, size, scale_factor: int):
        """Scales width and height by a scale factor and produces a new size"""
        return cls(size.width * scale_factor, size.height * scale_factor)

    @classmethod
    def from_qt(cls, qsize: QSize):
        """Returns the Qsize version of the object"""
        return cls(*qsize.toTuple())

    @classmethod
    def from_dict(cls, dic: dict, default_width: int = 1, default_height: int = 1):
        """Makes a 2d size from a dictionary of values"""
        width = dic["width"] if "width" in dic else default_width
        height = dic["height"] if "height" in dic else default_height
        return cls(width, height)

    def __add__(self, other):
        if isinstance(other, Size):
            return Size(self.width + other.width, self.height + other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width + other, self.height + other)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Size):
            return Size(self.width - other.width, self.height - other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width - other, self.height - other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, Size):
            return Size(other.width - self.width, other.height - self.height)
        elif isinstance(other, (int, float)):
            return Size(other - self.width, other - self.height)

    def __mul__(self, other):
        if isinstance(other, Size):
            return Size(self.width * other.width, self.height * other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width * other, self.height * other)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Size):
            return Size(self.width / other.width, self.height / other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width / other, self.height / other)
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, Size):
            return Size(other.width / self.width, other.height / self.height)
        elif isinstance(other, (int, float)):
            return Size(other / self.width, other / self.height)
        else:
            return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Size):
            return Size(self.width // other.width, self.height // other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width // other, self.height // other)
        else:
            return NotImplemented

    def __rfloordiv__(self, other):
        if isinstance(other, Size):
            return Size(other.width // self.width, other.height // self.height)
        elif isinstance(other, (int, float)):
            return Size(other // self.width, other // self.height)
        else:
            return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Size):
            return Size(self.width % other.width, self.height % other.height)
        elif isinstance(other, (int, float)):
            return Size(self.width % other, self.height % other)
        else:
            return NotImplemented

    def __rmod__(self, other):
        if isinstance(other, Size):
            return Size(other.width % self.width, other.height % self.height)
        elif isinstance(other, (int, float)):
            return Size(other % self.width, other % self.height)
        else:
            return NotImplemented

    def __iadd__(self, other):
        """Implicity add"""
        if isinstance(other, Size):
            self.width += other.width
            self.height += other.height
        elif isinstance(other, (int, float)):
            self.width += other
            self.height += other
        else:
            return NotImplemented
        return self

    def __isub__(self, other):
        """Implicity subtract"""
        if isinstance(other, Size):
            self.width -= other.width
            self.height -= other.height
        elif isinstance(other, (int, float)):
            self.width -= other
            self.height -= other
        else:
            return NotImplemented
        return self

    def __imul__(self, other):
        """Implicity multiply"""
        if isinstance(other, Size):
            self.width *= other.width
            self.height *= other.height
        elif isinstance(other, (int, float)):
            self.width *= other
            self.height *= other
        else:
            return NotImplemented
        return self

    def __itruediv__(self, other):
        """Implicity division"""
        if isinstance(other, Size):
            self.width /= other.width
            self.height /= other.height
        elif isinstance(other, (int, float)):
            self.width /= other
            self.height /= other
        else:
            return NotImplemented
        return self

    def __ifloordiv__(self, other):
        """Implicity divide"""
        if isinstance(other, Size):
            self.width //= other.width
            self.height //= other.height
        elif isinstance(other, (int, float)):
            self.width //= other
            self.height //= other
        else:
            return NotImplemented
        return self

    def __imod__(self, other):
        """Implicity mod"""
        if isinstance(other, Size):
            self.width %= other.width
            self.height %= other.height
        elif isinstance(other, (int, float)):
            self.width %= other
            self.height %= other
        else:
            return NotImplemented
        return self
