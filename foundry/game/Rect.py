from PySide2.QtCore import QRect
from foundry.core.geometry.Size.Size import Size
from foundry.core.geometry.Position.Position import Position


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

    def dirty_intersecting(self, rect):
        for pos in self.positions():
            for other_pos in rect.positions():
                if pos == other_pos:
                    return True
        return False

    def to_relative_position(self, obj) -> Position:
        """Return the position of a position assuming it is inside the rect"""
        if isinstance(obj, Rect):
            return obj.pos + self.pos
        elif isinstance(obj, Position):
            return obj + self.pos
        else:
            return NotImplemented

    def relative_position(self, obj) -> Position:
        """Gets the relative position of a rect"""
        if isinstance(obj, Rect):
            return obj.pos - self.pos
        elif isinstance(obj, Position):
            return obj - self.pos
        else:
            return NotImplemented

    def normalize_position(self, obj) -> Position:
        """Normalizes a position in terms of this rect"""
        if isinstance(obj, Rect):
            return obj.pos + self.pos
        elif isinstance(obj, Position):
            return obj + self.abs_pos
        else:
            return NotImplemented

    def pos_from_relative_rect_position(self, rect, pos):
        """
        Finds the position of a relative position inside another rect in terms of this rect
        :param Rect rect: The relative Rect
        :param Position pos: The relative Position
        :return: The real position
        :rtype Position
        """
        return self.normalize_position(rect.normalize_position(pos))

    def pos_index_relative_rect_positions(self, rect, width=True) -> int:
        """
        Makes a generator that finds the position of a relative position inside another rect in terms of this rect
        as an index
        :param rect: Rect rect: The relative Rect
        :param width: Determines if the width or height is the low or high value
        :return: An index for a matrix
        :rtype: int
        """
        positions = rect.positions(width)
        for pos in positions:
            normalized_pos = self.pos_from_relative_rect_position(rect, pos)
            yield self.index_position(normalized_pos, width)

    @property
    def indexes(self):
        """
        Provides the total amount of positions (width * height)
        :return: int
        """
        return self.abs_size.width * self.abs_size.height

    def index_position(self, pos: Position, width=True) -> int:
        """
        Converts position to an index for a matrix
        :param Position pos: A relative position for a matrix
        :param bool width: Determines if the width or height is the low or high value
        :return: An index for a matrix
        :rtype: int
        """
        return self.abs_size.index_position(pos, width)

    def position_from_index(self, x: int) -> Position:
        """Provides the position from a index"""
        return Position(x % self.abs_size.width, x // self.abs_size.width)

    def width_positions(self) -> Position:
        """
        Provides a generator for every relative position inside the width
        :return: A generator of relative positions
        :rtype: Generator of Positions
        """
        generator = self._index_positions(width=True)
        yield next(generator)

    def height_positions(self):
        """
        Provides a generator for every relative position inside the height
        :return: A generator of relative positions
        :rtype: Generator of Positions
        """
        generator = self._index_positions(width=False)
        yield next(generator)

    def position_indexes(self):
        """Provides a range of position index to iterate over"""
        return range(self.abs_size.height * self.abs_size.width)

    def positions(self, width=True):
        """
        Provides every single idx from the matrix of positions in terms of the current rect's position
        :param bool width: Determines if we are finding the width or height
        :return: A generator of relative positions
        :rtype: Generator of Positions
        """
        for pos in self.relative_positions(width):
            yield pos + self.abs_pos

    def relative_positions(self, width=True):
        """
        Provides every single idx from the matrix of positions
        :param bool width: Determines if we are finding the width or height
        :return: A generator of relative positions
        :rtype: Generator of Positions
        """
        for pos in self._index_positions(not width):
            for other_pos in self._index_positions(width):
                yield pos + other_pos

    def _index_positions(self, width=True):
        """
        Provides a generator for every relative position inside the width/height
        :param bool width: Determines if we are finding the width or height
        :return: A generator of relative positions
        :rtype: Generator of Positions
        """
        if width:
            return self.abs_size.width_positions()
        else:
            return self.abs_size.height_positions()

    @classmethod
    def scale_from(cls, rect: QRect, scale_factor: int):
        """Returns a new rect with the scaled dimensions"""
        pos = Rect._abs_pos(rect)
        pos *= scale_factor
        size = Rect._abs_size(rect)
        size *= scale_factor
        return cls.from_size_and_position(size, pos)

    @classmethod
    def from_qrect(cls, qrect: QRect):
        """Makes a qrect become a rect"""
        return cls.from_size_and_position(Rect._abs_size(qrect), Rect._abs_pos(qrect))

    @classmethod
    def from_size_and_position(cls, size: Size, pos: Position):
        """Make a rect from a size and position"""
        return cls(pos.to_qt(), size.to_qt())
