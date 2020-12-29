"""
This module includes the AbstractBlock
BlockWidget: An abstract representation of what a block is.  Unlike gfx/Block this is meant to retain state.
"""

from typing import Optional

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.core.geometry.Size.Size import Size

from .AbstractBlock import AbstractBlock


class Block(AbstractBlock):
    """A generic implementation of a Block"""

    @classmethod
    def from_tsa(
            cls,
            size: Optional[Size],
            index: int,
            ptn_tbl: PatternTableHandler,
            pal_set: PaletteSet,
            tsa_offset: int,
            transparency: bool = True
    ):
        """Creates a block from a tsa offset"""
        from foundry.game.File import ROM, TSA_TABLE_SIZE, TSA_TABLE_INTERVAL
        tsa_data = ROM().bulk_read(TSA_TABLE_SIZE, (tsa_offset * TSA_TABLE_INTERVAL) + 0x10)
        return cls(size, index, ptn_tbl, pal_set, tsa_data, transparency)

    @property
    def size(self) -> Size:
        """The size of the block in units of 16 pixels"""
        return self._size

    @size.setter
    def size(self, size: Size) -> None:
        self._size = size

    @property
    def index(self) -> int:
        """The index of the block"""
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        self._index = index

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        return self._tsa_data

    @tsa_data.setter
    def tsa_data(self, tsa_data: bytearray) -> None:
        self._tsa_data = tsa_data

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return self._transparency

    @transparency.setter
    def transparency(self, transparency: bool) -> None:
        self._transparency = transparency
