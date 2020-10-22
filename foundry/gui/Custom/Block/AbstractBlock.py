"""
This module includes the AbstractBlock
BlockWidget: An abstract representation of what a block is.  Unlike gfx/Block this is meant to retain state.
"""


from abc import abstractmethod
from typing import Optional
from PySide2.QtGui import QPainter

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.drawable.Block import Block

from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size


class AbstractBlock:
    """The abstract representation of a block"""
    def __init__(
            self,
            size: Optional[Size],
            index: int,
            ptn_tbl: PatternTableHandler,
            pal_set: PaletteSet,
            tsa_data: bytearray,
            transparency: bool = True
    ) -> None:
        self._size = size
        self._index = index
        self._pattern_table = ptn_tbl
        self._palette_set = pal_set
        self._tsa_data = tsa_data
        self._transparency = transparency

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.size}, {self.index}, {self.pattern_table}, " \
               f"{self.palette_set}, {self.tsa_data}, {self.transparency})"

    @property
    @abstractmethod
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""

    @size.setter
    @abstractmethod
    def size(self, size: Size) -> None:
        """"""

    @property
    @abstractmethod
    def index(self) -> int:
        """The index of the block"""

    @index.setter
    def index(self, index: int) -> None:
        """"""

    @property
    @abstractmethod
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""

    @property
    @abstractmethod
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""

    @pattern_table.setter
    @abstractmethod
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        """"""

    @property
    @abstractmethod
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""

    @palette_set.setter
    @abstractmethod
    def palette_set(self, palette_set: PaletteSet) -> None:
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
    def block(self) -> Block:
        """The actual block provided"""
        return Block.from_rom(self.index, self.palette_set, self.pattern_table, self.tsa_data)

    def draw(self, painter: QPainter, position: Position, size: Optional[Size] = None,
             transparency: Optional[bool] = None):
        """Draws the block to a given point"""
        size = size if size is not None else self.size
        transparency = transparency if transparency is not None else self.transparency
        self.block.draw(painter, position, size, transparency)
