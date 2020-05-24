from PySide2.QtCore import QRect
from foundry.game.Size import Size
from foundry.game.Position import Position


class Rect(QRect):
    """Add properties to the original qrect for additional functionality"""

    @property
    def abs_size(self):
        """Returns the size of the rect"""
        return self._abs_size(self)

    @staticmethod
    def _abs_size(qrect: QRect):
        """Legacy method for qrects"""
        return Size.from_qt(qrect.size())

    @property
    def abs_pos(self):
        """Returns the position of the rect"""
        return self._abs_pos(self)

    @staticmethod
    def _abs_pos(qrect: QRect):
        """Legacy method for qrects"""
        return Position.from_qt(qrect.topLeft())

    @classmethod
    def scale_from(cls, rect: QRect, scale_factor: int):
        """Returns a new rect with the scaled dimensions"""
        pos = Position.scale_from(Rect._abs_pos(rect), scale_factor)
        size = Size.scale_from(Rect._abs_size(rect), scale_factor)
        return cls.from_size_and_position(size, pos)

    @classmethod
    def from_qrect(cls, qrect: QRect):
        """Makes a qrect become a rect"""
        return cls.from_size_and_position(Rect._abs_size(qrect), Rect._abs_pos(qrect))

    @classmethod
    def from_size_and_position(cls, size: Size, pos: Position):
        """Make a rect from a size and position"""
        return cls(pos.to_qt(), size.to_qt())
