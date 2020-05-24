from dataclasses import dataclass
from PySide2.QtCore import QSize

@dataclass
class Size:
    """Defines a 2d shape"""
    width: int = 0
    height: int = 0

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
