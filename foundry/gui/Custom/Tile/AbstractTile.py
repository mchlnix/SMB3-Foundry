"""
This module includes the AbstractBlock
BlockWidget: An abstract representation of what a block is.  Unlike gfx/Block this is meant to retain state.
"""


from abc import abstractmethod
from typing import Optional
from PySide2.QtGui import QPainter

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import Palette
from foundry.game.gfx.drawable.Tile import Tile

from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size


class AbstractTile:
    """The abstract representation of a block"""
    def __init__(
            self,
            size: Optional[Size],
            index: int,
            ptn_tbl: PatternTableHandler,
            pallet: Palette,
            transparency: bool = True
    ) -> None:
        self._size = size
        self._index = index
        self._pattern_table = ptn_tbl
        self._palette = pallet
        self._transparency = transparency

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.size}, {self.index}, {self.pattern_table}, " \
               f"{self.palette}, {self.transparency})"

    @property
    @abstractmethod
    def size(self) -> Size:
        """The size of the tile in units of 8 pixels"""

    @size.setter
    @abstractmethod
    def size(self, size: Size) -> None:
        """"""

    @property
    @abstractmethod
    def index(self) -> int:
        """The index of the tile"""

    @index.setter
    def index(self, index: int) -> None:
        """"""

    @property
    @abstractmethod
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tile"""

    @pattern_table.setter
    @abstractmethod
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        """"""

    @property
    @abstractmethod
    def palette(self) -> Palette:
        """The palette currently used by tile"""

    @palette.setter
    @abstractmethod
    def palette(self, palette_set: Palette) -> None:
        """"""

    @property
    @abstractmethod
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""

    @transparency.setter
    @abstractmethod
    def transparency(self, transparency: bool) -> None:
        """"""

    @property
    def tile(self) -> Tile:
        """The actual tile provided"""
        return Tile.from_rom_and_palette(self.index, self.palette, self.pattern_table)

    def draw(self, painter: QPainter, position: Position, size: Optional[Size] = None,
             transparency: Optional[bool] = None):
        """Draws the tile to a given point"""
        size = size if size is not None else self.size * 16
        transparency = transparency if transparency is not None else self.transparency
        self.tile.draw(painter, position, size, transparent=transparency)
