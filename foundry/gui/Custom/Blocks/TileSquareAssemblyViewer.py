

from typing import Optional

from PySide2.QtCore import QSize
from PySide2.QtGui import QPaintEvent, QPainter
from PySide2.QtWidgets import QWidget

from foundry.core.geometry.Position.Position import Position
from foundry.core.geometry.Size.Size import Size
from foundry.core.Settings.util import get_setting

from foundry.game.File import ROM, TSA_TABLE_SIZE, TSA_TABLE_INTERVAL

from foundry.game.gfx.PatternTableHandler import PatternTableHandler
from foundry.game.gfx.Palette import PaletteSet
from foundry.game.gfx.drawable.Block import Block


class TileSquareAssemblyViewer(QWidget):
    """Views the tile in a given tsa"""
    def __init__(
            self,
            parent: Optional[QWidget],
            ptn_tbl: PatternTableHandler,
            pal_set: PaletteSet,
            tsa_offset: int
            ) -> None:
        super().__init__(parent)
        self.parent = parent
        self.can_update = False
        self.pattern_table = ptn_tbl
        self.palette_set = pal_set
        self.size = Size(1, 1)
        self.tsa_offset = tsa_offset
        self._tsa_data = None
        self.can_update = True
        self.update()

    def synthetic_update(self):
        """Updates the widget safely and quickly"""
        if self.can_update:
            self.update()

    @property
    def tsa_data(self) -> bytearray:
        """Find the tsa data from a given offset"""
        if not self._tsa_data:
            return ROM().bulk_read(TSA_TABLE_SIZE, (self.tsa_offset * TSA_TABLE_INTERVAL) + 0x10)
        else:
            return self._tsa_data

    @property
    def tsa_offset(self) -> int:
        """The offset in banks to the current tsa"""
        return self._tsa_offset

    @tsa_offset.setter
    def tsa_offset(self, offset: int) -> None:
        self._tsa_offset = offset
        self.synthetic_update()

    @property
    def pattern_table(self) -> PatternTableHandler:
        """The pattern table for the tiles"""
        return self._pattern_table

    @pattern_table.setter
    def pattern_table(self, pattern_table: PatternTableHandler) -> None:
        self._pattern_table = pattern_table
        self.synthetic_update()

    @property
    def size(self) -> Size:
        """The size of the blocks"""
        return self._size

    @size.setter
    def size(self, size: Size) -> None:
        self._size = size
        self.synthetic_update()

    @property
    def palette_set(self) -> PaletteSet:
        """The palette currently used by the tsa"""
        return self._palette_set

    @palette_set.setter
    def palette_set(self, palette_set: PaletteSet) -> None:
        self._palette_set = palette_set
        self.synthetic_update()

    @property
    def transparency(self) -> bool:
        """Determines if the blocks will be transparent"""
        return get_setting("block_transparency", True)

    def sizeHint(self):
        """The ideal size of the widget"""
        return QSize(Block.image_length * self.size.width, Block.image_height * self.size.height)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the widget"""
        painter = QPainter(self)

        for i in range(0x100):
            block = Block.from_rom(i, self.palette_set, self.pattern_table, self.tsa_data)

            x = (i % 0x10) * Block.image_length * self.size.width
            y = (i // 0x10) * Block.image_height * self.size.height

            block.draw(
                painter,
                Position(x, y),
                Size(Block.image_length * self.size.width, Block.image_length * self.size.width),
                transparent=self.transparency
            )

        super().paintEvent(event)