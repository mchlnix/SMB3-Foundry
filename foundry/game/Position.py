from dataclasses import dataclass
from PySide2.QtCore import QPoint

@dataclass
class Position:
    x: int = 0
    y: int = 0

    def to_qt(self) -> QPoint:
        """Returns the qpoint version of position"""
        return QPoint(self.x, self.y)

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